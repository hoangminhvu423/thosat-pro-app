# ROUTINES — lịch tự động
## Janitor tuần (đã tạo 2026-07-23 qua create_trigger)
- Lịch: thứ Hai 02:00 UTC (= 09:00 VN). Phiên MỚI, model rẻ.
- Prompt: "Clone/pull repo thosat-pro-app nhánh claude/du-an-air-drop-y3ifan, đọc hq/skills/don-dep/SKILL.md và thực hiện đúng quy trình đó. Báo cáo ≤10 dòng."
- Quản lý: list_triggers / update_trigger / delete_trigger trong phiên cloud bất kỳ.

## BTC Shadow-Run đêm (tạo 2026-07-23)
- Lịch: hằng ngày 20:00 UTC (= 03:00 VN). Phiên MỚI.
- Việc: pull nhánh → curl data Bitstamp updates → python3 rbea-research/forward/shadow_btc.py → commit/push nếu log đổi.
- Mục đích: tích bằng chứng FORWARD cho sleeve BTC (đóng băng R7g) trước/song song demo G4. KHÔNG phải mining.
