# Skills dùng chung — LUẬT ĐỒNG BỘ (chi tiết: hq/CLAUDE.md)

- **NGUỒN CHUẨN DUY NHẤT**: thư mục này (`.claude/skills/`), nhánh `claude/du-an-air-drop-y3ifan`,
  repo `hoangminhvu423/thosat-pro-app` trên GitHub.
- **CACHE máy MacBook**: `~/.claude/skills/` — mọi cửa sổ / phiên / dự án Claude Code cùng đọc
  (đây là cơ chế chia sẻ skill giữa các phiên).
- **BACKUP**: `~/.claude/backups/skills/*.zip` (MacBook) + Google Drive account hoangminhvu423
  `Drive của tôi/CLAUDE_SKILLS_BACKUP/`.
- **Sửa/thêm skill**: sửa TẠI ĐÂY → commit + push → chạy `dong-bo-skills/sync.sh`.
  CẤM sửa bản cache rồi bỏ quên repo. Lệch nhau: bản repo THẮNG.
- Skill mới chỉ được tính là "đã phát hành" khi: có frontmatter `name` + `description`,
  đã push lên nhánh chuẩn, và đã chạy sync.

## Danh sách hiện hành
| Skill | Mảng | Ghi chú |
|---|---|---|
| ea-code-audit | Quant/MQL5 | Checklist lỗi âm thầm trước deploy EA |
| guardian-rules | Quant/VPS | Cổng an toàn VPS MT5 — KHÔNG NGOẠI LỆ |
| catalogue-audit | ThợSắt Pro | Audit công thức mẫu trước phát hành |
| phat-hanh | ThợSắt Pro | Quy trình phát hành PWA (3 bộ đếm version) |
| them-mau | ThợSắt Pro | Thêm/sửa mẫu catalogue (4 bước bắt buộc) |
| dong-bo-skills | Hạ tầng | Đồng bộ repo → cache máy → backup + Drive |

(Runbook thao tác VPS/HQ nằm ở `hq/skills/` — deploy-vps, don-dep, dong-phien.)
