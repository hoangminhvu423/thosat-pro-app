# REVIEW từ phiên CLOUD (giám khảo độc lập) — đọc TRƯỚC khi chạy sweep

> Người viết: phiên cloud (không dính tay vào code lab → vai audit độc lập).
> Bối cảnh: đã đọc `data/GHI-CHU.md`. 4 cảnh báo dưới đây phải xử lý TRƯỚC khi quét 145 triệu nến,
> kẻo chạy cả đêm trên giả định sai rồi phải làm lại. Sửa xong thì ghi lại cách xử ở cuối file này.

## 🔴 1. Múi giờ — CHỈ ảnh hưởng logic THEO GIỜ, không ảnh hưởng phần còn lại
> LÀM RÕ: cảnh báo này KHÔNG loại vàng/PA/SMC-cấu-trúc. Chỉ nhóm dùng **giờ trong ngày**
> (ICT killzone, Asian/London/NY session range) mới cần tz. Mọi thứ khác chạy bình thường ngay.

**Người dùng không biết tz (data tải mạng) — KHÔNG SAO, tự dò từ data:**
- **Dò tz tự động (làm bước này trước):**
  1. **Khe cuối tuần**: forex đóng ~17:00 New York (Fri), mở ~17:00 (Sun). Tìm khe ~48h → nến cuối
     trước khe cho biết offset server tz.
  2. **Profile biến động theo giờ**: `mean(|return|)` theo `hour-of-day` → 2 bướu (London mở, NY mở)
     ghim offset. Chéo với (1) → ra tz trong ±1h.
  - `xauusd` đã biết tz = **EST** (histdata) → dùng làm **mốc chuẩn** để hiệu chỉnh/kiểm bộ intraday.
- **Phân nhóm logic (gắn cột `phu_thuoc_gio=true/false` trong ledger):**
  - `false` — **CHẠY NGAY, không cần tz**: Price Action (pin/engulfing/BOS), SMC cấu trúc
    (order block, FVG, CHoCH), breakout, supply/demand theo swing, Elliott/Wyckoff heuristic.
  - `true` — **chạy SAU khi dò tz**: ICT killzone, session range, judas swing.
- **KHÔNG** trộn kết quả nhóm `phu_thuoc_gio=true` vào bảng xếp hạng chung nếu tz chưa dò xong.

## 🟢 Phạm vi test (chốt rõ để khỏi hiểu lầm)
- **Price Action: TEST ĐẦU TIÊN** (session-agnostic).
- **Vàng XAUUSD: CÓ test** (trong 18 mã) — và là mã biết tz sẵn.
- **BTC: chưa test vì CHƯA CÓ data BTC M1 trên máy** (xem GHI-CHU). Muốn test → tải data BTC M1 rồi thả vào `data/`.
- Chỉ **ICT theo giờ** là chờ bước dò tz (vài giây), không phải chờ người dùng.

## 🟠 2. So sánh chéo symbol phải CÙNG THỜI KỲ
- `eurusd`: chỉ 1,0 triệu nến (2023-09→nay). `chfjpy`: cụt ở 2023-09. → hai mã **gần như không trùng kỳ**.
- Vòng "kiểm sống sót trên symbol khác" (bước 3 NHIEM-VU) chỉ có nghĩa khi so **cùng regime/thời kỳ**.
  So một mã 2010–2015 với một mã 2023–2026 = so hai chế độ thị trường khác nhau → kết luận sai.
- **Xử lý:** khi validate chéo, chỉ ghép các mã có **khoảng thời gian giao nhau đủ dài**. eurusd (N nhỏ)
  luôn gắn cờ `N_thap=true`, KHÔNG để nó một mình xác nhận "sống sót".

## 🟡 3. Khe data + resample sạch
- xauusd thiếu **trọn 2012**; M1 mọi mã có khe (cuối tuần/lễ/mất tick).
- Resample M5/M15/H1/H4 xong **BỎ nến rỗng**, **CẤM fill-forward** (nến ma làm sai ATR, sai tín hiệu →
  một dạng look-ahead ngầm). Kiểm: sau resample, chênh lệch thời gian giữa 2 nến liền kề không vượt
  ngưỡng khung (vd H1 mà cách nhau >3h giữa tuần thì đó là khe → không nối tín hiệu xuyên khe).

## 🟡 4. Không có volume
- `GHI-CHU.md`: data **không có volume**. Mọi logic SMC/order-block/liquidity/Wyckoff phải là **bản
  KHÔNG dùng volume** (chỉ price action + cấu trúc). Nếu một logic cần volume → **bỏ**, ghi rõ lý do,
  đừng thay bằng tick-count giả.

## Nhắc lại nguyên tắc vàng
Đa số kết quả sẽ EV≈0 sau phí — **đó là dữ liệu, không phải thất bại.** Con nào đẹp → nghi look-ahead/
overfit trước tiên. Sweep 145 triệu nến rất tốn thời gian: **chạy 1 mã × 1 khung × vài logic để
sanity-check pipeline TRƯỚC**, rồi mới quét toàn bộ.

---
## Nhật ký xử lý (phiên Mac điền vào đây sau khi giải quyết)
- [ ] TZ: cách xử lý = ...
- [ ] Cùng thời kỳ khi validate chéo: ...
- [ ] Resample bỏ khe: ...
- [ ] Volume-agnostic: ...
