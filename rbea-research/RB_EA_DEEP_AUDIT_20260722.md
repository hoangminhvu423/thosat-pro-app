# RB_EA — BÁO CÁO KIỂM CHỨNG ĐỐI KHÁNG CHUYÊN SÂU (độc lập)
Ngày: 2026-07-22 · Phạm vi: RB_EA v0.1 + toàn bộ log 21-22/07 (12 file) · Vai: kiểm toán độc lập (Claude Code)
Chuẩn: AUDIT_GOVERNANCE R1-R7 (finding phải có bằng chứng + kịch bản hỏng cụ thể). Đây là TIỀN THẬT.

---

## 0. KẾT LUẬN ĐIỀU HÀNH — **NO-GO tiền thật (chưa)**; GO cho DEMO sau khi vá 4 lỗi chặn

Dự án làm rất bài bản (2 engine độc lập, preregister, control-run V02, LESSON-04). Edge backtest **có thật về mặt thống kê điểm** nhưng nhỏ và còn 4 lỗi chặn + 1 lỗ hổng khái niệm lớn phải xử lý trước khi tin con số +0.099R.

**Xếp hạng việc phải làm trước khi lên VPS demo:**
1. 🔴 **C1** — EA v0.1 chạy chế độ NGƯỜI-VẼ-VÙNG, nhưng backtest 21y đo chế độ ROLLING-BOX tự động. Theo chính LESSON-04 của bạn, edge KHÔNG chuyển giữa 2 cơ chế xây vùng. ⇒ **+0.099R KHÔNG đại diện cho cái EA sắp chạy.**
2. 🔴 **C2 (F1)** — time-stop 48 nến không được implement → live lệch backtest.
3. 🔴 **C3 (F4)** — không kiểm STOPS_LEVEL/spread → lệnh bị broker từ chối trên live.
4. 🟠 **C4** — lệnh BREAK vào trễ tới 4h tại giá thị trường; cần xác nhận backtest mô hình đúng độ trễ này.
5. 🟠 **C5 (F2)** — budget bị trừ cả khi lệnh không vào (đúng cả RANGE lẫn BREAK, không chỉ BREAK).

**Điểm son:** kiến trúc an toàn (Lyapunov fixed-fractional + 2 breaker + budget + cấm DCA/grid) là **vững** — rủi ro cháy tài khoản do *cơ chế* gần như bằng 0; rủi ro thật nằm ở (i) lệch backtest, (ii) edge thực chưa đo, (iii) gap/override.

---

## 1. AUDIT CODE MQL5 (live ≠ backtest & an toàn)

### 🔴 C2 / F1 — Time-stop 48 nến KHÔNG được thực thi *(đã xác nhận)*
- **Bằng chứng:** `I_MaxHoldBars=48` khai báo ở dòng 37, nhưng **không có** đoạn nào trong `OnNewH4()`/`OnTick()` đếm số nến giữ lệnh hay đóng theo thời gian. Grep toàn file: biến chỉ xuất hiện 1 lần (khai báo).
- **Kịch bản hỏng:** backtest có ~4.6% lệnh thoát kiểu TIME (48 nến). Live: lệnh RANGE không chạm SL/TP sẽ treo vô thời hạn (chỉ bị dọn bởi Friday cleanup — mà cleanup KHÔNG đóng lệnh, chỉ disarm). ⇒ phân phối kết quả live khác backtest, expectancy đã validate bị sai.
- **Fix (đúng như V02 chốt):** implement đóng lệnh khi `(TimeCurrent()-POSITION_TIME) >= 48*PeriodSeconds(PERIOD_H4)` = 192h. Dùng `POSITION_TIME` để bền qua restart, KHÔNG phải 48 giờ.

