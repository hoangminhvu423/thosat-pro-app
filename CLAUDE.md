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

Đo lại 22/09/2026 trên **27.626 request thật** (1,12 tỷ token quy đổi, ~3 tháng): fan-out chiếm
**17,5%**, trong đó **86% đang chạy Opus** → vẫn phải hạ bậc, nhưng trần tiết kiệm chỉ **14,1%**.
Con số "85% fan-out" đo 31/07 đã lỗi thời (sai ~5 lần) — **đây là đòn bẩy thứ BA, không phải thứ nhất.**

| Dùng cho | `subagent_type` | Model |
|---|---|---|
| Quét / kiểm kê / đo đếm / tìm file | **`scout`** | haiku |
| Phản biện / verify / red-team / panel | **`judge`** | fable |
| Tổng hợp, phán quyết cuối | mặc định | opus |

Trong Workflow: `agent(prompt, {agentType:'scout'})` hoặc `{model:'fable'}`.
Preamble dùng chung **≤300 token** — để agent tự đọc file, đừng nhồi tài liệu vào prompt từng
agent (nhồi 2.000 token × 58 agent là nguyên nhân cache-ghi nổ 6,2×).

Workflow là thứ đắt nhất. Cân nhắc trước khi chạy; **không chạy 3 lần một ngày**.

## 2. Phiên khổng lồ — ĐÒN BẨY SỐ 1 — và KHÔNG BAO GIỜ đề nghị Sếp mở cửa sổ mới

Đo 22/09/2026: **8 phiên trên tổng 1.138 (0,7% số phiên) ngốn 74,3% toàn bộ chi phí.**
Phiên lớn nhất một mình chiếm **31%** — 6.216 request, context trung bình ~575k. Cả 8 phiên đều
chạy 500–730k. Tiền chảy ở đây, không phải ở fan-out.

Sếp rất ngại mở cửa sổ mới, và **không cần**: `/compact` nén tại chỗ, cùng cửa sổ, giữ nguyên
mạch việc. Phiên cũ không mất (`claude -c`, `--resume`, `--fork-session`).

**Ngưỡng cứng: context vượt ~150k thì chốt trạng thái vào file TRƯỚC, rồi `/compact` ngay.**
Mạch việc phải nằm ở file, không nằm ở lịch sử chat — trí tuệ model không phải ràng buộc; context
có trần và **mỗi request đọc lại toàn bộ**. Phiên 940k đắt ~9× phiên 100k cho cùng câu hỏi, và
tự-nén là **lossy** nên phiên vô hạn còn *nhớ tệ dần*.

## 2b. Không làm vỡ cache — đòn bẩy số 2 (12,5%)

Cache tự động trúng **97,3%**, đã cắt sẵn ~87% chi phí đầu vào — harness lo phần này rất tốt,
không cần cấu hình gì. Nhưng **352 lần vỡ cache** đã ghi lại 111,7 triệu token = **12,5% tổng**;
cú lớn nhất ghi lại **926.955 token trong MỘT request**.

Vỡ cache = sửa phần ĐẦU prompt. Ba nguyên nhân, đều tránh được:

- **Đổi model giữa phiên** → chọn model từ đầu, không `/model` giữa chừng.
- **Sửa `CLAUDE.md`/skill khi đang có phiên chạy** → sửa xong rồi mới mở phiên.
- **Nạp thêm MCP server / skill giữa chừng** → bật sẵn từ đầu.

Luật 2 và 2b nhân nhau: vỡ ở phiên 100k mất 100k, vỡ ở phiên 926k mất 926k. Cắt phiên nhỏ lại
thì vỡ cache cũng tự rẻ đi.

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
