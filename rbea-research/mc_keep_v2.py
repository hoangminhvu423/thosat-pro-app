#!/usr/bin/env python3
"""R7f — CPPI-LADDER cho vai KEEP: risk thang theo DEM LOI NHUAN (cushion) + chinh sach payout.
Muc tieu: nang payout 2-4%/nam ma KHONG pha survival cua 0.25% flat.
Ladder (du doan truoc): cushion<1%: 0.25% | 1-3%: 0.50% | >3%: 0.75%. Payout moi 'quy' (15 lenh):
rut phan cushion vuot 2% (giu dem 2%). So voi flat 0.25 va flat 0.5. Phan phoi nhu R7e (validated & degraded).
"""
SEED=20260723
def lcg():
    s=SEED
    while True:
        s=(s*6364136223846793005+1442695040888963407)%(2**64); yield s/2**64
def draw(rng,scale):
    u=next(rng)
    if u<0.686: return -1.5 if next(rng)<0.05 else -1.0
    u2=next(rng)
    return (0.5 if u2<0.40 else (2.0 if u2<0.75 else 6.5))*scale

def run(policy, scale, paths=8000, years=2, tpy=60):
    rng=lcg(); n=int(tpy*years)
    died=0; months=0.0; paid=[]; 
    for p in range(paths):
        eq=1.0; wd=0.0; alive=True; mdeath=years*12
        for t in range(n):
            cush=eq-1.0
            if policy=='flat25': r=0.0025
            elif policy=='flat50': r=0.005
            else:  # ladder CPPI
                r=0.0025 if cush<0.01 else (0.005 if cush<0.03 else 0.0075)
            eq+=draw(rng,scale)*r/0.0025*0.0025   # R multiple * risk fraction
            # payout moi 15 lenh: rut phan vuot dem 2%
            if (t+1)%15==0 and eq-1.0>0.02:
                take=eq-1.0-0.02; wd+=take; eq-=take
            if eq<=0.91:
                died+=1; alive=False; mdeath=(t+1)/tpy*12; break
        months+=mdeath if not alive else years*12
        paid.append(wd/years)
    paid.sort()
    return dict(pd=100*died/paths, mo=months/paths, med=100*paid[len(paid)//2], mean=100*sum(paid)/len(paid))

print("[R7f CPPI-LADDER] payout=rut vuot dem 2% moi 15 lenh | 8k paths x 2 nam | breaker -9% initial")
print(f"{'policy':>8} {'scenario':>10} {'P(chet 2y)':>11} {'thang-quy/24':>13} {'median payout %/nam':>20} {'mean %/nam':>11}")
for scale,nm in [(0.985,'validated'),(0.936,'degraded')]:
    for pol in ['flat25','flat50','ladder']:
        m=run(pol,scale)
        print(f"{pol:>8} {nm:>10} {m['pd']:>10.1f}% {m['mo']:>12.1f} {m['med']:>19.2f}% {m['mean']:>10.2f}%")
