#!/usr/bin/env bash
# Cài bộ khung agentic-engineering sang dự án khác hoặc vào ~/.claude (toàn máy).
# _Install this Claude Code kit into another repo, or into ~/.claude (global)._
#
# Dùng / Usage:
#   bash docs/claude-setup/install.sh <thư-mục-đích>   # copy .claude/ + CLAUDE.md vào repo khác
#   bash docs/claude-setup/install.sh --global          # copy .claude/* vào ~/.claude (áp dụng mọi dự án)
#
# Lưu ý: chạy từ GỐC repo này. Không ghi đè file đích đã có tên trùng mà chưa xác nhận.
set -euo pipefail

GOC="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "--global" ]; then
  DICH="${HOME}/.claude"
  echo "→ Cài toàn cục vào: ${DICH}"
  mkdir -p "${DICH}"
  cp -rn "${GOC}/.claude/." "${DICH}/"
  echo "✓ Đã copy .claude/* → ${DICH} (không ghi đè file trùng tên)."
  echo "  CLAUDE.md không copy vào ~/.claude tự động — nếu muốn memory toàn cục, tự copy: cp ${GOC}/CLAUDE.md ${DICH}/CLAUDE.md"
  exit 0
fi

DICH="${1:-}"
if [ -z "${DICH}" ]; then
  echo "Thiếu tham số. Xem hướng dẫn ở đầu file." >&2
  exit 1
fi
if [ ! -d "${DICH}" ]; then
  echo "Thư mục đích không tồn tại: ${DICH}" >&2
  exit 1
fi

echo "→ Cài vào repo: ${DICH}"
mkdir -p "${DICH}/.claude"
cp -rn "${GOC}/.claude/." "${DICH}/.claude/"
if [ ! -f "${DICH}/CLAUDE.md" ]; then
  cp "${GOC}/CLAUDE.md" "${DICH}/CLAUDE.md"
  echo "  ✓ Đã copy CLAUDE.md (đích chưa có)."
else
  echo "  ! ${DICH}/CLAUDE.md đã tồn tại — bỏ qua, tự gộp thủ công nếu cần."
fi
echo "✓ Xong. Nhớ chỉnh .claude/rules/ cho đúng loại dự án ở đích."
