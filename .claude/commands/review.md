---
description: Pha 4 — Rà soát / Review thay đổi
---

# /review — Rà soát (Review)

Bạn đang ở **pha Review**. Mục tiêu: tự soi lại thay đổi trước khi phát hành.

Phạm vi: `$ARGUMENTS` (mặc định: diff hiện tại `git diff`).

Hãy:
1. Giao subagent `reviewer` (hoặc skill `code-review` nếu có) rà soát diff.
2. Kiểm 4 tiêu chí: **đúng** (correctness/bug), **đơn giản** (không phức tạp thừa), **tái dùng** (có bỏ sót hàm sẵn có?), **không phá vỡ** (regression).
3. Với dự án thợ sắt: kiểm cả quy ước (mm số nguyên, logic ở engine, mẫu `nhap` cấm cắt thật). Với quant: kiểm look-ahead bias, chi phí giao dịch, tái lập được.
4. **Sửa ngay** những gì tìm ra; nếu không chắc, hỏi người dùng.

Chỉ sang `/ship` khi review sạch.
