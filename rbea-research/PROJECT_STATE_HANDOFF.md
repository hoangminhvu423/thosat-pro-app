> ⚠️ **ĐÍNH CHÍNH 2026-07-23:** kết luận trong file này đã bị SỬA sau cross-validation Fable-B.
> Đọc **CROSSVAL_CORRECTION_20260723.md** — N-shape = regime-dependent (không phải all-OOS robust); E1 = KHÔNG cải thiện (đã gỡ khỏi EA, v0.21 dùng market-ngay-tại-xác-nhận).

# RB_EA — PROJECT STATE & HANDOFF (cho agent nối tiếp nếu gián đoạn/hết context)
Cập nhật: 2026-07-23 · Chủ dự án: Sep · Data chuẩn: XAU_30m_data.csv (243,821 M30, 2004-06→2025-07, delim ';', fmt Y.m.d H:M)

## 0. DỰ ÁN LÀ GÌ
RB_EA = EA MQL5 XAUUSD H4 BÁN TỰ ĐỘNG (người vẽ vùng, máy thi hành). State machine RANGE/BREAK/NEUTRAL,
budget 3 lệnh/ngày, DD breaker 3%/8%, Telegram 2 chiều, persist GlobalVariable. Chiến lược pass quỹ = tầng NGƯỜI;
giữ quỹ = tầng AUTO (Skinner: prop = option lồi, keep-vol thấp). Governance: preregister → control-run → Fable độc lập;
finding phải verify bằng số chạy lại; CHỐNG look-ahead & overfit; "reference ≠ apply".

## 1. ĐÃ CHỨNG MINH (net phí, data chuẩn, OOS 3 đoạn: 2004-12 / 2012-22 / 2022-25)
- **E1 continuation entry**: vào BREAK bằng STOP tại đỉnh/đáy nến break (không phải close/market-nến-sau).
  Sleeve BREAK: v0.1 baseline ALL −0.013/PF0.98 → E1 ALL +0.068/PF1.10, net+ cả 3 OOS. Đồng thời SỬA C4.
  Xác nhận 2 test độc lập (proxy M30 + replica production). TIN CẬY.
- **N-SHAPE** (impulse→pullback→continuation, SL cấu trúc tại higher-low): edge MẠNH NHẤT.
  net ALL +0.235 (2R) / +0.340 (5R) / +0.288 (MM), PF 1.39–1.51, net+ cả 3 OOS. Gấp 2–5× edge production.
  = phiên bản "đầy đủ" của E1 (thêm ngữ cảnh impulse+pullback). ỨNG VIÊN sleeve mới / thay BREAK. Ưu tiên cao.
- Trend filter default OFF (PHASE1 robust hơn; filterON tụt regime bull 2022-25).
- TP: MM(đo leg1)/5R > fixed-2R cho setup cấu trúc.

## 2. ĐÃ BÁC (test rồi, KHÔNG đưa vào auto)
- Trailing/partial TP: churn net-âm OOS sau phí.
- pinbar/engulfing (context-free & in-context): fail OOS-B nặng (WR sập).
- retest-limit entry: DEV chết.
- wick-structure N≥2: fail (lag ăn edge).
- "chạm nhiều → break mạnh hơn": SAI cho breakout (MIRROR: vỡ tươi 0-1 chạm tốt nhất; nhiều chạm=hấp thụ=yếu).
- Volume real/fake N (của trader TQ): KHÔNG xác nhận trên tick-volume (sau vá look-ahead, fake≥real). Caveat tick-vol.

## 3. LỖI AUDIT (đã vá trong RB_EA_v0.2.mq5)
C1 (EA=human-zone nhưng backtest=rolling-box → edge chưa đo đúng mode; DÙNG demo làm phép đo đầu) ·
C2/F1 time-stop 192h · C3/F4 STOPS_LEVEL clamp · C4 (E1 giải quyết) · C5/F2 budget-chỉ-trừ-khi-fill ·
C6 Friday-flat option · C7 mốc tuần Monday.

## 4. TRẠNG THÁI CODE
- RB_EA_v0.1.mq5 (gốc, trên Drive) — CHƯA vá.
- **RB_EA_v0.2.mq5** — đã vá E1+F1+F4+F2+C6+C7. CHƯA compile / CHƯA audit Phase-4 / CHƯA demo.
  Điểm cần audit: buy/sell-stop khi giá đã vượt trigger (v0.2 tạm BỎ lệnh — bảo thủ).

## 5. VIỆC TIẾP THEO (ưu tiên)
1. [CAO] Chạy lại **E1 + N-SHAPE trên engine Fable-A/B** (engine đã tái tạo PHASE1) — thay proxy, vào hồ sơ chính thức.
   Lý do: replica prod_engine.py của mình KHÔNG tái tạo PHASE1 (RANGE thô) → chỉ tin hiệu số A/B, chưa tin mức tuyệt đối.
2. [CAO] Prereg N-shape (IMP/retrace/k sensitivity) → nếu vững → thiết kế sleeve N hoặc thay BREAK trong v0.3.
3. compile v0.2 (MetaEditor) → ea-code-audit Phase-4 → demo VPS ≥4 tuần/≥40 lệnh (Guardian Rules).
4. Journal R1 (JOURNAL_R1_schema.md) đo human-alpha cho tầng người (2 setup wick của Sep) — mảnh chặn vế PASS.
5. Viết lại RANGE replica cho khớp PHASE1 (nếu muốn số cả-hệ tin cậy) HOẶC dùng thẳng Fable engine.

## 6. INVENTORY FILE (scratchpad + đã lưu Drive/GitHub)
Báo cáo: RB_EA_DEEP_AUDIT_20260722.md · PREREG_ENTRY_TP_STUDY.md · RESULTS_v0.2.md · NSHAPE_STUDY_RESULTS.md ·
  JOURNAL_R1_schema.md · PLAN_v0.2.md · PROJECT_STATE_HANDOFF.md (file này)
Code EA: RB_EA_v0.2.mq5
Harness (Python stdlib, chạy: python3 X.py <csv> [cost]): entry_study.py (H4), entry_study_v2.py (M30+wick setup),
  prod_engine.py (replica prod A/B E1), nshape_study.py (N-shape + volume + freshness)
Vị trí: GitHub repo hoangminhvu423/thosat-pro-app nhánh claude/du-an-air-drop-y3ifan thư mục rbea-research/ ·
  Google Drive folder RB_EA (id 1ieXx8k_QZumVlu5W4Tdv-z3eMf2c1V40).

## 7. LƯU Ý QUAN TRỌNG CHO AGENT
- Sandbox: chỉ ra raw.githubusercontent.com + pypi/npm. Internet chung & GitHub search API BỊ CHẶN.
- Data chuẩn upload tại /root/.claude/uploads/.../64966031-XAU_30m_data.csv (file M5 rỗng, bỏ).
- Mọi harness dùng Python stdlib (không pandas). Chạy ~3-5s.
- Nguyên tắc Sep: chưa có số liệu chắc chắn thì KHÔNG thêm gì; tham khảo ≠ áp dụng; số phải kèm n+OOS+net phí.
