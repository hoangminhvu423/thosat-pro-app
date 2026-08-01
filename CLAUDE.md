# Luật làm việc — repo ThợSắt Pro

> File này nằm TRONG repo nên **mọi môi trường đều đọc được**: Claude Code trên máy, trên web,
> trên mobile, và cloud agent. Memory (`~/.claude/projects/*/memory/`) **không** tới được các
> môi trường đó — nó chỉ nằm trên một máy và còn bị đóng khung theo từng project. Vì thế luật
> cần đúng ở mọi nơi thì phải ở đây.
>
> ⚠️ Repo này **PUBLIC**. Không ghi vào đây: IP máy chủ, số tài khoản, token, đường dẫn hạ tầng.
> Hạ tầng và vận hành nằm ở repo private `qtq-rbea`.

## 1. Phân tầng model — fan-out KHÔNG được kế thừa Opus

Subagent **kế thừa model của phiên cha**. Nếu không chỉ định gì thì mọi agent đều chạy Opus.
Đo thật 31/07/2026: **85% quota do fan-out** (Workflow 48,6% + Worktree 35,8%) — 5.523 request
Opus so với 68 Sonnet và 0 Fable, trong khi hạn mức Fable mới dùng 27%.

| Dùng cho | `subagent_type` | Model |
|---|---|---|
| Quét / kiểm kê / đo đếm / tìm file | **`scout`** | haiku |
| Phản biện / verify / red-team / panel | **`judge`** | fable |
| Tổng hợp, phán quyết cuối | mặc định | opus |

Trong Workflow: `agent(prompt, {agentType:'scout'})` hoặc `{model:'fable'}`.
Preamble dùng chung **≤300 token** — để agent tự đọc file, đừng nhồi tài liệu vào prompt từng
agent (nhồi 2.000 token × 58 agent là nguyên nhân cache-ghi nổ 6,2×).

Workflow là thứ đắt nhất. Cân nhắc trước khi chạy; **không chạy 3 lần một ngày**.

## 2. Giữ mạch việc — KHÔNG BAO GIỜ đề nghị Sếp mở cửa sổ mới

Sếp rất ngại mở cửa sổ mới, và **không cần**: `/compact` nén tại chỗ, cùng cửa sổ, giữ nguyên
mạch việc. Phiên cũ không mất (`claude -c`, `--resume`, `--fork-session`).

Xong một mảng việc thì **chốt trạng thái vào file TRƯỚC, rồi `/compact`**. Mạch việc phải nằm ở
file, không nằm ở lịch sử chat — trí tuệ model không phải ràng buộc; context có trần và **mỗi
request đọc lại toàn bộ**. Phiên 940k đắt ~9× phiên 100k cho cùng câu hỏi, và tự-nén là **lossy**
nên phiên vô hạn còn *nhớ tệ dần*.

## 3. Không đẩy việc lên Sếp

Sếp chỉ được yêu cầu **QUYẾT ĐỊNH** hoặc **SỞ HỮU** (bí mật gốc, yếu tố thứ hai, cho phép việc
không hoàn tác, chấp nhận rủi ro còn lại) — **không bao giờ yêu cầu THỰC THI**. Cảnh báo là lời
thừa nhận thiếu một cơ chế; cảnh báo nổ lần thứ hai cùng nguyên nhân thì phải thành cơ chế, hoặc bị xoá.

## 4. Riêng repo này

Chỉ chứa app ThợSắt Pro: `app/`, `catalogue/`, `index.html`. Mọi thứ RB_EA/quant đã tách sang
repo private. Hook `pre-push` chặn đường dẫn mật và nội dung mật — nếu nó từ chối thì **đừng
lách, hãy bỏ file khỏi track**.

Thêm/sửa mẫu catalogue: dùng skill `them-mau` (đủ 4 bước, dễ quên rebuild bundle + precache).
Phát hành: skill `phat-hanh` (3 bộ đếm KHÔNG đồng bộ nhau).
Trước khi phát hành mẫu mới: skill `catalogue-audit`.
