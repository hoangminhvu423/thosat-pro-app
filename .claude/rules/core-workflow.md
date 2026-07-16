# Rule — Quy trình lõi: Agentic Engineering

> STOP VIBE CODING. Từ "vibe coding" (ném ngôn ngữ tự nhiên lỏng lẻo cho LLM) sang
> **agentic engineering** (kiến trúc quy trình có kỷ luật). Áp dụng cho MỌI dự án.
> _The core loop below applies to every project, current and future._

## Vòng lặp R → P → E → R → S / The loop
Mọi task không tầm thường đều đi theo 5 pha. Đừng nhảy thẳng vào code.

1. **Research (Nghiên cứu)** — Hiểu trước khi viết. Đọc code liên quan, tìm hàm/tiện ích tái dùng được, xác định ràng buộc. Ưu tiên dùng subagent `researcher` / lệnh `/research`. Không đoán khi có thể kiểm chứng.
2. **Plan (Lập kế hoạch)** — Viết ra cách làm: file nào sửa, tận dụng gì sẵn có, rủi ro, cách kiểm chứng. Dùng `/plan` hoặc subagent `planner`. Kế hoạch phải đủ để một người khác thực thi.
3. **Execute (Thực thi)** — Làm đúng kế hoạch. Thay đổi nhỏ, có thể kiểm chứng. Viết code khớp phong cách xung quanh (naming, comment, idiom). Dùng `/execute`.
4. **Review (Rà soát)** — Tự soi lại: đúng, đơn giản, không phá vỡ gì. Dùng subagent `reviewer` / lệnh `/review` (hoặc skill `code-review`). Sửa những gì tìm ra.
5. **Ship (Phát hành)** — Kiểm chứng end-to-end (chạy thật, không chỉ đọc code), rồi commit + push với message rõ ràng. Dùng `/ship`.

## Mô hình điều phối: Command → Agent → Skill
- **Command** (`.claude/commands/*.md`): điểm vào một pha của quy trình, do người dùng gọi bằng `/tên`.
- **Agent** (`.claude/agents/*.md`): subagent chuyên trách, chạy song song/độc lập, trả về kết luận gọn.
- **Skill** (`.claude/skills/*/SKILL.md`): quy trình lặp lại, đóng gói theo từng dự án (vd: thêm mẫu, phát hành).

## Nguyên tắc chung / Principles
- **Tái dùng trước, viết mới sau.** Tìm hàm/pattern có sẵn trước khi tạo code mới.
- **Kiểm chứng bằng hành vi thật**, không chỉ typecheck/test. Chạy luồng bị ảnh hưởng.
- **Báo cáo trung thực.** Test fail thì nói fail kèm output; bước bị bỏ qua thì nói rõ.
- **Xác nhận trước** với hành động khó đảo ngược hoặc hướng ra ngoài (push, xóa, gửi).
- **Commit/push chỉ khi được yêu cầu.** Nếu đang ở nhánh mặc định, tạo nhánh trước.

## Tự nhận diện dự án / Project auto-detection
Đầu phiên (SessionStart hook), xác định đang ở dự án nào và nạp đúng rule:
- Có `app/engine.js` + `catalogue/schema.json` → **App Thợ Sắt** → đọc `.claude/rules/thosat-app.md`.
- Có tín hiệu quant (backtest, pandas, strategy, `data/` OHLCV...) → **Quant Trading** → đọc `.claude/rules/quant-trading.md`.
- Không rõ → hỏi người dùng dự án thuộc loại nào.

## Ngôn ngữ / Language
Song ngữ: nội dung chính tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh. Với dự án thợ sắt, giữ định danh/UI tiếng Việt.
