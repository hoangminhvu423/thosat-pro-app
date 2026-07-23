# ĐÍNH CHÍNH SAU CROSS-VALIDATION FABLE-B (2026-07-23) — GHI ĐÈ các claim trước đó
Trạng thái: CHÍNH THỨC. File này SỬA các kết luận trong NSHAPE_STUDY_RESULTS / NSHAPE_SWEEP_RESULTS / RESULTS_v0.2.
Quy trình: Fable-B (engine độc lập, viết từ SPEC, không xem code gốc) chạy trên cùng data chuẩn → KHÔNG hội tụ → truy nguyên → engine gốc CÓ BUG → lấy Fable-B làm chuẩn → chạy lại toàn bộ.

## 1. BUG ĐÃ TÌM RA (trong harness Claude-A, nshape_study.py cũ)
**Fill lạc quan / look-ahead sót:** với pattern mà mức trigger (H1) ĐÃ BỊ PHÁ trong 2 nến chưa-xác-nhận-pivot
(L1+1..L1+2), engine cũ vẫn vào lệnh TẠI GIÁ TRIGGER — mức giá không còn tồn tại. Fable-B xử lý đúng: SKIP
(646-1123 case tùy config, ~40-60% số pattern!). Bug này thổi phồng CẢ n LẪN avgR.

## 2. KẾT QUẢ ĐÚNG (engine chuẩn Fable-B, fill bảo thủ, net 0.04R)

### N-SHAPE — RÚT LẠI claim "edge mạnh all-OOS". Kết quả thật: REGIME-DEPENDENT
Sweep 36 cấu hình (IMP×k×retrace) trên engine chuẩn: **0/36 net+ cả 3 OOS** (trước đó báo 36/36 — artifact của bug).
Nhưng mẫu hình NHẤT QUÁN tuyệt đối trên cả 36 config:
- OOS-A (2004-12, trend): 36/36 DƯƠNG (+0.07..+0.47)
- DEV   (2012-22, chop):  36/36 ÂM   (−0.006..−0.21)
- OOS-B (2022-25, trend): 36/36 DƯƠNG (+0.13..+0.55)
→ N-shape KHÔNG phải edge vô điều kiện. Nó là **edge CÓ ĐIỀU KIỆN REGIME**: ăn ở thập kỷ trend, chết ở thập kỷ chop.
Giống hệt hồ sơ trend-filter PHASE1. Config đại diện (IMP1.5/k2/0.2-0.7, TP=MM): n=402, ALL +0.124R PF1.20;
DEV −0.047; OOS-B +0.473 PF2.0.

### E1 — RÚT LẠI claim "E1 nâng sleeve BREAK"
Fable-B: baseline ALL +0.022/PF1.03 vs E1 +0.008/PF1.01 (E1 chỉ nhỉnh ở DEV). → E1 KHÔNG cải thiện.
Con số "+0.068 all-OOS" trước đó đến từ replica có RANGE lỗi + so sánh không cùng điều kiện.
**Hành động: E1 pending-stop ĐÃ GỠ khỏi EA.** v0.21 quay về entry đúng spec: MARKET NGAY tại nến xác nhận
(fix C4 — v0.1 vào trễ 1 nến; PHASE1 backtest validate entry tại close xác nhận).

## 3. CÁI GÌ CÒN ĐỨNG VỮNG (không đổi)
- 5 bản vá audit trong v0.21: F1 time-stop 192h, F4 STOPS_LEVEL, F2 budget-khi-fill, C6 Friday-flat, C7 mốc tuần. (Bug code là bug code — không phụ thuộc backtest.)
- Các kết luận BÁC: trailing/partial TP, pinbar/engulfing, retest-limit, wick-structure, volume-filter — cả 2 engine đều không ủng hộ.
- PHASE1 (+0.078/+0.099) — của Fable-A/B gốc, không bị ảnh hưởng.
- 2 setup wick của Sếp → tầng NGƯỜI + journal R1 (không đổi).
- Cả 2 engine ĐỒNG Ý: N-shape dương toàn kỳ (+0.12 vs +0.29 — mức khác nhau nhưng cùng dấu) và RẤT mạnh ở regime hiện tại 2022-25 (+0.47..+0.55).

## 4. TRIỂN VỌNG MỚI (giả thuyết — CHƯA prereg, cấm code vào EA trước khi qua vòng đo)
**R7c (đề xuất prereg):** N-shape như sleeve CÓ CỔNG REGIME — chỉ bật khi thị trường trend (vd: |close−SMA200|>X×ATR
hoặc ADX/vol-regime). Dự đoán viết trước: gate đúng sẽ giữ ~+0.3..0.5R của regime trend và cắt phần âm DEV.
RỦI RO: gate chọn hậu nghiệm = data mining → phải prereg tiêu chí gate TRƯỚC, test trên Fable engine, control-run.

## 5. TRẠNG THÁI EA
RB_EA_v0.2.mq5 → **v0.21**: [C4-fix] market ngay tại xác nhận (E1 đã gỡ) + F1/F4/F2/C6/C7. CHƯA compile/audit/demo.

## 6. BÀI HỌC (thêm vào META_LESSONS đề xuất — LESSON-05)
Một engine tự viết + tự sweep = chưa là bằng chứng. 36/36 "robust" vẫn có thể là artifact của MỘT bug fill chung.
Cross-val độc lập từ SPEC là bắt buộc TRƯỚC khi tuyên bố edge — đúng thiết kế Fable-A/B của dự án. Quy tắc thao tác:
mọi backtest có stop/limit fill phải kiểm "mức giá còn tồn tại tại thời điểm lệnh được phép đặt".
