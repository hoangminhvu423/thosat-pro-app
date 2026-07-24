---
name: don-dep
description: Janitor tuần — quét dọn, cập nhật INDEX/STATE, báo cáo 10 dòng. Chạy bằng model rẻ (Haiku).
---
# /don-dep — quy trình
1. `git pull`. Đọc hq/INDEX.md.
2. Quét repo: file mới ngoài cấu trúc (root, rbea-research/) → phân loại: thuộc dự án nào? → nếu mồ côi >7 ngày → chuyển vào `archive/YYYY-MM/` (git mv, KHÔNG xóa).
3. Đối chiếu INDEX.md với thực tế: dự án thiếu/dư dòng → sửa.
4. Kiểm mỗi projects/*/STATE.md: mục "VIỆC TIẾP THEO" còn đúng không (so DECISION_LOG mới nhất). Stale >14 ngày → gắn cờ ⚠️ STALE ở dòng đầu.
5. Drive (nếu connector có): liệt kê file mới folder RB_EA, thêm link vào INDEX nếu thiếu. KHÔNG xóa gì trên Drive.
6. Commit "hq: don dep tuan YYYY-MM-DD" + push. Báo cáo ≤10 dòng: đã chuyển gì, cờ gì, INDEX đổi gì.
CẤM: xóa file, sửa nội dung STATE/LOG (chỉ gắn cờ), đụng vào code EA/app.

## BƯỚC THÊM (2026-07-24): kiểm drift skill
So sánh `~/.claude/skills/{ea-code-audit,guardian-rules}/SKILL.md` với `<repo>/.claude/skills/...`
(diff từng file). Nếu lệch: báo trong báo cáo, KHÔNG tự ghi đè (repo là nguồn chuẩn, người quyết).
