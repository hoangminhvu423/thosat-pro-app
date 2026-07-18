#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logics.py — Bộ phương pháp giao dịch phổ biến, số hoá thành hàm score vectorized.

Mỗi hàm: score(o,h,l,c) -> np.array cùng độ dài, giá trị ∈ [-1,+1].
  score[i] > 0 = thiên LONG, < 0 = thiên SHORT, 0 = không tín hiệu.
  score[i] CHỈ được dùng dữ liệu tại/ trước i (nến đã đóng) — no look-ahead.

⚠️ GHI RÕ: đây là MỘT cách diễn giải mỗi phương pháp (nhất là Elliott/Wyckoff/SMC — vốn
   tacit, 100 người 100 kiểu). Kết quả xấu = "bản CODE NÀY chết", KHÔNG kết luận cho
   phương pháp gốc. Mục tiêu: số hoá "bản đồ nghĩa địa", không phải chứng minh method sai.

Cách kiểm no-look-ahead: chạy toàn bộ trên random-walk (run_all.py --selftest) → EV phải ≈ 0.
Hàm nào cho EV dương rõ trên random-walk = có look-ahead, phải sửa.
"""
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- rolling helpers (no look-ahead)
def _s(a): return pd.Series(np.asarray(a, float))
def prev_max(a, w):  return _s(a).rolling(w).max().shift(1).to_numpy()   # max của w nến TRƯỚC i (không gồm i)
def prev_min(a, w):  return _s(a).rolling(w).min().shift(1).to_numpy()
def roll_mean(a, w): return _s(a).rolling(w).mean().to_numpy()            # gồm i
def roll_std(a, w):  return _s(a).rolling(w).std(ddof=0).to_numpy()

def rsi(c, n=14):
    """RSI Wilder, vectorized. Chỉ dùng quá khứ (ewm nhân quả)."""
    c = _s(c); d = c.diff()
    up = d.clip(lower=0); dn = (-d).clip(lower=0)
    au = up.ewm(alpha=1/n, adjust=False).mean()
    ad = dn.ewm(alpha=1/n, adjust=False).mean()
    rs = au / ad.replace(0, np.nan)
    return (100 - 100/(1+rs)).fillna(50).to_numpy()

def pivots(h, l, w=2):
    """Fractal pivot high/low. Trả (ph_avail, pl_avail): giá pivot GẦN NHẤT đã XÁC NHẬN tại ≤ i.
    Xác nhận = k+w (cần w nến bên phải) → shift(w) đảm bảo no look-ahead."""
    hs = _s(h); ls = _s(l)
    win = 2*w + 1
    is_ph = (hs.to_numpy() >= hs.rolling(win, center=True).max().to_numpy())
    is_pl = (ls.to_numpy() <= ls.rolling(win, center=True).min().to_numpy())
    ph_val = np.where(is_ph, np.asarray(h, float), np.nan)
    pl_val = np.where(is_pl, np.asarray(l, float), np.nan)
    ph_avail = pd.Series(ph_val).shift(w).ffill().to_numpy()
    pl_avail = pd.Series(pl_val).shift(w).ffill().to_numpy()
    return ph_avail, pl_avail

def _clip(x): return np.clip(np.nan_to_num(x, nan=0.0), -1.0, 1.0)

def _prev_distinct(vals):
    """Giá trị PHÂN BIỆT liền trước của chuỗi bậc thang (vd pivot ffill): trả giá trước lần đổi gần nhất."""
    s = pd.Series(vals)
    ch = s != s.shift(1)
    return s.shift(1).where(ch).ffill().to_numpy()

# ================================================================ PRICE ACTION
def pa_pinbar(o, h, l, c):
    """Pin bar / rejection: bất đối xứng râu nến. Râu dưới dài = từ chối giảm = bullish."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    rng = np.where((h-l) > 0, h-l, np.nan)
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    return _clip((lower - upper) / rng)

def pa_engulfing(o, h, l, c):
    """Nến nhấn chìm: thân i bao trùm thân i-1 + đảo màu."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    po = np.roll(o,1); pc = np.roll(c,1)
    sc = np.zeros(len(c))
    bull = (c>o) & (pc<po) & (c>=po) & (o<=pc)
    bear = (c<o) & (pc>po) & (c<=po) & (o>=pc)
    sc[bull] = 0.7; sc[bear] = -0.7; sc[0] = 0.0
    return sc

def pa_inside_outside(o, h, l, c):
    """Outside bar (mở rộng biên) theo hướng đóng cửa = momentum. Inside bar → 0 (chờ phá)."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    ph = np.roll(h,1); pl = np.roll(l,1)
    outside = (h>ph) & (l<pl)
    sc = np.where(outside, np.sign(c-o)*0.7, 0.0)
    sc[0] = 0.0
    return sc

def pa_bos(o, h, l, c):
    """Break of structure: close phá pivot high đã xác nhận (bull) / pivot low (bear)."""
    ph, pl = pivots(h, l, w=2)
    c = np.asarray(c, float)
    sc = np.zeros(len(c))
    sc[c > ph] = 0.7
    sc[c < pl] = -0.7
    return sc

