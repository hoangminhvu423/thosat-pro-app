#!/usr/bin/env python3
"""EA-SEMANTICS SIM — mo phong Python dung NGU NGHIA RB_EA (v0.31+) de doi chieu voi backtest overlap
va voi MT5 Strategy Tester. Cong cu bang chung cua FINDING_MINLOT_20260724.md.
Chay: python3 ea_semantics_sim.py <btc_bitstamp_1min_csv> [balance] [risk_pct]
  vd: python3 ea_semantics_sim.py btc_latest.csv 4600 0.15
In ra 3 tang: A) engine overlap chuan R7g  B) ngu nghia EA khong min-lot  C) ngu nghia EA + min-lot 0.01.
Ket luan da kiem chung 2026-07-24: A=187, B=159 (flag-b chi cat ~15%), C=2 (min-lot nuot 171 lenh)
tren cua so 18 thang 01/2025-07/2026 — tester 13 lenh/PF 2.24 la artifact chon mau do min-lot.
Ngu nghia EA mo phong: 1-vi-the, budget 1 BREAK/ngay, gap 60', state RANGE/BREAK/NEUTRAL voi
false-break khoa het ngay, day-reset tra mode ve RANGE, time-stop 192h, fee 0.04R, balance compound.
"""
import sys
from datetime import datetime, timedelta

FEE = 0.04

