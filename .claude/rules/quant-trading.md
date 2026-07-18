# Rule — Dự án Quant Trading (MT5 / MQL5 / Exness)

> Áp dụng khi làm việc với hệ giao dịch định lượng của người dùng. Stack thật:
> **EA MQL5 chạy trên MetaTrader 5, tài khoản Exness, VPS 36-chart.** KHÔNG phải Python.
> _Read before touching any trading code. This is an MT5/MQL5 shop, not a Python backtesting one._

## Bối cảnh / Setup
- **Công cụ**: viết EA bằng **MQL5**, backtest bằng **MT5 Strategy Tester**, deploy lên **VPS** qua pipeline (`deploy-ea`, `safe-compile`).
- **Sản phẩm giao dịch**: **thuần CFD** — forex (cặp tiền), **BTC**, và **chỉ số** (vd US500). Không dùng sàn spot / API bên thứ ba.
- **Kiểu vốn**: theo luật prop-firm (FTMO-style) — có mốc daily-loss / max-loss.
- Magic tách biệt theo chiến lược (vd 707001 calendar · 707002 rsi2).

## ⚠️ LUÔN dùng skill trước khi thao tác
- **`guardian-rules`** — cổng an toàn BẮT BUỘC trước mọi thao tác compile/deploy/kill/close trên VPS live. KHÔNG ngoại lệ.
- **`ea-code-audit`** — audit đối kháng EA trước khi deploy (lỗi âm thầm làm live ≠ backtest).
- Trước khi kết luận "có bug": đọc `SYSTEM_BRIEF.md` + `DECISION_LOG.md`.

## Nguyên tắc số 1: live PHẢI = backtest / No live-vs-backtest skew
- Nguồn lỗi lớn nhất là **repaint / look-ahead**: tín hiệu phải đọc **nến ĐÃ ĐÓNG (index 1)** + new-bar gating (`iTime(sym,TF,0)` đổi), KHÔNG đọc nến đang hình thành (index 0).
- Cache indicator handle (`iATR/iMA/iRSI`) — KHÔNG tạo/huỷ mỗi tick. Handle chưa có data → `CopyBuffer` trả 0 → bỏ lỡ entry.
- Chi tiết checklist: skill `ea-code-audit`.

## Chi phí & thực thi / Costs & execution — luôn tính vào
- **Spread, commission, slippage** — CFD forex/chỉ số/BTC chi phí nằm nhiều trong spread; backtest bỏ qua là **vô nghĩa**.
- **Swap / phí qua đêm**: forex + chỉ số + BTC CFD đều có swap khi giữ lệnh qua đêm/cuối tuần → cộng vào PnL.
- **Filling mode đúng theo symbol** (`SetTypeFillingBySymbol`) — vd US500 chỉ nhận FOK (rc=10030 nếu sai) → lệnh/breaker có thể KHÔNG khớp.

## Rủi ro / Risk — ưu tiên trước lợi nhuận
- **Sizing**: xử lý `lot < volume_min` rõ ràng; **trần risk cứng mỗi lệnh**; SL width phải validate (không "một cỡ cho mọi sleeve").
- **Circuit-breaker** phải có retry + verify (`PositionSelectByTicket`), không được thất bại âm thầm.
- Mốc max-loss / daily-baseline lưu bền (`GlobalVariable`/file), KHÔNG để biến RAM → reset khi restart là hỏng guard.
- Daily-loss tính theo **SERVER-day** (`TimeCurrent`), gồm cả floating (chuẩn FTMO).
- **CẤM DCA / martingale / grid** — bao giờ.

## Reproducibility / Tái lập được
- Ghi lại: version EA, tham số, khoảng dữ liệu backtest, commit hash cho mỗi kết quả. Backtest-validate trước khi deploy thay đổi logic.

## Đánh giá / Evaluation
- Báo cáo: Sharpe, max drawdown, hit rate, profit factor, exposure — không chỉ tổng lợi nhuận. Cẩn trọng overfitting: walk-forward, kiểm trên nhiều chế độ thị trường.

## Kiểm chứng / Verify
- Trước khi tin một chiến lược: chạy Strategy Tester end-to-end, xem đường vốn + vài giao dịch mẫu bằng tay để chắc logic đúng, không chỉ nhìn con số Sharpe.
