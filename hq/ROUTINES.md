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

## GOLD PROXY FEED — XAUT/PAXG mỗi 4h (dựng 2026-07-24, CHỜ KÍCH HOẠT)
- Vấn đề giải quyết: sandbox bị chặn API mọi sàn (OKX/Binance/Bybit/Gate đều HTTP 000) → không tự kéo
  data vàng được. Đường vòng: **GitHub Actions chạy trên hạ tầng GitHub — không bị chặn.**
- Kiến trúc: workflow cron mỗi 4h → `fetch_gold_30m.py` kéo nến 30m XAUT-USDT (OKX, dự phòng Gate.io)
  + PAXG-USDT (Binance mirror) → commit CSV vào nhánh **data-gold** (tách riêng, không bẩn nhánh code).
  Sandbox đọc lại qua raw.githubusercontent.com (host duy nhất đang thông).
- Files: `rbea-research/forward/fetch_gold_30m.py` (fetcher, chỉ nến đã đóng, dedupe, backfill ~40 ngày
  lần đầu) · `rbea-research/forward/gold-data.yml` (bản staging của workflow) ·
  `rbea-research/forward/xaut_shadow.py` (shadow engine đóng băng R7g, log riêng, GOLIVE 2026-07-24).
- **KÍCH HOẠT (cần Sếp duyệt 1 lần):** copy `gold-data.yml` vào `.github/workflows/gold-data.yml` trên
  nhánh **main** (luật GitHub: schedule chỉ chạy từ default branch). Sau đó bấm Run workflow lần đầu
  trên tab Actions (hoặc chờ mốc 4h kế tiếp).
- **RANH GIỚI (LESSON-04):** XAUT/PAXG là vàng token-hóa 24/7 ≠ XAUUSD CFD (weekend, spread, thanh khoản).
  Log XAUT chỉ là PROXY THAM CHIẾU ĐỘC LẬP với MT5; KHÔNG dùng làm bằng chứng gate G4. Việc đầu tiên khi
  Sếp export MT5 lần tới: đo tracking-error XAUT vs XAUUSD đoạn trùng để định giá trị proxy.
