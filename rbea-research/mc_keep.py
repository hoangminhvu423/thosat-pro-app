#!/usr/bin/env python3
"""R7e — MONTE CARLO SURVIVAL cho vai KEEP tren FTMO 200k Swing (Q3 cua LOGIC_FRAMEWORK I.B).
Cau hoi: risk%/lenh nao toi da hoa "thang-quy cam duoc" (capital-months) + P(song sot) + payout?
Phan phoi lenh: tu PHASE1 fOFF validated (WR 31.4%, avgR +0.078, duoi beo Q2: top10% lenh ~ 80% totR).
Mo hinh: loss -1R (5% loss dinh gap -1.5R); win mixture {+0.5R:40%, +2R:35%, +6.5R:25%} -> E[win]~+2.53R
  => avgR = 0.314*2.53 - 0.686*1.025 ~ +0.078 (khop PHASE1). Degraded: edge/2. Zero: avgR=0.
60 lenh/nam (fOFF), toi da 3 lenh/ngay. FTMO: total loss 10% (tinh tu INITIAL), EA breaker cung -9%.
Deterministic RNG (LCG seed co dinh) - tai lap duoc.
"""
SEED=20260723
def lcg():
    s=SEED
    while True:
        s=(s*6364136223846793005+1442695040888963407)%(2**64)
        yield s/2**64
rng=lcg()
def draw(scale):
    u=next(rng)
    if u<0.686:               # loss
        return -1.5 if next(rng)<0.05 else -1.0
    u2=next(rng)
    if u2<0.40: w=0.5
    elif u2<0.75: w=2.0
    else: w=6.5
    return w*scale            # degraded: scale<1 keo avgR xuong

def scenario_avg(scale,n=200000):
    global rng; rng=lcg()
    return sum(draw(scale) for _ in range(n))/n

def run_mc(risk_pct, scale, years=2, paths=8000, trades_per_year=60):
    global rng; rng=lcg()
    n_tr=int(trades_per_year*years)
    breach=0; surv_months=0.0; ann_rets=[]; sc_hits=0
    for p in range(paths):
        eq=1.0; alive=True; month_of_death=years*12
        monthly=[]; m_eq=1.0; tr_per_month=trades_per_year/12
        acc=0.0; cnt=0
        rets=[]
        for t in range(n_tr):
            r=draw(scale)*risk_pct/100
            eq+=r                      # fixed-$ risk tu initial (chuan prop: R tinh tren initial)
            rets.append(r)
            if alive and eq<=0.91:     # EA breaker -9% tu initial
                breach+=1; alive=False; month_of_death=(t+1)/trades_per_year*12
                break
        surv_months+=month_of_death if not alive else years*12
        ann_rets.append(eq-1.0 if alive else -0.09)
        # scaling check: cua so 4 thang (~20 lenh) tang >= +10%?
        if alive:
            win=int(tr_per_month*4)
            for i in range(0,len(rets)-win):
                if sum(rets[i:i+win])>=0.10: sc_hits+=1; break
    ann=sorted(ann_rets)
    med=ann[len(ann)//2]/years
    return dict(p_breach=100*breach/paths, cap_months=surv_months/paths,
                med_annual=100*med, p_scale=100*sc_hits/paths)

print("[R7e MC-KEEP] FTMO 200k Swing | 60 lenh/nam | 2 nam | 8k paths | breaker cung -9% initial")
print(f"kiem phan phoi: validated avgR={scenario_avg(0.985):+.3f} (muc tieu +0.078) | degraded={scenario_avg(0.936):+.3f} | zero={scenario_avg(0.887):+.3f}")
print(f"\n{'risk%':>6} {'scenario':>10} {'P(breach 2y)':>13} {'thang-quy TB/24':>16} {'median %/nam':>13} {'P(scale +10%/4mo)':>18}")
for scale,name in [(0.985,"validated"),(0.936,"degraded"),(0.887,"zero-edge")]:
    for risk in (0.25,0.5,0.75,1.0,1.5):
        m=run_mc(risk,scale)
        print(f"{risk:>6} {name:>10} {m['p_breach']:>12.1f}% {m['cap_months']:>15.1f} {m['med_annual']:>+12.2f}% {m['p_scale']:>17.1f}%")
print("""
Doc ket qua:
- 'thang-quy cam duoc' = so thang trung binh con giu account (max 24) — metric 'cam max quy'.
- P(scale) = xac suat co cua so 4 thang +10% (dieu kien FTMO Scaling Plan) — do auto co tu scale duoc khong.
""")