### 🔴 C3 / F4 — Không kiểm STOPS_LEVEL / spread trước khi đặt SL/TP
- **Bằng chứng:** `MarketIn()` (dòng 239-250) và nhánh BREAK (dòng 327-329) đặt SL/TP thẳng, không so với `SYMBOL_TRADE_STOPS_LEVEL`/`SYMBOL_TRADE_FREEZE_LEVEL`. RANGE chỉ chặn RR bằng `sl-c1>0.05*atr` (dòng 352) — không phải chặn khoảng cách tối thiểu của broker.
- **Kịch bản hỏng:** vùng hẹp / ATR nhỏ / spread giãn (tin, phiên Á) → SL hoặc TP nằm trong stops-level → `Buy/Sell` trả về lỗi `TRADE_RETCODE_INVALID_STOPS`, lệnh KHÔNG vào. Backtest (spread lý tưởng) vẫn vào. ⇒ live bỏ lệnh mà backtest có, lệch mạnh và âm thầm.
- **Fix:** trước khi đặt, kẹp SL/TP ra ngoài `stops_level*point`; nếu vùng hẹp hơn stops-level thì bỏ lệnh + log.

### 🟠 C4 — Lệnh BREAK vào trễ 1 nến (≤4h) tại giá thị trường
- **Bằng chứng:** nến N xác nhận break → set `g_pend_break_dir` (dòng 342) rồi `return`; nến N+1 mới khớp `MarketIn` tại ASK/BID hiện tại với SL/TP tính từ `px` + ATR mới (dòng 325-330).
- **Kịch bản hỏng:** breakout XAU nhanh → sau 4h giá đã chạy xa; vào tại giá mới, SL/TP dời theo → R thực khác R backtest. Nếu backtest vào tại close nến break (không trễ) thì đây là **lệch hệ thống**, đặc biệt trên sleeve BREAK — mà chính sleeve BREAK là **nguồn edge chính** (+0.084..+0.146 gross). Lệch ở đúng chỗ tạo tiền.
- **Cần làm:** đối chiếu backtest engine — nếu backtest KHÔNG mô hình độ trễ 1 nến này thì con số của sleeve BREAK bị thổi. Fix: hoặc vào ngay tại nến xác nhận (như backtest), hoặc thêm độ trễ 1 nến vào backtest cho khớp.

### 🟠 C5 / F2 — Budget bị trừ cả khi lệnh không vào (cả RANGE lẫn BREAK)
- **Bằng chứng:** BREAK: `MarketIn(d,...); g_bud_bk--;` (dòng 329) — trừ vô điều kiện. RANGE_SELL: `MarketIn(-1,...); g_bud_rs--;` (dòng 353); RANGE_BUY dòng 360 tương tự. `MarketIn`→`CalcLot` trả 0 (lot<min) hoặc lệnh fail thì hàm return sớm **nhưng budget vẫn đã bị trừ**. Dự án chỉ nêu BREAK — **thực ra cả 3 đều dính**.
- **Kịch bản hỏng:** tài khoản nhỏ / vùng rộng → lot<min → lệnh bỏ nhưng budget về 0 → cả ngày không vào lệnh dù có setup hợp lệ. Live ít lệnh hơn backtest.
- **Fix:** chỉ `g_bud_*--` khi `MarketIn` trả true (đổi `MarketIn` thành trả bool).

### 🟠 C6 — Vị thế giữ qua cuối tuần với SL (gap risk); Friday cleanup không đóng lệnh
- **Bằng chứng:** `OnTick` Friday cleanup (dòng 278-284) chỉ `disarm + CancelAllPending`, **không** `CloseAllOurs`. Chỉ `/flat` mới đóng.
- **Kịch bản:** lệnh mở tối thứ 6 → gap Chủ nhật vượt SL → lỗ > R dự kiến. Framework II.C tự nhận đây là 1 trong 3 cửa phá vỡ ổn định.
- **Fix:** tùy chọn `I_FridayFlat` đóng hết vị thế trước weekend, hoặc chấp nhận có chủ đích và ghi rõ trong Guardian Rules.

### 🟡 C7 — Mốc reset TUẦN lệch chuẩn broker/FTMO
- **Bằng chứng:** `wk=(TimeCurrent()+3*86400)/(7*86400)` (dòng 294) → ranh giới tuần rơi vào thứ 5 UTC (epoch 1970-01-01 là thứ 5). Weekly DD breaker & `g_week_eq0` reset lệch tuần giao dịch (CN mở/T6 đóng) và lệch tuần FTMO.
- **Fix:** neo tuần theo Chủ nhật/thứ Hai giờ server cho khớp chuẩn prop-firm.

