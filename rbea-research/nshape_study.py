#!/usr/bin/env python3
"""
PHAN TACH CHINH XAC HINH THAI CHU N (mo hinh chu N cua trader TQ) + test tren data chuan.
Dinh nghia N (up): pivotLow L0 -> pivotHigh H1 (LEG1 impulse >= IMP*ATR) -> pivotLow L1 (higher-low,
  retrace 20-70% cua leg1) -> gia PHA len tren H1 (LEG2 continuation) = TRIGGER vao lenh.
  SL = L1 - 0.2*ATR (cau truc). TP: 2R / 5R (RR co ay) / MM (measured-move = chieu cao leg1).
  N-REAL (type A) = break kem volume TANG (>1.2x avg N); N-FAKE (type B) = volume giam.
  Freshness = so lan H1 bi test truoc khi pha (0/1/2+).
Pivot fractal k=2. Path M30 cho exit. Net phi. OOS 3 doan. INDICATIVE (tick-volume).
Chay: python3 nshape_study.py <csv> [cost_R] [IMP] [RRTP]
"""
import sys, csv
from datetime import datetime
def load(p):
    rows=[]
    with open(p,newline='') as f:
        s=f.readline(); f.seek(0)
        d=';' if s.count(';')>s.count(',') else ('\t' if s.count('\t')>s.count(',') else ',')
        rd=csv.reader(f,delimiter=d); hd=[c.strip().lower() for c in next(rd)]
        def ix(*ns):
            for n in ns:
                for i,c in enumerate(hd):
                    if c==n or n in c: return i
        di,oi,hi,li,ci,vi=ix('date'),ix('open'),ix('high'),ix('low'),ix('close'),ix('vol')
        for r in rd:
            if not r or len(r)<=max(oi,hi,li,ci): continue
            try: rows.append((r[di].strip(),float(r[oi]),float(r[hi]),float(r[li]),float(r[ci]),float(r[vi]) if vi is not None and len(r)>vi else 0.0))
            except: pass
    return rows
def pts(s):
    for f in ("%Y.%m.%d %H:%M","%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%Y-%m-%dT%H:%M:%S","%Y-%m-%d"):
        try: return datetime.strptime(s,f)
        except: pass
