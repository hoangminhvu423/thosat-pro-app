#!/usr/bin/env python3
"""R7f v2 — quet chinh sach: retention buffer x chu ky rut x ladder. Edge CO DINH (validated/degraded)."""
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
def run(ladder, keepbuf, period, scale, paths=8000, years=3, tpy=60):
    rng=lcg(); n=int(tpy*years)
    died=0; months=0.0; paid=[]
    for p in range(paths):
        eq=1.0; wd=0.0; alive=True; md=years*12
        for t in range(n):
            c=eq-1.0
            r=ladder[0] if c<ladder[1] else (ladder[2] if c<ladder[3] else ladder[4])
            eq+=draw(rng,scale)*r
            if (t+1)%period==0 and eq-1.0>keepbuf:
                take=eq-1.0-keepbuf; wd+=take; eq-=take
            if eq<=0.91: died+=1; alive=False; md=(t+1)/tpy*12; break
        if alive: wd+=max(0,eq-1.0)*0  # con lai trong acc khong tinh payout
        months+=md if not alive else years*12
        paid.append(wd/years)
    paid.sort()
    return dict(pd=100*died/paths, mo=months/paths, med=100*paid[len(paid)//2], mean=100*sum(paid)/len(paid))
LADDERS={
 'L1(.25/.5/.75)': (0.0025,0.02,0.005,0.04,0.0075),
 'L2(.25/.5/1.0)': (0.0025,0.02,0.005,0.05,0.010),
 'L3(.3/.6/.9)':   (0.0030,0.02,0.006,0.05,0.009),
}
print("[R7f v2] 3 nam, 8k paths | payout = rut vuot BUF moi PERIOD lenh | breaker -9%")
print(f"{'ladder':>15} {'BUF':>4} {'per':>4} {'scen':>9} {'P(chet3y)':>10} {'median%/nam':>12} {'mean%/nam':>10}")
for scale,nm in [(0.985,'validated'),(0.936,'degraded')]:
    m=run((0.0025,9,0.0025,9,0.0025),0.02,15,scale)
    print(f"{'flat25 (chuan)':>15} {'2%':>4} {15:>4} {nm:>9} {m['pd']:>9.1f}% {m['med']:>11.2f}% {m['mean']:>9.2f}%")
    for lname,lad in LADDERS.items():
        for buf in (0.04,0.06):
            for per in (30,60):
                m=run(lad,buf,per,scale)
                print(f"{lname:>15} {int(buf*100):>3}% {per:>4} {nm:>9} {m['pd']:>9.1f}% {m['med']:>11.2f}% {m['mean']:>9.2f}%")
