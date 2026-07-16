# Rule — Dự án Quant Trading

> Áp dụng khi làm việc trong repo giao dịch định lượng. Đây là quy ước nền tảng (chưa gắn với code cụ thể) —
> khi có codebase thật, bổ sung chi tiết vào file này.
> _Baseline conventions for quantitative trading projects; extend once a real codebase exists._

## Nguyên tắc số 1: KHÔNG look-ahead bias / No look-ahead bias
- Mọi feature/tín hiệu tại thời điểm `t` chỉ được dùng dữ liệu có tại `t` trở về trước. Không dùng giá đóng cửa tương lai, không `shift` sai chiều.
- Backtest và live phải dùng **cùng một** đoạn code tính tín hiệu (tránh train/serve skew).

## Reproducibility / Tái lập được
- Cố định seed ngẫu nhiên. Ghi lại phiên bản dữ liệu, tham số, và commit hash cho mỗi kết quả backtest.
- Kết quả phải tái lập được từ đầu bằng một lệnh (ví dụ `make backtest` hoặc script `run.py`).

## Data hygiene / Vệ sinh dữ liệu
- Xử lý rõ ràng: survivorship bias, corporate actions (split/dividend), múi giờ, ngày nghỉ giao dịch, dữ liệu thiếu.
- Tách biệt in-sample / out-of-sample; **không** tinh chỉnh tham số trên tập test.

## Rủi ro & chi phí / Risk & costs — luôn tính vào backtest
- Slippage, phí giao dịch, spread, market impact. Backtest bỏ qua chi phí là **vô nghĩa**.
- Ràng buộc vị thế, đòn bẩy, drawdown tối đa, position sizing. Ưu tiên rủi ro trước lợi nhuận.

## Đánh giá / Evaluation
- Báo cáo: Sharpe, Sortino, max drawdown, hit rate, turnover, exposure — không chỉ tổng lợi nhuận.
- Cẩn trọng overfitting: số tham số so với số quan sát, walk-forward, kiểm định trên nhiều chế độ thị trường.

## Kỹ thuật / Engineering
- Ngôn ngữ mặc định Python (pandas/numpy; backtest với vectorbt/backtrader/tự viết event-driven — chốt với người dùng).
- Tách lớp rõ ràng: `data/` (nạp & làm sạch) → `features/` → `strategy/` (tín hiệu) → `backtest/` (mô phỏng) → `report/`.
- Với LLM/agent trong pipeline: dùng model Claude mới nhất; xem skill `claude-api` khi cần tra cứu model id/pricing.

## Kiểm chứng / Verify
- Trước khi tin một chiến lược: chạy backtest end-to-end, kiểm tra đường vốn (equity curve) và một vài giao dịch mẫu bằng tay để chắc logic đúng, không chỉ nhìn con số Sharpe.
