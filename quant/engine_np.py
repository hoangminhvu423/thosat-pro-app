#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine_np.py — Engine backtest vectorized (numpy) cho bộ quét phương pháp.

Giao thức CỨNG (khớp docs/quant-handoff.md + quant/backtest_vote.py):
  1. Tín hiệu tính tại nến ĐÃ ĐÓNG index i (score chỉ dùng bars[<=i]) → vào lệnh OPEN nến i+1.
  2. SL/TP theo ATR (đo tại i, tức đã đóng). PnL chuẩn hoá R-multiple, cùng RR cho MỌI phương pháp.
  3. Same-bar cả SL lẫn TP đều chạm → tính SL trước (bảo thủ, vì OHLC không cho thứ tự intrabar).
  4. Phí = spread+commission+slippage (round-turn, theo price) / độ rộng SL → ra R. KHÔNG có look-ahead.
  5. Walk-forward: chọn ngưỡng CHỈ trên IS, đóng băng cho OOS + validation. Bootstrap CI 95% cho EV.

Engine tách khỏi logic (logics.py) để test được: chạy trực tiếp file này = selftest ATR/mô phỏng.
"""
import numpy as np

# ---------------------------------------------------------------- ATR (no look-ahead)
def atr(h, l, c, n=14):
    """ATR[i] = SMA(TR) trên [i-n+1..i]. TR[i] dùng c[i-1] → chỉ quá khứ+hiện tại. NaN khi chưa đủ n."""
    h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    prev_c = np.empty_like(c); prev_c[0] = c[0]; prev_c[1:] = c[:-1]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    out = np.full(len(c), np.nan)
    if len(c) > n:
        cs = np.cumsum(tr)
        out[n:] = (cs[n:] - cs[:-n]) / n          # sum(tr[i-n+1..i]) = cs[i]-cs[i-n]
    return out

# ---------------------------------------------------------------- bảng phí Exness (round-turn, PRICE)
# spread + commission + slippage, gộp thành 1 số theo đơn vị giá của symbol. cost_R = cost_price / SL_width.
# Nguồn: mức Exness Pro/Raw thực tế ~2026 (majors ~0.6–1.0 pip all-in; cross rộng hơn; kim loại theo point).
# Chỉnh ở đây nếu có bảng phí chính xác hơn — engine chỉ đọc số này.
_PIP = 0.0001
_PIP_JPY = 0.01
COST_PRICE = {
    # FX majors non-JPY: ~1.0 pip all-in
    'eurusd': 1.0*_PIP, 'gbpusd': 1.0*_PIP, 'usdchf': 1.0*_PIP, 'usdcad': 1.0*_PIP,
    'audusd': 1.0*_PIP, 'nzdusd': 1.0*_PIP,
    'usdjpy': 1.0*_PIP_JPY,
    # FX cross non-JPY: ~1.8 pip
    'eurcad': 1.8*_PIP, 'eurchf': 1.8*_PIP, 'eurgbp': 1.8*_PIP, 'gbpchf': 1.8*_PIP,
    # FX cross JPY: ~1.8 pip
    'eurjpy': 1.8*_PIP_JPY, 'gbpjpy': 1.8*_PIP_JPY, 'audjpy': 1.8*_PIP_JPY,
    'nzdjpy': 1.8*_PIP_JPY, 'chfjpy': 1.8*_PIP_JPY,
    # kim loại (point = 1.0 giá)
    'xauusd': 0.35, 'xagusd': 0.035,
}
DEFAULT_COST = 1.5*_PIP   # symbol lạ → coi như cross

ASSET_CLASS = {
    **{s: 'fx_major' for s in ['eurusd','gbpusd','usdchf','usdcad','audusd','nzdusd','usdjpy']},
    **{s: 'fx_cross' for s in ['eurcad','eurchf','eurgbp','gbpchf','eurjpy','gbpjpy','audjpy','nzdjpy','chfjpy']},
    'xauusd': 'metal', 'xagusd': 'metal',
}

def cost_price_of(symbol):
    return COST_PRICE.get(symbol, DEFAULT_COST)

# ---------------------------------------------------------------- mô phỏng lệnh (per-trade numpy exit)
def mo_phong(o, h, l, c, atr_arr, signal, cost_price,
             lo, hi, sl_mult=1.5, tp_mult=2.25, max_bar=20):
    """Chạy mô phỏng cho entries có decision-index i ∈ [lo, hi).
    signal[i] ∈ {-1,0,+1} tại nến đóng i → vào OPEN i+1. Không chồng lệnh (1 lệnh/lúc).
    Trả về np.array R-multiple đã trừ phí. Exit dò bằng numpy trên cửa sổ ≤ max_bar (nhanh)."""
    o = np.asarray(o, float); h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    N = len(c)
    hi = min(hi, N - 1)                                  # cần o[i+1]
    rr = tp_mult / sl_mult                               # R khi ăn TP
    # chỉ xét các nến có tín hiệu trong đoạn — thưa hơn nhiều so với quét từng nến
    idx = np.nonzero(signal[lo:hi] != 0)[0] + lo
    trades = []
    last_exit = lo - 1
    for i in idx:
        if i <= last_exit:                              # còn kẹt trong lệnh trước
            continue
        d = signal[i]
        a = atr_arr[i]
        if not (a > 0) or np.isnan(a):
            continue
        entry = o[i+1]
        sl_w = sl_mult * a
        if d > 0:
            sl = entry - sl_w; tp = entry + tp_mult * a
        else:
            sl = entry + sl_w; tp = entry - tp_mult * a
        end = min(i + 1 + max_bar, N)
        wl = l[i+1:end]; wh = h[i+1:end]
        if d > 0:
            sl_hits = np.nonzero(wl <= sl)[0]
            tp_hits = np.nonzero(wh >= tp)[0]
        else:
            sl_hits = np.nonzero(wh >= sl)[0]
            tp_hits = np.nonzero(wl <= tp)[0]
        si = sl_hits[0] if sl_hits.size else None
        ti = tp_hits[0] if tp_hits.size else None
        if si is not None and (ti is None or si <= ti):  # SL trước (hoặc hoà bar → bảo thủ)
            r = -1.0; jrel = si
        elif ti is not None:
            r = rr; jrel = ti
        else:                                            # time-stop theo close nến cuối cửa sổ
            jrel = (end - 1) - (i + 1)
            r = d * (c[end-1] - entry) / sl_w
        cost_r = cost_price / sl_w                        # phí quy R (phụ thuộc độ rộng SL tại i)
        trades.append(r - cost_r)
        last_exit = (i + 1) + jrel
    return np.array(trades, float)

# ---------------------------------------------------------------- thống kê
def thong_ke(trades):
    if trades is None or len(trades) == 0:
        return None
    t = np.asarray(trades, float); n = len(t)
    ev = float(t.mean())
    win = float((t > 0).mean())
    lai = float(t[t > 0].sum()); lo = float(-t[t < 0].sum())
    pf = (lai / lo) if lo > 0 else float('inf')
    sd = float(t.std())
    sharpe = (ev / sd) if sd > 0 else 0.0                 # Sharpe per-trade (chưa annualize)
    eq = np.cumsum(t); peak = np.maximum.accumulate(eq); maxdd = float((peak - eq).max()) if n else 0.0
    return {'n': n, 'ev': ev, 'win': win, 'pf': pf, 'sharpe': sharpe, 'maxdd': maxdd}

def bootstrap_ci(trades, lan=2000, seed=1):
    """CI 95% cho EV bằng bootstrap trên chuỗi lệnh."""
    t = np.asarray(trades, float); n = len(t)
    if n < 30:
        return (float('nan'), float('nan'))
    rng = np.random.default_rng(seed)
    means = t[rng.integers(0, n, size=(lan, n))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return (float(lo), float(hi))

# ---------------------------------------------------------------- selftest engine
if __name__ == '__main__':
    # random-walk: không có edge → EV mô phỏng phải ≈ 0 (âm nhẹ do phí). ATR phải >0 sau warmup.
    rng = np.random.default_rng(0)
    steps = rng.normal(0, 0.4, 6000)
    c = 100 + np.cumsum(steps)
    o = np.empty_like(c); o[0] = 100; o[1:] = c[:-1]
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.2, 6000))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.2, 6000))
    a = atr(h, l, c)
    assert np.nanmin(a[20:]) > 0, "ATR phải dương sau warmup"
    sig = np.zeros(6000, int); sig[50:-2:7] = rng.choice([-1, 1], size=len(sig[50:-2:7]))
    tr = mo_phong(o, h, l, c, a, sig, cost_price=0.01, lo=50, hi=6000)
    st = thong_ke(tr); ci = bootstrap_ci(tr)
    print(f"[selftest engine] N={st['n']}  EV={st['ev']:+.4f}R  win={st['win']*100:.1f}%  "
          f"PF={st['pf']:.2f}  CI95=[{ci[0]:+.4f},{ci[1]:+.4f}]")
    print("Kỳ vọng: EV ≈ 0 (âm nhẹ vì phí). Nếu EV dương rõ trên random-walk → nghi look-ahead trong engine.")
