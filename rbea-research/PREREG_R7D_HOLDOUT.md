# PREREG R7d — HOLDOUT TEST N-shape + cổng ER trên DATA MỚI (khóa 2026-07-23, TRƯỚC khi lấy data)
Mục đích: phân xử near-miss R7c bằng dữ liệu CHƯA TỪNG NHÌN. Data chuẩn kết thúc 2025-07-15 → holdout = XAU
sau 2025-07-15 (≈1 năm) và/hoặc thị trường khác (BTC/EUR — prereg R7c cho phép).

## THAM SỐ ĐÓNG BĂNG (từ R7c, KHÔNG chỉnh bất kỳ số nào theo data mới)
- Engine: Fable-B chuẩn (fill bảo thủ, skip early-break, path M30 hoặc TF nhỏ nhất có).
- N-shape: pivot k=2, IMP=1.5×ATR20(H4), retrace [0.2,0.7], entry stop tại H1, SL=L1∓0.2×ATR, TP=MM, cửa sổ 12 nến.
- Cổng: **ER(20) ≥ 0.35** tính tại nến H4 đã đóng ngay trước fill. Phí 0.04R.

## DỰ ĐOÁN KHÓA TRƯỚC
- P1: Trên XAU 2025-07→nay (regime vàng vẫn trend), N-gated-ER cho avgR > 0. — tin TB
- P2: n sẽ NHỎ (~10-20 lệnh/năm sau cổng) → kết quả chỉ mang tính CHỈ HƯỚNG, không đủ kết luận thống kê.
  Cam kết trước: KHÔNG tuyên "PASS/FAIL cuối cùng" trên n<30; chỉ cộng dồn vào hồ sơ forward.
- P3: ON-subset > OFF-subset trên holdout (dấu tách lặp lại). — tin TB
- P4 (nếu lấy được thị trường khác): dấu hiệu cùng chiều (ON>OFF) nhưng biên độ có thể khác (LESSON-04: edge
  là thuộc tính thị trường × payoff × cơ chế vùng). — tin THẤP-TB

## TIÊU CHÍ DATA HỢP LỆ (khóa trước)
- Nguồn công khai tải được qua raw URL; TF ≤ H1 (để dựng H4 + path exit); có OHLC.
- BẮT BUỘC kiểm chéo chất lượng: đoạn trùng với data chuẩn (nếu có) phải khớp giá H4 close trong ±0.1%;
  nếu nguồn không trùng đoạn nào → so sánh 3-5 mốc giá nổi tiếng (ATH...) với giá trị công khai.
- Nếu KHÔNG tìm được data đạt chuẩn → dừng, báo trung thực, không hạ chuẩn data.

## KẾT QUẢ VÒNG 1 — BTC cross-market (chạy 2026-07-23)
Data: Bitstamp BTC/USD 1-min → M30 (255,199 nến, 2012-01→2026-07-23, cập-nhật-tới-hôm-nay).
Chất lượng PASS: max 2013=1,163 / 2017=19,666 / 2021=69,000 — khớp chính xác mốc lịch sử.
Nguồn: github ff137/bitstamp-btcusd-minute-data (auto-update daily). Engine Fable-B, tham số ĐÓNG BĂNG.

### N-shape KHÔNG cổng (n=422 / 14 năm):
P1 2012-19: +0.270 (n=196) | P2 2019-22: +0.042 (98) | P3 2022-25.5: +0.053 (101) | HOLDOUT >2025-07: +0.211 (27)
→ **DƯƠNG Ở MỌI ĐOẠN, kể cả cửa sổ bear/chop 2026.** Lõi N-shape (impulse→pullback→continuation) LẶP LẠI
được trên thị trường khác — bằng chứng cross-market đầu tiên cho pattern thô.

### Cổng ER>=0.35 (đóng băng từ R7c):
P1: ON +0.183 < OFF +0.308 (LÀM HẠI) | P2: hòa | P3: ON +0.127 > OFF +0.027 ✓ | HOLDOUT: ON +0.555 > OFF +0.090 ✓ (n=7!)
→ **Cổng ER KHÔNG lặp lại nhất quán trên BTC.** Đúng LESSON-04: cổng là thuộc tính thị-trường-cụ-thể
(XAU có cấu trúc phiên; BTC 24/7). G0 random: không tách nhất quán (sanity ✓).

