# PREREG R7c — CỔNG REGIME cho sleeve N-SHAPE (khóa 2026-07-23, TRƯỚC khi chạy)
Câu hỏi: có tồn tại cổng regime TÍNH ĐƯỢC REAL-TIME (không nhìn tương lai) tách được phần trend-ăn khỏi phần chop-chết
của N-shape không? Engine: Fable-B chuẩn (fill bảo thủ). Config N đại diện: IMP1.5/k2/retrace(0.2,0.7)/TP=MM
+ kiểm chéo 2 config phụ (IMP1.0/k3 và IMP2.0/k2/(0.15,0.8)) để tránh cherry-pick config.

## CỔNG ỨNG VIÊN (khóa trước, grid nhỏ — tính tại nến H4 ĐÃ ĐÓNG ngay trước nến fill)
- **G1 TrendDist**: |close − SMA200(H4)| / ATR20 ≥ θ, θ ∈ {1.0, 2.0}. (xa MA dài = có trend)
- **G2 ER**: Kaufman Efficiency Ratio 20 nến = |c[i]−c[i−20]| / Σ|Δc| ≥ θ, θ ∈ {0.25, 0.35}. (đường đi thẳng = trend)
- **G3 ADX(14)** Wilder ≥ θ, θ ∈ {20, 25}.
- **G0 ĐỐI CHỨNG**: cổng giả ngẫu-nhiên-tất-định (hash chẵn/lẻ theo index nến, ~50% lệnh) — cắt lệnh NGẪU NHIÊN
  KHÔNG được phép cải thiện avgR. Nếu G0 "cải thiện" → phương pháp đánh giá có lỗi.

## TIÊU CHÍ PASS (khóa trước — một cổng chỉ được coi là THẬT nếu đủ CẢ 3)
1. **Tách trong-từng-đoạn**: avgR(ON) > avgR(OFF) ở CẢ 3 đoạn (không phải chỉ tách A/B khỏi DEV — chống date-picker).
2. **DEV-ON ≥ 0**: phần được cổng cho phép trong chính thập kỷ chop không được âm đáng kể (≥ −0.02R).
3. **Không thoái hóa**: cổng giữ ≥ 30% số lệnh toàn kỳ, và kết quả cùng chiều trên cả 2 config phụ.

## DỰ ĐOÁN FALSIFIABLE (của Claude, chấm sau)
- P1: G1 hoặc G2 đạt tiêu chí 1 (ON>OFF cả 3 đoạn). — tin TB
- P2: ÍT NHẤT một cổng cho DEV-ON ≥ 0. — tin TB-THẤP (đây là bài test thật; hoàn toàn có thể fail)
- P3: G0 đối chứng KHÔNG tách (chênh <0.05R). — tin CAO
- P4: Nếu mọi cổng fail tiêu chí 2 → kết luận trung thực: N-shape KHÔNG cứu được bằng cổng đơn giản → xếp kho,
  không cố thêm cổng phức tạp hơn (chống mining). — cam kết trước.

## LỐI RA (khóa trước)
- PASS → thiết kế sleeve N-gated cho v0.3, vẫn phải qua control-run + audit + demo.
- FAIL → N-shape vào kho giả thuyết, EA giữ nguyên v0.21. Không có lối "thử thêm 20 cổng nữa".

## KẾT QUẢ (chạy 2026-07-23, engine Fable-B, 3 config, net 0.04R)

### Bảng chính (PRIMARY IMP1.5/k2, avgR ON per segment; ngoặc = OFF)
```
gate           A-ON(OFF)        DEV-ON(OFF)      B-ON(OFF)      keep%
khong gate     +0.192           -0.047           +0.473         100
G1 dist>=2.0   +0.298(-0.107)   -0.141(+0.202)   +0.550(+0.271)  73   <- G1 làm DEV TỆ HƠN: BÁC
G2 ER>=0.25    +0.182(+0.200)   +0.167(-0.225)   +0.661(+0.264)  48   <- DEV-OK, hụt SEP ở A
G2 ER>=0.35    +0.357(+0.130)   +0.290(-0.142)   +0.785(+0.280)  27   <- SEP3/3 + DEV-OK, keep<30%
G3 ADX>=25     +0.172(+0.218)   +0.123(-0.188)   +0.630(+0.346)  49   <- DEV-OK, hụt SEP ở A
G0 random50    +0.115(+0.263)   -0.074(-0.018)   +0.118(+0.889)  50   <- không tách DEV (chuẩn)
```
ALT1 (IMP1.0/k3): ER>=0.35 SEP3/3, keep 31%, nhưng DEV-ON = −0.026 (hụt ngưỡng −0.02 một sợi tóc).
ALT2 (IMP2.0/k2): ER>=0.35 SEP3/3 + DEV-OK, keep 24%.

### CHẤM DỰ ĐOÁN
- P1 ĐÚNG: ER>=0.35 đạt SEP3/3 trên CẢ 3 config.
- P2 ĐÚNG: nhiều cổng cho DEV-ON ≥ 0 (ER, ADX) — phần chop CÓ tách được.
- P3 ĐÚNG: G0 không tách DEV (chênh 0.056R — trong nhiễu). CAVEAT: G0 cho thấy đoạn B (n~76) nhiễu lớn
  (random tách ±0.7R!) → mọi chênh lệch riêng đoạn B KHÔNG đáng tin; DEV (n=204) mới là bài test thật.
- P4 KÍCH HOẠT: không cổng nào PASS đủ 3 tiêu chí trên primary + lặp lại ở alt.

### VERDICT (theo lối ra đã khóa)
**FAIL-theo-prereg → N-shape + cổng XẾP KHO, EA giữ v0.21.** KHÔNG dò thêm ngưỡng trên cùng data (= mining).

### NEAR-MISS ghi nhận trung thực (cho vòng SAU, trên DATA MỚI — không phải data này)
- **Họ ER (efficiency ratio) là cổng đúng hướng rõ rệt**: ER>=0.35 đạt SEP3/3 trên cả 3 config, DEV-ON dương
  ở 2/3 config; mỗi config chỉ hụt MỘT tiêu chí (keep% hoặc DEV sát ngưỡng). G1 (khoảng cách SMA200) bị BÁC hẳn.
- Đường đi hợp lệ duy nhất: FORWARD-TEST sleeve N-gated-ER trên demo/dữ liệu 2025-26+ hoặc thị trường khác,
  prereg mới. Lưu ý keep ~25-30% → chỉ ~10-15 lệnh/năm: cần thời gian dài mới đủ mẫu.
- Insight cơ chế (2 engine đồng thuận): N-shape ăn khi ĐƯỜNG ĐI GIÁ THẲNG (ER cao) — khớp bản chất continuation;
  KHÔNG phải khi "xa MA" (G1 bác) — xa MA có thể là cuối trend/quá mua.
