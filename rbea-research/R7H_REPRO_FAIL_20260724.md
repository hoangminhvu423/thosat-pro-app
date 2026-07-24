# R7h — KHÔNG TÁI LẬP ĐƯỢC 15-17% + phát hiện mâu thuẫn dữ liệu (2026-07-24)

## Việc: Sếp yêu cầu tái lập R7h (mc_personal.py) để chốt số PERSONAL trước khi cắm tiền thật.

## Kết quả: KHÔNG tái lập được — và dữ liệu truy cập được cho kết quả NGƯỢC.
- CSV gốc `mret_XAU.csv` + `mret_BTC.csv` (input của mc_personal.py) KHÔNG có trên repo lẫn 2 Drive.
  Chỉ có script + kết quả trong commit 62b2c6d.
- Tôi dựng lại `mret_BTC` từ `forward/btc_shadow_log.csv` (backfill R7g thật, 19 tháng 2025-01→2026-07):
  **tổng −23,5R, TB −1,23R/tháng (ÂM)**. → MC 1-sleeve BTC lãi kép 5y:
  | risk | CAGR med | medMaxDD | P(DD>30%) |
  |---|---|---|---|
  | 0.75% | −12,1% | 50,6% | 96,1% |
  | 0.85% | −13,8% | 55,6% | 97,8% |
  | 1.0%  | −16,2% | 61,9% | 99,0% |
  (bản dựng lại: forward/mret_BTC_RECON_from_shadow.csv)

## MÂU THUẪN 3 NGUỒN cùng "BTC BREAK Donchian-20" cùng kỳ — cần điều tra:
1. G2 tester RB_EA v0.32 (chạy 24/07): **13 lệnh / +48 / PF 2.24** (DƯƠNG, thưa).
2. btc_shadow_log (forward monitor): **187 lệnh / −23,5R** (ÂM, dày gấp ~14×).
3. R7h commit: đủ dương để ra +14-18%.
→ 187 vs 13 lệnh = shadow engine ≠ EA compiled (khác TF/logic). 3 nguồn KHÔNG khớp = không thể
   tin con số nào cho tiền thật tới khi hoà giải.

## Khuyến nghị (real-money safety)
- **HOÃN cắm PERSONAL 0.85%** tới khi: (a) tìm được mret gốc R7h HOẶC regenerate đúng từ backtest R7g
  trên XAUUSDc M1 (có trên Drive 05_Live_Validation) + BTC bằng ĐÚNG logic EA compiled (không phải shadow);
  (b) giải thích khoảng cách 187 vs 13 lệnh; (c) chạy lại MC ra số nhất quán.
- FUND (0.15%) & HUMAN_ALPHA (0.20%) KHÔNG bị ảnh hưởng (số keep, DD nhỏ, đã vững) — build được.
- I_Mode mechanism build được ngay; chỉ để PERSONAL risk = `TẠM - CHỜ CHỐT (R7h chưa tái lập)`.
