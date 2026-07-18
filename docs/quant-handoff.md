# HANDOFF BRIEF — Phiên quant/loop (2026-07-18)

> Dán file này (hoặc nội dung của nó) làm tin nhắn đầu tiên cho phiên Claude Code MỚI trên MacBook —
> nơi có data MT5 thật — để tiếp tục không mất ngữ cảnh. Bản web-cloud và bản CLI-local là 2 runtime tách biệt,
> nên context KHÔNG tự mang theo; brief này là cầu nối.
> _Paste this as the first message in a fresh local Claude Code session on the Mac (which has the real MT5 data)._

## 0) Mục tiêu phiên tới
Viết + chạy **một backtest thống kê NGHIÊM TÚC** cho ý tưởng "EA tự động hoàn toàn dùng vote" trên **DATA THẬT**,
để trả lời câu hỏi đang mở (mục 4). Không kết luận trước khi có số liệu sạch.

## 1) Ai đang làm (context người dùng)
- **Builder-first quant**, ~2 năm làm EA/MQL5, đã phá bỏ **hàng nghìn EA**. Giao dịch **forex + BTC + chỉ số dạng CFD** trên **MT5 / Exness**. Đang thi **FTMO 100k 2-step**. Vừa có bước ngoặt về **risk & tâm lý (~1–2 tháng)**.
- Stack: **MQL5 EA + MT5 Strategy Tester + VPS**. Skill liên quan: `guardian-rules`, `ea-code-audit` (đang ở `~/.claude/skills`).
- Data thật nằm trên Mac (History Center / export CSV). `SYSTEM_BRIEF.md` + `DECISION_LOG.md` cũng ở máy.

## 2) Triết lý đã thống nhất
- **STOP vibe coding → agentic engineering.** Vòng lặp R→P→E→R→S.
- **Mọi logic tĩnh đóng băng đều decay** ("logic tĩnh chết"). Cái sống sót không phải method, mà là **tốc độ thích nghi của con người**.
- **Máy giỏi nhất**: thực thi/kỷ luật không mệt + tìm kiếm. **Dở nhất**: quyết định dưới thị trường phi dừng (non-stationary).
- **Entry đẹp cơ học** = ai cũng thấy → bị arbitrage → vô edge. **Entry đẹp trực giác** = tacit, không copy → mang edge.
- **Edge = hệ quả** của trực giác được tôi luyện, VỚI điều kiện: nhất quán + có sổ (DECISION_LOG) + risk + còn sống. **Bất định ≠ ngẫu nhiên.**

## 3) Ý tưởng đang test (của người dùng)
EA tự động hoàn toàn:
- Nhiều logic PTKT/PTPT (phân kỳ, phân kỳ ẩn, price action, SMC, Wyckoff, supply/demand...) → mỗi cái cho **một xác suất hướng**.
- **2 bộ lọc**: (1) bỏ/vào lệnh; (2) buy/sell.
- **Cơ chế**: với mỗi tham số, **rút ngẫu nhiên có trọng số theo xác suất** → phiếu YES/NO; **đa số** quyết định "vào/bỏ", và riêng "buy/sell". → cố ý đưa **tính phi tất định** vào để mô phỏng độ biến thiên của trực giác. Ý: "lựa chọn của EA cũng trở thành biến số như con người."

## 4) Kết quả SƠ BỘ — CHƯA KẾT LUẬN (chỉ trên DATA GIẢ)
- Monte Carlo **đồ chơi (KHÔNG phải data thật)**: hợp nhất tất định/Bayes ~58.7% "đúng" vs random-vote ~54%.
- **NHƯNG** edge đó **100% là look-ahead bias** (feature = xác_suất_thật + nhiễu). Bản trung thực (random-walk, feature chỉ từ quá khứ) → **50.04%, EV≈0**.
- ⚠️ **Do đó: CHƯA có kết luận hợp lệ nào về vote trên thị trường thật. CÂU HỎI ĐANG MỞ. Đừng tin số liệu tổng hợp.**
- Caveat độc lập dữ liệu duy nhất: probability-matching ≤ deterministic-max (single-shot, stationary) — **nhưng kể cả nó cũng chưa chắc chuyển sang trading thật** (path-dependency, sizing, decorrelation danh mục).

## 5) GIAO THỨC BẮT BUỘC khi backtest (không có = lại dính look-ahead)
1. **No look-ahead**: tín hiệu tính trên **nến ĐÃ ĐÓNG (index 1)**, vào lệnh nến kế (đúng `ea-code-audit`).
2. **Out-of-sample / walk-forward**; KHÔNG tinh chỉnh trên tập test.
3. **Cộng đủ chi phí**: spread + commission + slippage + **swap qua đêm**.
4. **Nhiều symbol** (forex + BTC + index) → tránh ăn may một thị trường.
5. Đủ số lệnh để có ý nghĩa thống kê → **bootstrap / t-test trên chuỗi lệnh**.
6. **So 4 phương án**: (a) random-vote; (b) hợp nhất tất định (log-odds/trọng số); (c) một logic đơn tốt nhất; (d) buy&hold. + kiểm "random-skip robustness".
7. **Báo cáo**: EV/lệnh, win%, profit factor, Sharpe, max drawdown, số lệnh, turnover — không chỉ tổng PnL.

## 6) Chạy ở đâu
Ưu tiên **MT5 Strategy Tester** (tick thật + spread/commission/filling thật) — chuẩn hơn Python đồ chơi.
Hoặc **export CSV → backtest Python** theo đúng giao thức mục 5.

## 7) Câu hỏi mở chính
Trên **data thật**, cơ chế **vote ngẫu nhiên có trọng số** có **thêm** gì so với **hợp nhất tất định** không —
hay chỉ **pha loãng edge** (như toy model gợi ý), TRỪ trường hợp **decorrelation danh mục** khi chạy nhiều instance?

## 8) Nguyên tắc vàng
Mặc định **mọi đường cong backtest đẹp là look-ahead/overfit cho tới khi chứng minh bằng OOS nghiêm ngặt trên data thật.**
Việc của con người = **nghi ngờ cái đường cong đẹp của máy trước tiên.**
