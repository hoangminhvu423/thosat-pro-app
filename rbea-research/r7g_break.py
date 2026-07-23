#!/usr/bin/env python3
"""R7g — BREAK sleeve Donchian-20 (logic Fable-B Task2 NGUYEN BAN) tren 1 symbol.
Chay: python3 r7g_break.py <csv> <tag>. Net 0.04R. Xuat monthly returns -> mret_<tag>.csv"""
import sys
from datetime import datetime, timedelta
FEE=0.04
def pts(s):
    for f in ("%Y-%m-%d %H:%M:%S","%Y.%m.%d %H:%M","%Y-%m-%d %H:%M"):
        try: return datetime.strptime(s,f)
        except: pass
def load(p):
    rows=[]
    with open(p) as f:
        s=f.readline(); f.seek(0)
        d=';' if s.count(';')>s.count(',') else ','
        import csv as _c; rd=_c.reader(f,delimiter=d); hd=[c.strip().lower() for c in next(rd)]
        def ix(n):
            for i,c in enumerate(hd):
                if n in c: return i
        di,oi,hi,li,ci=ix('date'),ix('open'),ix('high'),ix('low'),ix('close')
        for r in rd:
            try:
                dt=pts(r[di].strip())
                if dt: rows.append((dt,float(r[oi]),float(r[hi]),float(r[li]),float(r[ci])))
            except: pass
    rows.sort(key=lambda x:x[0]); return rows
def main():
    rows=load(sys.argv[1]); tag=sys.argv[2]
    # gap scan (>12h ngoai weekend)
    holes=0; prev=None
    for r in rows:
        if prev and (r[0]-prev)>timedelta(hours=12) and not(prev.weekday()==4 and r[0].weekday() in (0,6)): holes+=1
        prev=r[0]
    # H4
    h=[]; cur=None
    for dt,o,hh,ll,c in rows:
        k=dt.replace(hour=(dt.hour//4)*4,minute=0,second=0)
        if cur is None or k!=cur[0]:
            if cur: h.append(cur)
            cur=[k,o,hh,ll,c,len(h4m:=[]),0]
        else:
            cur[2]=max(cur[2],hh); cur[3]=min(cur[3],ll); cur[4]=c
    if cur: h.append(cur)
    # map m-index ranges
    hm0=[];hm1=[];cur=None
    for i,(dt,o,hh,ll,c) in enumerate(rows):
        k=dt.replace(hour=(dt.hour//4)*4,minute=0,second=0)
        if cur is None or k!=cur:
            hm0.append(i); hm1.append(i); cur=k
        else: hm1[-1]=i
    nH=len(h)
    P=20
    tr=[h[0][2]-h[0][3]]+[max(h[i][2]-h[i][3],abs(h[i][2]-h[i-1][4]),abs(h[i][3]-h[i-1][4])) for i in range(1,nH)]
    atr=[None]*nH
    if nH>P:
        atr[P-1]=sum(tr[:P])/P
        for i in range(P,nH): atr[i]=(atr[i-1]*(P-1)+tr[i])/P
    def path_exit(j0,d,ep,sl,tp):
        for j in range(j0,len(rows)):
            _,o,hh,ll,c=rows[j]
            if d==1:
                if ll<=sl: return (o if o<sl else sl)
                if hh>=tp: return (o if o>tp else tp)
            else:
                if hh>=sl: return (o if o>sl else sl)
                if ll<=tp: return (o if o<tp else tp)
        return rows[-1][4]
    trades=[]; prevc=0
    for i in range(P,nH-1):
        a=atr[i]
        if not a or a<=0: prevc=0; continue
        bh=max(h[k][2] for k in range(i-P,i)); bl=min(h[k][3] for k in range(i-P,i))
        c=h[i][4]
        cond=1 if c>bh+0.25*a else (-1 if c<bl-0.25*a else 0)
        fresh=(cond!=0 and cond!=prevc); prevc=cond
        if not fresh: continue
        d=cond; mj=hm0[i+1]; ep=rows[mj][1]
        sl=ep-d*a; tp=ep+d*2*a
        x=path_exit(mj,d,ep,sl,tp)
        trades.append((rows[mj][0], d*(x-ep)/a - FEE))
    ys=sorted({t[0].year for t in trades}); n3=max(1,len(ys)//3)
    segs=[('S1',set(ys[:n3])),('S2',set(ys[n3:2*n3])),('S3',set(ys[2*n3:]))]
    def st(rs):
        n=len(rs)
        if n==0: return "n=0"
        w=[r for r in rs if r>0]; lo=[-r for r in rs if r<0]
        return f"n={n:4d} avgR={sum(rs)/n:+.3f} PF={(sum(w)/sum(lo) if lo else 9.9):.2f}"
    print(f"[{tag}] rows={len(rows)} H4={nH} holes={holes} {rows[0][0].date()}->{rows[-1][0].date()}")
    allr=[r for _,r in trades]
    print(f"  ALL  {st(allr)}")
    seg_pos=0
    for nm,yy in segs:
        rs=[r for t,r in trades if t.year in yy]
        print(f"  {nm}({min(yy)}-{max(yy)}) {st(rs)}")
        if rs and sum(rs)/len(rs)>0: seg_pos+=1
    n=len(allr); avg=sum(allr)/n if n else 0
    w=[r for r in allr if r>0]; lo=[-r for r in allr if r<0]; pf=(sum(w)/sum(lo)) if lo else 9.9
    verdict = "PASS" if (avg>0 and seg_pos>=2 and n>=100 and pf>=1.03) else "FAIL"
    print(f"  VERDICT: {verdict} (avg{'+' if avg>0 else '-'}, seg+ {seg_pos}/3, n={n}, PF={pf:.2f})")
    # monthly returns
    mm={}
    for t,r in trades:
        k=f"{t.year}-{t.month:02d}"; mm[k]=mm.get(k,0)+r
    with open(f"mret_{tag}.csv","w") as f:
        for k in sorted(mm): f.write(f"{k},{mm[k]:.4f}\n")
if __name__=='__main__': main()
