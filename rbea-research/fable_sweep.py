#!/usr/bin/env python3
"""Robustness sweep N-shape TREN ENGINE FABLE-B (engine chuan, fill bao thu, anti-lookahead skip).
Logic copy NGUYEN VAN tu fable_b_engine.py, chi tham so hoa k / IMP / retrace band. TP=MM. Net 0.04R.
Chay: python3 fable_sweep.py"""
import sys
from datetime import datetime

CSV = "/root/.claude/uploads/c184c64a-1e6b-51fd-8c5d-ec395e073c64/64966031-XAU_30m_data.csv"
FEE_R = 0.04

# ---------------- load M30 (nguyen van Fable-B) ----------------
m_dt=[];m_o=[];m_h=[];m_l=[];m_c=[]
with open(CSV) as f:
    f.readline()
    for line in f:
        line=line.strip()
        if not line: continue
        d,o,h,l,c,v=line.split(";")
        m_dt.append(datetime(int(d[0:4]),int(d[5:7]),int(d[8:10]),int(d[11:13]),int(d[14:16])))
        m_o.append(float(o));m_h.append(float(h));m_l.append(float(l));m_c.append(float(c))
nM=len(m_dt)
# ---------------- H4 resample (nguyen van) ----------------
h_dt=[];h_o=[];h_h=[];h_l=[];h_c=[];h_m0=[];h_m1=[]
cur=None
for i in range(nM):
    dt=m_dt[i]; key=(dt.year,dt.month,dt.day,(dt.hour//4)*4)
    if key!=cur:
        cur=key
        h_dt.append(datetime(*key)); h_o.append(m_o[i]);h_h.append(m_h[i]);h_l.append(m_l[i]);h_c.append(m_c[i])
        h_m0.append(i);h_m1.append(i)
    else:
        if m_h[i]>h_h[-1]:h_h[-1]=m_h[i]
        if m_l[i]<h_l[-1]:h_l[-1]=m_l[i]
        h_c[-1]=m_c[i];h_m1[-1]=i
nH=len(h_dt)
# ---------------- ATR Wilder(20) (nguyen van) ----------------
P=20
tr=[0.0]*nH; tr[0]=h_h[0]-h_l[0]
for i in range(1,nH):
    pc=h_c[i-1]; tr[i]=max(h_h[i]-h_l[i],abs(h_h[i]-pc),abs(h_l[i]-pc))
atr=[None]*nH
atr[P-1]=sum(tr[:P])/P
for i in range(P,nH): atr[i]=(atr[i-1]*(P-1)+tr[i])/P

def pivots(K):
    piv=[]
    for i in range(K,nH-K):
        isH=all(h_h[i]>=h_h[i+j] and h_h[i]>=h_h[i-j] for j in range(1,K+1))
        isL=all(h_l[i]<=h_l[i+j] and h_l[i]<=h_l[i-j] for j in range(1,K+1))
        if isH: piv.append((i,'H'))
        if isL: piv.append((i,'L'))
    return piv

def m30_exit_one(start_m,ep,sl,tp,direction):
    j=start_m
    while j<nM:
        o,hi,lo=m_o[j],m_h[j],m_l[j]
        if direction==1:
            if lo<=sl: return o if o<sl else sl
            if hi>=tp: return o if o>tp else tp
        else:
            if hi>=sl: return o if o>sl else sl
            if lo<=tp: return o if o<tp else tp
        j+=1
    return m_c[nM-1]

def find_stop_fill(m_start,m_end,trigger,direction):
    for j in range(m_start,m_end+1):
        if direction==1 and m_h[j]>=trigger: return j,(m_o[j] if m_o[j]>trigger else trigger)
        if direction==-1 and m_l[j]<=trigger: return j,(m_o[j] if m_o[j]<trigger else trigger)
    return None,None

def seg_of(dt):
    y=dt.year
    if y<2012: return 'A'
    if y<2022: return 'D'
    return 'B'

def run_nshape(K,IMP,RLO,RHI,piv):
    trades=[]  # (seg, netR) — TP=MM only
    skipped=0
    for a in range(len(piv)-2):
        (i0,t0),(i1,t1),(i2,t2)=piv[a],piv[a+1],piv[a+2]
        if i0==i1 or i1==i2: continue
        if t0=='L' and t1=='H' and t2=='L':
            d=1; L0v,H1v,L1v=h_l[i0],h_h[i1],h_l[i2]
            if atr[i1] is None: continue
            leg1=H1v-L0v
            if leg1<IMP*atr[i1]: continue
            if not (L1v>L0v): continue
            r=(H1v-L1v)/leg1
            if not (RLO<=r<=RHI): continue
            trig=H1v; sl=L1v-0.2*atr[i1]
        elif t0=='H' and t1=='L' and t2=='H':
            d=-1; H0v,L1p,H1p=h_h[i0],h_l[i1],h_h[i2]
            if atr[i1] is None: continue
            leg1=H0v-L1p
            if leg1<IMP*atr[i1]: continue
            if not (H1p<H0v): continue
            r=(H1p-L1p)/leg1
            if not (RLO<=r<=RHI): continue
            trig=L1p; sl=H1p+0.2*atr[i1]
        else: continue
        first_bar=i2+K+1; last_bar=min(i2+12,nH-1)
        if first_bar>=nH: continue
        # anti-lookahead: level pha trong nen chua-xac-nhan -> SKIP (chuan Fable-B)
        early=False
        for b in range(i2+1,min(i2+K,nH-1)+1):
            if d==1 and h_h[b]>=trig: early=True
            if d==-1 and h_l[b]<=trig: early=True
        if early: skipped+=1; continue
        mj,ep=find_stop_fill(h_m0[first_bar],h_m1[last_bar],trig,d)
        if mj is None: continue
        risk=(ep-sl) if d==1 else (sl-ep)
        if risk<=0: continue
        tp=ep+d*leg1
        x=m30_exit_one(mj,ep,sl,tp,d)
        gross=(x-ep)/risk if d==1 else (ep-x)/risk
        trades.append((seg_of(m_dt[mj]),gross-FEE_R))
    return trades,skipped

def st(rs):
    n=len(rs)
    if n==0: return None
    w=sum(1 for r in rs if r>0); gp=sum(r for r in rs if r>0); gl=-sum(r for r in rs if r<0)
    return dict(n=n,wr=100*w/n,avg=sum(rs)/n,pf=(gp/gl if gl>0 else 9.9))

print(f"[FABLE-SWEEP] engine=Fable-B chuan | H4={nH} | TP=MM net {FEE_R}R")
print(f"{'IMP':>4} {'k':>2} {'retrace':>10} | {'n':>4} {'skip':>4} {'A':>7} {'DEV':>7} {'B':>7} {'ALL':>7} {'PF':>5}  verdict")
robust=0; total=0
piv_cache={}
for K in (1,2,3):
    piv_cache[K]=pivots(K)
    for IMP in (1.0,1.5,2.0,2.5):
        for (RLO,RHI) in ((0.2,0.7),(0.3,0.6),(0.15,0.8)):
            ts,skipped=run_nshape(K,IMP,RLO,RHI,piv_cache[K])
            sA=st([r for s,r in ts if s=='A']); sD=st([r for s,r in ts if s=='D']); sB=st([r for s,r in ts if s=='B']); sAll=st([r for _,r in ts])
            if not sAll or sAll['n']<40:
                print(f"{IMP:>4} {K:>2} {str((RLO,RHI)):>10} |  n={sAll['n'] if sAll else 0} qua nho"); continue
            a=sA['avg'] if sA else 0; dv=sD['avg'] if sD else 0; b=sB['avg'] if sB else 0
            total+=1
            pos=sum(x>0 for x in (a,dv,b))
            ok=(pos==3)
            if ok: robust+=1
            v="ROBUST(3/3)" if ok else (f"ok({pos}/3)" if pos==2 else "YEU")
            print(f"{IMP:>4} {K:>2} {str((RLO,RHI)):>10} | {sAll['n']:>4} {skipped:>4} {a:+7.3f} {dv:+7.3f} {b:+7.3f} {sAll['avg']:+7.3f} {sAll['pf']:5.2f}  {v}")
print(f"\n=> {robust}/{total} cau hinh net+ CA 3 OOS tren ENGINE CHUAN (fill bao thu).")
