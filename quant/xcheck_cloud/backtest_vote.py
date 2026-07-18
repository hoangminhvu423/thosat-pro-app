#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backtest_vote.py — So sánh RANDOM-VOTE vs HỢP NHẤT TẤT ĐỊNH trên data thật.
Giao thức: no-look-ahead / walk-forward / cộng phí / bootstrap. Thuần stdlib.

Chạy:  python3 quant/backtest_vote.py duong_dan_data.csv --spread-r 0.05
Tự kiểm harness (random-walk, kỳ vọng EV≈0):  python3 quant/backtest_vote.py --selftest

CSV hỗ trợ (tự nhận diện): MT5 export (tab, cột <DATE> <TIME> <OPEN>...),
MT4 history (2023.01.02,00:00,o,h,l,c,v), hoặc CSV thường có header Date/Open/High/Low/Close.

NGUYÊN TẮC CỨNG (theo docs/quant-handoff.md):
  1. Tín hiệu tính tại nến ĐÃ ĐÓNG index i (chỉ dùng bars[<=i]) → vào lệnh tại OPEN nến i+1.
  2. Calibration (map score→xác suất, chọn ngưỡng) CHỈ trên in-sample (60% đầu), đóng băng cho OOS.
  3. Phí = spread + commission + slippage, tính bằng R (tỉ lệ trên SL) qua --spread-r.
  4. PnL chuẩn hoá theo R-multiple (risk cố định mỗi lệnh), TP/SL theo ATR — giống nhau cho MỌI biến thể.
  5. Random-vote chạy 25 seed → báo median + khoảng, vì nó phi tất định.
