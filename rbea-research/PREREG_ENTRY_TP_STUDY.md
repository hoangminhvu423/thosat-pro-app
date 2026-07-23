# PREREGISTER — Entry-reference & TP study cho sleeve BREAK (RB_EA)
Ngày khóa: 2026-07-23 · Trạng thái: PREREGISTERED (khóa TRƯỚC khi thấy kết quả) · Chuẩn: RESEARCH_PROGRAM (cơ chế đi trước, phép đo đi sau)
Câu hỏi chủ: (Q-A) close có phải mốc tham chiếu tốt nhất để vào break? (Q-B) bộ lọc wick-structure/pinbar/engulfing có THẮNG close-break trần? (Q-C) TP fixed-2R có đang cắt cụt đuôi béo?

## 0. DỮ LIỆU & CHUẨN BỊ (cố định)
- Input: XAU OHLC intraday (M30 ưu tiên; H1 chấp nhận). Nếu M30 → resample H4; nếu H1 → resample H4.
- Timezone: giữ nguyên của nguồn, GHI RÕ; session-analysis chỉ dùng nếu khớp broker GMT+2/3 (nếu không, bỏ phần session).
- ATR = Wilder(20) trên H4 (khớp EA). Mọi R đo bằng bội ATR tại thời điểm vào.
- Nguồn data phải log: URL, số dòng, khoảng ngày, số gap > 1 phiên.

## 1. ĐỊNH NGHĨA BREAKOUT (baseline, cố định — khớp production H4PURE)
- Box = rolling 20-nến H4: bh=max(high[1..20]), bl=min(low[1..20]).
- Break UP xác nhận khi close[H4] > bh + 0.25×ATR; DOWN khi close < bl − 0.25×ATR. (spec L3)
- SL baseline = 1.0×ATR ngược hướng từ giá vào; đây là mẫu số R.
- 1 lệnh/hướng/lần break; gap ≥ 60' giữa 2 lệnh (khớp EA).

## 2. BIẾN ENTRY-REFERENCE (Q-A, Q-B) — so với baseline E0
- **E0 (baseline):** vào MARKET tại close nến xác nhận break (không trễ 4h — sửa luôn C4 để tách bạch).
- **E1:** STOP order tại extreme nến break (high nếu up), hết hạn sau 1 nến. (bắt continuation)
- **E2:** LIMIT retest tại mức box bị phá (bh cho up), hết hạn sau K∈{1,2,3} nến. (giá tốt hơn, có thể miss)
- **E3 (wick-structure):** sau khi break xác nhận, chờ N nến liên tiếp có **râu-đáy cao dần** (up) / **râu-đỉnh thấp dần** (down) rồi vào MARKET. Định nghĩa chính xác: với up, low[i] (râu dưới) thỏa min(low của nến i) > min(low nến i−1) cho N nến liên tiếp. N ∈ {1,2,3,4}.
- **E4:** vào chỉ khi nến xác nhận (hoặc nến kế) là **pinbar** (thân ≤ 33% range, râu thuận hướng ≥ 2× thân) HOẶC **engulfing** (thân nến phủ toàn thân nến trước) — tái dùng logic sleeve đã khai tử, NHƯNG làm bộ lọc TIMING trong ngữ cảnh break (không phải signal độc lập).
- **E5:** engulfing một CỤM (thân phủ tổng 2-3 nến trước). 

## 3. BIẾN TP (Q-C) — so với baseline T0
- **T0 (baseline):** fixed 2.0×ATR.
- **T1:** TRAVERSE (biên box đối diện).
- **T2:** trailing cấu trúc — dời SL về dưới đáy 3-nến gần nhất (chandelier hoá), không TP cứng.
- **T3:** partial — chốt ½ tại 2R, ½ còn lại trailing T2.
SL cố định 1×ATR cho mọi biến (để R so sánh được).

## 4. METRIC (mỗi cấu hình)
n · WR · avgR · PF · totR · **tail = % totR đến từ top 10% lệnh** (Q2) · maxDD(R) · worst-year(R) · avg entry-slippage vs E0.

## 5. OOS & CONTROL-RUN (chống overfit — bắt buộc)
- Split 3 đoạn: **2004–2012 (OOS-A)** / **2012–2022 (DEV)** / **2022–2025 (OOS-B)**. Chọn cấu hình trên DEV, xác nhận trên A và B.
- **Luật control-run (V02):** một biến chỉ được "GIỮ" nếu THẮNG baseline (E0/T0) về avgR **≥ +0.02R** VÀ worst-year không tệ hơn, trên **CẢ HAI** OOS-A và OOS-B. Chỉ thắng DEV = BÁC.
- **Multiple-testing:** grid = 6 entry × 4 N (cho E3) × 4 TP ≈ 80 ô → KHÔNG đọc ô tốt nhất là thật; chỉ ô sống cả 2 OOS mới tính. Ghi số ô test.

