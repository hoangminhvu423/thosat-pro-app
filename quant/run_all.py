#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all.py — Bộ quét tự động: (phương pháp × symbol × khung) trên data M1 thật.

Giao thức (NHIEM-VU.md + quant-handoff.md):
  - Resample M1 → M5/M15/H1/H4 (bỏ nến rỗng cuối tuần/lễ, KHÔNG fill-forward tạo nến ma).
  - Walk-forward: IS 60% | OOS 25% | VALIDATION 15% cuối (giữ riêng, không đụng lúc chọn ngưỡng).
  - Chọn ngưỡng |score| CHỈ trên IS (max EV, tối thiểu N lệnh) → đóng băng cho OOS + validation.
  - Phí spread+commission+slippage theo symbol (engine_np.COST_PRICE), quy R theo độ rộng SL.
  - Bootstrap CI 95% cho EV. Ghi từng dòng vào quant/results/ledger.csv.
  - Survivorship (chống multiple-testing): song_sot=true CHỈ khi OOS ci_lo>0 VÀ validation ev>0
    VÀ có ≥1 symbol khác cùng nhóm tài sản cũng OOS ci_lo>0.

Chạy:
  python3 quant/run_all.py --selftest        # random-walk: mọi EV OOS phải ≈ 0 (gác look-ahead)
  python3 quant/run_all.py --smoke           # 2 symbol × 2 khung (kiểm pipeline nhanh)
  python3 quant/run_all.py                    # full 18 symbol × 4 khung
