# MIGRATE hq/ → repo riêng qtq-hq (khi Sếp tạo repo)
1. Sếp tạo repo private `qtq-hq` trên github.com (GitHub App hiện KHÔNG có quyền tạo repo — 403 đã thử 2026-07-23).
2. Cấp quyền cho Claude GitHub App vào repo mới (Settings → Integrations) để phiên cloud add_repo được.
3. Trong 1 phiên: `git subtree split -P hq -b hq-only && git push <url-qtq-hq> hq-only:main` — giữ nguyên lịch sử.
4. CLAUDE.md của hq/ trở thành CLAUDE.md gốc repo mới (tự nạp mọi phiên). Cập nhật INDEX + ROUTINES prompt sang repo mới.
