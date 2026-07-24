#!/usr/bin/env python3
"""
rbea_ship.py — TRỤ 2: 1 lệnh = cả vòng đánh giá RB_EA (headless, KHÔNG đụng terminal live).
=========================================================================================
Vòng "sửa → đánh giá" từ ~30 phút nhiều lượt xuống ~1 phút 1 lệnh. Chạy trên MacBook.

  python3 rbea-research/tools/rbea_ship.py            # đánh giá trên bar data đã lưu
  python3 rbea-research/tools/rbea_ship.py --pull     # kéo bar mới từ VPS trước (bridge), rồi đánh giá

Làm 4 việc:
 1. (tuỳ chọn --pull) kéo BTCUSD+XAUUSD H4 mới từ VPS qua bridge sẵn có.
 2. Backtest sleeve BREAK Donchian-20 (đúng logic EA) → trades/PF/WR/DD/tần suất mỗi symbol.
 3. R7h MC lãi kép cho các mức risk 3 mode → CAGR/DD → kiểm PERSONAL đạt 15-17%.
 4. Min-lot clearance mỗi mode × balance → cảnh báo under-trade (bài học G2 13 lệnh).
Xuất verdict PASS/FAIL + bảng số. KHÔNG thay MT5 tester (cổng cuối trước live), mà là màn sàng nhanh.

LƯU Ý PARITY: engine này xấp xỉ EA (bar-close, không tick). Số dùng để SÀNG + so tương đối giữa
các bản sửa. Trước khi cho tiền thật vẫn chạy MT5 tester 1 lần (authoritative).
"""
import sys, csv, collections, argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "rbea-research/data"
SEED = 20260723

# Bó tham số 3 mode (khớp ApplyMode trong RB_EA_v0.5)
MODES = {"FUND": 0.15, "HUMAN_ALPHA": 0.20, "PERSONAL": 0.85}
# spec symbol (Exness) để tính min-lot: loss cho 1 lot khi giá đi 'dist'
SPEC = {"BTCUSD": dict(lpl=lambda d: d,       vol_min=0.01),
        "XAUUSD": dict(lpl=lambda d: d * 100, vol_min=0.01)}


def load(sym):
    rows = []
    for x in csv.DictReader(open(DATA / f"bars_{sym}_H4.csv")):
        rows.append((x["time"], float(x["open"]), float(x["high"]), float(x["low"]), float(x["close"])))
    return rows


def atr(b, i, n=20):
    if i < n:
        return 0.0
    return sum(max(b[k][2] - b[k][3], abs(b[k][2] - b[k - 1][4]), abs(b[k][3] - b[k - 1][4]))
               for k in range(i - n + 1, i + 1)) / n


def backtest(bars):
    """BREAK-only, AutoZone Donchian-20 shift2, SL 1ATR/TP 2ATR, 1 vị thế, budget 1/ngày, timestop 48."""
    tr = []; pos = None; last_day = None; bud = 0
    for t in range(21, len(bars) - 1):
        tm, o, h, l, c = bars[t]; day = tm[:10]
        if day != last_day:
            last_day = day; bud = 1
        if pos:
            d, entry, sl, tp, et = pos; hit = None
            if d > 0:
                hit = -1.0 if l <= sl else (2.0 if h >= tp else None)
            else:
                hit = -1.0 if h >= sl else (2.0 if l <= tp else None)
            if hit is None and t - et >= 48:
                hit = (c - entry) / abs(entry - sl) * d
            if hit is not None:
                tr.append((tm, hit, abs(entry - sl))); pos = None
        if pos or bud <= 0:
            continue
        a = atr(bars, t - 1)
        if a <= 0:
            continue
        hi = max(bars[k][2] for k in range(t - 21, t - 1))
        lo = min(bars[k][3] for k in range(t - 21, t - 1))
        c1 = bars[t - 1][4]
        d = 1 if c1 > hi + 0.25 * a else (-1 if c1 < lo - 0.25 * a else 0)
        if d:
            entry = c; pos = (d, entry, entry - d * a, entry + d * 2 * a, t); bud -= 1
    return tr


def lcg():
    s = SEED
    while True:
        s = (s * 6364136223846793005 + 1442695040888963407) % (2 ** 64)
        yield s / 2 ** 64


