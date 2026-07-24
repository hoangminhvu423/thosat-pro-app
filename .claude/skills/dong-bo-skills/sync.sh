#!/bin/bash
# dong-bo-skills/sync.sh — đồng bộ skill dùng chung (LUẬT ĐỒNG BỘ, hq/CLAUDE.md)
# Repo GitHub = nguồn chuẩn → cache máy ~/.claude/skills → backup MacBook + Google Drive.
set -euo pipefail

REPO="$HOME/Downloads/thosat-pro-app"
BRANCH="claude/du-an-air-drop-y3ifan"
URL="https://github.com/hoangminhvu423/thosat-pro-app.git"
SRC="$REPO/.claude/skills"
DEST="$HOME/.claude/skills"
BACKUP_DIR="$HOME/.claude/backups/skills"
DRIVE="$HOME/Library/CloudStorage/GoogleDrive-hoangminhvu423@gmail.com/Drive của tôi/CLAUDE_SKILLS_BACKUP"

# 1. Kéo nguồn chuẩn (tự clone nếu chưa có)
if [ ! -d "$REPO/.git" ]; then
  git clone --branch "$BRANCH" --single-branch "$URL" "$REPO"
else
  git -C "$REPO" pull --ff-only || echo "⚠️  Pull thất bại (offline? nhánh lệch?) — dùng bản đang có trên máy."
fi
[ -d "$SRC" ] || { echo "❌ Không thấy $SRC — dừng."; exit 1; }

# 2. Chép repo → cache máy (không xoá gì ở máy)
mkdir -p "$DEST"
for d in "$SRC"/*/; do
  cp -R "${d%/}" "$DEST/"
done
cp "$SRC/README.md" "$DEST/" 2>/dev/null || true
# Cảnh báo skill chỉ có ở máy (không có trên repo)
for d in "$DEST"/*/; do
  name="$(basename "$d")"
  [ -d "$SRC/$name" ] || echo "⚠️  Skill chỉ có ở máy, KHÔNG có trên repo: $name (đưa lên repo hoặc dọn)"
done

# 3. Backup MacBook (giữ 10 bản mới nhất)
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
ZIP="$BACKUP_DIR/skills-$STAMP.zip"
(cd "$REPO/.claude" && zip -rq "$ZIP" skills)
ls -t "$BACKUP_DIR"/skills-*.zip 2>/dev/null | tail -n +11 | while read -r f; do rm -f "$f"; done

# 4. Backup Google Drive (nếu Drive đang mount)
if [ -d "$(dirname "$DRIVE")" ]; then
  mkdir -p "$DRIVE"
  cp "$ZIP" "$DRIVE/"
  DRIVE_OK="OK ($DRIVE)"
else
  DRIVE_OK="BỎ QUA — Drive chưa mount"
fi

N="$(find "$SRC" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
echo "✅ Đồng bộ xong: $N skill từ repo → $DEST"
echo "   Backup MacBook: $ZIP"
echo "   Backup Drive:   $DRIVE_OK"
echo "   Nhắc: mở PHIÊN MỚI để Claude Code nạp lại danh sách skill."
