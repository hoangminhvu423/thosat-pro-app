#!/usr/bin/env python3
"""R7c REGIME-GATE study tren engine Fable-B chuan. Theo PREREG_R7C_REGIME_GATE.md (khoa truoc khi chay).
Gate tinh tai nen H4 DA DONG ngay truoc nen fill (khong look-ahead). TP=MM, net 0.04R.
Chay: python3 fable_gate_study.py"""
from datetime import datetime

CSV="/root/.claude/uploads/c184c64a-1e6b-51fd-8c5d-ec395e073c64/64966031-XAU_30m_data.csv"
FEE_R=0.04

# ---------- load M30 + H4 resample + ATR (nguyen van Fable-B) ----------
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
h_dt=[];h_h=[];h_l=[];h_c=[];h_m0=[];h_m1=[]
cur=None
for i in range(nM):
    dt=m_dt[i];key=(dt.year,dt.month,dt.day,(dt.hour//4)*4)
    if key!=cur:
        cur=key;h_dt.append(datetime(*key));h_h.append(m_h[i]);h_l.append(m_l[i]);h_c.append(m_c[i])
        h_m0.append(i);h_m1.append(i)
    else:
        if m_h[i]>h_h[-1]:h_h[-1]=m_h[i]
        if m_l[i]<h_l[-1]:h_l[-1]=m_l[i]
        h_c[-1]=m_c[i];h_m1[-1]=i
nH=len(h_dt)
m2h=[0]*nM
for i in range(nH):
    for j in range(h_m0[i],h_m1[i]+1): m2h[j]=i
P=20
tr=[0.0]*nH;tr[0]=h_h[0]-h_l[0]
for i in range(1,nH):
    pc=h_c[i-1];tr[i]=max(h_h[i]-h_l[i],abs(h_h[i]-pc),abs(h_l[i]-pc))
atr=[None]*nH;atr[P-1]=sum(tr[:P])/P
for i in range(P,nH):atr[i]=(atr[i-1]*(P-1)+tr[i])/P

# ---------- indicators for gates (closed-bar) ----------
sma200=[None]*nH;s=0.0
for i in range(nH):
    s+=h_c[i]
    if i>=200:s-=h_c[i-200]
    if i>=199:sma200[i]=s/200
er=[None]*nH   # Kaufman ER 20
for i in range(20,nH):
    num=abs(h_c[i]-h_c[i-20]);den=sum(abs(h_c[k]-h_c[k-1]) for k in range(i-19,i+1))
    er[i]=(num/den) if den>0 else 0.0
# ADX(14) Wilder
A=14
pdm=[0.0]*nH;ndm=[0.0]*nH
for i in range(1,nH):
    up=h_h[i]-h_h[i-1];dn=h_l[i-1]-h_l[i]
    pdm[i]=up if (up>dn and up>0) else 0.0
    ndm[i]=dn if (dn>up and dn>0) else 0.0
adx=[None]*nH
if nH>2*A:
    str_=sum(tr[1:A+1]);sp=sum(pdm[1:A+1]);sn=sum(ndm[1:A+1])
    dxs=[]
    prev_adx=None
    for i in range(A+1,nH):
        str_=str_-str_/A+tr[i];sp=sp-sp/A+pdm[i];sn=sn-sn/A+ndm[i]
        pdi=100*sp/str_ if str_>0 else 0;ndi=100*sn/str_ if str_>0 else 0
        dx=100*abs(pdi-ndi)/(pdi+ndi) if (pdi+ndi)>0 else 0
        dxs.append(dx)
        if len(dxs)==A: prev_adx=sum(dxs)/A;adx[i]=prev_adx
        elif len(dxs)>A: prev_adx=(prev_adx*(A-1)+dx)/A;adx[i]=prev_adx

def pivots(K):
    piv=[]
    for i in range(K,nH-K):
        if all(h_h[i]>=h_h[i+j] and h_h[i]>=h_h[i-j] for j in range(1,K+1)):piv.append((i,'H'))
        if all(h_l[i]<=h_l[i+j] and h_l[i]<=h_l[i-j] for j in range(1,K+1)):piv.append((i,'L'))
    return piv
def exit_one(sm,ep,sl,tp,d):
    j=sm
    while j<nM:
        o,hi,lo=m_o[j],m_h[j],m_l[j]
        if d==1:
            if lo<=sl:return o if o<sl else sl
            if hi>=tp:return o if o>tp else tp
        else:
            if hi>=sl:return o if o>sl else sl
            if lo<=tp:return o if o<tp else tp
        j+=1
    return m_c[nM-1]
def fill_in(m0,m1,trig,d):
    for j in range(m0,m1+1):
        if d==1 and m_h[j]>=trig:return j,(m_o[j] if m_o[j]>trig else trig)
        if d==-1 and m_l[j]<=trig:return j,(m_o[j] if m_o[j]<trig else trig)
    return None,None
def seg_of(dt):
    y=dt.year
    return 'A' if y<2012 else ('D' if y<2022 else 'B')

def nshape_trades(K,IMP,RLO,RHI):
    """tra list (seg, netR, gate_bar) — gate_bar = H4 index NGAY TRUOC nen fill (da dong)."""
    piv=pivots(K);out=[]
    for a in range(len(piv)-2):
        (i0,t0),(i1,t1),(i2,t2)=piv[a],piv[a+1],piv[a+2]
        if i0==i1 or i1==i2:continue
        if t0=='L' and t1=='H' and t2=='L':
            d=1;L0v,H1v,L1v=h_l[i0],h_h[i1],h_l[i2]
            if atr[i1] is None:continue
            leg1=H1v-L0v
            if leg1<IMP*atr[i1]:continue
            if not L1v>L0v:continue
            r=(H1v-L1v)/leg1
            if not (RLO<=r<=RHI):continue
            trig=H1v;sl=L1v-0.2*atr[i1]
        elif t0=='H' and t1=='L' and t2=='H':
            d=-1;H0v,L1p,H1p=h_h[i0],h_l[i1],h_h[i2]
            if atr[i1] is None:continue
            leg1=H0v-L1p
            if leg1<IMP*atr[i1]:continue
            if not H1p<H0v:continue
            r=(H1p-L1p)/leg1
            if not (RLO<=r<=RHI):continue
            trig=L1p;sl=H1p+0.2*atr[i1]
        else:continue
        fb=i2+K+1;lb=min(i2+12,nH-1)
        if fb>=nH:continue
        early=False
        for b in range(i2+1,min(i2+K,nH-1)+1):
            if d==1 and h_h[b]>=trig:early=True
            if d==-1 and h_l[b]<=trig:early=True
        if early:continue
        mj,ep=fill_in(h_m0[fb],h_m1[lb],trig,d)
        if mj is None:continue
        risk=(ep-sl) if d==1 else (sl-ep)
        if risk<=0:continue
        tp=ep+d*leg1
        x=exit_one(mj,ep,sl,tp,d)
        gross=(x-ep)/risk if d==1 else (ep-x)/risk
        gb=m2h[mj]-1                        # nen H4 da dong ngay truoc fill
        out.append((seg_of(m_dt[mj]),gross-FEE_R,gb))
    return out

GATES=[
 ('G1 dist>=1.0', lambda g: sma200[g] is not None and atr[g] and abs(h_c[g]-sma200[g])>=1.0*atr[g]),
 ('G1 dist>=2.0', lambda g: sma200[g] is not None and atr[g] and abs(h_c[g]-sma200[g])>=2.0*atr[g]),
 ('G2 ER>=0.25',  lambda g: er[g] is not None and er[g]>=0.25),
 ('G2 ER>=0.35',  lambda g: er[g] is not None and er[g]>=0.35),
 ('G3 ADX>=20',   lambda g: adx[g] is not None and adx[g]>=20),
 ('G3 ADX>=25',   lambda g: adx[g] is not None and adx[g]>=25),
 ('G0 random50',  lambda g: ((g*2654435761)>>4)&1==0),
]
def st(rs):
    n=len(rs)
    if n==0:return None
    w=sum(1 for r in rs if r>0);gp=sum(r for r in rs if r>0);gl=-sum(r for r in rs if r<0)
    return dict(n=n,avg=sum(rs)/n,pf=(gp/gl if gl>0 else 9.9))

CONFIGS=[('PRIMARY',1.5,2,0.2,0.7),('ALT1',1.0,3,0.2,0.7),('ALT2',2.0,2,0.15,0.8)]
print(f"[R7c GATE STUDY] engine Fable-B chuan | TP=MM net {FEE_R}R | gate tai nen dong truoc fill")
for cname,IMP,K,RLO,RHI in CONFIGS:
    ts=nshape_trades(K,IMP,RLO,RHI)
    print(f"\n===== {cname}: IMP{IMP}/k{K}/({RLO},{RHI})  n={len(ts)} =====")
    base={}
    for sg in 'ADB':
        s=st([r for s_,r,_ in ts if s_==sg]); base[sg]=s
    print(f"{'gate':14} {'':4} "+" | ".join(f"{sg}: n avgR" for sg in ['A','DEV','B'])+" | keep%")
    b=" | ".join(f"{(base[sg]['n'] if base[sg] else 0):4d} {(base[sg]['avg'] if base[sg] else 0):+.3f}" for sg in 'ADB')
    print(f"{'(khong gate)':14} {'':4} {b}")
    for gname,fn in GATES:
        on=[(s_,r) for s_,r,g in ts if g>=0 and fn(g)]
        off=[(s_,r) for s_,r,g in ts if not (g>=0 and fn(g))]
        row_on=[];row_off=[];sep_all=True;dev_on_ok=False
        for sg in 'ADB':
            so=st([r for s_,r in on if s_==sg]);sf=st([r for s_,r in off if s_==sg])
            row_on.append(f"{(so['n'] if so else 0):4d} {(so['avg'] if so else 0):+.3f}")
            row_off.append(f"{(sf['n'] if sf else 0):4d} {(sf['avg'] if sf else 0):+.3f}")
            if not so or not sf or so['avg']<=sf['avg']:sep_all=False
            if sg=='D' and so and so['avg']>=-0.02:dev_on_ok=True
        keep=100*len(on)/max(1,len(ts))
        verdict=[]
        if sep_all:verdict.append("SEP3/3")
        if dev_on_ok:verdict.append("DEV-OK")
        if keep>=30:verdict.append("keep>=30")
        v="PASS" if len(verdict)==3 else ",".join(verdict) if verdict else "fail"
        print(f"{gname:14} {'ON':4} "+" | ".join(row_on)+f" | {keep:4.0f}%  [{v}]")
        print(f"{'':14} {'OFF':4} "+" | ".join(row_off))
print("\nTieu chi PASS (prereg): ON>OFF ca 3 doan + DEV-ON>=-0.02 + keep>=30%, va lap lai tren config phu.")
