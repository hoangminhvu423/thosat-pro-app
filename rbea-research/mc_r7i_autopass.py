#!/usr/bin/env python3
"""R7i — AUTO-PASS FTMO bang RB_EA (prereg chot 2026-07-24, Sep duyet):
GIA THUYET: ton tai r* trong [0.5..2.0]%/sleeve sao cho P(pass 2-step) >= 40% va net-EV/attempt > 0.
PHUONG PHAP: block-bootstrap NGAY (block 10) tu daily-R joint XAU+BTC (engine EA-parity, 2023-2026);
  risk fixed-$ theo initial (khop I_InitBalance) -> equity tuyen tinh theo cumR;
  Phase1: +10% truoc -10% · Phase2: +5% truoc -10% · daily -5%: khong the cham (<=2 lenh/ngay, cap -1R/lenh,
  can r>=2.5% moi cham) — verify trong sim. FTMO Swing khong gioi han thoi gian. 8k paths/muc, seed co dinh.
KINH TE (Skinner): fee $600 (Sep chot); E[payout funded nam dau] = $2,500 (FUND-mode ~3-4%/nam x100k x split80,
  khop R7e/f $2-3k — so THAN TRONG, chua tinh scaling). net EV = P(pass)*2500 - 600.
KILL: P(pass)<25% tai moi r HOAC net-EV<0 tai moi r.
"""
import sys, collections
sys.path.insert(0, "tools")
from rbea_ship import load, backtest

SEED = 20260723
FEE = 600.0; PAYOUT = 2500.0
def lcg():
    s = SEED
    while True:
        s = (s*6364136223846793005+1442695040888963407) % (2**64); yield s/2**64

# 1. daily joint R (theo ngay EXIT — PnL hien thuc; SL cap -1R nen floating bounded)
daily = collections.defaultdict(float)
for sym in ["BTCUSD", "XAUUSD"]:
    for tm, r, _ in backtest(load(sym)):
        daily[tm[:10]] += r
days = [daily[k] for k in sorted(daily)]
n = len(days)
print(f"[R7i] daily-R joint: {n} ngay co lenh, tong {sum(days):+.1f}R, min-day {min(days):+.2f}R (daily-5%% can {-5:.0f}R/r)")

rng = lcg()
def phase(target_R, loss_R, maxdays=2000, block=10):
    """1 phase: random walk daily-R, absorbing +target_R / -loss_R. Tra (pass, so_ngay)."""
    cum = 0.0; d = 0
    while d < maxdays:
        i = int(next(rng)*(n-block))
        for j in range(block):
            cum += days[i+j]; d += 1
            if cum >= target_R: return True, d
            if cum <= -loss_R: return False, d
            if d >= maxdays: break
    return False, d  # qua lau -> tinh la fail (opportunity cost)

def sim(r, paths=8000):
    p1 = p2 = 0; days_tot = 0; both = 0
    for _ in range(paths):
        ok1, d1 = phase(10.0/r, 10.0/r)
        if not ok1: days_tot += d1; continue
        p1 += 1
        ok2, d2 = phase(5.0/r, 10.0/r)
        days_tot += d1+d2
        if ok2: p2 += 1; both += 1
    P = both/paths
    ev = P*PAYOUT - FEE
    return p1/paths, P, ev, days_tot/paths

print(f"{'r%/sleeve':>9} {'P(ph1)':>7} {'P(pass2step)':>12} {'netEV/$':>9} {'E[ngay-co-lenh]':>15} {'E[attempts]':>11}")
best = None
for r in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
    P1, P, ev, ed = sim(r)
    ea = (1/P) if P > 0 else float('inf')
    print(f"{r:>8.2f}% {P1:>7.1%} {P:>12.1%} {ev:>+9.0f} {ed:>15.0f} {ea:>11.1f}")
    if best is None or ev > best[1]: best = (r, ev, P)
r, ev, P = best
print(f"\n=> r* = {r}%/sleeve: P(pass)={P:.0%}, net EV = {ev:+.0f}$/attempt (fee 600, payout than trong 2500)")
print("KILL-CHECK:", "SONG (P>=25% & EV>0)" if (P >= 0.25 and ev > 0) else "CHET theo prereg")