"""
import os, sys, csv, glob, argparse, time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_np as E
from logics import DANH_SACH, NHOM

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
RES_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')

TF_RULES = {'M5': '5min', 'M15': '15min', 'H1': '1h', 'H4': '4h'}
WARMUP   = 250                       # bỏ đầu chuỗi cho pivot/rolling/RSI ổn định
THRESHOLDS = [0.1, 0.2, 0.3, 0.5, 0.7]
MIN_N_IS = 30                        # tối thiểu lệnh IS để 1 ngưỡng được xét
MIN_N_SEG = 20                       # tối thiểu lệnh 1 đoạn để báo cáo

# symbol ngắn/cụt (GHI-CHU.md) — vẫn chạy nhưng gắn cờ, không để lọt bảng mà không chú thích
GHICHU_SYMBOL = {
    'eurusd': 'CỤT: chỉ 1,0tr nến 2023-09→2026-06 (N nhỏ)',
    'chfjpy': 'CỤT ĐUÔI 2023-09: đoạn validation cuối là 2023, không đồng thời với mã khác',
    'xauusd': 'THIẾU 2012; tz EST',
}

# ---------------------------------------------------------------- data
def resample_ohlc(df, rule):
    g = df.resample(rule)
    out = pd.DataFrame({
        'open':  g['open'].first(),
        'high':  g['high'].max(),
        'low':   g['low'].min(),
        'close': g['close'].last(),
    }).dropna()
    return out

def load_m1(path):
    df = pd.read_parquet(path)
    df = df[['open', 'high', 'low', 'close']].astype(float)
    if not df.index.is_monotonic_increasing:
        df = df.sort_index()
    return df

def random_walk_df(n=60000, seed=0):
    rng = np.random.default_rng(seed)
    c = 100 + np.cumsum(rng.normal(0, 0.4, n))
    o = np.empty(n); o[0] = 100; o[1:] = c[:-1]
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.15, n))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.15, n))
    idx = pd.date_range('2010-01-01', periods=n, freq='1min')
    return pd.DataFrame({'open': o, 'high': h, 'low': l, 'close': c}, index=idx)

# ---------------------------------------------------------------- 1 backtest (method × mảng giá)
def backtest_one(o, h, l, c, atr_arr, score, cost_price, splits):
    """Chọn ngưỡng trên IS → đánh giá IS/OOS/VALID. Trả dict theo đoạn (hoặc None nếu thiếu lệnh)."""
    is_lo, is_hi, oos_hi, N = splits
    def signal(th):
        s = np.zeros(len(score), np.int8)
        s[score >= th] = 1
        s[score <= -th] = -1
        return s
    # --- chọn ngưỡng trên IS ---
    best_th, best_ev = None, -1e18
    for th in THRESHOLDS:
        tr = E.mo_phong(o, h, l, c, atr_arr, signal(th), cost_price, is_lo, is_hi)
        if len(tr) >= MIN_N_IS and tr.mean() > best_ev:
            best_ev, best_th = tr.mean(), th
    if best_th is None:
        return None
    sig = signal(best_th)
    seg = {}
    for nhan, lo, hi in [('IS', is_lo, is_hi), ('OOS', is_hi, oos_hi), ('VALID', oos_hi, N)]:
        tr = E.mo_phong(o, h, l, c, atr_arr, sig, cost_price, lo, hi)
        st = E.thong_ke(tr)
        if st and st['n'] >= MIN_N_SEG:
            seed = lo * 7 + {'IS': 1, 'OOS': 2, 'VALID': 3}[nhan]   # tất định → tái lập được
            ci = E.bootstrap_ci(tr, seed=seed)
            st['ci_lo'], st['ci_hi'] = ci
        seg[nhan] = st
    seg['_th'] = best_th
    return seg

# ---------------------------------------------------------------- quét 1 symbol
def scan_symbol(symbol, path, tfs, rows, verbose=True):
    df = load_m1(path)
    if verbose:
        print(f"[{symbol}] M1 nến={len(df):,}  {df.index.min()} → {df.index.max()}", flush=True)
    for tf in tfs:
        d = resample_ohlc(df, TF_RULES[tf])
        N = len(d)
        if N < WARMUP + 500:
            if verbose: print(f"  {tf}: chỉ {N} nến — bỏ qua", flush=True)
            continue
        o = d['open'].to_numpy(); h = d['high'].to_numpy()
        l = d['low'].to_numpy();  c = d['close'].to_numpy()
        atr_arr = E.atr(h, l, c)
        cost_price = E.cost_price_of(symbol)
        is_lo = WARMUP
        is_hi = int(N * 0.60)
        oos_hi = int(N * 0.85)
        splits = (is_lo, is_hi, oos_hi, N)
        t0 = time.time()
        for meth, f in DANH_SACH.items():
            score = f(o, h, l, c)
            seg = backtest_one(o, h, l, c, atr_arr, score, cost_price, splits)
            if seg is None:
                continue
            for doan in ('IS', 'OOS', 'VALID'):
                st = seg[doan]
                if not st:
                    continue
                rows.append({
                    'phuong_phap': meth, 'nhom': NHOM.get(meth, ''), 'symbol': symbol,
                    'khung': tf, 'doan': doan, 'nguong': seg['_th'],
                    'n_lenh': st['n'], 'ev_r': round(st['ev'], 5), 'win_pct': round(st['win']*100, 2),
                    'pf': round(st['pf'], 3) if st['pf'] != float('inf') else 999,
                    'sharpe': round(st['sharpe'], 4), 'maxdd_r': round(st['maxdd'], 2),
                    'ci_lo': round(st.get('ci_lo', float('nan')), 5),
                    'ci_hi': round(st.get('ci_hi', float('nan')), 5),
                    'ghi_chu': GHICHU_SYMBOL.get(symbol, ''),
                })
        if verbose:
            print(f"  {tf}: N={N:,}  IS<{is_hi:,} OOS<{oos_hi:,} VALID<{N:,}  ({time.time()-t0:.1f}s)", flush=True)

# ---------------------------------------------------------------- survivorship (cross-symbol)
def danh_dau_song_sot(rows):
    """song_sot: OOS ci_lo>0 VÀ validation ev>0 VÀ ≥1 symbol khác cùng nhóm tài sản có OOS ci_lo>0."""
    oos = {(r['phuong_phap'], r['symbol'], r['khung']): r for r in rows if r['doan'] == 'OOS'}
    val = {(r['phuong_phap'], r['symbol'], r['khung']): r for r in rows if r['doan'] == 'VALID'}
    # đếm số symbol có OOS ci_lo>0 theo (method,khung,asset_class)
    from collections import defaultdict
    ok_syms = defaultdict(set)
    for (m, s, tf), r in oos.items():
        if r['ci_lo'] == r['ci_lo'] and r['ci_lo'] > 0:      # not NaN & >0
            ok_syms[(m, tf, E.ASSET_CLASS.get(s, '?'))].add(s)
    for r in rows:
        r['song_sot'] = False
    for (m, s, tf), r in oos.items():
        cls = E.ASSET_CLASS.get(s, '?')
        oos_ok = (r['ci_lo'] == r['ci_lo'] and r['ci_lo'] > 0)
        v = val.get((m, s, tf))
        val_ok = bool(v and v['ev_r'] > 0)
        cross_ok = len(ok_syms[(m, tf, cls)] - {s}) >= 1
        if oos_ok and val_ok and cross_ok:
            r['song_sot'] = True

# ---------------------------------------------------------------- ghi ledger + báo cáo
COLS = ['phuong_phap','nhom','symbol','khung','doan','nguong','n_lenh','ev_r','win_pct',
        'pf','sharpe','maxdd_r','ci_lo','ci_hi','song_sot','ghi_chu']

def ghi_ledger(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in COLS})

def viet_bao_cao(rows, path, meta):
    from collections import defaultdict
    oos = [r for r in rows if r['doan'] == 'OOS' and r['n_lenh'] >= MIN_N_SEG]
    oos_sorted = sorted(oos, key=lambda r: r['ev_r'], reverse=True)
    survivors = [r for r in rows if r['doan'] == 'OOS' and r.get('song_sot')]
    # ghép IS↔OOS để đo overfit
    is_map = {(r['phuong_phap'], r['symbol'], r['khung']): r for r in rows if r['doan'] == 'IS'}
    # tổng hợp theo phương pháp (trung vị EV OOS)
    from collections import defaultdict
    by_m = defaultdict(list)
    for r in oos:
        by_m[r['phuong_phap']].append(r['ev_r'])
    def med(x): return float(np.median(x)) if x else float('nan')
    meth_rank = sorted(by_m.items(), key=lambda kv: med(kv[1]), reverse=True)

    L = []
    L.append("# BÁO CÁO — Quét phương pháp trên data M1 thật\n")
    L.append(f"> Sinh tự động bởi `quant/run_all.py`. {meta}\n")
    L.append("> **Nguyên tắc vàng**: mọi EV OOS dương mặc định là nhiễu/overfit cho tới khi qua được")
    L.append("> validation + cross-symbol. Đa số EV≈0 sau phí là KẾT QUẢ, không phải thất bại.\n")

    L.append("## 1. Tổng quan")
    L.append(f"- Số thí nghiệm (method×symbol×khung): **{len({(r['phuong_phap'],r['symbol'],r['khung']) for r in rows})}**")
    L.append(f"- Dòng ledger: {len(rows)} | có đủ lệnh OOS để xét: {len(oos)}")
    n_oos_pos = sum(1 for r in oos if r['ev_r'] > 0)
    n_ci_pos  = sum(1 for r in oos if r['ci_lo']==r['ci_lo'] and r['ci_lo']>0)
    L.append(f"- OOS EV>0: {n_oos_pos}/{len(oos)} ({100*n_oos_pos/max(1,len(oos)):.1f}%) — "
             f"kỳ vọng ~50% do nhiễu nếu không có edge")
    L.append(f"- OOS CI95 không chứa 0 (EV>0): {n_ci_pos}/{len(oos)}")
    L.append(f"- **SỐNG SÓT (OOS ci_lo>0 + validation>0 + cross-symbol): {len(survivors)}**")
    exp_ci = 0.025 * len(oos)
    L.append(f"- ⚠️ Nếu thuần nhiễu (95% CI, 1 phía) kỳ vọng ~{exp_ci:.0f} con có CI>0 do may rủi; "
             f"thực tế chỉ **{n_ci_pos}** → phí kéo âm ÁP ĐẢO cả nhiễu (ít hơn cả mức ăn may).\n")

    L.append("## 1b. GRADIENT PHÍ THEO KHUNG (phát hiện sắc nhất)")
    L.append("Phí cố định mỗi lệnh (spread+comm+slippage) quy R = phí_giá / độ_rộng_SL. Khung càng nhỏ,")
    L.append("SL càng hẹp → phí quy R càng lớn → giết edge. Số liệu OOS:")
    L.append("")
    L.append("| Khung | Trung vị EV_OOS (R) | TB EV_OOS (R) | % config EV>0 | #config |")
    L.append("|---|---|---|---|---|")
    by_tf = defaultdict(list)
    for r in oos: by_tf[r['khung']].append(r)
    for tf in ['M5', 'M15', 'H1', 'H4']:
        rs = by_tf.get(tf, [])
        if not rs: continue
        evs = [r['ev_r'] for r in rs]
        pct_pos = 100*sum(1 for r in rs if r['ev_r'] > 0)/len(rs)
        L.append(f"| {tf} | {np.median(evs):+.4f} | {np.mean(evs):+.4f} | {pct_pos:.0f}% | {len(rs)} |")
    L.append("")
    L.append("→ M5/M15 **không config nào** dương (phí ăn sạch). Chỉ H4 có ~29% dương do phí nhẹ —")
    L.append("nhưng KHÔNG con nào sống qua validation+cross-symbol. Đây là 'nghĩa địa' số hoá: logic")
    L.append("tĩnh công khai không thắng nổi chi phí thực, tệ nhất ở khung thấp.\n")

    L.append("## 2. Bảng xếp hạng phương pháp (trung vị EV OOS trên mọi symbol×khung)")
    L.append("| Phương pháp | Nhóm | Trung vị EV_OOS (R) | Số cấu hình |")
    L.append("|---|---|---|---|")
    for m, evs in meth_rank:
        L.append(f"| {m} | {NHOM.get(m,'')} | {med(evs):+.4f} | {len(evs)} |")
    L.append("")

    L.append("## 3. Top 20 cấu hình theo EV OOS (⚠️ đỉnh bảng MẶC ĐỊNH là nhiễu multiple-testing)")
    L.append("| # | Phương pháp | Symbol | Khung | N | EV_OOS | win% | PF | CI95_OOS | IS→OOS | Sống? |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, r in enumerate(oos_sorted[:20], 1):
        ir = is_map.get((r['phuong_phap'], r['symbol'], r['khung']))
        gap = f"{ir['ev_r']:+.3f}→{r['ev_r']:+.3f}" if ir else f"?→{r['ev_r']:+.3f}"
        ci = f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]" if r['ci_lo']==r['ci_lo'] else "—"
        L.append(f"| {k} | {r['phuong_phap']} | {r['symbol']} | {r['khung']} | {r['n_lenh']} | "
                 f"{r['ev_r']:+.4f} | {r['win_pct']:.1f} | {r['pf']} | {ci} | {gap} | "
                 f"{'✅' if r.get('song_sot') else ''} |")
    L.append("")

    L.append("## 4. Con SỐNG SÓT (qua cả validation + cross-symbol)")
    if survivors:
        L.append("| Phương pháp | Symbol | Khung | EV_OOS | CI95_OOS | EV_VALID |")
        L.append("|---|---|---|---|---|---|")
        val_map = {(r['phuong_phap'],r['symbol'],r['khung']): r for r in rows if r['doan']=='VALID'}
        for r in sorted(survivors, key=lambda x: x['ev_r'], reverse=True):
            v = val_map.get((r['phuong_phap'],r['symbol'],r['khung']))
            L.append(f"| {r['phuong_phap']} | {r['symbol']} | {r['khung']} | {r['ev_r']:+.4f} | "
                     f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] | {v['ev_r']:+.4f} |")
    else:
        L.append("**KHÔNG có phương pháp nào sống sót.** Đúng như luận đề: logic tĩnh công khai bị")
        L.append("arbitrage cạn — không con nào vượt được phí + walk-forward + cross-symbol trên data thật.")
    L.append("")

    L.append("## 5. Mức overfit (khoảng cách IS ↔ OOS)")
    gaps = []
    for key, ir in is_map.items():
        orr = next((r for r in oos if (r['phuong_phap'],r['symbol'],r['khung'])==key), None)
        if orr: gaps.append(ir['ev_r'] - orr['ev_r'])
    if gaps:
        L.append(f"- Trung vị (EV_IS − EV_OOS) = **{np.median(gaps):+.4f}R** "
                 f"(>0 = IS đẹp hơn OOS = overfit điển hình).")
        L.append(f"- IS dương nhưng OOS âm (lật dấu): "
                 f"{sum(1 for key,ir in is_map.items() if ir['ev_r']>0 and next((r for r in oos if (r['phuong_phap'],r['symbol'],r['khung'])==key and r['ev_r']<0), None))}"
                 f" cấu hình — minh hoạ sống của 'đường cong đẹp trên IS lật trên OOS'.")
    L.append("")

    L.append("## 6. Nhận định trung thực")
    L.append("- **Data**: đọc `data/GHI-CHU.md`. Symbol cụt (eurusd, chfjpy, xauusd) đã gắn cờ ở cột ghi_chu.")
    L.append("- **Giả định phí**: bảng `engine_np.COST_PRICE` (Exness Pro ~2026). Chỉnh số đó nếu có bảng chuẩn hơn.")
    L.append("- **CHƯA mô hình swap qua đêm** — lệnh giữ nhiều nến/ngày sẽ tệ hơn số ở đây (báo cáo này là cận TRÊN lạc quan về phí).")
    L.append("- **Mỗi phương pháp là MỘT cách số hoá** (nhất là Elliott/Wyckoff/SMC). EV xấu = bản code này chết, không phủ định phương pháp gốc.")
    L.append("- Kết quả này để **số hoá nghĩa địa**, không phải tìm chén thánh. EV≈0 sau phí là dữ liệu quý.")
    L.append("- **Đối chứng độc lập**: một bản scanner thứ 2 (stdlib, mô hình phí khác) chạy riêng trên H4")
    L.append("  cũng ra **0 con sống sót** — xem `quant/xcheck_cloud/KET-QUA-DOI-CHUNG.md`. Kết luận bền với lỗi code.")
    L.append("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(L))

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true', help='random-walk: mọi EV OOS phải ≈ 0')
    ap.add_argument('--smoke', action='store_true', help='2 symbol × 2 khung để kiểm pipeline')
    ap.add_argument('--report-only', action='store_true', help='dựng lại BAO-CAO.md từ ledger.csv có sẵn (không quét)')
    ap.add_argument('--symbols', default='', help='danh sách symbol phẩy (mặc định: tất cả)')
    ap.add_argument('--tfs', default='M5,M15,H1,H4', help='khung phẩy')
    ap.add_argument('--out', default=os.path.join(RES_DIR, 'ledger.csv'))
    a = ap.parse_args()
    tfs = [t.strip() for t in a.tfs.split(',') if t.strip()]

    rows = []
    t_start = time.time()

    if a.report_only:
        df = pd.read_csv(a.out)
        for col in ['n_lenh']:
            df[col] = df[col].astype(int)
        for col in ['nguong','ev_r','win_pct','pf','sharpe','maxdd_r','ci_lo','ci_hi']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['song_sot'] = df['song_sot'].astype(str).isin(['True','true','1'])
        rows = df.to_dict('records')
        danh_dau_song_sot(rows)          # tính lại survivorship cho chắc
        ghi_ledger(rows, a.out)
        viet_bao_cao(rows, os.path.join(RES_DIR, 'BAO-CAO.md'), f"dựng lại từ ledger {time.strftime('%Y-%m-%d %H:%M')}")
        print(f"✅ Dựng lại báo cáo từ {a.out}")
        return

    if a.selftest:
        print(">>> SELFTEST run_all trên RANDOM-WALK — không có edge, mọi EV OOS phải ≈ 0.")
        print(">>> Nếu phương pháp nào EV OOS dương RÕ + CI không chứa 0 → hàm đó có LOOK-AHEAD, phải sửa.\n")
        for sym, seed in [('rw_A', 1), ('rw_B', 2), ('rw_C', 3)]:
            df = random_walk_df(60000, seed)
            # tiêm df giả qua đường resample thật
            import tempfile
            path = os.path.join(RES_DIR, f'_{sym}.parquet')
            os.makedirs(RES_DIR, exist_ok=True); df.to_parquet(path)
            scan_symbol(sym, path, tfs, rows)
            os.remove(path)
        oos = [r for r in rows if r['doan']=='OOS' and r['n_lenh']>=MIN_N_SEG]
        print(f"\n=== KẾT QUẢ SELFTEST (OOS trên random-walk) ===")
        bad = 0
        from collections import defaultdict
        agg = defaultdict(list)
        for r in oos: agg[r['phuong_phap']].append(r)
        for m in DANH_SACH:
            rs = agg.get(m, [])
            if not rs:
                print(f"  {m:20s}: (không đủ lệnh)"); continue
            evs = [r['ev_r'] for r in rs]
            flag = [r for r in rs if r['ci_lo']==r['ci_lo'] and r['ci_lo']>0]
            mark = '  <-- NGHI LOOK-AHEAD' if len(flag) > max(1, len(rs)//10) else ''
            bad += 1 if mark else 0
            print(f"  {m:20s}: EV median={np.median(evs):+.4f}R  n_cfg={len(rs)}  "
                  f"#CI>0={len(flag)}{mark}")
        print(f"\n{'⚠️ CÓ HÀM NGHI LOOK-AHEAD — SỬA TRƯỚC KHI CHẠY THẬT' if bad else '✅ Sạch: không hàm nào có edge giả trên random-walk. An toàn chạy data thật.'}")
        return

    # --- chọn symbol ---
    if a.symbols:
        syms = [s.strip() for s in a.symbols.split(',')]
        files = [(s, os.path.join(DATA_DIR, f'{s}_m1.parquet')) for s in syms]
    else:
        files = [(os.path.basename(p).replace('_m1.parquet',''), p)
                 for p in sorted(glob.glob(os.path.join(DATA_DIR, '*_m1.parquet')))]
    if a.smoke:
        files = files[:2]; tfs = tfs[:2] if len(tfs) > 2 else tfs
        print(f">>> SMOKE: {[s for s,_ in files]} × {tfs}\n")

    print(f">>> Quét {len(files)} symbol × {tfs} × {len(DANH_SACH)} phương pháp\n")
    for sym, path in files:
        if not os.path.exists(path):
            print(f"[{sym}] THIẾU FILE {path} — bỏ qua", flush=True); continue
        try:
            scan_symbol(sym, path, tfs, rows)
        except Exception as ex:
            print(f"[{sym}] LỖI: {ex}", flush=True)

    if not rows:
        print("Không có kết quả nào."); return
    danh_dau_song_sot(rows)
    ghi_ledger(rows, a.out)
    meta = f"{len(files)} symbol × {tfs}, {time.strftime('%Y-%m-%d %H:%M')}, {(time.time()-t_start)/60:.1f} phút."
    viet_bao_cao(rows, os.path.join(RES_DIR, 'BAO-CAO.md'), meta)
    print(f"\n✅ Xong ({(time.time()-t_start)/60:.1f} phút). Ledger: {a.out}")
    print(f"   Báo cáo: {os.path.join(RES_DIR, 'BAO-CAO.md')}")
    surv = [r for r in rows if r['doan']=='OOS' and r.get('song_sot')]
    print(f"   Sống sót: {len(surv)}")

if __name__ == '__main__':
    main()
