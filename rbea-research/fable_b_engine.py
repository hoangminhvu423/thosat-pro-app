#!/usr/bin/env python3
"""FABLE-B independent verification engine for RB_EA.

Written from SPEC only. Pure stdlib. No reference to any other implementation.

Interpretations chosen (reported in output):
 - k=2 fractal pivots, condition uses >= (<=) so flat tops/bottoms can yield
   multiple pivots.
 - H4 bucket key: (calendar date, hour//4*4). Bars formed from whatever M30
   candles exist in the bucket (weekend gaps => missing buckets, no padding).
 - Wilder ATR(20): TR[0]=H-L; ATR seeded at bar index 19 as SMA of TR[0..19],
   then ATR[i] = (ATR[i-1]*19 + TR[i]) / 20. ATR undefined (None) before idx 19.
 - N pattern uses three CONSECUTIVE pivots in the chronological merged pivot
   list with strict alternation (L,H,L for up; H,L,H for down). If two pivots
   of the same type are adjacent, no pattern is formed across them.
 - ATR reference for leg1 filter AND for the 0.2*ATR SL buffer = ATR at the H1
   (middle pivot) bar.
 - Entry: buy-stop at H1 level, armed from H4 bar (L1_idx + k + 1) onward,
   valid through H4 bar (L1_idx + 12) inclusive. If the H1 level is already
   broken during the un-confirmed bars (L1+1 .. L1+k) the pattern is SKIPPED
   (cannot enter without look-ahead). Fill price = trigger level, or the open
   of the triggering M30 candle if it gaps beyond the trigger.
 - Trigger condition: M30 high >= H1 (touch fills the stop). Symmetric short.
 - Exit sim on M30 candles, SL checked before TP inside each candle
   (conservative). SL fills at min(SL, open) for longs (gap-through). TP fills
   at open if the candle opens beyond TP, else at TP. Open trades at data end
   are closed at final M30 close.
 - Fees: net R = gross R - 0.04 per trade.
 - Task 2 Donchian: box over the 20 PRIOR H4 bars (current excluded). A break
   signal is taken only on a FRESH cross (the previous bar did not satisfy the
   break condition). Both directions (up & down) are traded symmetrically;
   long-only numbers are also reported for convergence checking.
 - Task 2 ATR reference = ATR at the break (signal) bar. Risk unit = 1*ATR, so
   TP hit = +2R gross, SL hit = -1R gross (gap slippage can worsen/improve).
 - Baseline entry: market at the open of the first M30 candle of the next H4
   bar. E1: stop at break-bar high (low for shorts); only fills if H4 bar
   (i+1) touches/exceeds it; fill = trigger or M30 open if gapped through.
 - Segments by ENTRY timestamp year: OOS-A [2004,2012), DEV [2012,2022),
   OOS-B [2022,2026).
"""

import sys
from datetime import datetime

CSV = "/root/.claude/uploads/c184c64a-1e6b-51fd-8c5d-ec395e073c64/64966031-XAU_30m_data.csv"
K = 2
FEE_R = 0.04

# ---------------------------------------------------------------- load M30
m_dt = []; m_o = []; m_h = []; m_l = []; m_c = []; m_v = []
with open(CSV, "r") as f:
    header = f.readline()
    prev = None
    bad_order = 0
    for line in f:
        line = line.strip()
        if not line:
            continue
        d, o, h, l, c, v = line.split(";")
        dt = datetime(int(d[0:4]), int(d[5:7]), int(d[8:10]),
                      int(d[11:13]), int(d[14:16]))
        if prev is not None and dt <= prev:
            bad_order += 1
        prev = dt
        m_dt.append(dt)
        m_o.append(float(o)); m_h.append(float(h))
        m_l.append(float(l)); m_c.append(float(c)); m_v.append(float(v))
nM = len(m_dt)