### 🟡 C8 — WebRequest đồng bộ trong OnTimer chặn luồng EA
- **Bằng chứng:** `TGPoll()` (OnTimer mỗi 5s) và `TG()` gọi `WebRequest(...,3000,...)` đồng bộ. Telegram chậm → chặn tới 3s.
- **Kịch bản:** MT5 chạy OnTick/OnTimer đơn luồng; nếu poll treo đúng lúc cần xử lý exit → trễ. Nhẹ (H4, ít nhạy) nhưng nên biết. Lưu ý: WebRequest không chạy trong Strategy Tester → toàn bộ Telegram CHƯA backtest.
- **Fix:** giảm tần suất poll, hoặc bọc timeout ngắn + bỏ qua khi lỗi (đã có `!=200 return`, ổn).

### 🟢 Điểm ĐÚNG (đã kiểm, không phải lỗi — công nhận)
- **Không repaint:** chỉ đọc `iClose/iHigh/iLow` index 1 (nến đã đóng) và hành động 1 lần/nến (dòng 311-314). Chuẩn.
- **Handle indicator cache** trong OnInit + IndicatorRelease (dòng 258-259, 270-271). Chuẩn.
- **Min-lot KHÔNG ép:** lot<min thì bỏ lệnh, không over-risk (dòng 233-236). Chuẩn (nhưng dính C5).
- **AutoFill** theo SYMBOL_FILLING_MODE, không hardcode FOK (dòng 100-105) — đúng bài học SC6.
- **Close retry+verify** 3 lần (dòng 107-118). Chuẩn.
- **F3 (parse JSON thô):** thật nhưng LOW — chỉ ảnh hưởng lệnh Telegram lỗi, không phá giao dịch. Chấp nhận v0.1.

---

## 2. LỖ HỔNG KHÁI NIỆM LỚN NHẤT

### 🔴 C1 — Cái được backtest KHÁC cái sắp chạy live
- EA v0.1 lấy vùng từ **2 hline người vẽ** (`ReadZone`, dòng 179-191). **Không có** code rolling-box trong EA.
- Backtest 21y (PHASE1) chạy nhánh production **H4PURE = rolling 20-nến H4 tự động** (V02 nói rõ: "Production dùng vùng ROLLING 20-nến H4").
- **V02_CONTROL_RUN đã tự chứng minh:** cùng chiến lược, đổi cơ chế xây vùng → finding đảo dấu (gio London: study −0.23 vs production +0.51). LESSON-04: *finding là thuộc tính của (thị trường × payoff × CƠ CHẾ XÂY VÙNG)*.
- **Hệ quả:** +0.099R là của **full-auto rolling-box**, KHÔNG phải của **semi-auto người-vẽ** mà EA v0.1 hiện thực. **Edge thực của EA sắp demo là CHƯA ĐO.**
- **Khuyến nghị:**
  1. Coi demo là **PHÉP ĐO ĐẦU TIÊN** của edge semi-auto, KHÔNG phải "xác nhận" backtest. Đừng vào tiền thật dựa trên +0.099R.
  2. Nếu muốn dùng con số 21y: thêm **chế độ AUTO rolling-box vào chính EA** (đúng logic đã backtest) để demo song song, đo human-alpha = hiệu PnL người-vs-auto (đúng thiết kế T1+T2+T3 của bạn). EA v0.1 hiện KHÔNG chạy được "demo song song 2 chế độ" như framework nói vì thiếu mode auto.

---

## 3. THỐNG KÊ

### 🟠 S1 — Chưa có khoảng tin cậy; edge nhỏ trên mẫu mỏng ở regime mới
- avgR +0.078..+0.099R, WR 31-35%. Q1 (bootstrap CI) mới là **DỰ ĐOÁN**, chưa chạy. Claim "có edge" đang dựa vào ước lượng điểm.
- OOS 2022-2025 (regime bull, đang chạy): filterON tụt còn **+0.039R PF1.06, n=134** — chính dự án cảnh báo "chưa phân biệt hòa vốn". Đúng mức. ⇒ đừng bật filterON mặc định cho regime hiện tại.
- **Làm trước GO:** chạy Q1 (CI 95% của avgR) + Q3 (Monte Carlo maxDD/khả năng chạm breaker). Nếu P(edge≤0) > 10% → hạ kỳ vọng xuống "khung gấm thuần".

