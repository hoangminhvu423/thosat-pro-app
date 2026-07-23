#!/usr/bin/env python3
"""Portfolio MC: XAU + BTC break-sleeves, joint-month block bootstrap (giu tuong quan + duoi beo).
Payout: skim vuot dem 2% moi quy. Breaker -9% chung. 24 thang, 8k paths."""
SEED=20260723
def lcg():
    s=SEED
    while True:
        s=(s*6364136223846793005+1442695040888963407)%(2**64); yield s/2**64
def readm(p):
    d={}
    for l in open(p):
        k,v=l.strip().split(','); d[k]=float(v)
    return d
X=readm('mret_XAU.csv'); B=readm('mret_BTC.csv')
common=sorted(set(X)&set(B))
xs=[X[k] for k in common]; bs=[B[k] for k in common]
n=len(common)
mx=sum(xs)/n; mb=sum(bs)/n
sx=(sum((a-mx)**2 for a in xs)/n)**.5; sb=(sum((a-mb)**2 for a in bs)/n)**.5
corr=sum((xs[i]-mx)*(bs[i]-mb) for i in range(n))/(n*sx*sb)
print(f"overlap {common[0]}..{common[-1]} n={n} thang | XAU {mx:+.2f}R/mo BTC {mb:+.2f}R/mo | corr={corr:+.3f}")
rng=lcg()
def mc(wx,wb,paths=8000,months=24,block=3):
    died=0; paid=[]
    for p in range(paths):
        eq=1.0; wd=0.0; alive=True; m=0
        while m<months:
            i=int(next(rng)*(n-block))
            for j in range(block):
                if m>=months: break
                r=xs[i+j]*wx/100 + bs[i+j]*wb/100
                eq+=r; m+=1
                if m%3==0 and eq-1.0>0.02:
                    take=eq-1.0-0.02; wd+=take; eq-=take
                if eq<=0.91: died+=1; alive=False; m=months; break
        paid.append(wd/2)
    paid.sort()
    return 100*died/paths, 100*paid[len(paid)//2], 100*sum(paid)/len(paid)
print(f"{'wXAU%':>6} {'wBTC%':>6} {'P(chet2y)':>10} {'median%/nam':>12} {'mean%/nam':>10}")
print(f"{'0.25':>6} {'0':>6}  (doi chieu don-XAU break-only)")
for wx,wb in [(0.25,0.0),(0.25,0.15),(0.20,0.20),(0.15,0.15),(0.25,0.25)]:
    pd,med,mean=mc(wx,wb)
    print(f"{wx:>6} {wb:>6} {pd:>9.1f}% {med:>11.2f}% {mean:>9.2f}%")
