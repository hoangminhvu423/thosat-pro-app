# Luật làm việc — repo ThợSắt Pro

> File này nằm TRONG repo nên **mọi môi trường đều đọc được**: Claude Code trên máy, trên web,
> trên mobile, và cloud agent. Memory (`~/.claude/projects/*/memory/`) **không** tới được các
> môi trường đó — nó chỉ nằm trên một máy và còn bị đóng khung theo từng project. Vì thế luật
> cần đúng ở mọi nơi thì phải ở đây.
>
> ⚠️ Repo này **PUBLIC**. Không ghi vào đây: IP máy chủ, số tài khoản, token, đường dẫn hạ tầng.
> Hạ tầng và vận hành nằm ở repo private `qtq-rbea`.

## 0. Token KHÔNG phải ràng buộc — đừng tối ưu nhầm

Gói **Max 5x**. Đo 23/09/2026: tuần **12%**, Fable tuần **5%**, credit **$0,00**, **chưa bao giờ
bị chặn hạn mức**. Token không quy ra tiền, và hạn mức còn thừa rất nhiều.

Mọi tính toán kiểu "tiết kiệm 30% token" là tối ưu một hàm mục tiêu Sếp **không** chịu. Chỉ có
**hai** ràng buộc thật, cả hai đều không phải tiền:

1. **Trần context 1.000.000** — đâm vào là mất việc (luật 1).
2. **Hạn mức riêng của Fable** — pool chật nhất (luật 2).

## 1. Đừng đâm vào trần 1M

Context tối đa **1.000.000 token**. Phiên `5a4a5833` từng chạy tới **997.910** — cách trần đúng
2.090 token. Ở mức đó **`/compact` KHÔNG chạy được**: nén cần chỗ trống để chứa bản tóm tắt, mà
không còn chỗ nào. Phiên chạm trần = không nén được, không làm tiếp được; chưa chốt trạng thái
thì **mất việc thật**.

**Ngưỡng: 🟢 dưới 400k · 🟡 400–700k tính chuyện nén · 🔴 trên 700k nén trước khi quá muộn.**

Đây **không** phải ngưỡng tiết kiệm tiền. Ngưỡng 150k ở bản trước là sai — nó bắt nén 20–50 lần
mỗi phiên để đổi lấy khoản tiết kiệm không tồn tại. 400k/700k vẫn chừa 300k đệm trước tường mà
chỉ phải nén 4–10 lần.

Nén tại chỗ bằng `/compact`, **không cần mở cửa sổ mới** (`claude -c`, `--resume`, `--fork-session`).
Chốt trạng thái ra file TRƯỚC khi nén — tự-nén là *lossy*.

Phiên đã quá trần thì `/compact` vô dụng: dùng `~/.claude/cong-cu/trich-trang-thai.py`, nó đọc
transcript thẳng từ đĩa nên không vướng trần.

Kiểm tra: `python3 ~/.claude/cong-cu/dang-chay.py`

## 2. Fable là pool chật — ĐỪNG đẩy fan-out sang đó theo phản xạ

Subagent **kế thừa model của phiên cha**. Không chỉ định thì chạy Opus hết. Fan-out chiếm 39,5%
lượng token (17,5% subagent + 22,1% **worktree** — worktree chạy thành phiên riêng, không mang cờ
`isSidechain` nên rất dễ đếm sót).

Nhưng **Opus 5 ở mức high/max chưa bao giờ chạm trần, còn Fable 5.1 thì chớp mắt là chạm** —
Fable có hạn mức tuần RIÊNG và chật hơn nhiều. Hạ bậc fan-out sang Fable là **chuyển tải từ pool
rộng sang pool chật**: tối ưu ngược.

| Dùng cho | Model | Vì sao |
|---|---|---|
| Quét / kiểm kê / tìm file | `scout` (haiku) | rẻ, tính vào pool chung |
| Phản biện / verify | **cân nhắc** — `judge` (fable) ăn vào pool chật nhất |
| Việc chính, tổng hợp, fan-out nặng | opus | pool rộng, chưa từng chạm trần |

Preamble dùng chung **≤300 token** — để agent tự đọc file, đừng nhồi tài liệu vào prompt từng agent.

## 2b. Vỡ cache — chuyện nhỏ, nhưng tránh được thì tránh

⛔ `/model` giữa phiên và bật/tắt MCP làm ghi lại toàn bộ context (đo được 69k ở phiên nhỏ; ở
phiên 900k sẽ là ~900k). **Chọn model từ đầu phiên.**
✅ Sửa file `.md` khi phiên đang chạy thì **KHÔNG vỡ** — đã đo 2 lần, request kế tiếp chỉ ghi
82–732 token. Cứ sửa thoải mái, không cần đợi task xong.

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
