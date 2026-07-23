#!/usr/bin/env python3
"""Robustness sweep N-shape: quet IMP x pivot-k x retrace-band. Kiem edge co ben qua tham so & OOS khong.
Chay: python3 nshape_sweep.py <csv> [cost_R]"""
import sys
from nshape_study import load, build, atr_w, pivots, study, stat, seg
cost=float(sys.argv[2]) if len(sys.argv)>2 else 0.04
m30,h4=build(load(sys.argv[1])); atr=atr_w(h4)
print(f"[SWEEP] cost={cost}R H4={len(h4)}  {h4[0][0].date()}->{h4[-1][0].date()}  (TP=MM; avgR moi doan)")
print(f"{'IMP':>4} {'k':>2} {'retrace':>9} | {'n':>5} {'A':>7} {'DEV':>7} {'B':>7} {'ALL':>7} {'PF':>5}  verdict")
IMPs=[1.0,1.5,2.0,2.5]; Ks=[1,2,3]; RBs=[(0.2,0.7),(0.3,0.6),(0.15,0.8)]
piv_cache={}
robust=0; total=0
for k in Ks:
    if k not in piv_cache: piv_cache[k]=pivots(h4,k)
    ph,pl=piv_cache[k]
    for imp in IMPs:
        for (rlo,rhi) in RBs:
            ts=study(m30,h4,atr,ph,pl,'MM',cost,imp,rlo,rhi)
            sA=stat(seg(ts,2004,2012)); sD=stat(seg(ts,2012,2022)); sB=stat(seg(ts,2022,2026)); sAll=stat(ts)
            if not sAll or sAll['n']<40:
                print(f"{imp:>4} {k:>2} {str((rlo,rhi)):>9} |  (mau qua nho n={sAll['n'] if sAll else 0})"); continue
            a=sA['avg'] if sA else 0; dv=sD['avg'] if sD else 0; b=sB['avg'] if sB else 0
            total+=1
            ok = (a>0 and dv>0 and b>0)          # net+ CA 3 doan = ben
            if ok: robust+=1
            v = "ROBUST(+3/3)" if ok else ("ok(+2/3)" if sum(x>0 for x in (a,dv,b))>=2 else "YEU")
            print(f"{imp:>4} {k:>2} {str((rlo,rhi)):>9} | {sAll['n']:>5} {a:+7.3f} {dv:+7.3f} {b:+7.3f} {sAll['avg']:+7.3f} {sAll['pf']:5.2f}  {v}")
print(f"\n=> {robust}/{total} bo tham so net-duong CA 3 OOS. Neu da so ROBUST -> edge KHONG phu thuoc 1 bo tham so (khong overfit).")