### 🟠 S2 — Chọn best-of-12 → rủi ro overfit
- FABLE_A là ma trận 12 nhánh (H4PURE/H4M15 × TRAV/MID/R2 × ON/OFF); chọn H4PURE/TRAV. Có giảm thiểu bằng OOS 2 đầu, nhưng nhánh thắng lại tụt ở OOS gần nhất (S1). Giữ cảnh giác; đừng tinh chỉnh thêm tham số.

### 🟡 S3 — Chi phí & data một nguồn
- Phí $0.35→$0.50 chưa gồm slippage của lệnh BREAK trễ 4h (C4) và spread giãn giờ tin. Nên stress thêm với slippage thực tế.
- 2 engine cross-validate **logic**, nhưng CÙNG 1 file CSV → lỗi data (tick xấu, gap, giờ broker) chưa được kiểm chéo. Nên đối chiếu 1 nguồn data thứ 2 (HuggingFace/Kaggle đã tìm ra).

---

## 4. NỀN TẢNG LYAPUNOV & LOGIC

### 🟢 L1 — Chứng minh ổn định: ĐÚNG về chất
Fixed-fractional → V_t=f hằng số → chuỗi thua giảm theo (1-f)^k (hội tụ); martingale phân kỳ theo d^k. Lập luận vững, khớp thực tế QTQ (DD 110% = điểm k*). **Giả định ẩn cần ghi rõ:** "không bao giờ âm vốn" giả định SL LUÔN khớp (không gap) và không đòn bẩy dồn — tức C6 (gap) là ngoại lệ thật của định lý. Nên phát biểu là "ổn định *có điều kiện: SL fill được*".

### 🟠 L2 — Value prop "semi-auto là sản phẩm chính" dựa trên human-alpha CHƯA ĐO
- Framework III: semi-auto = sàn máy + **human-alpha (chưa đo)** + thuế-sợ-hãi (prior RRR 4.82 vs 1.95 **từ dự án QTQ CŨ**, chưa đo cho RB_EA).
- ⇒ Giá trị cốt lõi của sản phẩm chính hiện là **giả thuyết**. Kết hợp với C1 (edge semi-auto chưa đo), đây là **rủi ro chiến lược #1**: đang xây niềm tin trên số chưa thuộc về hệ này.
- **Làm:** journal R1 (mỗi lần ARM) ≥ 50 vùng trên demo để đo human-alpha TRƯỚC khi coi semi-auto hơn full-auto.

### 🟢 L3 — Tầng T3 = đúng câu trả lời cho "chỉ báo/bộ công cụ hybrid chưa ưng ý"
- Đây chính là thứ bạn hỏi ở đầu phiên. Thiết kế **advisory-only** (hiển thị lúc /arm: lambda_24h, phiên, số lần chạm, lịch tin — người quyết) là **ĐÚNG HƯỚNG**, vì dữ liệu dự án cho thấy **máy tự bắn tín hiệu entry chết** (EDGE_V4_SIGNAL bị bác 4/4; MC-003 0/3). Chỉ báo phải TRỢ LỰC người, không quyết thay.
- **Vì sao "chưa ưng ý":** vì T3 là tầng **duy nhất chưa có cơ sở số liệu** — không phải lỗi thiết kế, mà là chưa đo. Không thể "ưng" một tầng chưa có dữ liệu forward.
- **Cách làm cho ưng:** (1) code T3 chỉ là panel hiển thị lúc /arm (không đặt lệnh); (2) journal schema R1 ghi mọi lần ARM + nhãn người; (3) sau ≥50 ARM, đo human-alpha; (4) chỉ khi human-alpha > 0 có ý nghĩa thì T3 mới "được ưng". Kỳ vọng advisory hữu ích nhất từ dữ liệu hiện có: **lambda_24h trung tính [-0.3..+0.2]** cho range-touch (MC-003, OOS +0.218R) và **spread trung-tính-vs-khuếch-đại 0.21R** (quan sát được TRƯỚC khi vào — giá trị thực cho người).

