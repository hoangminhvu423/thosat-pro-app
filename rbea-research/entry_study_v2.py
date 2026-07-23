#!/usr/bin/env python3
"""
Entry study v2 — dùng M30 làm PATH trong nến H4 (thực tế hơn), test:
  B0  close-entry + fixed-1ATR SL + 2R           (baseline)
  E1  stop-continuation (vượt đỉnh/đáy nến break) + fixed-1ATR SL + 2R
  E6  Setup A user: retest RÂU nến break (limit) + SL cấu trúc tại râu + 2R   [cần nến break râu mạnh]
  E7  Setup B user: nến break RÂU MẠNH đóng cùng chiều -> vào market + SL cấu trúc + 2R
  E7mm E7 nhưng TP = measured-move (chiều cao box) thay vì 2R
Break xác nhận trên H4 close (Donchian-20). Path exit trên M30 (SL trước TP trong 1 M30 bar - bảo thủ).
Chạy: python3 entry_study_v2.py <csv> [cost_R]
"""
import sys, csv
from datetime import datetime
COST_R=0.0

def load(path):
    rows=[]
    with open(path,newline='') as f:
        s=f.readline(); f.seek(0)
        d=';' if s.count(';')>s.count(',') else ('\t' if s.count('\t')>s.count(',') else ',')
        rd=csv.reader(f,delimiter=d); hd=[c.strip().lower() for c in next(rd)]
        def ix(*ns):
            for n in ns:
                for i,c in enumerate(hd):
                    if c==n: return i
            for n in ns:
                for i,c in enumerate(hd):
                    if n in c: return i
        di,oi,hi,li,ci=ix('datetime','date','time'),ix('open'),ix('high'),ix('low'),ix('close')
        for r in rd:
            if not r or len(r)<=max(oi,hi,li,ci): continue
            try: rows.append((r[di].strip(),float(r[oi]),float(r[hi]),float(r[li]),float(r[ci])))
            except: pass
    return rows
def pts(s):
    for f in ("%Y.%m.%d %H:%M","%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%Y-%m-%dT%H:%M:%S","%Y-%m-%d"):
        try: return datetime.strptime(s,f)
        except: pass
