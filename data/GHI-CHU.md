# GHI CHÚ DATA — đọc trước khi viết run_all.py

**18 mã × M1, tổng ~145,8 triệu nến.** Tất cả là **parquet** (không phải CSV như NHIEM-VU.md
viết ban đầu — đọc bằng `pd.read_parquet`). Schema thống nhất: index = `timestamp`
(datetime64), cột `open, high, low, close` (float64). **Không có volume.**

## Nguồn vật lý (QUAN TRỌNG — 17 file là SYMLINK)
- 17 cặp fx → symlink tới `~/Downloads/VPS_LIVE_EA/R_and_D_Lab/data/intraday/`
  (bộ data đã dùng ở lab trước, dựng 05/07/2026). **Đừng xoá/di chuyển thư mục gốc đó.**
- `xauusd_m1.parquet` → file THẬT, gộp từ 15 file năm histdata.com
  (`~/Documents/TradingData/XAUUSD/M1_HistData/`), đã sort + khử trùng lặp.

## Kiểm kê
| Mã | Nến | Khoảng | Lưu ý |
|---|---|---|---|
| audjpy, audusd, eurcad, eurchf, eurgbp, eurjpy, gbpchf, gbpjpy, gbpusd, usdcad, usdchf, usdjpy | 8,8–9,2 triệu/mã | 2001-01 → 2026-06 | bộ lõi, 25 năm |
| nzdjpy, nzdusd | ~8,4 triệu/mã | 2003-01 → 2026-06 | |
| xagusd (bạc) | 5,88 triệu | 2001-01 → 2026-06 | |
| chfjpy | 8,1 triệu | 2001-01 → **2023-09** | cụt đuôi — không có đoạn validation 15% cuối cùng thời kỳ với các mã khác |
| eurusd | **chỉ 1,0 triệu** | **2023-09 → 2026-06** | ngắn — N nhỏ, đừng để nó lọt bảng xếp hạng chung mà không ghi chú |
| xauusd (vàng) | 5,17 triệu | 2009-03 → **2024-12** | **THIẾU TRỌN NĂM 2012**; nguồn histdata, múi giờ EST (GMT-5, không DST) |

## Bẫy cần nhớ
1. Múi giờ có thể KHÔNG đồng nhất giữa bộ intraday (nguồn cũ, chưa rõ tz) và xauusd (EST).
   Logic theo nến thuần thì không sao; logic theo phiên (London/NY) thì phải kiểm tz trước.
2. M1 có khe (cuối tuần, lễ, mất tick). Resample M5/M15/H1/H4 xong phải bỏ nến rỗng,
   đừng fill-forward tạo nến ma.
3. `data/` đã vào `.gitignore` — KHÔNG commit data, chỉ commit code + `quant/results/`.
4. Alternate không dùng (tránh trùng): `~/Downloads/GBPUSD_M1_2001_2023.csv`, `AUDJPY_M1.csv`,
   `USDCAD_M1.csv` (trùng mã với bộ parquet). BTC chưa có M1 dài trên máy — khoảng trống đã biết.
