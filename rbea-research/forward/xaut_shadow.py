#!/usr/bin/env python3
"""XAUT SHADOW-RUN (PROXY vang 24/7) — sleeve BREAK Donchian-20 DONG BANG (R7g), doc lap voi MT5.
Chay: python3 xaut_shadow.py <xaut_30m.csv> [log_csv]
Data: nhanh data-gold cua repo nay (bot GitHub Actions cap nhat moi 4h):
  curl -sSL https://raw.githubusercontent.com/hoangminhvu423/thosat-pro-app/data-gold/xaut_30m.csv
CANH BAO (LESSON-04): XAUT la vang token-hoa giao dich 24/7 tren san crypto — KHONG PHAI XAUUSD CFD
(khac gio weekend, spread, thanh khoan). Log nay la PROXY THAM CHIEU DOC LAP; ground truth cua
sleeve XAU van la MT5 export / VPS demo. Khong dung log nay lam bang chung PASS/FAIL gate G4.
- Chi ghi lenh DA DONG. Idempotent: dedupe theo (entry_ts,dir). GOLIVE 2026-07-24 (truoc do tag B).
"""
import sys, os
from datetime import datetime
FEE = 0.04
GOLIVE = datetime(2026, 7, 24)
LOG = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "xaut_shadow_log.csv")

def load_30m(p):
    rows = []
    with open(p) as f:
        f.readline()
        for line in f:
            q = line.strip().split(',')
            if len(q) < 6:
                continue
            try:
                dt = datetime.strptime(q[0], "%Y-%m-%d %H:%M")
                rows.append((dt, float(q[1]), float(q[2]), float(q[3]), float(q[4])))
            except Exception:
                continue
    rows.sort(key=lambda x: x[0])
    return rows

def run(rows):
    h = []; hm0 = []; cur = None
    for i, (dt, o, hh, ll, c) in enumerate(rows):
        k = dt.replace(hour=(dt.hour // 4) * 4, minute=0)
        if cur != k:
            h.append([k, o, hh, ll, c]); hm0.append(i); cur = k
        else:
            h[-1][2] = max(h[-1][2], hh); h[-1][3] = min(h[-1][3], ll); h[-1][4] = c
    nH = len(h); P = 20
    if nH <= P + 1:
        return [], 0
    tr = [h[0][2] - h[0][3]] + [max(h[i][2] - h[i][3], abs(h[i][2] - h[i-1][4]), abs(h[i][3] - h[i-1][4])) for i in range(1, nH)]
    atr = [None] * nH
    atr[P-1] = sum(tr[:P]) / P
    for i in range(P, nH):
        atr[i] = (atr[i-1] * (P - 1) + tr[i]) / P
    trades = []; open_ct = 0; prevc = 0
    for i in range(P, nH - 1):
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
        sl = ep - d * a; tp = ep + d * 2 * a
        x = None; xt = None
        for j in range(mj, len(rows)):
            _, o, hh, ll, cc = rows[j]
            if d == 1:
                if ll <= sl: x = (o if o < sl else sl); xt = rows[j][0]; break
                if hh >= tp: x = (o if o > tp else tp); xt = rows[j][0]; break
            else:
                if hh >= sl: x = (o if o > sl else sl); xt = rows[j][0]; break
                if ll <= tp: x = (o if o < tp else tp); xt = rows[j][0]; break
        if x is None:
            open_ct += 1; continue
        trades.append((rows[mj][0], d, round(d * (x - ep) / a - FEE, 3), xt))
    return trades, open_ct

def main():
    rows = load_30m(sys.argv[1])
    if not rows:
        print("[xaut] khong co data"); return
    trades, open_ct = run(rows)
    seen = set()
    if os.path.exists(LOG):
        for l in open(LOG):
            p = l.strip().split(',')
            if len(p) >= 2 and not l.startswith('#'):
                seen.add((p[0], p[1]))
    new = []
    for et, d, r, xt in trades:
        key = (et.strftime('%Y-%m-%d %H:%M'), str(d))
        if key not in seen:
            tag = 'F' if et >= GOLIVE else 'B'
            new.append(f"{key[0]},{d},{r},{xt:%Y-%m-%d %H:%M},{tag}")
    mode = 'a' if os.path.exists(LOG) else 'w'
    with open(LOG, mode) as f:
        if mode == 'w':
            f.write("# entry_ts,dir,netR,exit_ts,tag(B/F) | XAUT-USDT PROXY (24/7, khong phai XAUUSD CFD) | BREAK Donchian-20 R7g | golive 2026-07-24\n")
        for l in new:
            f.write(l + "\n")
    fwd = [l for l in open(LOG) if l.strip().endswith(',F')]
    fr = [float(l.split(',')[2]) for l in fwd]
    print(f"[xaut] data den {rows[-1][0]:%Y-%m-%d %H:%M} | moi ghi: {len(new)} | dang mo: {open_ct}")
    print(f"[xaut] FORWARD tich luy: n={len(fr)} totR={sum(fr):+.2f} avgR={(sum(fr)/len(fr)) if fr else 0:+.3f}")

if __name__ == '__main__':
    main()
