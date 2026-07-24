---
name: rbea-devops
description: Vòng đời RB_EA nhanh — 1 lệnh đánh giá (rbea_ship), kéo data (rbea_pull_bars), monitor chủ động (rbea_watch). Dùng khi sửa/đánh giá/theo dõi RB_EA để KHỎI đụng terminal live + khỏi các bước loằng ngoằng.
---
# /rbea-devops — vòng đời RB_EA tốc độ cao (giảm rủi ro vận hành)

Tất cả chạy trên MacBook, headless, KHÔNG đụng terminal live (trừ MT5 tester cổng-cuối trước tiền thật).

## 1. Đánh giá 1 lệnh (Trụ 2) — sau mỗi lần sửa code/mẫu
```
python3 rbea-research/tools/rbea_ship.py            # dùng bar đã lưu
python3 rbea-research/tools/rbea_ship.py --pull     # kéo bar mới từ VPS rồi đánh giá
python3 rbea-research/tools/rbea_ship.py --balance 3900   # kiểm min-lot ở balance khác
```
Ra: backtest BREAK mỗi symbol (lệnh/PF/WR/DD/tần suất) · min-lot clearance mỗi mode · R7h MC (CAGR/DD
mỗi mode) · VERDICT PASS/FAIL. Mốc chuẩn hiện tại: PERSONAL 0.85% → ~+15,5%/năm DD15% (PASS).
→ Vòng "sửa→đánh giá" ~1 phút thay vì đóng/mở terminal nhiều lượt.

## 2. Compile G1 (không đụng live)
`cd ~/Downloads/VPS_LIVE_EA && python3 quant_lab/safe_compile.py "QTQ_MultiTF_DEMO/RB_EA_vX.mq5"`
(MetaEditor riêng, không phải terminal — an toàn).

## 3. Monitor chủ động (Trụ 3, read-only) — bắt lỗi âm thầm SỚM
```
python3 rbea-research/tools/rbea_watch.py
```
Tự chạy mỗi 30' qua launchd `com.qtq.rbea-watch` → log `~/Library/Logs/qtq_rbea_watch.log`.
Cảnh báo: EA rụng · algo đổi · không trade >21 ngày (nghi detach/min-lot/halt) · DD tới ngưỡng ·
perm_halt=1 sót trong Common. **Telegram**: đặt `~/.config/rbea_tg.txt` (dòng1 token, dòng2 chat_id
— Sếp tự tạo, agent không chạm) → cảnh báo tự đẩy Telegram; không có file = chỉ log.

## 4. Deploy live (vẫn giữ 1 CLICK tay — cổng an toàn cuối, Sếp chọn)
Sau khi ship PASS + MT5 tester sạch: profile RBEA5 (mode nạp sẵn) → Sếp File→Profiles→RBEA5 → bật Algo.
(Auto hot-restart CHƯA bật — cần Sếp duyệt cơ chế restart-2-lớp; xem DEVOPS_PROPOSAL.)

## Nguyên tắc parity
rbea_ship là engine python xấp xỉ (bar-close) để SÀNG nhanh + so tương đối. MT5 tester vẫn là
authoritative trước khi cho tiền thật. Bar data: rbea-research/data/bars_*_H4.csv (kéo lại bằng --pull).
