# FINDING KHẨN — MIN-LOT làm hệ "câm" trên account nhỏ (2026-07-24 tối, R&D cloud)
Điều tra theo lệnh Sếp: "chênh lệch cực kỳ bất thường" giữa backtest (~10 lệnh/tháng BTC) và
MT5 tester v0.32 (0.7 lệnh/tháng, PF 2.24 vs 1.19). Phương pháp: mô phỏng Python NGỮ NGHĨA EA
(1-vị-thế, budget, state machine, time-stop) trên cùng data Bitstamp, cùng cửa sổ thời gian.

## KẾT QUẢ ĐO (BTC, 18 tháng 01/2025–07/2026)
| Engine | n | totR | PF |
|---|---|---|---|
| A. Overlap (chuẩn R7g) | 187 | −23.5 | 0.83 |
| B. Ngữ nghĩa EA (không min-lot) | 159 | −15.4 | 0.86 |
| C. Ngữ nghĩa EA + min-lot 0.01, bal 4600, risk 0.15% | **2** (171 lệnh SKIP) | +3.9 | — |
| MT5 tester v0.32 (bal 4600, risk 0.15%) | 13 | +48.6 | 2.24 |

## KẾT LUẬN
1. Ràng buộc thiết kế (flag b) chỉ cắt ~15% (187→159) — KHÔNG phải nguyên nhân chính.
2. **Nguyên nhân chính: LƯỢNG TỬ HÓA LOT.** Risk 0.15% × 4,600 = $6.9/lệnh; ATR H4 BTC 2025-26
   median $1,089 → lot cần ≈ 0.006 < min 0.01 → EA skip ĐÚNG THIẾT KẾ (audit xanh "không ép min-lot").
   ~90% tín hiệu bị nuốt. 13 lệnh của tester = mẫu SÓT lúc ATR thấp (khác C=2 do chi tiết contract
   spec sàn; cùng cơ chế). → **PF 2.24 là artifact chọn mẫu (chỉ trade lúc ATR thấp), KHÔNG phải edge.**
3. **XAU cũng nghẹn**: min-lot 0.01 = 1oz, ATR median $24/oz → risk tối thiểu/lệnh $24.
   Bal 3,909-4,600 @ 0.15% ($5.9-6.9) và cả 0.5% ($19.5-23) → **SKIP TOÀN BỘ**. Cấu hình profile RBEA
   hiện tại (risk 0.15) trên account này = EA gần như KHÔNG BAO GIỜ trade, cả 2 chân.
4. Blind spot hệ thống: MỌI backtest/MC (R7e/R7g/R7h) giả định lot chia vô hạn — đúng với prop
   100k-400k (0.15% × 200k = $300, lot thoải mái), SAI với account nhỏ. Không model nào bắt được
   vì không ai đưa min-lot vào giả định — lỗi giả định, không phải lỗi tính.
5. Phụ: 2025-26 BTC là regime XẤU thật (cả 2 engine âm) — đúng caveat R7g "S3 yếu, demo là phán quyết".
   Con số +48.6 của tester không mâu thuẫn: nó là 13 lệnh được lọc bởi filter-ATR-thấp tàng hình.

## HỆ QUẢ HÀNH ĐỘNG
- **G2 verdict re-qualify**: PASS cơ học (EA bắn lệnh, risk cap đúng), thống kê KHÔNG DÙNG ĐƯỢC.
- **CẤM cắm profile hiện tại (risk 0.15) lên account 3,909** — không nguy hiểm, nhưng vô nghĩa (0 lệnh).
- Lựa chọn cho account 3,909 (Sếp quyết):
  A) **Profile PERSONAL đúng R7h**: risk 1.0%/sleeve ($39 > ATR-max XAU $35.5 → hết nghẹn cả 2 chân).
     Kỳ vọng R7h: median +17.9%/năm, maxDD ~24%, P(DD>30%) 50% — khớp DD-budget 25-30% Sếp đã duyệt.
     0.75% vẫn nghẹn XAU một phần (risk $29 < ATR lúc cao) → thành filter ngầm, tránh.
  B) XAU-only @1% (tắt BTC vì regime 2025-26 xấu) — bớt tần suất, bớt DD.
  C) Không chạy account nhỏ — đợi FTMO 200k nơi mọi số R7g áp dụng đúng (0.15% = $300, min-lot vô hại).
- **R4 (v0.4, BẮT BUỘC)**: OnInit tính "min-lot risk" = ATR×contract_min và TG CẢNH BÁO nếu
  risk% cấu hình < ngưỡng trade được; log mỗi lệnh SKIP min-lot ra TG hằng ngày (đếm), không im lặng.
- **R5 (R&D)**: thêm lot-quantization vào mọi backtest/MC khi đánh giá account size cụ thể.