### CHẤM DỰ ĐOÁN R7d
P1 (XAU holdout): CHƯA test — cần Sếp export XAUUSD M30 2025-07→nay từ MT5 (không tìm được nguồn công khai đạt chuẩn).
P2 ĐÚNG: n holdout nhỏ (27 thô / 7 sau cổng) — chỉ chỉ-hướng. P3 ĐÚNG-chỉ-hướng (ON>OFF ở holdout, n=7).
P4 SAI một nửa: pattern thô lặp lại (dương mọi đoạn) nhưng CỔNG không lặp lại → cổng ER hạ cấp thành "ứng viên XAU-specific".

### KẾT LUẬN VÒNG 1
1. **Nâng cấp N-shape thô**: giờ có bằng chứng 2 thị trường (XAU: trend-ăn/chop-chết; BTC: dương mọi đoạn ~+0.04..+0.27).
2. **Hạ cấp cổng ER**: không phải cơ chế phổ quát; nếu dùng chỉ được coi là tham số riêng cho XAU, cần forward XAU xác nhận.
3. Việc còn lại: XAU holdout 2025-07→nay (chờ export MT5 của Sếp) — mảnh phân xử cuối.

## KẾT QUẢ VÒNG 2 — XAU HOLDOUT THẬT (M15 MT5 export của Sếp, chạy 2026-07-23)
Data: XAU M15 2004-06→2026-01-30, CÙNG FEED data chuẩn (kiểm chéo đoạn trùng: chênh 0.000–0.0096% — PASS).
Hội tụ engine: đoạn 2022→2025.5 ra ĐÚNG +0.473/n=76 như canonical → cùng data cùng engine, xác nhận pipeline.
⚠️ Data holdout có 2 LỖ HỔNG: 2025-09-12→10-15 (32 ngày!) và 2026-01-13→01-22 (9 ngày) — giới hạn lịch sử M15 server.

### Holdout 2025-07-15→2026-01-30 (vàng parabol 3,327→4,889):
- 10 lệnh thô: avgR −1.43 — NHƯNG 1 lệnh −13.53R là ARTIFACT của hố 32 ngày (short kẹt trong hố, fill giả).
- **9 lệnh sạch: avgR ≈ −0.08R (tổng −0.7R, WR 3/9) — quanh hòa vốn, hơi âm.**
- Cổng ER≥0.35: ON 3 lệnh −0.17 vs OFF-sạch −0.04 → **tách ON>OFF BIẾN MẤT sau khi loại artifact** (tách "đẹp"
  trước đó do artifact nằm bên OFF).

### CHẤM DỰ ĐOÁN CUỐI
- P1 (N-gated-ER dương trên XAU holdout): **SAI** (−0.17, n=3).
- P2 (n nhỏ, chỉ chỉ-hướng): ĐÚNG (9 lệnh hợp lệ / 6.5 tháng).
- P3 (ON>OFF lặp lại): **KHÔNG xác nhận trên XAU holdout** sau khi làm sạch artifact.
- Ghi chú cơ chế: vàng parabol nhưng N-shape chỉ tìm được ~10 setup và ~hòa — pullback trong parabol quá nông
  (<20% retrace → rớt filter), setup qualify được thường là short ngược trend → bị cán.

### VERDICT R7d CUỐI CÙNG
**N-shape + cổng ER: GIỮ NGUYÊN TRẠNG THÁI XẾP KHO. EA giữ v0.21, KHÔNG thêm gì.**
Tổng bằng chứng 3 vòng: (XAU 21y: regime-dependent, fail prereg) + (BTC 14y: pattern thô dương mọi đoạn, cổng không lặp)
+ (XAU holdout 6.5 tháng: ~hòa vốn, cổng không tách). Điều DUY NHẤT bền: pattern thô có xương sống yếu-nhưng-thật
cross-market; mọi lớp tinh chỉnh (cổng, TP, entry) đều không qua nổi kiểm chứng độc lập. Đường duy nhất còn lại
cho N-shape: theo dõi FORWARD dài hơi (journal/demo), không phải backtest thêm.