def build(rows):
    m30=[]
    for ts,o,h,l,c,v in rows:
        dt=pts(ts)
        if dt: m30.append((dt,o,h,l,c,v))
    m30.sort(key=lambda x:x[0])
    h4=[]; cur=None; st=0
    for idx,(dt,o,h,l,c,v) in enumerate(m30):
        k=dt.replace(hour=(dt.hour//4)*4,minute=0,second=0)
        if cur is None or k!=cur[0]:
            if cur is not None: h4.append(cur+[st,idx-1])
            cur=[k,o,h,l,c,v]; st=idx
        else:
            cur[2]=max(cur[2],h); cur[3]=min(cur[3],l); cur[4]=c; cur[5]+=v
    if cur is not None: h4.append(cur+[st,len(m30)-1])
    return m30,h4   # h4=[dt,o,h,l,c,vol,m0,m1]
def atr_w(h4,n=20):
    tr=[]; out=[None]*len(h4)
    for i,r in enumerate(h4):
        tr.append(r[2]-r[3] if i==0 else max(r[2]-r[3],abs(r[2]-h4[i-1][4]),abs(r[3]-h4[i-1][4])))
    a=None
    for i in range(len(h4)):
        if i<n: continue
        a=sum(tr[1:n+1])/n if i==n else (a*(n-1)+tr[i])/n; out[i]=a
    return out
def pivots(h4,k=2):
    ph=[False]*len(h4); pl=[False]*len(h4)
    for i in range(k,len(h4)-k):
        H=h4[i][2]; L=h4[i][3]
        if all(H>=h4[i+j][2] for j in range(-k,k+1)): ph[i]=True
        if all(L<=h4[i+j][3] for j in range(-k,k+1)): pl[i]=True
    return ph,pl
def walk(m30,j0,d,ep,sl,tp):
    risk=abs(ep-sl)
    if risk<=0: return None,j0
    for j in range(j0,len(m30)):
        h,l=m30[j][2],m30[j][3]
        if (l<=sl) if d>0 else (h>=sl): return d*(sl-ep)/risk,j
        if (h>=tp) if d>0 else (l<=tp): return d*(tp-ep)/risk,j
    return d*(m30[-1][4]-ep)/risk,len(m30)-1

def study(m30,h4,atr,ph,pl,tp_mode='MM',cost=0.0,imp=1.5,rlo=0.2,rhi=0.7):
    trades=[]  # (dt,R,volflag,fresh)
    N=len(h4)
    # duyet cac bo pivot lien tiep tao chu N
    piv=[(i,'H') for i in range(N) if ph[i]]+[(i,'L') for i in range(N) if pl[i]]
    piv.sort()
    for a in range(len(piv)-2):
        (i0,t0),(i1,t1),(i2,t2)=piv[a],piv[a+1],piv[a+2]
        if not atr[i1] or atr[i1]<=0: continue
        # UP-N: L0 -> H1 -> L1
        if t0=='L' and t1=='H' and t2=='L':
            L0=h4[i0][3]; H1=h4[i1][2]; L1=h4[i2][3]
            leg1=H1-L0
            if leg1 < imp*atr[i1]: continue
            if not (L1>L0): continue
            rt=(H1-L1)/leg1
            if not (rlo<=rt<=rhi): continue
            d=1; trig=H1; sl=L1-0.2*atr[i1]
        elif t0=='H' and t1=='L' and t2=='H':
            H0=h4[i0][2]; L1v=h4[i1][3]; H1h=h4[i2][2]
            leg1=H0-L1v
            if leg1<imp*atr[i1]: continue
            if not (H1h<H0): continue
            rt=(H1h-L1v)/leg1
            if not (rlo<=rt<=rhi): continue
            d=-1; trig=L1v; sl=H1h+0.2*atr[i1]
        else: continue
        # tim bar pha trigger sau pivot cuoi (i2), trong <=12 nen H4
        # [FIX look-ahead] pivot i2 (k=2) chi XAC NHAN sau i2+2 -> chi duoc hanh dong tu i2+3
        fresh=0; fill=None; brk_bar=None
        for t in range(i2+3,min(i2+15,N)):
            if d>0 and h4[t][2]>=trig:  # cham/vuot trig
                # dem freshness: so nen truoc do cham gan trig ma chua pha close
                for j in range(brk_bar or (i2+1), t):
                    pass
                # tim M30 dau tien vuot trig
                for jj in range(h4[t][6],h4[t][7]+1) if False else range(h4[t][6],h4[t][7]+1):
                    if m30[jj][2]>=trig: fill=jj; brk_bar=t; break
                if fill is not None: break
            if d<0 and h4[t][3]<=trig:
                for jj in range(h4[t][6],h4[t][7]+1):
                    if m30[jj][3]<=trig: fill=jj; brk_bar=t; break
                if fill is not None: break
        if fill is None: continue
        # freshness = so nen giua i2 va brk_bar cham vao vung trig (approach within 0.1 atr)
        fresh=sum(1 for t in range(i2+3,brk_bar) if (d>0 and h4[t][2]>=trig-0.1*atr[i1]) or (d<0 and h4[t][3]<=trig+0.1*atr[i1]))
        ep=trig
        risk=abs(ep-sl)
        if risk<=0: continue
        if tp_mode=='2R': tp=ep+d*2*risk
        elif tp_mode=='5R': tp=ep+d*5*risk
        else: tp=ep+d*leg1     # measured-move = chieu cao leg1
        # volume: nen pha vs trung binh 10 nen truoc
        vavg=sum(h4[t][5] for t in range(max(0,brk_bar-10),brk_bar))/max(1,min(10,brk_bar))
        volflag='UP' if (vavg>0 and h4[brk_bar][5]>1.2*vavg) else ('DN' if vavg>0 and h4[brk_bar][5]<0.8*vavg else 'MID')
        R,_=walk(m30,fill+1,d,ep,sl,tp)
        trades.append((h4[brk_bar][0],R-cost,volflag,min(fresh,2)))
    return trades

def stat(ts):
    if not ts: return None
    rs=[r for _,r,_,_ in ts]; n=len(rs); w=[r for r in rs if r>0]; lo=[-r for r in rs if r<0]
    return dict(n=n,wr=100*len(w)/n,avg=sum(rs)/n,tot=sum(rs),pf=(sum(w)/sum(lo) if lo else 9.9))
def seg(ts,y0,y1): return [x for x in ts if y0<=x[0].year<y1]
def line(tag,ts):
    for nm,y0,y1 in [('OOS-A',2004,2012),('DEV',2012,2022),('OOS-B',2022,2026),('ALL',2004,2026)]:
        s=stat(seg(ts,y0,y1))
        if s: print(f"{tag:16} {nm:6} {s['n']:5d} {s['wr']:5.1f} {s['avg']:+7.3f} {s['tot']:+8.1f} {s['pf']:5.2f}")
def main():
    cost=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
    m30,h4=build(load(sys.argv[1])); atr=atr_w(h4); ph,pl=pivots(h4)
    print(f"[N-study] cost={cost}R IMP={IMP}xATR  H4={len(h4)} pivotsH={sum(ph)} pivotsL={sum(pl)}  {h4[0][0].date()}->{h4[-1][0].date()}")
    for tpm in ['2R','5R','MM']:
        ts=study(m30,h4,atr,ph,pl,tpm,cost)
        print(f"\n=== TP={tpm} (n_total={len(ts)}) ===")
        print(f"{'cut':16} {'seg':6} {'n':>5} {'WR%':>5} {'avgR':>7} {'totR':>8} {'PF':>5}")
        line('N all',ts)
        line('N vol-UP(real)',[x for x in ts if x[2]=='UP'])
        line('N vol-DN(fake)',[x for x in ts if x[2]=='DN'])
        line('N fresh0-1',[x for x in ts if x[3]<=1])
        line('N fresh2+',[x for x in ts if x[3]>=2])
    print("\n[!] Pivot fractal k=2; path M30; tick-volume proxy. INDICATIVE - chay lai tren Fable engine de vao ho so.")
if __name__=='__main__': main()
