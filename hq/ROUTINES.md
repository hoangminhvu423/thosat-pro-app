# ROUTINES — lịch tự động
## Janitor tuần (đã tạo 2026-07-23 qua create_trigger)
- Lịch: thứ Hai 02:00 UTC (= 09:00 VN). Phiên MỚI, model rẻ.
- Prompt: "Clone/pull repo thosat-pro-app nhánh claude/du-an-air-drop-y3ifan, đọc hq/skills/don-dep/SKILL.md và thực hiện đúng quy trình đó. Báo cáo ≤10 dòng."
- Quản lý: list_triggers / update_trigger / delete_trigger trong phiên cloud bất kỳ.

## BTC Shadow-Run đêm (tạo 2026-07-23)
- Lịch: hằng ngày 20:00 UTC (= 03:00 VN). Phiên MỚI.
- Việc: pull nhánh → curl data Bitstamp updates → python3 rbea-research/forward/shadow_btc.py → commit/push nếu log đổi.
- Mục đích: tích bằng chứng FORWARD cho sleeve BTC (đóng băng R7g) trước/song song demo G4. KHÔNG phải mining.

## XAU Shadow (bán tự động — tạo 2026-07-23)
- Data XAU KHÔNG có nguồn công khai đạt chuẩn (đã chứng minh R7d) → nguồn duy nhất = MT5 export của Sếp.
- Quy trình: mỗi ~2 tuần Sếp export XAUUSD M15/M30 (Ctrl+U → Bars) → đưa vào phiên bất kỳ →
  phiên chạy `python3 rbea-research/forward/xau_shadow.py <file>` → log tự append + push.
- Script có HOLE-GUARD: tự bỏ lệnh có đường đi xuyên lỗ hổng data (bài học artifact −13.5R).
