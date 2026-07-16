---
description: Pha 5 — Phát hành / Ship (kiểm chứng thật + commit + push)
---

# /ship — Phát hành (Ship)

Bạn đang ở **pha Ship**. Mục tiêu: kiểm chứng end-to-end rồi giao hàng.

Nhiệm vụ: `$ARGUMENTS`

Hãy:
1. **Kiểm chứng bằng hành vi thật** — chạy luồng bị ảnh hưởng, không chỉ đọc code. Báo cáo trung thực (fail thì nói fail kèm output).
2. Với **app thợ sắt**, nếu là phát hành app → dùng skill `phat-hanh` (bump `TEN_CACHE` trong `sw.js`, bump `?v=` trong `index.html`, rebuild `catalogue-all.json` nếu đổi mẫu).
3. Commit với message rõ ràng, đúng phong cách repo. App thợ sắt dùng: `Phát hành thosat-pro-vNN — DD/MM/YYYY HH:MM`.
4. **Chỉ commit/push khi được yêu cầu.** Đang ở nhánh mặc định thì tạo nhánh trước. Push: `git push -u origin <branch>` (retry backoff nếu lỗi mạng).
5. **Không tạo Pull Request** trừ khi người dùng yêu cầu tường minh.

Kết thúc bằng tóm tắt: đã làm gì, kiểm chứng ra sao, commit/branch nào.
