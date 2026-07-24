# RUNBOOK cho Sếp — 3 việc chỉ tay người làm được (24/07/2026)

Agent KHÔNG tự làm 3 việc này vì đụng giới hạn cứng: **nhập mật khẩu**, **tạo bot Telegram**,
và **bấm hộp thoại GUI trên RDP**. Mỗi việc ≤3 phút.

## A. AUTOLOGON sau reboot (lỗ hổng: reboot → EA chết im lặng đến khi Sếp RDP)
Cách an toàn (mật khẩu mã hoá trong LSA, KHÔNG plaintext registry):
1. RDP vào VPS → tải Sysinternals Autologon:
   `https://download.sysinternals.com/files/AutoLogon.zip` (của Microsoft, tin cậy).
2. Giải nén → chạy `Autologon.exe` → nhập: Username=`Administrator`, Domain=(để trống hoặc tên máy),
   Password=`<mật khẩu VPS>` → Enable.
3. Xong: reboot thử 1 lần cuối giờ ít giao dịch → xác nhận Windows tự login + MT5 tự mở
   (nhờ task `StartMT5`/watchdog) + EA lên chart.
> LƯU Ý: KHÔNG set autologon bằng cách ghi DefaultPassword vào registry (lộ plaintext). Chỉ dùng tool trên.

## B. BOT TELEGRAM RIÊNG cho RB_EA (tránh giành getUpdates với plan_bot/HM)
1. Mở Telegram → chat `@BotFather` → `/newbot` → đặt tên (vd `RB_EA_ThoSat_bot`) → nhận **token**.
2. Nhắn 1 tin bất kỳ cho bot vừa tạo (để nó thấy chat_id).
3. Lấy chat_id: mở `https://api.telegram.org/bot<TOKEN>/getUpdates` → chép số trong `"chat":{"id":...}`.
4. Đưa token + chat_id cho agent (hoặc tự điền vào ô `I_TGToken`/`I_TGChatID` khi RB_EA đã gắn) —
   agent sẽ điền vào 2 chart RB_EA. **Đừng dùng chung token với bot đang chạy.**

## C. ĐÓNG TERMINAL FTMO (đang chạy rỗng: auth failed, 0 EA)
Agent thử đóng nhẹ nhưng MT5 treo ở hộp thoại "Are you sure you want to exit?" (chỉ tay người bấm).
- Trên RDP: click terminal FTMO (`C:\MT5_FTMO`) → File → Exit → OK.
- Hoặc để nguyên cũng được (không giữ tiền, chỉ tốn RAM). Nếu muốn dùng lại FTMO thì sửa login trước.

## D. GẮN RB_EA v0.32 — KHÔNG cần đóng terminal (dùng profile RBEA)
Agent đã tạo profile **RBEA** sẵn 2 chart v0.32 (XAUUSD SEMI magic 20260723 + BTCUSD AUTO magic
20260724), đủ 28 tham số, **I_InitBalance=3909**, Telegram trống. Sếp làm 3 bước:
1. **TẮT AlgoTrading trước** (bấm nút "Algo Trading" cho về xám/đỏ) — vì BTC AUTO sẽ vào lệnh THẬT
   ngay khi profile nạp nếu algo còn bật. (Đang ON tại 24/07 10:22.)
2. **File → Profiles → RBEA** (hoặc menu profile góc dưới) → 2 chart hiện ra, RB_EA v0.32 gắn sẵn đủ số.
3. Rà input (double-click EA → Inputs), điền Telegram (mục B) khi có bot. Bật Algo lại CHỈ KHI muốn
   chạy thật — và tốt nhất sau khi đã chạy nốt XAU SEMI visual (G2).
> Vì sao dùng profile thay vì đóng terminal: MT5 chỉ ghi đè profile ĐANG mở lúc thoát; profile RBEA
> là folder riêng nên nạp được ngay khi chuyển, không mất view hiện tại của Sếp.
