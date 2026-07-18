# REVIEW từ phiên CLOUD (giám khảo độc lập) — đọc TRƯỚC khi chạy sweep

> Người viết: phiên cloud (không dính tay vào code lab → vai audit độc lập).
> Bối cảnh: đã đọc `data/GHI-CHU.md`. 4 cảnh báo dưới đây phải xử lý TRƯỚC khi quét 145 triệu nến,
> kẻo chạy cả đêm trên giả định sai rồi phải làm lại. Sửa xong thì ghi lại cách xử ở cuối file này.

## 🔴 1. Múi giờ + phương pháp phụ thuộc phiên (RỦI RO VALIDITY LỚN NHẤT)
- `GHI-CHU.md` ghi: bộ intraday lõi **tz chưa rõ**; xauusd = **EST**. Không đồng nhất.
- **SMC/ICT sống bằng session** (London/NY killzone, Asian range, judas swing). Nếu tz sai/lệch →
  test ICT/SMC **vô hiệu**: method tốt vẫn ra xấu, hoặc rác lại ra đẹp (false positive nguy hiểm hơn).
- **Xử lý bắt buộc (chọn một):**
  - (a) Xác nhận tz thật của bộ intraday trước (hỏi người dùng / kiểm bằng giờ mở-đóng phiên).
  - (b) Nếu chưa chắc tz → **CHỈ chạy các logic session-agnostic** (PA thuần nến, breakout cấu trúc,
    supply/demand theo swing). **Hoãn** mọi logic dùng giờ phiên (ICT killzone) tới khi tz xác nhận.
  - (c) Gắn cột `phu_thuoc_session=true/false` trong ledger để tách nhóm khi đọc kết quả.
- **KHÔNG** trộn kết quả session-based với tz chưa xác nhận vào bảng xếp hạng chung.

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