def mc(xs, bs, w, rng, paths=8000, months=60, block=3):
    n = min(len(xs), len(bs)); cagrs = []; dd30 = 0; mdds = []
    for _ in range(paths):
        eq = 1.0; peak = 1.0; mdd = 0.0; m = 0
        while m < months:
            i = int(next(rng) * (n - block))
            for j in range(block):
                if m >= months:
                    break
                eq *= (1 + (xs[i + j] + bs[i + j]) * w / 100); m += 1
                peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
        cagrs.append(eq ** (12.0 / months) - 1); mdds.append(mdd)
        if mdd > 0.30:
            dd30 += 1
    cagrs.sort(); mdds.sort()
    return cagrs[len(cagrs) // 2] * 100, mdds[len(mdds) // 2] * 100, 100 * dd30 / paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", action="store_true", help="kéo bar mới từ VPS trước")
    ap.add_argument("--balance", type=float, default=3909.0, help="balance để kiểm min-lot")
    args = ap.parse_args()

    if args.pull:
        print(">>> Kéo bar mới từ VPS (bridge)... (chạy tools/rbea_pull_bars.py)")
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).with_name("rbea_pull_bars.py"))], check=False)

    verdict = []; monthly = {}
    print("=" * 72)
    print("RB_EA SHIP — đánh giá nhanh (headless, không đụng terminal live)")
    print("=" * 72)
    for sym in ["BTCUSD", "XAUUSD"]:
        f = DATA / f"bars_{sym}_H4.csv"
        if not f.exists():
            print(f"  ❌ thiếu {f.name} — chạy với --pull"); return 1
        bars = load(sym); tr = backtest(bars)
        n = len(tr); tot = sum(r for _, r, _ in tr); wins = sum(1 for _, r, _ in tr if r > 0)
        span_m = (int(bars[-1][0][:4]) - int(bars[0][0][:4])) * 12 + int(bars[-1][0][5:7]) - int(bars[0][0][5:7]) or 1
        print(f"\n[{sym}] {bars[0][0][:7]}→{bars[-1][0][:7]}  {n} lệnh, tổng {tot:+.1f}R, "
              f"WR {100*wins/n:.0f}%, TB {tot/n:+.3f}R, ~{n/span_m*12:.0f} lệnh/năm")
        verdict.append((f"{sym} expectancy>0", tot > 0))
        # monthly R-sum cho MC
        mon = collections.OrderedDict()
        for tm, r, _ in tr:
            mon[tm[:7]] = mon.get(tm[:7], 0.0) + r
        monthly[sym] = mon
        # min-lot clearance mỗi mode
        print(f"  min-lot clear @balance {args.balance:.0f}:", end=" ")
        for mode, risk in MODES.items():
            clr = 0
            for _, _, dist in tr:
                lot = (args.balance * risk / 100.0) / SPEC[sym]["lpl"](dist)
                lot = int(lot / 0.01) * 0.01
                if lot >= SPEC[sym]["vol_min"]:
                    clr += 1
            print(f"{mode} {clr}/{n}", end="  ")
        print()

    # R7h MC joint
    common = sorted(set(monthly["XAUUSD"]) & set(monthly["BTCUSD"]))
    xs = [monthly["XAUUSD"][k] for k in common]; bs = [monthly["BTCUSD"][k] for k in common]
    print(f"\n[R7h MC] joint XAU+BTC, {len(common)} tháng chung, lãi kép 5y 8k paths:")
    print(f"  {'mode':>12} {'risk':>6} {'CAGR med':>9} {'medMaxDD':>9} {'P(DD>30%)':>10}")
    rng = lcg()
    for mode, risk in MODES.items():
        cg, dd, p30 = mc(xs, bs, risk, rng)
        flag = ""
        if mode == "PERSONAL":
            ok = 13 <= cg <= 20
            verdict.append(("PERSONAL CAGR ~15-17%", ok)); flag = " ✅" if ok else " ⚠️"
        print(f"  {mode:>12} {risk:>5.2f}% {cg:>+8.1f}% {dd:>8.1f}% {p30:>9.1f}%{flag}")

    print("\n" + "=" * 72)
    allok = all(v for _, v in verdict)
    for name, v in verdict:
        print(f"  {'✅' if v else '❌'} {name}")
    print(f"\n VERDICT: {'PASS ✅' if allok else 'FAIL ❌ — xem trên'}")
    print("=" * 72)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
