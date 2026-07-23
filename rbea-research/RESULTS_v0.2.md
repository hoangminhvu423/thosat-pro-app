> ⚠️ **ĐÍNH CHÍNH 2026-07-23:** kết luận trong file này đã bị SỬA sau cross-validation Fable-B.
> Đọc **CROSSVAL_CORRECTION_20260723.md** — N-shape = regime-dependent (không phải all-OOS robust); E1 = KHÔNG cải thiện (đã gỡ khỏi EA, v0.21 dùng market-ngay-tại-xác-nhận).

# KẾT QUẢ hoàn thiện logic → v0.2 (2026-07-23, data chuẩn XAU_30m 2004-2025)

## 1. TRUNG THỰC TRƯỚC: replica full-system KHÔNG tái tạo PHASE1
- Replica baseline filterOFF (gross): avgR −0.026, WR 22.9% — KHÁC PHASE1 (+0.078, WR 31.4%).
- Nguyên nhân: RANGE sleeve mình code thô (vào tại close khi chạm, TP traverse, whipsaw xấp xỉ, one-position-jump).
- ⇒ KHÔNG dùng con số full-system làm bằng chứng. Chỉ dùng **A/B sleeve BREAK** (sạch — RANGE triệt tiêu).
- Việc phải làm để vào hồ sơ chính thức: chạy lại E1 trên **engine Fable-A/B** (engine ĐÃ tái tạo PHASE1), không phải replica này.

## 2. A/B SLEEVE BREAK (net phí 0.04R) — SẠCH, TIN CẬY
```
Break sleeve      OOS-A    DEV    OOS-B    ALL    PF     n(ALL)
v0.1 baseline    +0.006  -0.087  +0.151  -0.013  0.98    780
v0.2 E1          +0.087  +0.025  +0.134  +0.068  1.10    482
```
- E1 net-DƯƠNG cả 3 đoạn + toàn kỳ; baseline hòa-âm.
- E1 chọn lọc hơn (n 780→482): chỉ vào khi giá XÁC NHẬN continuation (phá tiếp đỉnh/đáy nến break).
- Khớp study proxy M30 trước (E1 cũng là biến duy nhất net+ cả 3 đoạn). HAI test độc lập đồng thuận.
- Sleeve BREAK là nguồn edge chính của hệ (framework I.A.2) → nâng entry BREAK = đúng đòn bẩy.

## 3. KẾT LUẬN — logic CHỐT cho v0.2 (chỉ proven)
GIỮ:
- **E1 continuation entry** cho BREAK: đặt STOP tại đỉnh/đáy nến break, chỉ vào khi phá tiếp. (vừa nâng edge vừa sửa C4)
- Trend filter default **OFF** (PHASE1).
- **Fixed-R TP** (2×ATR cho break) — trailing/partial ĐÃ BÁC (churn net-âm).
- RANGE sleeve giữ nguyên logic v0.1 (chưa có bằng chứng đổi).
VÁ (audit):
- **F1** time-stop 192h (48 nến H4) qua POSITION_TIME.
- **F4** clamp SL/TP ngoài STOPS_LEVEL; bỏ lệnh nếu quá sát.
- **F2** budget chỉ trừ khi lệnh THẬT vào (pending khớp), không trừ khi lot=0/không trigger.
- **C6** tùy chọn Friday-flat (đóng vị thế trước weekend).
- **C7** mốc reset tuần theo giờ server chuẩn (không lệch thứ 5 UTC).
BÁC (cấm vào auto): pinbar/engulfing, trailing/partial TP, retest-limit, wick-structure.
CHUYỂN TẦNG NGƯỜI: 2 setup wick của Sếp (hiếm+high-R) → journal R1 đo human-alpha.

## 4. Độ tin cậy tuyên bố
- "E1 nâng sleeve BREAK": TIN CẬY (A/B sạch, 2 test đồng thuận, net phí, OOS 3 đoạn).
- Mức tuyệt đối của cả hệ: CHƯA tin (replica RANGE lỗi) → phải chạy Fable engine.
- Code v0.2: viết xong, CHƯA compile/chưa audit Phase-4/chưa demo → BẮT BUỘC 3 bước đó trước tiền thật.
