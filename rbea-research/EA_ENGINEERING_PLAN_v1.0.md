# RB_EA — PHƯƠNG ÁN KỸ THUẬT THÀNH PHẨM v1.0 (2026-07-24)
Quan hệ tài liệu: MASTER_SPEC v1.0 = **CÁI GÌ** (logic đóng băng, đã kiểm chứng R7a-g).
Tài liệu này = **LÀM THẾ NÀO** (kỹ nghệ: module, giao diện, rủi ro, debug, giám sát, lộ trình).
Nguyên tắc tối thượng: KHÔNG thêm/bớt logic giao dịch nào ngoài MASTER_SPEC — mọi thứ dưới đây
là VỎ KỸ NGHỆ quanh engine đã kiểm chứng. Vỏ không bao giờ được phép tạo tín hiệu.

═══════════════════════════════════════════════════════
## 1. KIẾN TRÚC MODULE (v0.4 — tách từ v0.3 monolith)
```
RB_EA.mq5
├── SignalEngine    — Donchian-20/zone-người, ATR(20), state machine RANGE/BREAK/NEUTRAL
│                     (thuần hàm: input nến đóng → output tín hiệu; KHÔNG gọi trade)
├── ZoneManager     — SEMI: đọc hline RB_HI/RB_LO + lệnh /arm | AUTO: rolling Donchian
├── RiskManager     — sizing fixed-$, 4 tầng breaker, clamp STOPS_LEVEL, kiểm spec symbol
├── OrderExecutor   — CTrade wrapper: retry 3 lần backoff, kiểm filling-mode, magic
├── StateStore      — GlobalVariable theo (magic,symbol): budget ngày, whipsaw, PERM-HALT,
│                     init_balance — sống sót restart/redeploy
├── Panel           — giao diện trên chart (mục 2)
├── Notifier        — Telegram: lệnh vào/ra, breaker, lỗi, tổng kết ngày
├── Logger          — file CSV sự kiện (mục 4) — nguồn đối chiếu với engine Python
└── Watchdog        — heartbeat + tự kiểm tra bất biến mỗi nến (mục 5)
```
Lý do tách: audit từng phần được (G3), test SignalEngine tách biệt so khớp Python engine từng-tín-hiệu.

## 2. GIAO DIỆN
### 2.1 Panel trên chart (góc trái-trên, vẽ bằng OBJ_RECTANGLE_LABEL + OBJ_LABEL)
```
┌ RB_EA v0.4  XAUUSD  [SEMI]  ● LIVE ────────┐
│ State: RANGE   Box: 4012.5 / 3981.0  ATR 5.8│
│ Budget hôm nay: R-BUY ✓  R-SELL ✗  BREAK ✓  │
│ DD: ngày −0.4% | tuần −1.1% | tổng −2.3%    │
│ Vị thế: SELL 0.12 lot  +0.6R  (còn 31/48 H4)│
│ Lệnh tuần: 2 | Forward avgR: +0.21 (n=17)   │
└─────────────────────────────────────────────┘
```
- Nền đổi màu theo trạng thái: xám NEUTRAL · xanh RANGE · cam BREAK · **ĐỎ nhấp nháy PERM-HALT**.
- SEMI: vẽ thêm 2 đường zone đang armed + nhãn "ARMED 14:32".
- KHÔNG có nút bấm trên chart (chống bấm nhầm trên VPS) — mọi can thiệp qua Telegram.
### 2.2 Bộ lệnh Telegram (chat-id whitelist 1 người, token per-account)
`/status` panel dạng text · `/arm <hi> <lo>` (SEMI) · `/disarm` · `/flat` đóng hết + NEUTRAL hết ngày ·
`/halt` bật PERM-HALT tay · `/resume` gỡ halt (2 bước: /resume rồi /confirm trong 60s) ·
`/report` tổng kết tuần (n lệnh, R, DD, khoảng cách breaker).
### 2.3 Input groups (MetaEditor) — đặt tên nhóm rõ:
`=== LOGIC (KHÔNG CHỈNH — đóng băng R7g) ===` các tham số engine, mặc định khớp spec;
`=== PROFILE ===` I_AutoZone, I_RangeEnabled; `=== RISK ===` I_RiskPct (0.15 mặc định), 3 ngưỡng breaker;
`=== VẬN HÀNH ===` token/chat Telegram, I_FridayFlat, giờ server offset; `=== DEBUG ===` I_LogLevel, I_TesterArrows.

## 3. RỦI RO (thực thi 4 tầng của MASTER_SPEC + rủi ro kỹ thuật)
### 3.1 Tài chính (recap spec — không đổi): per-trade 0.15-0.20% fixed-$ · daily −3% · weekly −8% ·
total −9% PERM-HALT persist. Sizing: `lot = risk$ / (SL_points × tickvalue)`, làm tròn XUỐNG lot-step,
nếu < min-lot → BỎ lệnh + log WARN (không bao giờ ép min-lot vượt risk).
### 3.2 Kỹ thuật (mới — vỏ phải đỡ được):
| Rủi ro | Phòng bị |
|---|---|
| Requote/slippage | market order deviation 30 points; retry 3 lần; log FILL giá thật vs giá tín hiệu |
| Filling mode sai | dò SYMBOL_FILLING_MODE lúc OnInit, chọn FOK/IOC đúng sàn (bài học skill audit) |
| Restart giữa lệnh | StateStore đọc lại từ GlobalVariable + quét POSITION theo magic lúc OnInit |
| Nến H4 lệch giờ server | mọi mốc ngày/tuần dùng GIỜ SERVER, log kèm cả UTC để đối chiếu |
| 2 instance giẫm nhau | magic riêng 20260723/20260724; GlobalVariable prefix theo magic |
| Spread giãn lúc tin | kiểm spread < 0.15×ATR trước khi vào; không thì bỏ + log SKIP_SPREAD |
| Lỗi liên tiếp | 3 ERR liền trong 1 nến → tự NEUTRAL + Telegram alert (không tự PERM-HALT) |