# ================================================================ SMC / ICT
def smc_fvg(o, h, l, c):
    """Fair value gap 3 nến: l[i] > h[i-2] (imbalance up) = continuation bull, và ngược lại."""
    h,l = np.asarray(h,float), np.asarray(l,float)
    h2 = np.roll(h,2); l2 = np.roll(l,2)
    sc = np.zeros(len(h))
    sc[l > h2] = 0.6          # gap tăng
    sc[h < l2] = -0.6         # gap giảm
    sc[:2] = 0.0
    return sc

def smc_order_block(o, h, l, c):
    """Order block thô: nến i-1 ngược màu + nến i impulse phá qua → OB hình thành, đi theo impulse."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    a = _atr_body(o,h,l,c)
    po,pc,ph,pl = np.roll(o,1),np.roll(c,1),np.roll(h,1),np.roll(l,1)
    imp = np.abs(c-o) > 1.0*a
    sc = np.zeros(len(c))
    bull = imp & (c>o) & (pc<po) & (c>ph)      # OB tăng: sau nến giảm là impulse tăng phá đỉnh nến trước
    bear = imp & (c<o) & (pc>po) & (c<pl)
    sc[bull] = 0.6; sc[bear] = -0.6; sc[:2] = 0.0
    return sc

def smc_liquidity_sweep(o, h, l, c, W=20):
    """Liquidity sweep / stop hunt: quét thủng đáy W nến trước rồi ĐÓNG lại trên → bull (và ngược lại)."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    pmin = prev_min(l, W); pmax = prev_max(h, W)
    sc = np.zeros(len(c))
    bull = (l < pmin) & (c > pmin)
    bear = (h > pmax) & (c < pmax)
    sc[bull] = 0.7; sc[bear] = -0.7
    return _clip(sc)

def smc_premium_discount(o, h, l, c, W=50):
    """Premium/discount: giá dưới equilibrium (mid range W) = discount → bias LONG (mean-revert về eq)."""
    c = np.asarray(c, float)
    hi = prev_max(h, W); lo = prev_min(l, W)
    eq = (hi + lo) / 2.0
    half = (hi - lo) / 2.0
    half = np.where(half > 0, half, np.nan)
    return _clip((eq - c) / half)

# ================================================================ ELLIOTT (heuristic — MỘT cách diễn giải)
def elliott_zigzag(o, h, l, c):
    """Đếm sóng đơn giản hoá: xu hướng = pivot cao/thấp cùng dâng (hoặc cùng hạ). Vào theo sóng
    tiếp diễn khi hồi xong: uptrend + nến hiện phá đỉnh nến trước sau 1 nhịp chùng → 'sóng 3/5'.
    ⚠️ Đây là 1 nội suy thô của Elliott, không phải đếm sóng chuẩn."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    ph, pl = pivots(h, l, w=3)
    ph_prev = _prev_distinct(ph)               # pivot high PHÂN BIỆT trước đó (bền, không phải shift 1 nến)
    pl_prev = _prev_distinct(pl)
    up = (ph > ph_prev) & (pl > pl_prev)       # HH + HL → uptrend (trạng thái bền)
    dn = (ph < ph_prev) & (pl < pl_prev)       # LH + LL → downtrend
    poh = np.roll(h,1); pol = np.roll(l,1); poc = np.roll(c,1)
    resume_up = c > poh                          # phá đỉnh nến trước = nhịp tiếp diễn
    resume_dn = c < pol
    sc = np.zeros(len(c))
    sc[up & resume_up] = 0.6
    sc[dn & resume_dn] = -0.6
    sc[:5] = 0.0
    return sc

# ================================================================ WYCKOFF (heuristic)
def wyckoff_spring(o, h, l, c, W=60):
    """Spring/Upthrust quanh trading range: cần biên hẹp (range co) rồi quét thủng biên và đóng lại.
    Giống liquidity sweep nhưng W dài + lọc 'range' (biến động thấp) để gần tinh thần Wyckoff hơn."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    hi = prev_max(h, W); lo = prev_min(l, W)
    width = hi - lo
    med_width = pd.Series(width).rolling(W).median().to_numpy()
    is_range = width <= med_width               # đang co hẹp = có trading range
    spring   = is_range & (l < lo) & (c > lo)   # thủng đáy range rồi đóng lại → tích luỹ
    upthrust = is_range & (h > hi) & (c < hi)
    sc = np.zeros(len(c))
    sc[spring] = 0.7; sc[upthrust] = -0.7
    return _clip(sc)

# ================================================================ SUPPLY / DEMAND
def sd_zone(o, h, l, c, W=30):
    """Vùng cầu/cung từ swing: giá về gần đáy swing W (trong 0.4*ATR) + phản ứng bullish → LONG.
    Gần đỉnh swing + phản ứng bearish → SHORT."""
    o,h,l,c = map(lambda x: np.asarray(x,float), (o,h,l,c))
    a = _atr_body(o,h,l,c)
    lo = prev_min(l, W); hi = prev_max(h, W)
    near_demand = (l - lo) <= 0.4*a
    near_supply = (hi - h) <= 0.4*a
    sc = np.zeros(len(c))
    sc[near_demand & (c > o)] = 0.6
    sc[near_supply & (c < o)] = -0.6
    return _clip(sc)

