---
name: dong-phien
description: Nghi thức đóng phiên — cập nhật STATE + DECISION_LOG + push. Mọi phiên làm việc thực chất PHẢI chạy trước khi kết thúc.
---
# /dong-phien — quy trình (5 phút)
1. Xác định dự án đã đụng tới → mở hq/projects/<dự-án>/STATE.md.
2. Cập nhật: "ĐANG Ở ĐÂU" (3-5 dòng, kết quả mới nhất + file bằng chứng) và "VIỆC TIẾP THEO" (đánh số, ghi rõ AI làm: SẾP/PHIÊN MỚI/VPS).
3. Có quyết định mới? → thêm 1 dòng đầu DECISION_LOG.md (ngày + quyết định + lý do 1 câu).
4. Kết quả cho người đọc? → upload bản tóm tắt lên Drive folder dự án.
5. `git add hq/ && git commit -m "hq: dong phien <dự-án> <ngày>" && git push`.
6. Câu cuối trả lời user: xác nhận STATE đã cập nhật + 1 dòng "phiên sau bắt đầu từ đâu".
