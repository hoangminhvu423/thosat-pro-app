# ĐỐI CHỨNG ĐỘC LẬP — hai scanner viết tách biệt, cùng kết luận

> Hai phiên Claude Code dựng **độc lập** hai bộ quét khác nhau cho cùng nhiệm vụ (NHIEM-VU.md).
> Đây là kiểm chứng chéo mạnh nhất có thể: nếu hai bản viết tách biệt, khác stack, khác mô hình phí
> mà **cùng ra một kết luận**, thì kết luận đó bền với lỗi code (một bug chung gần như không thể).

## Hai bản

| | **Bản Mac** (`quant/run_all.py`, chính) | **Bản cloud** (`quant/xcheck_cloud/run_all.py`) |
|---|---|---|
| Tác giả | phiên Claude Code local (Mac) | phiên Claude Code cloud (độc lập) |
| Stack | numpy vectorized | stdlib per-bar loop (tái dùng `backtest_vote.py`) |
| Số logic | 14 | 12 |
| **Mô hình phí** | **per-symbol, R = phí_giá / độ_rộng_SL** | **phẳng `--spread-r 0.05` (1 số cho mọi mã/khung)** |
| Phạm vi chạy | 18 mã × M5/M15/H1/H4 = 1008 thí nghiệm | 18 mã × H4 = 215 thí nghiệm (đối chứng) |
| Walk-forward | IS60 / OOS25 / VALID15 | IS60 / OOS25 / VALID15 (giống) |

## Kết quả

- **SỐNG SÓT — bản Mac: 0/1008. Bản cloud (H4): 0/215.** Trùng khít.
- **Khớp dấu EV_OOS trên H4: 48/66 (73%)** ở các cặp method×symbol so được:
  - Method định nghĩa rõ khớp gần tuyệt đối: `engulfing` 6/6, `rsi_divergence` 6/6,
    `pinbar` 5/6, `inside_outside` 5/6, `fvg` 5/6, `supply_demand` 5/6.
  - Độ lớn rất sát bất chấp mô hình phí khác nhau:
    - engulfing/gbpusd/H4: Mac +0.095 vs cloud +0.064
    - order_block/usdchf/H4: Mac +0.088 vs cloud +0.098
    - rsi_diverg/nzdjpy/H4: Mac −0.117 vs cloud −0.130
  - **Lệch dấu tập trung ở heuristic** (`elliott` 1/6, `wyckoff` 2/6) — ĐÚNG như cảnh báo: đây là
    "một cách diễn giải", hai bản code khác nhau nên lệch. Nhưng đều quanh 0 (vd +0.001 vs −0.013),
    không con nào thoát walk-forward + validation.
- Cùng một mẫu overfit: config đẹp nhất trên OOS đều **lật âm trên VALIDATION** ở cả hai bản
  (vd cloud: `elliott_heur/nzdusd/H4` OOS +0.25 → VALID −0.57; Mac: `pa_engulfing/gbpusd/H4`
  OOS +0.095 → VALID −0.143).

## Kết luận
Hai implementation độc lập, khác stack, khác cách tính phí → **cùng khẳng định: không có logic tĩnh
công khai nào sống sót phí + walk-forward + validation trên data thật.** Sự lệch duy nhất nằm ở các
method heuristic (Elliott/Wyckoff), củng cố thêm nhận định "kết quả xấu = bản code này chết, không
phủ định phương pháp gốc".

Chạy lại đối chứng: `python3 quant/xcheck_cloud/run_all.py --data data --khung H4 --out quant/xcheck_cloud/results`
