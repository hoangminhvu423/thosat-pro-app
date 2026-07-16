# CLAUDE.md — Hub điều phối / Orchestration hub

> Claude Code (và mọi AI/dev) đọc file này **đầu mỗi phiên**. Đây là điểm vào bộ khung
> **agentic engineering** — dùng chung cho mọi dự án. Chi tiết từng dự án nằm ở `.claude/rules/`.
> _Read first every session. Entry point for the shared agentic-engineering workflow._

## Triết lý / Philosophy — STOP VIBE CODING
Không ném ngôn ngữ tự nhiên lỏng lẻo cho LLM rồi hy vọng. Thay vào đó **kiến trúc quy trình có kỷ luật**:
mọi task không tầm thường đi theo vòng lặp **Research → Plan → Execute → Review → Ship**.
Xem `.claude/rules/core-workflow.md` (áp dụng cho MỌI dự án).

## Tự nhận diện dự án / Project auto-detection
Đầu phiên, xác định đang ở dự án nào rồi đọc rule tương ứng:
- Có `app/engine.js` + `catalogue/schema.json` → **App Thợ Sắt (PWA)** → đọc `.claude/rules/thosat-app.md`.
- Có tín hiệu quant (backtest, pandas, strategy, dữ liệu OHLCV...) → **Quant Trading** → đọc `.claude/rules/quant-trading.md`.
- Không rõ → hỏi người dùng.

## Bộ công cụ sẵn có / Available tooling
- **Commands** (`.claude/commands/`): `/research` `/plan` `/execute` `/review` `/ship` — mỗi lệnh là một pha.
- **Agents** (`.claude/agents/`): `researcher`, `planner`, `reviewer` — subagent chuyên trách.
- **Skills** (`.claude/skills/`): `them-mau` (thêm mẫu catalogue), `phat-hanh` (phát hành app) — riêng dự án thợ sắt.
- **Rules** (`.claude/rules/`): `core-workflow`, `thosat-app`, `quant-trading`.

## Nguyên tắc chung / Core principles
- **Tái dùng trước, viết mới sau** — tìm hàm/pattern có sẵn trước.
- **Kiểm chứng bằng hành vi thật**, không chỉ đọc code / typecheck.
- **Báo cáo trung thực** — fail thì nói fail kèm output.
- **Xác nhận trước** với hành động khó đảo ngược / hướng ra ngoài (push, xóa, gửi).
- **Ngôn ngữ song ngữ**: nội dung chính tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh. Dự án thợ sắt giữ định danh/UI tiếng Việt.

## Tái sử dụng bộ khung / Reusing this kit
Copy `.claude/` + `CLAUDE.md` sang dự án khác, hoặc cài vào `~/.claude` (áp dụng toàn máy).
Xem `docs/claude-setup/README.md` và `docs/claude-setup/install.sh`.

---
> Lưu ý: repo này đồng thời là sản phẩm **ThợSắt Pro**. Mọi chi tiết kiến trúc/quy ước/quy trình
> phát hành của app nằm ở `.claude/rules/thosat-app.md` và `README.md`.
