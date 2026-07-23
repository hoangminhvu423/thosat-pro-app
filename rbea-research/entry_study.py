#!/usr/bin/env python3
"""
Entry-reference & TP study cho sleeve BREAK — theo PREREG_ENTRY_TP_STUDY.md
Chạy: python3 entry_study.py <path_to_ohlc_csv>
Data indicative (nguồn công khai) — phải chạy lại trên XAU_30m_data.csv chuẩn để vào hồ sơ.
"""
COST_R=0.0
import sys, csv, math, statistics as st
from datetime import datetime

# ---------- load & normalize ----------
def load(path):
    rows=[]
    with open(path, newline='') as f:
        sample=f.readline(); f.seek(0)
        delim=';' if (sample.count(';')>sample.count(',')) else ('\t' if sample.count('\t')>sample.count(',') else ',')
        rd=csv.reader(f, delimiter=delim)
        header=next(rd)
        h=[c.strip().lower() for c in header]
        def idx(*names):
            for n in names:
                for i,c in enumerate(h):
                    if c==n: return i
            for n in names:
                for i,c in enumerate(h):
                    if n in c: return i
            return None
        di=idx('datetime','date','time','timestamp'); oi=idx('open'); hi=idx('high'); li=idx('low'); ci=idx('close')
        if None in (oi,hi,li,ci): raise SystemExit(f"Thiếu cột OHLC. header={header}")
        for r in rd:
            if not r or len(r)<=max(x for x in (di,oi,hi,li,ci) if x is not None): continue
            try:
                ts=r[di].strip() if di is not None else str(len(rows))
                o=float(r[oi]); hh=float(r[hi]); ll=float(r[li]); cc=float(r[ci])
            except: continue
            rows.append((ts,o,hh,ll,cc))
    return rows

def parse_ts(s):
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%Y-%m-%dT%H:%M:%S","%Y.%m.%d %H:%M","%Y-%m-%d","%m/%d/%Y %H:%M"):
        try: return datetime.strptime(s,fmt)
        except: pass
    return None