# ================================================================ NHÓM ĐỐI CHỨNG (chỉ báo cổ điển)
def rsi_divergence(o, h, l, c, W=20):
    """Phân kỳ RSI thô: close đáy mới W nhưng RSI KHÔNG đáy mới → bull div (và ngược lại)."""
    c = np.asarray(c, float); r = rsi(c, 14)
    c_newlow  = c <= prev_min(c, W)
    c_newhigh = c >= prev_max(c, W)
    r_newlow  = r <= prev_min(r, W)
    r_newhigh = r >= prev_max(r, W)
    sc = np.zeros(len(c))
    sc[c_newlow  & (~r_newlow)]  = 0.6      # giá đáy mới, RSI không → bull div
    sc[c_newhigh & (~r_newhigh)] = -0.6
    return _clip(sc)

def channel_breakout(o, h, l, c, W=20):
    """Donchian breakout: close phá đỉnh/đáy kênh W nến trước → đi theo phá vỡ (trend)."""
    c = np.asarray(c, float)
    sc = np.zeros(len(c))
    sc[c > prev_max(h, W)] = 0.7
    sc[c < prev_min(l, W)] = -0.7
    return sc

def mean_reversion_z(o, h, l, c, W=20):
    """Z-score fade: close lệch xa trung bình W → đặt cược quay đầu (mean reversion)."""
    c = np.asarray(c, float)
    m = roll_mean(c, W); sd = roll_std(c, W)
    z = (c - m) / np.where(sd > 0, sd, np.nan)
    return _clip(-z / 2.0)

# ---------------------------------------------------------------- ATR thô (cho các hàm cần scale)
def _atr_body(o, h, l, c, n=14):
    """ATR đơn giản cho nội bộ logics (scale impulse). Không dùng cho SL — SL dùng engine_np.atr."""
    h,l,c = np.asarray(h,float),np.asarray(l,float),np.asarray(c,float)
    prev_c = np.roll(c,1); prev_c[0]=c[0]
    tr = np.maximum(h-l, np.maximum(np.abs(h-prev_c), np.abs(l-prev_c)))
    a = pd.Series(tr).rolling(n).mean().to_numpy()
    return np.where(np.isnan(a) | (a<=0), np.nanmean(tr[:n+1]) if len(tr)>n else 1.0, a)

# ---------------------------------------------------------------- registry
DANH_SACH = {
    'pa_pinbar':          pa_pinbar,
    'pa_engulfing':       pa_engulfing,
    'pa_inside_outside':  pa_inside_outside,
    'pa_bos':             pa_bos,
    'smc_fvg':            smc_fvg,
    'smc_order_block':    smc_order_block,
    'smc_liq_sweep':      smc_liquidity_sweep,
    'smc_premium_disc':   smc_premium_discount,
    'elliott_zigzag':     elliott_zigzag,
    'wyckoff_spring':     wyckoff_spring,
    'sd_zone':            sd_zone,
    'ctrl_rsi_diverg':    rsi_divergence,
    'ctrl_channel_break': channel_breakout,
    'ctrl_meanrev_z':     mean_reversion_z,
}

# nhóm để đọc báo cáo
NHOM = {
    'pa_pinbar':'PriceAction','pa_engulfing':'PriceAction','pa_inside_outside':'PriceAction','pa_bos':'PriceAction',
    'smc_fvg':'SMC/ICT','smc_order_block':'SMC/ICT','smc_liq_sweep':'SMC/ICT','smc_premium_disc':'SMC/ICT',
    'elliott_zigzag':'Elliott','wyckoff_spring':'Wyckoff','sd_zone':'Supply/Demand',
    'ctrl_rsi_diverg':'Đối chứng','ctrl_channel_break':'Đối chứng','ctrl_meanrev_z':'Đối chứng',
}

if __name__ == '__main__':
    # kiểm nhanh: mọi hàm chạy được, output trong [-1,1], đúng độ dài
    rng = np.random.default_rng(1)
    c = 100 + np.cumsum(rng.normal(0,0.4,2000))
    o = np.roll(c,1); o[0]=100
    h = np.maximum(o,c)+np.abs(rng.normal(0,0.2,2000))
    l = np.minimum(o,c)-np.abs(rng.normal(0,0.2,2000))
    for ten, f in DANH_SACH.items():
        s = f(o,h,l,c)
        assert len(s)==2000, ten
        assert np.nanmax(np.abs(s))<=1.0+1e-9, ten
        print(f"  {ten:20s} ok  nonzero={int((s!=0).sum()):5d}/2000  range=[{np.nanmin(s):+.2f},{np.nanmax(s):+.2f}]")
    print("Tất cả hàm score chạy được, output ∈ [-1,1].")
