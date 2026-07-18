# -*- coding: utf-8 -*-
"""
logics.py — Thư viện logic PTKT dạng score(bars, i) -> [-1, +1].
CHỈ dùng bars[<=i] (no look-ahead). Tất cả SESSION-AGNOSTIC + KHÔNG dùng volume
→ chạy được ngay bất kể múi giờ (xem quant/REVIEW-cloud.md).
bars = list dict {'o','h','l','c'} (đã resample về khung đang test, đã bỏ khe).

Đây là BẢN NỀN (baseline heuristic) để test CƠ CHẾ + pipeline. Phiên Mac có thể tinh chỉnh
từng logic sau — nhưng phải giữ 2 luật: chỉ dùng bars[<=i], trả [-1,1].
Nhóm 'chi_bao' (divergence, breakout) là ĐỐI CHỨNG "chỉ báo cổ điển".
"""

def _clip(x): return max(-1.0, min(1.0, x))

# ---------- Price Action ----------
def pin_bar(bars, i):
    """Nến rejection: đuôi dài. Đuôi dưới dài → +, đuôi trên dài → −."""
    b = bars[i]; rng = b['h'] - b['l']
    if rng <= 0: return 0.0
    duoi = min(b['o'], b['c']) - b['l']; tren = b['h'] - max(b['o'], b['c'])
    return _clip((duoi - tren) / rng)

def engulfing(bars, i):
    """Nến nhấn chìm nến trước."""
    if i < 1: return 0.0
    p, c = bars[i-1], bars[i]
    pc, cc = p['c']-p['o'], c['c']-c['o']
    if cc > 0 and pc < 0 and c['c'] >= p['o'] and c['o'] <= p['c']: return 1.0
    if cc < 0 and pc > 0 and c['c'] <= p['o'] and c['o'] >= p['c']: return -1.0
    return 0.0

def inside_outside(bars, i):
    """Outside bar → theo hướng đóng cửa; inside bar → 0 (nén, chưa rõ hướng)."""
    if i < 1: return 0.0
    p, c = bars[i-1], bars[i]
    if c['h'] > p['h'] and c['l'] < p['l']:               # outside
        return 1.0 if c['c'] > c['o'] else -1.0
    return 0.0

# ---------- Cấu trúc / SMC (không volume) ----------
def _swing_cao(bars, i, N):  return max(b['h'] for b in bars[i-N:i])
def _swing_thap(bars, i, N): return min(b['l'] for b in bars[i-N:i])

def bos(bars, i, N=20):
    """Break of structure: close vượt đỉnh/đáy N nến TRƯỚC (không tính i)."""
    if i < N+1: return 0.0
    cao, thap = _swing_cao(bars, i, N), _swing_thap(bars, i, N)
    if bars[i]['c'] > cao: return 1.0
    if bars[i]['c'] < thap: return -1.0
    return 0.0

def choch(bars, i, N=20):
    """Change of character: đảo cấu trúc. Đang tăng (close>SMA) mà thủng đáy N → −; ngược lại +."""
    if i < N+1: return 0.0
    sma = sum(b['c'] for b in bars[i-N:i]) / N
    cao, thap = _swing_cao(bars, i, N), _swing_thap(bars, i, N)
    if bars[i]['c'] > sma and bars[i]['l'] <= thap: return -1.0
    if bars[i]['c'] < sma and bars[i]['h'] >= cao: return 1.0
    return 0.0

def fvg(bars, i):
    """Fair value gap 3 nến: c1.high < c3.low → imbalance tăng (+); c1.low > c3.high → giảm (−)."""
    if i < 2: return 0.0
    c1, c3 = bars[i-2], bars[i]
    if c1['h'] < c3['l']: return 1.0
    if c1['l'] > c3['h']: return -1.0
    return 0.0

