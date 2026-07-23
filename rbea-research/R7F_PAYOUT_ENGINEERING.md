# R7f — Kỹ thuật nâng payout keep-sleeve lên 2-4%/năm (2026-07-23)
Quét: CPPI-ladder (risk thang theo đệm lợi nhuận) × retention buffer (2-6%) × chu kỳ rút (15-60 lệnh), 8k paths × 3 năm.

## KẾT QUẢ CỨNG
- flat 0.25%: P(chết/3y) 8.5% | median payout 1.20%/năm | mean 1.58%
- CPPI ladder (.25/.5/.75, buf 4%): P(chết) 8.6% (survival GIỮ NGUYÊN ✓) | mean 1.78-1.84% | **median 0.00%**
- ladder base 0.3%: P(chết) nhảy 15-20% — bác.
→ **KHÔNG có cấu trúc ví tiền nào ép được median payout 2-4% từ edge này.** Toán chặn: E[payout] = avgR(0.078) × 60 lệnh × risk%.
@0.25% → trần kỳ vọng ~1.2%/năm. CPPI chỉ làm lệch phân phối (năm tốt trả nhiều hơn, survival giữ) — không tạo ra kỳ vọng.

## BA ĐÒN BẨY THẬT (theo công thức payout = avgR × tần suất × risk)
1. risk: ĐÃ MAX (0.25 là trần survival; tuần này đo).
2. avgR: ĐÃ CẠN (mọi refinement chết qua 3 vòng kiểm chứng độc lập).
3. **TẦN SUẤT — đòn bẩy duy nhất còn mở: ĐA THỊ TRƯỜNG.** Chạy keep-sleeve trên 2-3 symbol ít tương quan
   (mỗi cái 0.15-0.2% risk) → tổng lệnh ×2-3, DD tổng tăng chậm hơn nhờ tương quan <1 → ước ~2-2.5%/năm
   @ survival tương đương. ĐIỀU KIỆN: validate edge TỪNG symbol qua pipeline Fable (LESSON-04 — không copy config).
   Đây là R&D thật, gate như mọi thứ khác.

## KHUYẾN NGHỊ CHỐT
- Target 2-4% CHỈ BẰNG auto đơn-symbol: KHÔNG khả thi — chấp nhận hoặc đổi cấu trúc.
- Cấu trúc đạt target NGAY: **auto floor 1-1.2% + human sleeve vài lệnh high-conviction/quý (0.3-0.5% risk, máy giữ exit) = 2-4% tổng.**
- Giữ CPPI-ladder như cải tiến MIỄN PHÍ (survival giữ nguyên, mean +0.2-0.3%/năm, năm tốt trả nhiều hơn) — không phải phép màu.
- Trung hạn: R&D đa-symbol keep (validate từng market) nếu muốn auto tự đứng 2%+.
