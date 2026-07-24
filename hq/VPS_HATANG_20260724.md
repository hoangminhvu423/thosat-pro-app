# RÀ SOÁT HẠ TẦNG VPS 24/07/2026 — logic chồng lấn ảnh hưởng EA (Sếp duyệt "fix triệt để")

## TÓM TẮT: 39 scheduled task → 6 nguồn chồng lấn/bug tìm thấy → 5 đã fix, 1 chờ Sếp quyết.
Mọi thay đổi có backup tại VPS `C:\Temp\backup_hatang_20260724\` (XML task + script gốc) — đảo ngược được 100%.

## ĐÃ FIX (verify xong)
1. **MT5_Watchdog (5 phút/lần) — vá script** `C:\Users\Administrator\mt5_watchdog.ps1`:
   - Lỗi cũ: check `terminal64` BẤT KỲ → FTMO còn chạy thì Exness chết cũng không cứu (watchdog mù);
     ngược lại có thể tự dựng Exness dậy giữa lúc bảo trì (MT5 restore chart+EA+algo → EA sống lại ngoài ý muốn).
   - Vá: (a) check đúng terminal Exness theo Path; (b) **CỜ BẢO TRÌ**: tồn tại `C:\Temp\mt5_maintenance.flag`
     (tuổi <4h) → watchdog đứng im. Test: chạy tay rc=0, không nhân đôi terminal.
2. **QTQ_EA_Watchdog + QM_Watchdog — DISABLE**: script đích đã bị xoá từ trước → fail rc=0xFFFD mỗi 5 phút
   suốt từ 15/06 (rác + che khuất lỗi thật). 
3. **SyncNewsHalts — DISABLE**: script TQT legacy đã mất → fail rc=2 mỗi 5 phút.
4. **StartMT5Cent — DISABLE (MÌN)**: task parked 2099 nhưng payload là `/config:vps_startup.ini` =
   đăng nhập **demo cũ Trial6 #413885821 + [Experts] Enabled=1 (TỰ BẬT ALGO)**. Ai lỡ `/run` là terminal
   nhảy sang account khác với algo bật. Đã disable; file ini giữ nguyên làm chứng.
5. **3 file halt cũ `RBEA2_*_halt.bin`** (nguồn G2-FAIL sáng nay, v0.32 không dùng nữa) — dời vào backup
   (không xoá). MCC_OnBoot (script .vbs mất) cũng disable.

## KHÔNG ĐỤNG (chủ đích/đúng thiết kế)
- `QTQ_Watchdog_Deadman` (20'): read-only tuyệt đối, chỉ báo Telegram — chuẩn Guardian, GIỮ.
- `QTQ_PlanBot` + `Keeper`, `QuantMaster_DailyBackup`, `VPS_Performance_Tracker`, `CTA_Rebalance`,
  `CFO_Evolving_Optimizer`, `QTM_*` (weekly monitor): không đụng MT5 process/EA state.
- `qtq_trendsleeve_control.csv: halt=1` — TrendSleeve đã khai tử, halt là ĐÚNG.
- `EA_HALT.json` (halt=true 30/06, "WATCHDOG_INTEGRITY_VIOLATION"): chỉ tool python cũ đọc, KHÔNG EA nào
  đọc — vô hại với RB_EA, giữ làm chứng tích.
- Task một lần đã hết hạn (StartMT5/Now/v2, MT5_Restart_Now, StartPythonBridge, QTQ_Daemon/TelegramBot
  parked 2030): trơ, không lịch chạy — để nguyên.

## GIAO THỨC MỚI — CỜ BẢO TRÌ (bắt buộc từ nay khi đụng terminal Exness)
```
# Trước khi đóng terminal (deploy/test):
echo bao tri > C:\Temp\mt5_maintenance.flag
# Làm việc... (flag tự vô hiệu sau 4h nếu quên xoá)
# Xong, mở lại terminal rồi:
del C:\Temp\mt5_maintenance.flag
```

## CHỜ SẾP QUYẾT (không tự làm)
1. **Autologon sau reboot — LỖ HỔNG THẬT**: VPS không bật AutoAdminLogon → Windows Update/reboot xong,
   không ai login → MT5 không mở → **EA chết im lặng** (deadman sẽ báo Telegram, nhưng phải RDP mở tay).
   Phương án an toàn: tải Sysinternals Autologon (lưu password vào LSA secret, không plaintext registry)
   — cần Sếp duyệt tải tool + tự nhập password 1 lần qua RDP.
2. **Telegram bot cho RB_EA**: RB_EA poll `getUpdates`. Nếu dùng CHUNG token với plan_bot/HM → 2 consumer
   giành update (conflict 409/mất lệnh). Khi cắm live: tạo **bot riêng** cho RB_EA.
3. **Terminal FTMO**: vẫn Authorization failed + 0 EA — chạy rỗng tốn RAM; đóng hay sửa login tùy Sếp.
