#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all.py — Quét mọi logic × symbol × khung theo giao thức no-look-ahead / walk-forward.

Chạy thật (trên Mac, cần pandas):  python3 quant/run_all.py --data data --khung M5 M15 H1 H4
Tự kiểm pipeline (stdlib, KHÔNG cần data/pandas):  python3 quant/run_all.py --selftest

Selftest sinh 4 symbol giả: 2 random-walk (kỳ vọng EV≈0 = không look-ahead) +
1 momentum + 1 mean-revert (pipeline PHẢI phát hiện được edge thật → chứng minh không bị "chết").

Chia dữ liệu: IS 60% (calibrate + chọn ngưỡng) | OOS 25% (đánh giá) | VALIDATION 15% cuối (giữ kín).
Kết quả: quant/results/ledger.csv + bảng xếp hạng OOS + đánh dấu song_sot (OOS>0 & CI_lo>0 & VALID>0).
Tái dùng: atr/mo_phong/bao_cao/bootstrap_ci/fit_k từ backtest_vote.py; logic từ logics.py.
"""
import os, sys, csv, math, random, argparse, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_vote import atr, mo_phong, bao_cao, bootstrap_ci, fit_k
from logics import DANH_SACH

H_OUTCOME = 5          # calibrate: hướng close H nến sau
CHI_PHI_MAC_DINH = 0.05

# ---------------------------------------------------------------- nạp + resample data thật (pandas)
def nap_symbol_parquet(path, khung_list):
    import pandas as pd
    df = pd.read_parquet(path)
    if 'timestamp' in df.columns: df = df.set_index('timestamp')
    df.index = pd.to_datetime(df.index)
    df = df[['open','high','low','close']].sort_index()
    rule = {'M5':'5min','M15':'15min','H1':'1h','H4':'4h'}
    out = {}
    for k in khung_list:
        r = df.resample(rule[k]).agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
        out[k] = ([{'o':o,'h':h,'l':l,'c':c} for o,h,l,c in
                   zip(r['open'],r['high'],r['low'],r['close'])], r.index)
    return out

def tz_dieu_tra(index):
    """Chẩn đoán tz thô từ profile biến động theo giờ (KHÔNG chặn — logic hiện đều session-agnostic)."""
    try:
        import pandas as pd
        s = pd.Series(index=index, data=1)
        gio = index.hour
        # giờ có nhiều nến nhất ~ giờ thị trường sôi động; chỉ để tham khảo
        from collections import Counter
        c = Counter(gio); dinh = c.most_common(1)[0][0]
        return f"giờ hoạt động đỉnh≈{dinh}h (tham khảo tz; logic hiện không phụ thuộc giờ)"
    except Exception:
        return "n/a"

# ---------------------------------------------------------------- data giả cho selftest (stdlib)
def sinh_symbol(kind, n=9000, seed=1):
    rng = random.Random(seed); p = 100.0; r_prev = 0.0; bars = []
    for _ in range(n):
        if kind == 'mom':   r = 0.25*r_prev + rng.gauss(0, 0.4)      # momentum thật
        elif kind == 'mr':  r = -0.25*r_prev + rng.gauss(0, 0.4)     # mean-revert thật
        else:               r = rng.gauss(0, 0.4)                    # random walk
        r_prev = r
        o = p; path = [o]
        for _ in range(4): path.append(path[-1] + rng.gauss(0, 0.15))
        c = o + r; h = max(max(path), o, c); l = min(min(path), o, c); p = c
        bars.append({'o':o,'h':h,'l':l,'c':c})
    return bars

# ---------------------------------------------------------------- đánh giá 1 (logic × bars)
def danh_gia(bars, score_fn, chi_phi_r):
    n = len(bars)
    if n < 300: return None
    scores = [score_fn(bars, i) for i in range(n)]
    is_end, oos_end = int(0.60*n), int(0.85*n)

    # calibrate k CHỈ trên IS
    xs, ys = [], []
    for i in range(50, is_end-H_OUTCOME):
        if scores[i] != 0.0:
            xs.append(scores[i]); ys.append(1 if bars[i+H_OUTCOME]['c'] > bars[i]['c'] else -1)
    k = fit_k(xs, ys) if len(xs) > 100 else 1.0
    def prob(i): return 0.5 + 0.5*math.tanh(k*scores[i])

    def quyet_dinh(th):
        return [0 if i < 50 or i >= n-1 else
                (1 if prob(i) > 0.5+th else (-1 if prob(i) < 0.5-th else 0)) for i in range(n)]

    def trades_seg(qd, lo, hi):
        seg = [qd[i] if lo <= i < hi else 0 for i in range(n)]
        return mo_phong(bars, seg, chi_phi_r)

    # chọn ngưỡng trên IS (đóng băng cho OOS/VALID)
    best_th, best_ev = 0.05, -9e9
    for th in [0.02, 0.05, 0.10, 0.15]:
        tr = trades_seg(quyet_dinh(th), 0, is_end)
        ev = statistics.mean(tr) if len(tr) >= 30 else -9e9
        if ev > best_ev: best_ev, best_th = ev, th
    qd = quyet_dinh(best_th)
    res = {}
    for nhan, lo, hi in [('IS',0,is_end), ('OOS',is_end,oos_end), ('VALID',oos_end,n)]:
        tr = trades_seg(qd, lo, hi); r = bao_cao(tr)
        if r and len(tr) >= 30: r['ci'] = bootstrap_ci(tr)
        res[nhan] = r
    res['k'], res['th'] = k, best_th
    return res

# ---------------------------------------------------------------- pipeline
def chay(symbols, khung_list, chi_phi_r, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    led_path = os.path.join(out_dir, 'ledger.csv')
    cols = ['phuong_phap','nhom','symbol','khung','doan','n_lenh','ev_r','win_pct','pf',
            'sharpe','maxdd_r','ci_lo','ci_hi','phu_thuoc_gio','n_thap','ghi_chu']
    rows, xep_hang = [], []
    for sym, khung_map in symbols.items():
        for khung, (bars, ghi_chu_tz) in khung_map.items():
            n_thap = len(bars) < 5000
            for ten, fn, nhom in DANH_SACH:
                res = danh_gia(bars, fn, chi_phi_r)
                if not res: continue
                for doan in ('IS','OOS','VALID'):
                    r = res[doan]
                    if not r:
                        continue
                    ci = r.get('ci', (None, None))
                    rows.append({'phuong_phap':ten,'nhom':nhom,'symbol':sym,'khung':khung,'doan':doan,
                        'n_lenh':r['n'],'ev_r':round(r['ev'],4),'win_pct':round(r['win']*100,1),
                        'pf':round(r['pf'],2),'sharpe':round(r['sharpe'],3),'maxdd_r':round(r['maxdd'],1),
                        'ci_lo':round(ci[0],4) if ci[0] is not None else '',
                        'ci_hi':round(ci[1],4) if ci[1] is not None else '',
                        'phu_thuoc_gio':False,'n_thap':n_thap,'ghi_chu':ghi_chu_tz if doan=='OOS' else ''})
                # ứng viên sống sót: OOS ev>0 & CI_lo>0 & VALID ev>0 & đủ số lệnh (N≥50)
                o, v = res['OOS'], res['VALID']
                song = bool(o and v and o['n'] >= 50 and o.get('ci',(None,))[0]
                            and o['ci'][0] > 0 and v['ev'] > 0)
                if o:
                    xep_hang.append((o['ev'], ten, nhom, sym, khung, o['n'],
                                     o.get('ci',(None,None)), (v['ev'] if v else None), song, n_thap))
    with open(led_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    xep_hang.sort(reverse=True)
    print(f"\n=== BẢNG XẾP HẠNG OOS (top 15 / {len(xep_hang)} tổ hợp) ===")
    print(f"{'EV_R':>8} {'logic':14} {'nhom':12} {'sym':10} {'khung':5} {'N':>6} {'VALID':>8} {'sống?':>6} {'ghi_chu'}")
    for ev, ten, nhom, sym, khung, N, ci, vev, song, nt in xep_hang[:15]:
        note = 'N_thấp' if nt else ''
        vv = f"{vev:+.4f}" if vev is not None else '-'
        print(f"{ev:+8.4f} {ten:14} {nhom:12} {sym:10} {khung:5} {N:6d} {vv:>8} {'✔' if song else '':>6} {note}")
    songs = [x for x in xep_hang if x[8]]
    print(f"\n>>> Ứng viên SỐNG SÓT (OOS>0 & CI_lo>0 & VALID>0): {len(songs)}")
    for ev, ten, nhom, sym, khung, N, ci, vev, song, nt in songs[:20]:
        print(f"    {ten}/{sym}/{khung}: OOS EV={ev:+.4f} (CI_lo={ci[0]:+.4f}) VALID={vev:+.4f}"
              + ("  [N thấp - thận trọng]" if nt else ""))
    if not songs:
        print("    (không có — đúng kỳ vọng: entry công khai đã bị arbitrage cạn. Đây là DỮ LIỆU, không phải fail.)")
    print(f"\nLedger đầy đủ: {led_path}")
    print("⚠️ Con sống sót phải kiểm tiếp CHÉO SYMBOL cùng thời kỳ trước khi tin (xem REVIEW-cloud.md).")

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data')
    ap.add_argument('--khung', nargs='+', default=['H1'])
    ap.add_argument('--spread-r', type=float, default=CHI_PHI_MAC_DINH)
    ap.add_argument('--out', default='quant/results')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        print(">>> SELFTEST (stdlib): RW phải EV≈0 (không look-ahead); MOM/MR phải lộ edge (pipeline sống).")
        syms = {
            'SYN_RW1':  {'H1': (sinh_symbol('rw',  seed=1), None)},
            'SYN_RW2':  {'H1': (sinh_symbol('rw',  seed=2), None)},
            'SYN_MOM':  {'H1': (sinh_symbol('mom', seed=3), None)},
            'SYN_MR':   {'H1': (sinh_symbol('mr',  seed=4), None)},
        }
        chay(syms, ['H1'], a.spread_r, a.out); return

    import glob
    files = sorted(glob.glob(os.path.join(a.data, '*_m1.parquet')) + glob.glob(os.path.join(a.data, '*.parquet')))
    files = sorted(set(files))
    if not files: sys.exit(f"Không thấy parquet trong {a.data}/")
    print(f"Tìm thấy {len(files)} file. Khung: {a.khung}. Phí: {a.spread_r}R.")
    syms = {}
    for p in files:
        sym = os.path.basename(p).replace('_m1.parquet','').replace('.parquet','')
        print(f"  nạp {sym} ...", flush=True)
        try:
            syms[sym] = nap_symbol_parquet(p, a.khung)
        except Exception as e:
            print(f"    BỎ QUA {sym}: {e}")
    chay(syms, a.khung, a.spread_r, a.out)

if __name__ == '__main__':
    main()