# ---------- resample to H4 ----------
def to_h4(rows):
    buckets={}
    order=[]
    for ts,o,h,l,c in rows:
        dt=parse_ts(ts)
        if dt is None: continue
        key=dt.replace(hour=(dt.hour//4)*4, minute=0, second=0)
        if key not in buckets:
            buckets[key]=[o,h,l,c]; order.append(key)
        else:
            b=buckets[key]; b[1]=max(b[1],h); b[2]=min(b[2],l); b[3]=c
    order.sort()
    return [(k,)+tuple(buckets[k]) for k in order]

def atr_wilder(bars, n=20):
    tr=[]; out=[None]*len(bars)
    for i,(k,o,h,l,c) in enumerate(bars):
        if i==0: tr.append(h-l)
        else:
            pc=bars[i-1][4]; tr.append(max(h-l,abs(h-pc),abs(l-pc)))
    a=None
    for i in range(len(bars)):
        if i< n: continue
        if i==n: a=sum(tr[1:n+1])/n
        else: a=(a*(n-1)+tr[i])/n
        out[i]=a
    return out

# ---------- backtest one config ----------
def simulate(bars, atr, entry='E0', N=2, tp='T0', retestK=2):
    n=len(bars); trades=[]
    W=20
    i=W+1
    while i<n-1:
        a=atr[i]
        if a is None or a<=0: i+=1; continue
        bh=max(b[2] for b in bars[i-W:i]); bl=min(b[3] for b in bars[i-W:i])
        c=bars[i][4]
        up = c> bh+0.25*a; dn = c< bl-0.25*a
        if not (up or dn): i+=1; continue
        d=1 if up else -1
        # ----- entry price & bar -----
        ei=i; ep=c
        if entry=='E1':  # stop beyond break-candle extreme, next bar
            ext=bars[i][2] if up else bars[i][3]
            if i+1>=n: break
            nb=bars[i+1]
            if (up and nb[2]>=ext) or (dn and nb[3]<=ext): ei=i+1; ep=ext
            else: i+=1; continue
        elif entry=='E2':  # limit retest at broken level within K bars
            lvl=bh if up else bl; hit=False
            for k in range(1,retestK+1):
                if i+k>=n: break
                nb=bars[i+k]
                if (up and nb[3]<=lvl) or (dn and nb[2]>=lvl): ei=i+k; ep=lvl; hit=True; break
            if not hit: i+=1; continue
        elif entry=='E3':  # wick-structure: N successive rising wick-lows (up)/falling wick-highs (dn)
            ok=True
            for k in range(1,N+1):
                if i+k>=n: ok=False; break
                if up and not (bars[i+k][3] > bars[i+k-1][3]): ok=False; break
                if dn and not (bars[i+k][2] < bars[i+k-1][2]): ok=False; break
            if not ok: i+=1; continue
            ei=i+N; ep=bars[ei][4]
        elif entry in ('E4','E5'):  # pinbar/engulfing confirm on break candle
            o,h,l,cl=bars[i][1],bars[i][2],bars[i][3],bars[i][4]
            rng=max(h-l,1e-9); body=abs(cl-o)
            pin = body<=0.33*rng and ((up and (min(o,cl)-l)>=2*body) or (dn and (h-max(o,cl))>=2*body))
            eng=False
            if entry=='E4' and i>=1:
                po,pc=bars[i-1][1],bars[i-1][4]
                eng = (min(o,cl)<=min(po,pc) and max(o,cl)>=max(po,pc))
            if entry=='E5' and i>=3:
                grp_lo=min(min(bars[j][1],bars[j][4]) for j in range(i-3,i))
                grp_hi=max(max(bars[j][1],bars[j][4]) for j in range(i-3,i))
                eng = (min(o,cl)<=grp_lo and max(o,cl)>=grp_hi)
            if not (pin or eng): i+=1; continue
        # ----- risk & exit -----
        sl=ep - d*1.0*a
        risk=abs(ep-sl)
        if risk<=0: i+=1; continue
        tp_px = ep + d*2.0*a if tp=='T0' else (bl if up else bh) if tp=='T1' else None
        rmult=None; trail=sl; took_half=False; half_r=0.0
        j=ei+1
        while j<n:
            hb,lb=bars[j][2],bars[j][3]
            # SL/trail hit (conservative: check stop first)
            stop = trail
            hit_stop = (lb<=stop) if up else (hb>=stop)
            hit_tp = (tp_px is not None) and ((hb>=tp_px) if up else (lb<=tp_px))
            if tp=='T3' and not took_half:
                half_tp = ep + d*2.0*a
                if (hb>=half_tp) if up else (lb<=half_tp):
                    took_half=True; half_r=0.5*2.0  # +2R on half
            if hit_stop:
                base = d*(stop-ep)/risk
                rmult = (0.5*base+half_r) if (tp=='T3' and took_half) else base
                break
            if hit_tp:
                rmult = d*(tp_px-ep)/risk; break
            # trailing update (T2/T3 runner): trail below last 3-bar low (up)
            if tp in ('T2','T3') and j>=ei+3:
                if up: trail=max(trail, min(bars[j-2][3],bars[j-1][3],bars[j][3]))
                else:  trail=min(trail, max(bars[j-2][2],bars[j-1][2],bars[j][2]))
            j+=1
        if rmult is None:  # ran out -> mark to last close
            rmult=d*(bars[-1][4]-ep)/risk
        cost = COST_R*(1.5 if tp=='T3' else 1.0)   # round-turn; T3 có 2 lần khớp
        trades.append((bars[ei][0], rmult-cost))
        i=ei+1
    return trades

def stats(trades):
    if not trades: return None
    rs=[r for _,r in trades]; n=len(rs)
    wins=[r for r in rs if r>0]; losses=[-r for r in rs if r<0]
    wr=100*len(wins)/n
    avg=sum(rs)/n; tot=sum(rs)
    pf=(sum(wins)/sum(losses)) if losses else float('inf')
    srt=sorted(rs,reverse=True); top=srt[:max(1,n//10)]
    tail=100*sum(x for x in top if x>0)/tot if tot>0 else float('nan')
    # maxDD in R
    eq=0; peak=0; dd=0
    for r in rs:
        eq+=r; peak=max(peak,eq); dd=min(dd,eq-peak)
    return dict(n=n,wr=wr,avg=avg,tot=tot,pf=pf,tail=tail,maxdd=dd)

def seg(bars, atr, y0, y1):
    idx=[i for i,b in enumerate(bars) if b[0].year>=y0 and b[0].year<y1]
    return idx

def main():
    if len(sys.argv)<2: raise SystemExit("cần path CSV")
    global COST_R
    COST_R=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
    print(f"[cost] {COST_R:.3f} R/lệnh (round-turn)")
    rows=load(sys.argv[1]); print(f"[data] {len(rows)} raw rows")
    bars=to_h4(rows)
    if bars: print(f"[data] {len(bars)} H4 bars, {bars[0][0].date()} -> {bars[-1][0].date()}")
    atr=atr_wilder(bars,20)
    SEGS=[('OOS-A',2004,2012),('DEV',2012,2022),('OOS-B',2022,2026)]
    # T1/TRAVERSE loại: là TP của sleeve RANGE, vô nghĩa với lệnh BREAK (TP nằm sau entry)
    configs=[('E0','T0',2),('E1','T0',2),('E2','T0',2),
             ('E3','T0',1),('E3','T0',2),('E3','T0',3),('E3','T0',4),
             ('E4','T0',2),('E5','T0',2),
             ('E0','T2',2),('E0','T3',2),('E1','T3',2),('E3','T3',1)]
    print(f"\n{'config':14} {'seg':7} {'n':>5} {'WR%':>5} {'avgR':>7} {'totR':>7} {'PF':>5} {'tail%':>6} {'maxDD':>7}")
    for e,tp,N in configs:
        allt=simulate(bars,atr,entry=e,N=N,tp=tp)
        for name,y0,y1 in SEGS:
            ts=[t for t in allt if t[0].year>=y0 and t[0].year<y1]
            s=stats(ts)
            tag=f"{e}/{tp}"+(f"/N{N}" if e=='E3' else "")
            if s: print(f"{tag:14} {name:7} {s['n']:5d} {s['wr']:5.1f} {s['avg']:+7.3f} {s['tot']:+7.1f} {s['pf']:5.2f} {s['tail']:6.1f} {s['maxdd']:7.1f}")
            else: print(f"{tag:14} {name:7}  (no trades)")
    print("\n[!] Data INDICATIVE. Chạy lại trên XAU_30m_data.csv chuẩn để vào hồ sơ. Kiểm P1-P6 sau bảng OOS.")

if __name__=='__main__': main()