def build(rows):
    m30=[]
    for ts,o,h,l,c in rows:
        dt=pts(ts)
        if dt: m30.append((dt,o,h,l,c))
    m30.sort(key=lambda x:x[0])
    # H4 buckets with m30 index range
    h4=[]; cur=None; st=0
    for idx,(dt,o,h,l,c) in enumerate(m30):
        k=dt.replace(hour=(dt.hour//4)*4,minute=0,second=0)
        if cur is None or k!=cur[0]:
            if cur is not None: h4.append(cur+[st,idx-1])
            cur=[k,o,h,l,c]; st=idx
        else:
            cur[2]=max(cur[2],h); cur[3]=min(cur[3],l); cur[4]=c
    if cur is not None: h4.append(cur+[st,len(m30)-1])
    return m30,h4  # h4 row = [dt,o,h,l,c, m0, m1]
def atr_w(h4,n=20):
    tr=[]; out=[None]*len(h4)
    for i,r in enumerate(h4):
        tr.append(r[2]-r[3] if i==0 else max(r[2]-r[3],abs(r[2]-h4[i-1][4]),abs(r[3]-h4[i-1][4])))
    a=None
    for i in range(len(h4)):
        if i<n: continue
        a=sum(tr[1:n+1])/n if i==n else (a*(n-1)+tr[i])/n
        out[i]=a
    return out

def exit_path(m30, start_idx, d, ep, sl, tp_px):
    risk=abs(ep-sl)
    if risk<=0: return None
    for j in range(start_idx, len(m30)):
        h,l=m30[j][2],m30[j][3]
        hit_sl=(l<=sl) if d>0 else (h>=sl)
        hit_tp=(h>=tp_px) if d>0 else (l<=tp_px)
        if hit_sl: return d*(sl-ep)/risk
        if hit_tp: return d*(tp_px-ep)/risk
    return d*(m30[-1][4]-ep)/risk

def run(m30,h4,atr,variant):
    W=20; trades=[]; t=W+1
    while t<len(h4)-1:
        a=atr[t]
        if not a or a<=0: t+=1; continue
        bh=max(h4[k][2] for k in range(t-W,t)); bl=min(h4[k][3] for k in range(t-W,t))
        o,h,l,c=h4[t][1],h4[t][2],h4[t][3],h4[t][4]
        up=c>bh+0.25*a; dn=c<bl-0.25*a
        if not(up or dn): t+=1; continue
        d=1 if up else -1
        body=abs(c-o); rng=max(h-l,1e-9)
        lw=min(o,c)-l; uw=h-max(o,c)              # lower/upper wick
        wick=lw if up else uw                      # wick chống lại hướng (rejection)
        m_end=h4[t][6]                             # M30 index cuối nến break
        r=None
        if variant=='B0':
            ep=c; sl=ep-d*a; tp=ep+d*2*a
            r=exit_path(m30,m_end+1,d,ep,sl,tp)
            t+=1
        elif variant=='E1':
            ext=h if up else l
            if t+1>=len(h4): break
            mi=h4[t+1][5]; fill=None
            for j in range(h4[t+1][5],h4[t+1][6]+1):
                if (up and m30[j][2]>=ext) or (dn and m30[j][3]<=ext): fill=j; break
            if fill is None: t+=1; continue
            ep=ext; sl=ep-d*a; tp=ep+d*2*a
            r=exit_path(m30,fill+1,d,ep,sl,tp); t+=1
        elif variant in ('E6','E7','E7mm'):
            if wick < 1.5*body or body<=0: t+=1; continue     # cần râu mạnh
            wtip=l if up else h                                # đỉnh râu tham chiếu
            if variant=='E6':   # retest râu trong 1-2 nến H4 kế
                fill=None
                for tt in (t+1,t+2):
                    if tt>=len(h4): break
                    for j in range(h4[tt][5],h4[tt][6]+1):
                        if (up and m30[j][3]<=wtip) or (dn and m30[j][2]>=wtip): fill=j; break
                    if fill is not None: break
                if fill is None: t+=1; continue
                ep=wtip; sl=wtip-d*0.2*a                       # SL sát dưới râu (cấu trúc)
                tp=ep+d*2*abs(ep-sl)
                r=exit_path(m30,fill+1,d,ep,sl,tp); t+=1
            else:               # E7 / E7mm: vào ngay tại close nến break râu mạnh
                ep=c; sl=wtip-d*0.2*a                          # SL sát ngoài râu
                if variant=='E7': tp=ep+d*2*abs(ep-sl)
                else:                                          # measured-move: chiều cao box
                    tp=ep+d*(bh-bl)
                r=exit_path(m30,m_end+1,d,ep,sl,tp); t+=1
        else: t+=1; continue
        if r is not None:
            trades.append((h4[t-1][0], r-COST_R))
    return trades

def stats(ts):
    if not ts: return None
    rs=[r for _,r in ts]; n=len(rs); w=[r for r in rs if r>0]; lo=[-r for r in rs if r<0]
    eq=pk=dd=0
    for r in rs: eq+=r; pk=max(pk,eq); dd=min(dd,eq-pk)
    return dict(n=n,wr=100*len(w)/n,avg=sum(rs)/n,tot=sum(rs),pf=(sum(w)/sum(lo) if lo else 9.99),dd=dd)

def main():
    global COST_R
    COST_R=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
    m30,h4=build(load(sys.argv[1])); atr=atr_w(h4)
    print(f"[cost {COST_R} R] M30={len(m30)} H4={len(h4)}  {h4[0][0].date()}->{h4[-1][0].date()}")
    SEG=[('OOS-A',2004,2012),('DEV',2012,2022),('OOS-B',2022,2026)]
    print(f"\n{'variant':8} {'seg':6} {'n':>5} {'WR%':>5} {'avgR':>7} {'totR':>7} {'PF':>5} {'maxDD':>7}")
    for v in ['B0','E1','E6','E7','E7mm']:
        allt=run(m30,h4,atr,v)
        for nm,y0,y1 in SEG:
            s=stats([x for x in allt if y0<=x[0].year<y1])
            if s: print(f"{v:8} {nm:6} {s['n']:5d} {s['wr']:5.1f} {s['avg']:+7.3f} {s['tot']:+7.1f} {s['pf']:5.2f} {s['dd']:7.1f}")
            else: print(f"{v:8} {nm:6}   (0)")
    print("\n[!] Path M30, SL/TP theo M30. E6/E7 SL cấu trúc sát râu (R nhỏ->R-mult cao khi thắng). INDICATIVE.")
if __name__=='__main__': main()