# ---------------------------------------------------------------- H4 resample
h_dt = []; h_o = []; h_h = []; h_l = []; h_c = []; h_v = []
h_m0 = []; h_m1 = []   # first / last M30 index of each H4 bar (inclusive)
cur_key = None
for i in range(nM):
    dt = m_dt[i]
    key = (dt.year, dt.month, dt.day, (dt.hour // 4) * 4)
    if key != cur_key:
        cur_key = key
        h_dt.append(datetime(key[0], key[1], key[2], key[3]))
        h_o.append(m_o[i]); h_h.append(m_h[i]); h_l.append(m_l[i])
        h_c.append(m_c[i]); h_v.append(m_v[i])
        h_m0.append(i); h_m1.append(i)
    else:
        if m_h[i] > h_h[-1]: h_h[-1] = m_h[i]
        if m_l[i] < h_l[-1]: h_l[-1] = m_l[i]
        h_c[-1] = m_c[i]; h_v[-1] += m_v[i]
        h_m1[-1] = i
nH = len(h_dt)

# ---------------------------------------------------------------- ATR Wilder(20)
P = 20
tr = [0.0] * nH
tr[0] = h_h[0] - h_l[0]
for i in range(1, nH):
    pc = h_c[i - 1]
    tr[i] = max(h_h[i] - h_l[i], abs(h_h[i] - pc), abs(h_l[i] - pc))
atr = [None] * nH
if nH >= P:
    atr[P - 1] = sum(tr[:P]) / P
    for i in range(P, nH):
        atr[i] = (atr[i - 1] * (P - 1) + tr[i]) / P

# ---------------------------------------------------------------- pivots k=2
piv = []  # (h4_idx, 'H' or 'L') chronological
both_count = 0
for i in range(K, nH - K):
    isH = all(h_h[i] >= h_h[i + j] and h_h[i] >= h_h[i - j] for j in range(1, K + 1))
    isL = all(h_l[i] <= h_l[i + j] and h_l[i] <= h_l[i - j] for j in range(1, K + 1))
    if isH and isL:
        both_count += 1
    if isH:
        piv.append((i, 'H'))
    if isL:
        piv.append((i, 'L'))

# ---------------------------------------------------------------- helpers
def m30_exit_sim(start_m, ep, sl, tps, direction):
    """Simulate exits on M30 from candle start_m (entry candle) onward.
    Returns list of exit prices aligned with tps. SL before TP in a candle."""
    res = [None] * len(tps)
    live = set(range(len(tps)))
    j = start_m
    while j < nM and live:
        o, hi, lo = m_o[j], m_h[j], m_l[j]
        if direction == 1:
            sl_hit = lo <= sl
            sl_px = o if o < sl else sl
        else:
            sl_hit = hi >= sl
            sl_px = o if o > sl else sl
        for t in list(live):
            tp = tps[t]
            if sl_hit:
                res[t] = sl_px
                live.discard(t)
            else:
                if direction == 1 and hi >= tp:
                    res[t] = o if o > tp else tp
                    live.discard(t)
                elif direction == -1 and lo <= tp:
                    res[t] = o if o < tp else tp
                    live.discard(t)
        j += 1
    for t in live:
        res[t] = m_c[nM - 1]
    return res


def find_stop_fill(m_start, m_end, trigger, direction):
    """First M30 candle in [m_start, m_end] touching trigger; return (idx, fill px)."""
    for j in range(m_start, m_end + 1):
        if direction == 1:
            if m_h[j] >= trigger:
                return j, (m_o[j] if m_o[j] > trigger else trigger)
        else:
            if m_l[j] <= trigger:
                return j, (m_o[j] if m_o[j] < trigger else trigger)
    return None, None


def segment(dt):
    y = dt.year
    if 2004 <= y < 2012: return "OOS-A"
    if 2012 <= y < 2022: return "DEV"
    if 2022 <= y < 2026: return "OOS-B"
    return None


def metrics(rs):
    n = len(rs)
    if n == 0:
        return "  n=%5d" % 0
    wins = sum(1 for r in rs if r > 0)
    gp = sum(r for r in rs if r > 0)
    gl = -sum(r for r in rs if r < 0)
    pf = (gp / gl) if gl > 0 else float("inf")
    return "  n=%5d  WR=%6.2f%%  avgR=%+.4f  PF=%.3f" % (
        n, 100.0 * wins / n, sum(rs) / n, pf)

# ---------------------------------------------------------------- TASK 1: N-shape
n_trades = []            # dict per entry: seg, dir, netR per variant
skipped_early_break = 0
patterns_found = 0
patterns_up = 0
patterns_dn = 0

for a in range(len(piv) - 2):
    (i0, t0), (i1, t1), (i2, t2) = piv[a], piv[a + 1], piv[a + 2]
    if i0 == i1 or i1 == i2:
        continue
    if t0 == 'L' and t1 == 'H' and t2 == 'L':
        direction = 1
        L0v, H1v, L1v = h_l[i0], h_h[i1], h_l[i2]
        if atr[i1] is None:
            continue
        leg1 = H1v - L0v
        if leg1 < 1.5 * atr[i1]:
            continue
        if not (L1v > L0v):
            continue
        retr = (H1v - L1v) / leg1
        if not (0.2 <= retr <= 0.7):
            continue
        trigger = H1v
        sl = L1v - 0.2 * atr[i1]
    elif t0 == 'H' and t1 == 'L' and t2 == 'H':
        direction = -1
        H0v, L1p, H1p = h_h[i0], h_l[i1], h_h[i2]
        if atr[i1] is None:
            continue
        leg1 = H0v - L1p
        if leg1 < 1.5 * atr[i1]:
            continue
        if not (H1p < H0v):          # lower-high, symmetric to higher-low
            continue
        retr = (H1p - L1p) / leg1
        if not (0.2 <= retr <= 0.7):
            continue
        trigger = L1p
        sl = H1p + 0.2 * atr[i1]
    else:
        continue

    patterns_found += 1
    if direction == 1:
        patterns_up += 1
    else:
        patterns_dn += 1

    # anti-lookahead: pivot at i2 confirmed after k more bars; entries allowed
    # from H4 bar i2+K+1 .. i2+12
    first_bar = i2 + K + 1
    last_bar = i2 + 12
    if last_bar >= nH:
        last_bar = nH - 1
    if first_bar >= nH:
        continue
    # if the level already broke during unconfirmed bars i2+1..i2+K -> skip
    early = False
    for b in range(i2 + 1, min(i2 + K, nH - 1) + 1):
        if direction == 1 and h_h[b] >= trigger:
            early = True
        if direction == -1 and h_l[b] <= trigger:
            early = True
    if early:
        skipped_early_break += 1
        continue

    mj, ep = find_stop_fill(h_m0[first_bar], h_m1[last_bar], trigger, direction)
    if mj is None:
        continue
    risk = (ep - sl) if direction == 1 else (sl - ep)
    if risk <= 0:
        continue
    if direction == 1:
        tps = [ep + 2 * risk, ep + 5 * risk, ep + leg1]
    else:
        tps = [ep - 2 * risk, ep - 5 * risk, ep - leg1]
    exits = m30_exit_sim(mj, ep, sl, tps, direction)
    netRs = []
    for x in exits:
        gross = (x - ep) / risk if direction == 1 else (ep - x) / risk
        netRs.append(gross - FEE_R)
    n_trades.append({"seg": segment(m_dt[mj]), "dir": direction, "rs": netRs})

# ---------------------------------------------------------------- TASK 2: BREAK
base_trades = []   # (seg, dir, netR)
e1_trades = []
box_signals_up = 0
box_signals_dn = 0
e1_no_fill = 0

def break_cond(i):
    """Return +1 break-up, -1 break-down, 0 none, for bar i (needs 20 prior bars)."""
    if i < P or atr[i] is None:
        return 0
    bh = max(h_h[i - P:i])
    bl = min(h_l[i - P:i])
    if h_c[i] > bh + 0.25 * atr[i]:
        return 1
    if h_c[i] < bl - 0.25 * atr[i]:
        return -1
    return 0

prev_cond = 0
for i in range(nH - 1):          # need bar i+1 to enter
    cond = break_cond(i)
    fresh = (cond != 0 and cond != prev_cond)
    prev_cond = cond
    if not fresh:
        continue
    d = cond
    if d == 1:
        box_signals_up += 1
    else:
        box_signals_dn += 1
    a = atr[i]

    # baseline: market at open of first M30 of bar i+1
    mj = h_m0[i + 1]
    ep = m_o[mj]
    sl = ep - d * a
    tp = ep + d * 2 * a
    x = m30_exit_sim(mj, ep, sl, [tp], d)[0]
    gross = d * (x - ep) / a
    base_trades.append((segment(m_dt[mj]), d, gross - FEE_R))

    # E1: stop at break-bar extreme, only during bar i+1
    trig = h_h[i] if d == 1 else h_l[i]
    mj2, ep2 = find_stop_fill(h_m0[i + 1], h_m1[i + 1], trig, d)
    if mj2 is None:
        e1_no_fill += 1
        continue
    sl2 = ep2 - d * a
    tp2 = ep2 + d * 2 * a
    x2 = m30_exit_sim(mj2, ep2, sl2, [tp2], d)[0]
    gross2 = d * (x2 - ep2) / a
    e1_trades.append((segment(m_dt[mj2]), d, gross2 - FEE_R))

# ---------------------------------------------------------------- REPORT
SEGS = ["OOS-A", "DEV", "OOS-B", "ALL"]

def pick(trs, seg, dirf=None):
    out = []
    for t in trs:
        if seg != "ALL" and t[0] != seg:
            continue
        if dirf is not None and t[1] != dirf:
            continue
        out.append(t[2])
    return out

print("=" * 78)
print("FABLE-B independent engine  |  data rows M30 =", nM,
      "| H4 bars =", nH, "| out-of-order rows =", bad_order)
print("H4 range:", h_dt[0], "->", h_dt[-1])
print("k =", K, "| pivots:", sum(1 for p in piv if p[1] == 'H'), "highs,",
      sum(1 for p in piv if p[1] == 'L'), "lows | bars both H&L pivot:", both_count)
print()
print("TASK 1 - N-shape (long+short). Patterns passing filters:", patterns_found,
      "(up %d / down %d)" % (patterns_up, patterns_dn))
print("  skipped (level broken during unconfirmed bars L1+1..L1+k):",
      skipped_early_break, "| entered trades:", len(n_trades))
VAR = ["TP=2R", "TP=5R", "TP=MM"]
for seg in SEGS:
    sub = [t for t in n_trades if seg == "ALL" or t["seg"] == seg]
    print("  [%s]" % seg)
    pooled = []
    for vi, vn in enumerate(VAR):
        rs = [t["rs"][vi] for t in sub]
        pooled += rs
        print("    %-6s%s" % (vn, metrics(rs)))
    print("    %-6s%s" % ("ALL*", metrics(pooled)))
print("  (*ALL = 3 TP variants pooled, same entries counted once per variant)")
print()
print("TASK 2 - BREAK sleeve, Donchian-20 fresh crosses: up=%d down=%d | "
      "E1 not filled next bar: %d" % (box_signals_up, box_signals_dn, e1_no_fill))
for seg in SEGS:
    print("  [%s]" % seg)
    print("    baseline %s" % metrics(pick(base_trades, seg)))
    print("    E1       %s" % metrics(pick(e1_trades, seg)))
print("  long-only breakdown (for convergence checks):")
for seg in SEGS:
    print("  [%s] baseline-L %s" % (seg, metrics(pick(base_trades, seg, 1))))
    print("  %s E1-L       %s" % (" " * len("[%s]" % seg), metrics(pick(e1_trades, seg, 1))))
