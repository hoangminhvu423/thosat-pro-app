# 📊 BÁO CÁO TỔNG KẾT — NGÀY R&D 22-23/07/2026
Người báo cáo: Claude (Fable 5) · Phạm vi: toàn bộ chu trình từ audit RB_EA v0.1 → hệ thống tự vận hành

## I. KẾT QUẢ NGHIÊN CỨU (7 vòng, 4 prereg, 2 engine độc lập)
### Đã CHỨNG MINH (net phí, OOS, cross-validated)
- **Portfolio keep XAU+BTC: payout 2.3-3.5%/năm @ P(chết 2 năm) 2-6%** — đạt target Sếp giao (R7g).
  Cơ chế: tần suất ×2 qua 2 thị trường tương quan ≈0 (corr +0.024), KHÔNG tăng risk/lệnh.
- BTC break-sleeve: +0.119R PF1.19 (14 năm, 3/3 đoạn dương, sống stress phí ×2) — phát hiện giá trị nhất.
- Risk keep tối ưu: 0.15-0.20%/sleeve (0.5% cũ có P(chết) 26% — gấp 7 lần 0.25%).
- FX majors (EUR/GBP/JPY): BÁC cho breakout H4 — loại vĩnh viễn.
### Đã BÁC & RÚT LẠI (trung thực)
- E1 entry, N-shape "36/36 robust", cổng ER, volume filter, trailing/partial TP, pinbar/engulfing,
  wick-count, retest-entry — TẤT CẢ fail kiểm chứng độc lập/holdout. 2 claim của chính tôi bị rút sau cross-val.
- Bug tự bắt: fill-lạc-quan (look-ahead sót) + artifact hố-data 32 ngày (−13.5R giả) → sinh LESSON-05 + hole-guard.

## II. SẢN PHẨM BÀN GIAO
- **RB_EA_v0.3.mq5**: 6 bản vá audit (F1/F2/F4/C4/C6/C7) + breaker tổng −9% permHalt + mode FULL-AUTO
  Donchian + range-toggle. Trạng thái: CHỜ G1 compile.
- **MASTER_SPEC_v1.0**: kiến trúc 2-sleeve, risk stack 4 tầng, compliance FTMO Swing, 5 gates, runbook VPS.
- 10 harness Python (stdlib, tất định) + 4 thẻ prereg đã chấm điểm + journal R1 schema.

## III. HẠ TẦNG CÔNG TY (mới thành lập hôm nay)
- **QTQ HQ** (hq/): hiến pháp 7 luật + INDEX + STATE 3 dự án + DECISION_LOG + skills don-dep/dong-phien.
- **3 guồng tự động**: BTC Shadow-Run MỖI ĐÊM 3h VN (forward-log, engine đóng băng, đêm nay chạy chuyến đầu) ·
  Janitor thứ Hai 9h · XAU Shadow bán-tự-động (chờ export MT5 ~2 tuần/lần, có hole-guard).
- Tam giác đối chứng G5: BACKTEST ↔ SHADOW ↔ DEMO — tách lỗi logic khỏi lỗi thực thi.

## IV. ĐÁNH GIÁ KINH DOANH (đã duyệt góc nhìn CEO)
- Mô hình: thuê bảng cân đối prop. Tiền túi rủi ro $5-10k (phí, hoàn khi payout đầu) → $400k vốn thuê.
- Auto = sàn giữ quỹ (94-98% sống/2 năm); human-alpha = trung tâm doanh thu (CHƯA ĐO — journal R1 là then chốt).
- Kỳ vọng năm 1 nếu human đạt ½ prior: 1-2 account funded, $5-15k payout. Worst case: mất bankroll phí.

## V. VIỆC CHỜ (theo thứ tự — không bỏ bậc)
1. [SẾP] G1: compile v0.3 MetaEditor + G2 Strategy Tester (khi mở máy tính).
2. [PHIÊN MỚI] G3: ea-code-audit v0.3 (3 flag chờ sẵn trong code).
3. [VPS] G4: demo 2 sleeve ≥4 tuần/≥40 lệnh + journal R1 song song (kỳ vọng 10-13 lệnh/tháng).
4. G5: đối chiếu demo↔shadow↔backtest → cắm FTMO Swing 0.15/0.15.
5. [TIỆN THÌ] Tạo repo qtq-hq (github.com/new trên browser điện thoại) → migrate theo hq/MIGRATE.md.

## VI. MỘT DÒNG
Vào ngày với 1 EA chưa audit và 1 câu hỏi "có edge không"; ra ngày với hệ 2-symbol validated 2.3-3.5%/năm,
EA v0.3 + spec production, công ty có hiến pháp, và 3 guồng máy tự chạy khi mọi người ngủ.
Tài sản quý nhất tạo ra hôm nay không phải con số — mà là BỘ MÁY KIỂM CHỨNG đã 2 lần bắt được chính người vận hành nó sai.
