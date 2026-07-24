---
name: dong-bo-skills
description: Đồng bộ skill dùng chung theo LUẬT ĐỒNG BỘ — kéo nguồn chuẩn GitHub (thosat-pro-app @ claude/du-an-air-drop-y3ifan) về cache máy ~/.claude/skills, rồi backup zip MacBook + Google Drive. Dùng sau khi sửa/thêm skill trong repo, hoặc khi dựng môi trường/cửa sổ mới.
---

# /dong-bo-skills — quy trình

Chạy script kèm skill này (đường dẫn nào có trước thì dùng):

```bash
bash ~/.claude/skills/dong-bo-skills/sync.sh
# hoặc: bash ~/Downloads/thosat-pro-app/.claude/skills/dong-bo-skills/sync.sh
```

Script làm 4 việc, theo đúng thứ tự:
1. **Kéo nguồn chuẩn**: `git pull --ff-only` clone tại `~/Downloads/thosat-pro-app`
   (tự clone nhánh `claude/du-an-air-drop-y3ifan` nếu máy chưa có).
2. **Chép repo → cache máy**: `<repo>/.claude/skills/*` → `~/.claude/skills/`.
   KHÔNG xoá gì ở máy; skill chỉ có ở máy mà không có trên repo → in cảnh báo ⚠️
   (người quyết định đưa lên repo hay bỏ).
3. **Backup MacBook**: zip toàn bộ vào `~/.claude/backups/skills/skills-<ngày-giờ>.zip`,
   giữ 10 bản mới nhất.
4. **Backup Google Drive**: chép zip sang
   `~/Library/CloudStorage/GoogleDrive-hoangminhvu423@gmail.com/Drive của tôi/CLAUDE_SKILLS_BACKUP/`.

## Quy tắc (trích hq/CLAUDE.md — LUẬT ĐỒNG BỘ)
- Repo GitHub = **nguồn chuẩn duy nhất**. `~/.claude/skills` và Drive chỉ là cache/backup.
- Muốn sửa skill: sửa trong repo → commit + push → chạy script này. CẤM sửa cache.
- Hai bản lệch nhau: **bản repo THẮNG**. Janitor `/don-dep` kiểm drift mỗi tuần.
- `~/.claude/skills` là cấp user → mọi cửa sổ, mọi phiên, mọi dự án trên MacBook
  tự thấy skill sau khi sync (mở phiên mới để nạp danh sách skill).