## 4. DEBUG — nguyên tắc "mọi quyết định tái lập được"
### 4.1 Log file: `RBEA_<magic>_<YYYYMM>.csv` trong MQL5/Files, mỗi dòng 1 sự kiện:
`ts_server,ts_utc,event,state,box_hi,box_lo,atr,close,dir,price,sl,tp,lot,ddD,ddW,ddT,note`
Event codes: SIG (tín hiệu) · ORD (gửi lệnh) · FILL · EXIT_SL/EXIT_TP/EXIT_TIME/EXIT_FLAT ·
BRK_D/BRK_W/BRK_T (breaker) · ARM/DISARM · SKIP_* (lý do bỏ lệnh) · WARN · ERR (kèm GetLastError).
Log đủ input tại thời điểm quyết định → tái lập offline 100%.
### 4.2 Đối chiếu chéo với Python (vũ khí chính — đã có sẵn engine):
script `verify_ea_log.py`: đọc log EA + data cùng kỳ → chạy fable-engine → so khớp TỪNG tín hiệu
(ts, dir, entry, sl, tp). Mọi lệch = bug hoặc khác biệt thực thi phải giải thích được. Chạy mỗi tuần demo.
### 4.3 Tester: I_TesterArrows vẽ mũi tên + comment tại mỗi SIG/FILL/EXIT; chạy visual 3 tháng (G2).
### 4.4 Bất biến (assert mỗi nến, vi phạm → ERR + NEUTRAL): ATR>0 · box_hi>box_lo · SL đúng phía ·
budget ∈ [0..3] · không position nào thiếu SL · |DD tính| khớp equity thật ±0.1%.

## 5. GIÁM SÁT (3 vòng, từ trong ra ngoài)
1. **Trong EA**: Watchdog ghi heartbeat GlobalVariable mỗi tick + Telegram tổng kết 1 tin/ngày 21:00
   server (equity, DD, n lệnh, state). Tin tức thời: FILL, EXIT, breaker, chuỗi ERR.
2. **Shadow đối chiếu (đã chạy sẵn)**: feed data-gold 4h/lần + shadow BTC đêm + xaut_shadow →
   routine so LỆNH EA (từ log Telegram/CSV) vs LỆNH shadow engine: trùng ≥90% là lành mạnh,
   lệch hệ thống = điều tra ngay. Đây là giám sát ĐỘC LẬP hạ tầng với VPS.
3. **Người (5'/tuần, checklist trong spec)**: equity vs initial · n lệnh tuần 2-3 · PERM-HALT flag ·
   VPS uptime · spot-check 1 lệnh vs backtest.
Sự cố VPS >4h: MT5 mobile kiểm vị thế — SL cứng luôn có, EA chết cũng không mất kiểm soát rủi ro.

## 6. LỘ TRÌNH & PHÂN CÔNG (nối vào gates G1-G5 của spec)
| Bước | Việc | Ai | DoD (định nghĩa xong) |
|---|---|---|---|
| P1 | G3-audit v0.3 (3 flag đã ghi trong header) | phiên Claude tươi + skill ea-code-audit | 0 finding đỏ |
| P2 | v0.4: tách module + Panel + Logger + Notifier + Watchdog (KHÔNG đổi logic) | Claude | diff logic = 0 vs v0.3; compile 0 warn |
| P3 | G1+G2: compile + tester visual 3 tháng, 2 profile | **Sếp** (MetaEditor) | không lệnh phi logic; arrows khớp log |
| P4 | verify_ea_log.py + so khớp tester-log vs Python engine | Claude | khớp ≥95% tín hiệu, lệch giải thích được |
| P5 | G4: demo VPS ≥4 tuần, ≥40 lệnh, giám sát 3 vòng chạy đủ | Sếp cắm, Claude trực log | tiêu chí spec mục 7 |
| P6 | G5 go/no-go → FTMO Swing 0.15/0.15 | Sếp quyết | so demo vs backtest đạt |
Thứ tự cứng: P1 → P2 (audit trước, đắp vỏ sau — không sơn nhà đang nứt móng).

## 7. ĐIỀU KHOẢN ĐÓNG BĂNG
Mọi thay đổi LOGIC sau tài liệu này phải đi qua: prereg mới + kiểm chứng 2 engine + cập nhật MASTER_SPEC
version mới. Vỏ kỹ nghệ (panel, log, notify) đổi tự do miễn diff-logic = 0. Cấm vĩnh viễn giữ nguyên
(DCA/grid/hedge/martingale, filter chưa kiểm chứng).
═══════════════════════════════════════════════════════
Soạn: team R&D QTQ 2026-07-24. Chờ Sếp duyệt phương án → khởi động P1 (audit) ở phiên tươi.