## 6. DỰ ĐOÁN FALSIFIABLE (khóa trước — của Claude, sẽ chấm đúng/sai)
- **P1:** E0 (close) > E-lấy-wick-làm-mốc; close-reference thắng touch/wick. → tin CAO.
- **P2:** E2 (retest-limit) cho entry-slippage tốt hơn nhưng **totR THẤP hơn E0** vì miss cú chạy thẳng (đuôi béo). → tin TB.
- **P3:** E3 có **điểm ngọt N=2**; N≥3 tụt (độ trễ ăn đuôi — chính bẫy confirmation-vs-lag). → tin TB.
- **P4:** E4/E5 (pinbar/engulfing) **KHÔNG thắng** baseline trên OOS (prior: sleeve đã chết). → tin TB-CAO.
- **P5 (quan trọng nhất):** **TP mới là đòn bẩy lớn** — T2 (trailing) hoặc T3 (partial) **THẮNG T0 (fixed-2R) về totR**, có thể ở WR/PF thấp hơn, vì bắt được đuôi béo (Q2). → tin TB-CAO.
- **P6:** Cải thiện lớn nhất đến từ **TP (bắt đuôi)**, không phải tinh chỉnh entry; entry refinement là bậc hai. → tin TB.

## 7. KẾT QUẢ (chạy 2026-07-23 trên XAU_30m_data.csv chuẩn — 243,821 M30 → 32,290 H4, 2004-06→2025-07)
LƯU Ý PHẠM VI: hệ test là **Donchian-20 breakout proxy** (không trend filter/session/state machine như production) → mức tuyệt đối
THẤP hơn PHASE1 (baseline gross +0.017..+0.059 vs production +0.078). Cái transferable là **THỨ HẠNG/CHIỀU HƯỚNG** entry-TP, KHÔNG phải mức.
Phí mô hình hóa PHẲNG 0.04R/lệnh (khớp mức PHASE1 mất ~0.03R khi lên $0.50).

### Bảng NET (phí 0.04R) — avgR theo đoạn:
```
config                OOS-A    DEV    OOS-B   nhận xét
E0/T0 close+2R        +0.019  -0.023  -0.013  baseline: NET ~hòa/ÂM sau phí
E1/T0 stop-vượt-đỉnh  -0.001  +0.116  +0.076  entry TỐT NHẤT (net dương DEV+OOS-B), ít lệnh hơn
E2/T0 retest-limit    -0.009  -0.042  +0.139  DEV chết -> retest không đáng tin
E3/T0 wick N=1        +0.016  -0.009  +0.080  biên
E3/T0 wick N=2        +0.033  +0.011  -0.064  fail OOS-B
E3/T0 wick N=3        -0.051  -0.048  -0.051  CHẾT (lag ăn hết)
E3/T0 wick N=4        -0.040  +0.055  -0.062  chết
E4    pinbar/engulf   -0.032  +0.076  -0.304  FAIL OOS-B nặng (WR sập 24%)
E5    engulf-cụm      -0.040  +0.027  -0.358  FAIL OOS-B nặng
E0/T2 trailing        -0.077  +0.110  -0.075  churn -> ÂM cả 2 OOS
E0/T3 partial         -0.046  +0.040  -0.058  ÂM cả 2 OOS
```
(T1/TRAVERSE loại: bug — traverse là TP sleeve RANGE, vô nghĩa với BREAK.)

### Chấm P1–P6:
- P1 (close > wick-mốc): KHÔNG test cô lập được (E3 dùng wick làm FILTER, không phải mốc vào) — bỏ ngỏ.
- P2 (retest tệ hơn): ĐÚNG — E2 DEV chết (-0.042 net).
- P3 (cơ chế N↑ = trễ↑ = tệ): **ĐÚNG cơ chế** (N≥3 âm mọi đoạn); nhưng "sweet spot N=2" SAI — N=2 fail OOS-B; N=1 nhất quán hơn mà chỉ biên.
- P4 (pinbar/engulf fail OOS): **ĐÚNG MẠNH** — OOS-B -0.30R, WR sập. Tái dùng sleeve chết KHÔNG cứu được kể cả làm filter trong ngữ cảnh.
- P5 (trailing/partial thắng fixed-2R): **SAI (net)** — gross thì T2/T3 thắng DEV to, nhưng SAU PHÍ chúng churn và ÂM cả 2 OOS. Fixed-2R robust hơn.
- P6 (TP là đòn bẩy lớn hơn entry): ĐÚNG về BIÊN ĐỘ (TP swing totR mạnh nhất) nhưng chiều net OOS là ÂM -> "lớn hơn" đúng, "tốt hơn" sai.

### KẾT LUẬN
- **Không biến nào sống control-run** (thắng baseline ≥+0.02R trên CẢ OOS-A và OOS-B). Refinement lấp lánh ở DEV đều chết OOS = đúng bài học overfit (S2).
- Ứng viên DUY NHẤT đáng test tiếp trên hệ PRODUCTION thật: **E1 (vào STOP khi giá vượt đỉnh/đáy nến break = xác nhận continuation)** — net dương DEV+OOS-B, chỉ đuối OOS-A (2004-12 uptrend sạch, lọc làm mất lệnh tốt).
- **Bỏ hẳn** hướng pinbar/engulfing (data nói không) và trailing/partial TP (churn net-âm).
- Meta: entry/TP tinkering KHÔNG phải nơi giấu edge bền — khớp kết luận cũ "auto là khung gấm mỏng". Edge bền phải đến từ chỗ khác (human-alpha / chọn regime / cơ chế xây vùng production).

### CAVEAT
Proxy ≠ production; phí phẳng; exit-sim trên H4 (không intraday path, giả định SL trước TP); 1 nguồn data; ~34 ô test. Phải chạy lại E1 trên chính logic RB_EA production để chốt.