3 logic mẫu (breakout cấu trúc, phân kỳ momentum, hồi quy về vùng) là PLACEHOLDER —
thay bằng logic thật (SMC/Wyckoff/PA...) bằng cách viết hàm score mới vào DANH_SACH_LOGIC.
"""
import csv, sys, math, random, argparse, statistics

# ---------------------------------------------------------------- đọc data
def doc_csv(path):
    """Đọc CSV OHLC nhiều định dạng MT4/MT5/generic. Trả list dict o/h/l/c."""
    with open(path, newline='', encoding='utf-8-sig', errors='replace') as f:
        mau = f.read(4096); f.seek(0)
        delim = '\t' if '\t' in mau.split('\n')[0] else (';' if mau.count(';') > mau.count(',') else ',')
        rows = list(csv.reader(f, delimiter=delim))
    if not rows: sys.exit("CSV rỗng.")
    head = [c.strip().lower().strip('<>') for c in rows[0]]
    def tim(*ten):
        for t in ten:
            if t in head: return head.index(t)
        return None
    bars = []
    if tim('open') is not None:                      # có header
        io_,ih,il,ic = tim('open'), tim('high'), tim('low'), tim('close')
        data = rows[1:]
    else:                                            # MT4 không header: date,time,o,h,l,c,v
        io_,ih,il,ic = 2,3,4,5
        data = rows
    for r in data:
        try:
            bars.append({'o':float(r[io_]),'h':float(r[ih]),'l':float(r[il]),'c':float(r[ic])})
        except (ValueError, IndexError):
            continue
    if len(bars) < 300: sys.exit(f"Chỉ đọc được {len(bars)} nến — cần ≥300.")
    return bars

def sinh_random_walk(n=6000, seed=99):
    """Data giả random-walk cho --selftest: harness đúng thì EV≈0 sau phí."""
    rng = random.Random(seed); p = 100.0; bars = []
    for _ in range(n):
        o = p
        steps = [rng.gauss(0, 0.4) for _ in range(4)]
        path = [o]
        for s in steps: path.append(path[-1] + s)
        c = path[-1]; h = max(path); l = min(path); p = c
        bars.append({'o':o,'h':h,'l':l,'c':c})
    return bars

# ---------------------------------------------------------------- chỉ số nền
def atr(bars, i, n=14):
    """ATR tại nến đã đóng i (dùng bars[i-n+1..i])."""
    if i < n: return None
    s = 0.0
    for k in range(i-n+1, i+1):
        tr = max(bars[k]['h']-bars[k]['l'], abs(bars[k]['h']-bars[k-1]['c']), abs(bars[k]['l']-bars[k-1]['c']))
        s += tr
    return s/n

# ---------------------------------------------------------------- 3 logic mẫu (thay bằng logic thật của cậu)
def logic_breakout(bars, i, N=20):
    """Cấu trúc: close so với dải cao/thấp N nến TRƯỚC ĐÓ (không tính nến i). Score [-1,1]."""
    if i < N+1: return 0.0
    cao = max(b['h'] for b in bars[i-N:i]); thap = min(b['l'] for b in bars[i-N:i])
    if cao == thap: return 0.0
    return max(-1.0, min(1.0, 2*((bars[i]['c']-thap)/(cao-thap)) - 1))

def logic_phan_ky(bars, i, W=24):
    """Phân kỳ thô: price lower-low nhưng momentum higher-low (bull) và ngược lại."""
    if i < W+4: return 0.0
    lows  = [bars[k]['l'] for k in range(i-W+1, i+1)]
    roc   = [bars[k]['c']-bars[k-3]['c'] for k in range(i-W+1, i+1)]
    h = W//2
    p1,p2 = min(lows[:h]), min(lows[h:]); m1,m2 = min(roc[:h]), min(roc[h:])
    q1,q2 = max(lows[:h] and [bars[k]['h'] for k in range(i-W+1,i-W+1+h)]), max(bars[k]['h'] for k in range(i-W+1+h,i+1))
    n1,n2 = max(roc[:h]), max(roc[h:])
    sc = 0.0
    if p2 < p1 and m2 > m1: sc += 0.7          # bull divergence
    if q2 > q1 and n2 < n1: sc -= 0.7          # bear divergence
    return sc

def logic_hoi_quy(bars, i, N=20):
    """Supply/demand thô: z-score của close quanh trung bình N nến → fade cực trị."""
    if i < N+1: return 0.0
    cs = [bars[k]['c'] for k in range(i-N+1, i+1)]
    m = sum(cs)/N; sd = (sum((x-m)**2 for x in cs)/N) ** 0.5
    if sd == 0: return 0.0
    return max(-1.0, min(1.0, -(bars[i]['c']-m)/(2*sd)))

DANH_SACH_LOGIC = [('breakout', logic_breakout), ('phan_ky', logic_phan_ky), ('hoi_quy', logic_hoi_quy)]

# ---------------------------------------------------------------- calibration (CHỈ in-sample)
def fit_k(scores, kq):
    """Map score→p bằng p=0.5+0.5*tanh(k*s); chọn k max log-likelihood trên IS."""
    best_k, best_ll = 0.5, -1e18
    for k in [x/10 for x in range(1, 61, 2)]:
        ll = 0.0
        for s, y in zip(scores, kq):
            p = min(0.999, max(0.001, 0.5 + 0.5*math.tanh(k*s)))
            ll += math.log(p) if y > 0 else math.log(1-p)
        if ll > best_ll: best_ll, best_k = ll, k
    return best_k

# ---------------------------------------------------------------- mô phỏng lệnh
def mo_phong(bars, quyet_dinh, chi_phi_r, sl_mult=1.5, tp_mult=2.25, max_bar=20):
    """quyet_dinh[i] ∈ {-1,0,+1} tại nến đóng i → vào OPEN i+1. SL/TP theo ATR. Trả list R-multiple."""
    trades, i, n = [], 0, len(bars)
    while i < n-2:
        d = quyet_dinh[i]
        if d == 0: i += 1; continue
        a = atr(bars, i)
        if not a or a <= 0: i += 1; continue
        vao = bars[i+1]['o']; sl_w = sl_mult*a
        sl = vao - d*sl_w; tp = vao + d*tp_mult*a
        r = None
        for j in range(i+1, min(i+1+max_bar, n)):
            b = bars[j]
            if d > 0:
                if b['l'] <= sl: r = -1.0; break        # chạm SL trước (bảo thủ)
                if b['h'] >= tp: r = tp_mult/sl_mult; break
            else:
                if b['h'] >= sl: r = -1.0; break
                if b['l'] <= tp: r = tp_mult/sl_mult; break
        else:
            j = min(i+max_bar, n-1)
        if r is None:                                   # time-stop: đóng theo close
            r = d*(bars[j]['c']-vao)/sl_w
        trades.append(r - chi_phi_r)
        i = j + 1                                       # 1 lệnh một lúc, không chồng
    return trades

# ---------------------------------------------------------------- thống kê
def bao_cao(trades):
    if not trades: return None
    n = len(trades); ev = statistics.mean(trades)
    win = sum(1 for t in trades if t > 0)/n
    lai = sum(t for t in trades if t > 0); lo = -sum(t for t in trades if t < 0)
    pf = lai/lo if lo > 0 else float('inf')
    sd = statistics.pstdev(trades); sharpe = ev/sd if sd else 0.0
    eq = mx = dd = 0.0
    for t in trades:
        eq += t; mx = max(mx, eq); dd = max(dd, mx-eq)
    return {'n':n,'ev':ev,'win':win,'pf':pf,'sharpe':sharpe,'maxdd':dd}

def bootstrap_ci(trades, lan=2000, seed=1):
    rng = random.Random(seed); n = len(trades); ms = []
    for _ in range(lan):
        ms.append(statistics.mean(rng.choices(trades, k=n)))
    ms.sort()
    return ms[int(0.025*lan)], ms[int(0.975*lan)]

def in_dong(ten, r, ci=None):
    if not r: print(f"  {ten:22s}: (không có lệnh)"); return
    s = (f"  {ten:22s}: N={r['n']:5d}  EV/lệnh={r['ev']:+.4f}R  win={r['win']*100:5.1f}%  "
         f"PF={r['pf']:5.2f}  Sharpe={r['sharpe']:+.3f}  maxDD={r['maxdd']:.1f}R")
    if ci: s += f"  CI95%EV=[{ci[0]:+.4f},{ci[1]:+.4f}]"
    print(s)

# ---------------------------------------------------------------- pipeline chính
def chay(bars, chi_phi_r, seeds=25):
    n = len(bars); chia = int(n*0.6)
    print(f"Nến: {n} | In-sample: 0..{chia-1} | OOS: {chia}..{n-1} | phí/lệnh: {chi_phi_r:.3f}R")

    # score mọi nến, mọi logic (chỉ dùng quá khứ tại từng nến)
    scores = {ten: [f(bars, i) for i in range(n)] for ten, f in DANH_SACH_LOGIC}

    # calibration trên IS: outcome = hướng close H nến sau (H=5), chỉ i+H < chia
    H = 5
    ks = {}
    for ten in scores:
        xs, ys = [], []
        for i in range(50, chia-H):
            if scores[ten][i] != 0.0:
                xs.append(scores[ten][i]); ys.append(1 if bars[i+H]['c'] > bars[i]['c'] else -1)
        ks[ten] = fit_k(xs, ys) if len(xs) > 100 else 1.0
    print("Hệ số calib k (IS):", {t: round(k,2) for t,k in ks.items()})

    def prob(ten, i):                                   # p(lên) của logic tại nến i
        return 0.5 + 0.5*math.tanh(ks[ten]*scores[ten][i])

    # --- các bộ quyết định (trả quyet_dinh[i] cho toàn chuỗi; đánh giá riêng IS/OOS) ---
    def qd_fusion(nguong):
        out = [0]*n
        for i in range(50, n-1):
            L = sum(math.log(max(1e-6, prob(t,i))/max(1e-6, 1-prob(t,i))) for t in scores)
            out[i] = 1 if L > nguong else (-1 if L < -nguong else 0)
        return out

    def qd_single(ten, nguong):
        out = [0]*n
        for i in range(50, n-1):
            p = prob(ten, i)
            out[i] = 1 if p > 0.5+nguong else (-1 if p < 0.5-nguong else 0)
        return out

    def qd_vote(seed):
        """Cơ chế của người dùng: 2 vòng phiếu ngẫu nhiên có trọng số, đa số quyết."""
        rng = random.Random(seed); out = [0]*n
        for i in range(50, n-1):
            ps = [prob(t, i) for t in scores]
            # vòng 1 — vào/bỏ: mỗi logic vote VÀO với xác suất = độ tin (max(p,1-p))
            vao = sum(1 for p in ps if rng.random() < max(p, 1-p))
            if vao < 2: continue
            # vòng 2 — buy/sell: mỗi logic vote BUY với xác suất = p(lên)
            buy = sum(1 for p in ps if rng.random() < p)
            out[i] = 1 if buy >= 2 else -1
        return out

    # chọn ngưỡng fusion/single TRÊN IS (đóng băng cho OOS)
    def ev_is(qd):
        tr = mo_phong(bars[:chia], qd[:chia], chi_phi_r)
        return (statistics.mean(tr) if len(tr) >= 30 else -9e9), len(tr)
    best_tau, best_ev = 0.3, -9e9
    for tau in [0.1,0.2,0.3,0.5,0.8,1.2]:
        ev,_ = ev_is(qd_fusion(tau))
        if ev > best_ev: best_ev, best_tau = ev, tau
    best_logic, best_th, be = list(scores)[0], 0.05, -9e9
    for t in scores:
        for th in [0.02,0.05,0.10,0.15]:
            ev,_ = ev_is(qd_single(t, th))
            if ev > be: be, best_logic, best_th = ev, t, th
    print(f"Chọn trên IS: fusion tau={best_tau} | single={best_logic} th={best_th}")

    # --- đánh giá: in cả IS lẫn OOS để thấy khoảng cách overfit ---
    for nhan, lo, hi in [("IN-SAMPLE", 0, chia), ("OUT-OF-SAMPLE", chia, n)]:
        print(f"\n=== {nhan} ===")
        seg = bars[lo:hi]
        def cat(qd): return qd[lo:hi]
        tr_f = mo_phong(seg, cat(qd_fusion(best_tau)), chi_phi_r)
        in_dong("FUSION (log-odds)", bao_cao(tr_f), bootstrap_ci(tr_f) if len(tr_f)>30 else None)
        tr_s = mo_phong(seg, cat(qd_single(best_logic, best_th)), chi_phi_r)
        in_dong(f"SINGLE ({best_logic})", bao_cao(tr_s), bootstrap_ci(tr_s) if len(tr_s)>30 else None)
        evs, shs, alln = [], [], []
        for sd in range(seeds):
            tr_v = mo_phong(seg, cat(qd_vote(1000+sd)), chi_phi_r)
            r = bao_cao(tr_v)
            if r: evs.append(r['ev']); shs.append(r['sharpe']); alln.append(r['n'])
        if evs:
            evs.sort(); shs.sort()
            print(f"  RANDOM-VOTE (x{seeds})   : N~{int(statistics.mean(alln))}  "
                  f"EV median={statistics.median(evs):+.4f}R  [min {evs[0]:+.4f} … max {evs[-1]:+.4f}]  "
                  f"Sharpe median={statistics.median(shs):+.3f}")
        # buy & hold quy đổi R thô: giữ luôn hướng long mỗi 20 nến
        tr_b = mo_phong(seg, [1 if k % 20 == 0 else 0 for k in range(len(seg))], chi_phi_r)
        in_dong("BUY&HOLD (tham chiếu)", bao_cao(tr_b))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv', nargs='?', help='đường dẫn CSV OHLC (MT4/MT5/generic)')
    ap.add_argument('--spread-r', type=float, default=0.05,
                    help='tổng phí mỗi lệnh tính theo R (spread+comm+slippage / độ rộng SL). Mặc định 0.05R')
    ap.add_argument('--selftest', action='store_true', help='chạy trên random-walk giả — EV phải ≈ 0')
    a = ap.parse_args()
    if a.selftest:
        print(">>> SELFTEST trên random-walk (không có edge thật — mọi EV phải ≈ 0 hoặc âm nhẹ do phí):")
        chay(sinh_random_walk(), a.spread_r); return
    if not a.csv: ap.error("cần đường dẫn CSV (hoặc --selftest)")
    chay(doc_csv(a.csv), a.spread_r)

if __name__ == '__main__':
    main()
