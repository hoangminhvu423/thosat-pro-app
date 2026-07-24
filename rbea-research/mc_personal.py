#!/usr/bin/env python3
"""R7h — PERSONAL account: khong co lan ranh prop, lai kep, chiu DD 25-30%.
Joint block-bootstrap thang XAU+BTC (nhu R7g). Sweep risk/sleeve. 5 nam, 8k paths.
Metrics: median CAGR, P(maxDD>25%), P(maxDD>30%), median maxDD."""
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
common=sorted(set(X)&set(B)); xs=[X[k] for k in common]; bs=[B[k] for k in common]; n=len(common)
rng=lcg()
def mc(w, paths=8000, months=60, block=3):
    cagrs=[]; dd25=0; dd30=0; mdds=[]
    for p in range(paths):
        eq=1.0; peak=1.0; mdd=0.0; m=0
        while m<months:
            i=int(next(rng)*(n-block))
            for j in range(block):
                if m>=months: break
                r=(xs[i+j]+bs[i+j])*w/100      # cung weight 2 sleeve, % cua EQUITY (lai kep)
                eq*=(1.0+r); m+=1
                if eq>peak: peak=eq
                dd=1-eq/peak
                if dd>mdd: mdd=dd
        cagrs.append(eq**(12.0/months)-1.0); mdds.append(mdd)
        if mdd>0.25: dd25+=1
        if mdd>0.30: dd30+=1
    cagrs.sort(); mdds.sort()
    return dict(med=100*cagrs[len(cagrs)//2], p25=100*cagrs[len(cagrs)//4], p75=100*cagrs[3*len(cagrs)//4],
                mdd=100*mdds[len(mdds)//2], d25=100*dd25/paths, d30=100*dd30/paths)
print("[R7h PERSONAL] lai kep, 5 nam, 8k paths, joint bootstrap XAU+BTC (corr 0.024)")
print(f"{'risk/sleeve':>11} {'CAGR p25':>9} {'MEDIAN':>8} {'p75':>7} {'medianMaxDD':>12} {'P(DD>25%)':>10} {'P(DD>30%)':>10}")
for w in (0.3,0.5,0.75,1.0,1.25,1.5):
    m=mc(w)
    print(f"{w:>10}% {m['p25']:>+8.1f}% {m['med']:>+7.1f}% {m['p75']:>+6.1f}% {m['mdd']:>11.1f}% {m['d25']:>9.1f}% {m['d30']:>9.1f}%")