def load_1min(p):
    m30 = {}; order = []
    with open(p) as f:
        f.readline()
        for line in f:
            try:
                ts, o, h, l, c, v = line.strip().split(',')
                t = int(float(ts))
            except Exception:
                continue
            dt = datetime.utcfromtimestamp(t)
            k = dt.replace(minute=(dt.minute // 30) * 30, second=0)
            if k not in m30:
                m30[k] = [float(o), float(h), float(l), float(c)]
            else:
                b = m30[k]; b[1] = max(b[1], float(h)); b[2] = min(b[2], float(l)); b[3] = float(c)
    return [(k,) + tuple(m30[k]) for k in sorted(m30)]

def h4_atr(rows, P=20):
    h = []; hm0 = []; cur = None
    for i, (dt, o, hh, ll, c) in enumerate(rows):
        k = dt.replace(hour=(dt.hour // 4) * 4, minute=0)
        if cur != k:
            h.append([k, o, hh, ll, c]); hm0.append(i); cur = k
        else:
            h[-1][2] = max(h[-1][2], hh); h[-1][3] = min(h[-1][3], ll); h[-1][4] = c
    nH = len(h)
    tr = [h[0][2] - h[0][3]] + [max(h[i][2] - h[i][3], abs(h[i][2] - h[i-1][4]), abs(h[i][3] - h[i-1][4])) for i in range(1, nH)]
    atr = [None] * nH
    atr[P-1] = sum(tr[:P]) / P
    for i in range(P, nH):
        atr[i] = (atr[i-1] * (P - 1) + tr[i]) / P
    return h, hm0, atr

def path_exit(rows, mj, d, ep, sl, tp, endt):
    for j in range(mj, len(rows)):
        t, o, hh, ll, cc = rows[j]
        if t >= endt:
            return (cc, t)
        if d == 1:
            if ll <= sl: return ((o if o < sl else sl), t)
            if hh >= tp: return ((o if o > tp else tp), t)
        else:
            if hh >= sl: return ((o if o > sl else sl), t)
            if ll <= tp: return ((o if o < tp else tp), t)
    return (rows[-1][4], rows[-1][0])

def run_overlap(rows, h, hm0, atr, P=20):
    out = []; prevc = 0
    for i in range(P, len(h) - 1):
        a = atr[i]
        if not a or a <= 0:
            prevc = 0; continue
        bh = max(h[k][2] for k in range(i - P, i)); bl = min(h[k][3] for k in range(i - P, i))
        c = h[i][4]
        cond = 1 if c > bh + 0.25 * a else (-1 if c < bl - 0.25 * a else 0)
        fresh = (cond != 0 and cond != prevc); prevc = cond
        if not fresh:
            continue
        d = cond; mj = hm0[i + 1]; ep = rows[mj][1]
        x, xt = path_exit(rows, mj, d, ep, ep - d * a, ep + d * 2 * a, datetime(2100, 1, 1))
        out.append((rows[mj][0], d * (x - ep) / a - FEE))
    return out

def run_ea(rows, h, hm0, atr, minlot_on, bal0, risk_pct, P=20, minlot=0.01, lotstep=0.01):
    out = []; skips = 0
    mode = 'RANGE'; day = None; bud = 1; pos_exit = None; last = None; fro = (0, 0); bal = bal0
    for i in range(P, len(h) - 1):
        bt = h[i + 1][0]
        if day != bt.date():
            day = bt.date(); bud = 1
            if mode in ('NEUTRAL', 'BREAK'):
                mode = 'RANGE'
        a = atr[i]
        if not a or a <= 0:
            continue
        in_pos = pos_exit is not None and bt < pos_exit
        c = h[i][4]
        if mode == 'RANGE':
            bh = max(h[k][2] for k in range(i - P, i)); bl = min(h[k][3] for k in range(i - P, i))
            if c > bh + 0.25 * a or c < bl - 0.25 * a:
                d = 1 if c > bh else -1
                fro = (bh, bl); mode = 'BREAK'
                gap = last is None or (bt - last) >= timedelta(minutes=60)
                if bud > 0 and gap and not in_pos:
                    mj = hm0[i + 1]; ep = rows[mj][1]
                    risk = bal * risk_pct / 100.0
                    lot = int(risk / a / lotstep) * lotstep   # floor theo lot-step (1 lot = 1 BTC, tv $1)
                    if minlot_on and lot < minlot:
                        skips += 1
                    else:
                        x, xt = path_exit(rows, mj, d, ep, ep - d * a, ep + d * 2 * a, bt + timedelta(hours=192))
                        rr = d * (x - ep) / a - FEE
                        out.append((rows[mj][0], rr))
                        bal += rr * risk
                        bud -= 1; last = bt; pos_exit = xt
        elif mode == 'BREAK':
            if fro[1] < c < fro[0]:
                mode = 'NEUTRAL'
    return out, skips

def report(tag, trades, w0, w1):
    r = [x[1] for x in trades if w0 <= x[0] < w1]
    w = [x for x in r if x > 0]; lo = [-x for x in r if x < 0]
    pf = (sum(w) / sum(lo)) if lo else 9.9
    print(f"  {tag:44s} n={len(r):4d} totR={sum(r):+8.2f} PF={pf:4.2f}")

def main():
    bal = float(sys.argv[2]) if len(sys.argv) > 2 else 4600.0
    rp = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
    rows = load_1min(sys.argv[1])
    h, hm0, atr = h4_atr(rows)
    A = run_overlap(rows, h, hm0, atr)
    B, _ = run_ea(rows, h, hm0, atr, False, bal, rp)
    C, sk = run_ea(rows, h, hm0, atr, True, bal, rp)
    for wn, w0, w1 in [("18 THANG 01/2025-07/2026", datetime(2025, 1, 1), datetime(2026, 7, 25)),
                       ("3 THANG 24/04-24/07/2026", datetime(2026, 4, 24), datetime(2026, 7, 25))]:
        print(f"=== {wn} (bal {bal:.0f}, risk {rp}%) ===")
        report("A engine OVERLAP (R7g)", A, w0, w1)
        report("B ngu nghia EA (khong min-lot)", B, w0, w1)
        report(f"C ngu nghia EA + min-lot 0.01", C, w0, w1)
    print(f"  Tong lenh SKIP boi min-lot (toan ky): {sk}")

if __name__ == '__main__':
    main()
