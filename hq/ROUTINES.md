# ROUTINES — lịch tự động
## XAU M30 rolling 45 ngày → Drive INBOX_FINDINGS (tạo 2026-07-24)
- Lịch: hằng ngày 08:00 giờ Mac (launchd `com.qtq.xau-rolling45` — Mac ngủ thì chạy bù khi thức).
- Việc: `python3 rbea-research/forward/xau_m30_rolling45.py` — SSH VPS (password Keychain) →
  MT5 python attach terminal Exness (READ-ONLY copy_rates) → CSV chuẩn MT5
  `Date;Open;High;Low;Close;Volume` (datetime `2026.07.24 08:00`, digits theo symbol) →
  ghi đè nguyên tử CÙNG file `QTQ_FABLE_BRIDGE/INBOX_FINDINGS/XAU_M30_rolling45d.csv`.
- Chốt an toàn: CHỈ cửa sổ trượt 45 ngày (~85KB/1500 nến, không bao giờ full history);
  <500 nến = bất thường → giữ nguyên file cũ, không ghi đè. Log: `~/Library/Logs/qtq_xau_rolling45.log`.
- Chạy tay bất kỳ lúc nào (idempotent): lệnh python3 ở trên, hoặc kèm sau mỗi lần /dong-bo-skills.

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

## [PENDING] Gộp XAUT vào routine đêm (chặn bởi approval gate 2026-07-24)
- Trạng thái: feed data-gold ĐÃ CHẠY (workflow run #1 OK, 2000 nến XAUT + 1000 nến PAXG, 0 gap).
  Log backfill 13 lệnh đã push. Routine đêm hiện CHỈ chạy BTC.
- Việc cần làm (phiên có quyền MCP trigger): update_trigger trig_012ufpG48hzGLgcCTB82LLY3, thêm bước:
  curl https://raw.githubusercontent.com/hoangminhvu423/thosat-pro-app/data-gold/xaut_30m.csv
  → python3 rbea-research/forward/xaut_shadow.py <file> → commit/push nếu log đổi.
- Trong lúc chờ: chạy tay lệnh trên trong phiên bất kỳ (idempotent, không sợ trùng).