---

## 5. QUẢN TRỊ & QUY TRÌNH

### 🟢 G1 — Quy trình mạnh (công nhận)
Preregister → control-run → 2 engine độc lập; kill-gate theo số chạy lại được; đã tự khai tử V3/V4-signal. Đây là kỷ luật tốt hơn 95% dự án EA cá nhân.

### 🟠 G2 — Rủi ro sai đồng thuận (correlated error)
Mọi tài liệu do cùng chuỗi agent (Fable-A/B) sinh trên **cùng data & cùng spec**. "2 engine độc lập" vẫn ăn chung 1 CSV và chung 1 spec do 1 người chốt. Điểm mù: nếu spec sai giả định (vd C1 — cơ chế vùng), cả 2 engine cùng sai. **Kiểm toán con người ngoài luồng (chính bạn) + data nguồn 2 là liều giải.**

### 🟡 G3 — MC-003: thay giả thuyết bị bác bằng diễn giải hậu nghiệm
0/3 dự đoán đúng → cơ chế cũ SAI, thay bằng "vị trí × độ sâu thanh khoản" (interpretive, chưa prereg). Bạn đã gắn nhãn TESTED + xếp R7b để prereg vòng sau — **đúng quy trình**, nhưng nhắc: đừng đưa diễn giải này vào EA trước khi prereg-test. Lesson-04 đã "cắn" 2 lần trong 1 ngày.

### 🟡 G4 — Gate không được bỏ qua
Thứ tự v0.2 (fix F1/F2 **+ C3/C4 trong báo cáo này**) → audit instance tươi → demo ≥4 tuần/≥40 lệnh → go/no-go. **Đừng rút gọn.** Bổ sung C1/C3/C4/C5 vào v0.2 trước khi compile.

---

## 6. CHECKLIST TRƯỚC DEMO (gộp, theo ưu tiên)

- [ ] **C1** Quyết: (a) coi demo là phép đo đầu tiên của semi-auto (không dùng +0.099R làm bảo chứng), HOẶC (b) thêm mode AUTO rolling-box vào EA để chạy song song đo human-alpha.
- [ ] **C2/F1** Implement time-stop 192h (48 nến H4) bằng POSITION_TIME.
- [ ] **C3/F4** Kiểm & kẹp STOPS_LEVEL/FREEZE_LEVEL trước mọi SL/TP; bỏ lệnh nếu vùng < stops-level.
- [ ] **C4** Đối chiếu độ trễ 1 nến của lệnh BREAK với backtest; sửa cho khớp (ưu tiên vào tại nến xác nhận).
- [ ] **C5/F2** Chỉ trừ budget khi MarketIn thành công (cả RANGE lẫn BREAK).
- [ ] **C6** Quyết đóng-hết-trước-weekend hay chấp nhận gap (ghi Guardian Rules).
- [ ] **C7** Neo mốc reset tuần theo giờ server chuẩn prop-firm.
- [ ] **S1/S3** Chạy Q1 (CI) + Q3 (Monte Carlo) + stress slippage thực; đối chiếu data nguồn 2.
- [ ] **L2/L3** Code T3 advisory-only + journal R1; KHÔNG bật filterON mặc định ở regime bull hiện tại (để OFF theo PHASE1).
- [ ] **G4** Guardian Rules VPS; audit instance tươi sau khi vá; demo ≥4 tuần/≥40 lệnh trước go/no-go.

---

## 7. TÓM TẮT 1 DÒNG
Kiến trúc AN TOÀN vững; QUY TRÌNH tốt; nhưng **con số +0.099R chưa thuộc về cái EA sắp chạy (C1)** và còn **3 lỗi làm live≠backtest (F1/F4/BREAK-trễ)** — vá xong 4 cái này rồi coi demo là phép đo thật, chưa phải lúc tin edge để vào tiền lớn.