def order_block(bars, i, k=1.2, n_atr=14):
    """OB thô: nến impulse lớn ngay sau nến ngược màu. Green impulse sau red → +."""
    if i < n_atr+1: return 0.0
    tr = sum(max(bars[j]['h']-bars[j]['l'], abs(bars[j]['h']-bars[j-1]['c']),
                 abs(bars[j]['l']-bars[j-1]['c'])) for j in range(i-n_atr+1, i+1)) / n_atr
    if tr <= 0: return 0.0
    body = bars[i]['c'] - bars[i]['o']; p = bars[i-1]['c'] - bars[i-1]['o']
    if body > k*tr and p < 0: return 1.0
    if body < -k*tr and p > 0: return -1.0
    return 0.0

def supply_demand(bars, i, N=20):
    """Vùng cầu/cung thô: z-score close quanh trung bình N → fade cực trị (mean-revert)."""
    if i < N+1: return 0.0
    cs = [b['c'] for b in bars[i-N+1:i+1]]
    m = sum(cs)/N; sd = (sum((x-m)**2 for x in cs)/N) ** 0.5
    if sd == 0: return 0.0
    return _clip(-(bars[i]['c']-m)/(2*sd))

# ---------- Heuristic diễn giải (GHI RÕ: 1 cách hiểu, xấu = bản này chết) ----------
def elliott_heur(bars, i, N=8):
    """Sóng đẩy thô: N nến liên tiếp higher-high & higher-low → tiếp diễn tăng (+)."""
    if i < N+1: return 0.0
    up = all(bars[j]['h'] >= bars[j-1]['h'] and bars[j]['l'] >= bars[j-1]['l'] for j in range(i-N+2, i+1))
    dn = all(bars[j]['h'] <= bars[j-1]['h'] and bars[j]['l'] <= bars[j-1]['l'] for j in range(i-N+2, i+1))
    return 1.0 if up else (-1.0 if dn else 0.0)

def wyckoff_heur(bars, i, N=20):
    """Spring/upthrust: thủng đáy range rồi đóng lại trong range → +; vượt đỉnh rồi đóng lại → −."""
    if i < N+1: return 0.0
    cao, thap = _swing_cao(bars, i, N), _swing_thap(bars, i, N)
    b = bars[i]
    if b['l'] < thap and b['c'] > thap: return 1.0      # spring
    if b['h'] > cao and b['c'] < cao: return -1.0       # upthrust
    return 0.0

# ---------- Đối chứng: chỉ báo cổ điển ----------
def breakout(bars, i, N=20):
    """Kênh Donchian: vị trí close trong dải cao/thấp N nến trước → [-1,1]."""
    if i < N+1: return 0.0
    cao, thap = _swing_cao(bars, i, N), _swing_thap(bars, i, N)
    if cao == thap: return 0.0
    return _clip(2*((bars[i]['c']-thap)/(cao-thap)) - 1)

def divergence(bars, i, W=24):
    """Phân kỳ momentum thô: price lower-low + ROC higher-low → bull (+); ngược lại −."""
    if i < W+4: return 0.0
    h = W//2
    lows = [bars[k]['l'] for k in range(i-W+1, i+1)]
    highs = [bars[k]['h'] for k in range(i-W+1, i+1)]
    roc = [bars[k]['c']-bars[k-3]['c'] for k in range(i-W+1, i+1)]
    sc = 0.0
    if min(lows[h:]) < min(lows[:h]) and min(roc[h:]) > min(roc[:h]): sc += 0.7
    if max(highs[h:]) > max(highs[:h]) and max(roc[h:]) < max(roc[:h]): sc -= 0.7
    return _clip(sc)

# ---------- Danh mục (phu_thuoc_gio=False cho TẤT CẢ — session-agnostic) ----------
DANH_SACH = [
    ('pin_bar', pin_bar, 'price_action'),
    ('engulfing', engulfing, 'price_action'),
    ('inside_outside', inside_outside, 'price_action'),
    ('bos', bos, 'smc'),
    ('choch', choch, 'smc'),
    ('fvg', fvg, 'smc'),
    ('order_block', order_block, 'smc'),
    ('supply_demand', supply_demand, 'smc'),
    ('elliott_heur', elliott_heur, 'heuristic'),
    ('wyckoff_heur', wyckoff_heur, 'heuristic'),
    ('breakout', breakout, 'chi_bao'),
    ('divergence', divergence, 'chi_bao'),
]
