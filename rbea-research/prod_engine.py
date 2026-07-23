#!/usr/bin/env python3
"""
REPLICA production RB_EA (rolling-box full-auto) — để A/B entry BREAK: baseline(v0.1) vs E1(continuation).
Sanity gate: tái tạo ballpark PHASE1 filterOFF (+0.078R, PF~1.10, n~1272 trên 21y).
Path M30 cho fill & exit. Net phí tham số. INDICATIVE (proxy rolling-box, không phải human-zone).
Chạy: python3 prod_engine.py <csv> [cost_R]
"""
import sys, csv
from datetime import datetime

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
        di,oi,hi,li,ci=ix('datetime','date'),ix('open'),ix('high'),ix('low'),ix('close')
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
    h4=[]; cur=None; st=0
    for idx,(dt,o,h,l,c) in enumerate(m30):
        k=dt.replace(hour=(dt.hour//4)*4,minute=0,second=0)
        if cur is None or k!=cur[0]:
            if cur is not None: h4.append(cur+[st,idx-1])
            cur=[k,o,h,l,c]; st=idx
        else:
            cur[2]=max(cur[2],h); cur[3]=min(cur[3],l); cur[4]=c
    if cur is not None: h4.append(cur+[st,len(m30)-1])
    return m30,h4
def atr_w(h4,n=20):
    tr=[]; out=[None]*len(h4)
    for i,r in enumerate(h4):
        tr.append(r[2]-r[3] if i==0 else max(r[2]-r[3],abs(r[2]-h4[i-1][4]),abs(r[3]-h4[i-1][4])))
    a=None
    for i in range(len(h4)):
        if i<n: continue
        a=sum(tr[1:n+1])/n if i==n else (a*(n-1)+tr[i])/n; out[i]=a
    return out
def sma(h4,n=200):
    out=[None]*len(h4); s=0
    for i,r in enumerate(h4):
        s+=r[4]
        if i>=n: s-=h4[i-n][4]
        if i>=n-1: out[i]=s/n
    return out

def walk_exit(m30, j0, d, ep, sl, tp, exp_idx=None):
    """path M30 từ index j0; SL trước TP; exp_idx: index M30 hết hạn time-stop -> đóng tại close."""
    risk=abs(ep-sl)
    if risk<=0: return None,j0
    for j in range(j0,len(m30)):
        h,l,c=m30[j][2],m30[j][3],m30[j][4]
        if (l<=sl) if d>0 else (h>=sl): return d*(sl-ep)/risk, j
        if (h>=tp) if d>0 else (l<=tp): return d*(tp-ep)/risk, j
        if exp_idx is not None and j>=exp_idx: return d*(c-ep)/risk, j
    return d*(m30[-1][4]-ep)/risk, len(m30)-1

def run(m30,h4,atr,sm, break_entry='baseline', timestop=True, trend=False, cost=0.0):
    W=20; BARS_H4=len(h4)
    trades=[]  # (dt, R, tag)
    t=max(W+1, 200 if trend else W+1)
    day=None; rb=rs=bk=1; blocked=0
    while t<BARS_H4-2:
        # day reset
        dk=h4[t][0].date()
        if dk!=day: day=dk; rb=rs=bk=1; blocked=0
        a=atr[t]
        if not a or a<=0: t+=1; continue
        bh=max(h4[k][2] for k in range(t-W,t)); bl=min(h4[k][3] for k in range(t-W,t))
        o,h,l,c=h4[t][1],h4[t][2],h4[t][3],h4[t][4]
        m_end=h4[t][6]
        exp=None
        if timestop:
            # 48 nến H4 -> index M30 xấp xỉ +48 bucket; tính theo giờ: 192h
            exp_bar=min(t+48, BARS_H4-1); exp=h4[exp_bar][6]
        # ---- BREAK ----
        up=c>bh+0.25*a; dn=c<bl-0.25*a
        if up or dn:
            d=1 if up else -1
            if bk>0:
                if break_entry=='baseline':
                    # vào market đầu nến kế (approx v0.1)
                    if t+1>=BARS_H4: break
                    jf=h4[t+1][5]; ep=m30[jf][1]
                    sl=ep-d*1.0*a; tp=ep+d*2.0*a
                    R,jx=walk_exit(m30,jf+1,d,ep,sl,tp,exp)
                    bk-=1; trades.append((h4[t][0],R-cost,'BK'))
                    # nhảy tới H4 sau khi thoát
                    t=next((k for k in range(t+1,BARS_H4) if h4[k][5]>jx),t+1); continue
                else: # E1: stop tại đỉnh/đáy nến break, trong nến kế
                    ext=h if up else l
                    if t+1>=BARS_H4: break
                    jf=None
                    for j in range(h4[t+1][5],h4[t+1][6]+1):
                        if (up and m30[j][2]>=ext) or (dn and m30[j][3]<=ext): jf=j; break
                    if jf is None:
                        t+=1; continue   # không continuation -> bỏ, giữ nguyên box tiếp
                    ep=ext; sl=ep-d*1.0*a; tp=ep+d*2.0*a
                    R,jx=walk_exit(m30,jf+1,d,ep,sl,tp,exp)
                    bk-=1; trades.append((h4[t][0],R-cost,'BK'))
                    t=next((k for k in range(t+1,BARS_H4) if h4[k][5]>jx),t+1); continue
            t+=1; continue
        # ---- RANGE ---- (giống nhau ở cả 2 nhánh -> hiệu số A/B = tác dụng E1)
        smav=sm[t] if trend else None
        sell_ok = not (trend and smav and c>smav)
        buy_ok  = not (trend and smav and c<smav)
        did=False
        if h>=bh-0.15*a and rs>0 and not (blocked&2) and sell_ok:
            ep=c; sl=bh+0.5*a; tp=bl
            if (sl-ep)>0.05*a and (ep-tp)/(sl-ep)>=1.0:
                R,jx=walk_exit(m30,m_end+1,-1,ep,sl,tp,exp)
                rs-=1
                if R<0 and abs(R+1)<0.1: blocked|=2   # SL -> block sell (approx whipsaw)
                trades.append((h4[t][0],R-cost,'RS')); did=True
                t=next((k for k in range(t+1,BARS_H4) if h4[k][5]>jx),t+1); continue
        if not did and l<=bl+0.15*a and rb>0 and not (blocked&1) and buy_ok:
            ep=c; sl=bl-0.5*a; tp=bh
            if (ep-sl)>0.05*a and (tp-ep)/(ep-sl)>=1.0:
                R,jx=walk_exit(m30,m_end+1,1,ep,sl,tp,exp)
                rb-=1
                if R<0 and abs(R+1)<0.1: blocked|=1
                trades.append((h4[t][0],R-cost,'RB')); did=True
                t=next((k for k in range(t+1,BARS_H4) if h4[k][5]>jx),t+1); continue
        t+=1
    return trades

def stat(ts):
    if not ts: return None
    rs=[r for _,r,_ in ts]; n=len(rs); w=[r for r in rs if r>0]; lo=[-r for r in rs if r<0]
    eq=pk=dd=0
    for r in rs: eq+=r; pk=max(pk,eq); dd=min(dd,eq-pk)
    return dict(n=n,wr=100*len(w)/n,avg=sum(rs)/n,tot=sum(rs),pf=(sum(w)/sum(lo) if lo else 9.9),dd=dd)
def seg(ts,y0,y1): return [x for x in ts if y0<=x[0].year<y1]
def show(tag,ts):
    for nm,y0,y1 in [('OOS-A',2004,2012),('DEV',2012,2022),('OOS-B',2022,2026),('ALL',2004,2026)]:
        s=stat(seg(ts,y0,y1))
        if s: print(f"{tag:18} {nm:6} {s['n']:5d} {s['wr']:5.1f} {s['avg']:+7.3f} {s['tot']:+8.1f} {s['pf']:5.2f} {s['dd']:8.1f}")

def main():
    cost=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
    m30,h4=build(load(sys.argv[1])); atr=atr_w(h4); sm=sma(h4)
    print(f"[cost {cost}R] M30={len(m30)} H4={len(h4)} {h4[0][0].date()}->{h4[-1][0].date()}")
    print(f"\n{'config':18} {'seg':6} {'n':>5} {'WR%':>5} {'avgR':>7} {'totR':>8} {'PF':>5} {'maxDD':>8}")
    print("--- SANITY: baseline entry, filterOFF, NO cost (so với PHASE1 +0.078/PF1.10) ---")
    show('SANITY base fOFF', run(m30,h4,atr,sm,'baseline',timestop=True,trend=False,cost=0.0))
    print("--- A/B NET (phí {}R), filterOFF ---".format(cost))
    base=run(m30,h4,atr,sm,'baseline',timestop=True,trend=False,cost=cost)
    e1  =run(m30,h4,atr,sm,'E1',      timestop=True,trend=False,cost=cost)
    show('v0.1 baseline', base); print()
    show('v0.2 E1', e1)
    print("--- BREAK sleeve RIÊNG (A/B sạch) ---")
    show('BK baseline', [x for x in base if x[2]=='BK']); print()
    show('BK E1', [x for x in e1 if x[2]=='BK'])
    print("\n[!] Replica proxy rolling-box. Hiệu số E1-baseline ở sleeve BK = tác dụng entry (RANGE giống nhau).")
if __name__=='__main__': main()
