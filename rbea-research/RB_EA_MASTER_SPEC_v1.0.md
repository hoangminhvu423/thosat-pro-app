# RB_EA — MASTER SPEC v1.0 (thiết kế production, 2026-07-23)
Trạng thái: THIẾT KẾ CHỐT — mọi quyết định dưới đây có nguồn bằng chứng (7 vòng R7a-g, 4 prereg, 2 engine độc lập).
Code hiện thực: RB_EA_v0.3.mq5 (GitHub rbea-research/). Trạng thái code: CHƯA compile / CHƯA audit / CHƯA demo.

═══════════════════════════════════════════════════════════════════
## 1. MỤC TIÊU & PHẠM VI
- Nhiệm vụ DUY NHẤT: **KEEP** — giữ account funded sống + payout đều. KHÔNG phải máy kiếm tiền tối đa.
- Target đã validate: payout 2.3-3.5%/năm/account @ survival 94-98%/2 năm (R7g portfolio MC).
- Vế PASS (challenge) = tầng NGƯỜI, ngoài phạm vi EA này (chỉ hỗ trợ exit-manage + journal).

## 2. KIẾN TRÚC — MA TRẬN INSTANCE (1 account FTMO Swing = 2 chart)
| Chart | Symbol | Profile | Zone | Range sleeve | Risk/lệnh | Magic |
|---|---|---|---|---|---|---|
| 1 | XAUUSD H4 | SEMI (người vẽ zone) | hline RB_HI/RB_LO | ON | 0.15-0.20% | 20260723 |
| 2 | BTCUSD H4 | AUTO (I_AutoZone=true) | rolling Donchian-20 | **OFF** (break-only) | 0.15-0.20% | 20260724 |
- Hai instance ĐỘC LẬP hoàn toàn (magic riêng, GlobalVariable riêng theo magic+symbol).
- Corr tháng đo được XAU-BTC = +0.024 → không cần cơ chế phối hợp giữa 2 sleeve.
- Cấu hình risk: khởi đầu 0.15/0.15 (survival-first); nâng 0.20/0.20 sau quý đầu sạch.

## 3. LOGIC SPEC (tham số ĐÓNG BĂNG — nguồn bằng chứng từng dòng)
### 3.1 Chung (cả 2 profile)
- TF quyết định: H4, chỉ hành động khi nến ĐÓNG (index 1) — chống repaint [audit OK v0.1].
- ATR Wilder(20) H4. Break xác nhận: close > boxHi + 0.25×ATR (đối xứng down) [PHASE1 spec L3].
- BREAK entry: MARKET NGAY tại nến xác nhận [C4-fix; E1 đã bác bởi Fable-B cross-val].
- SL break = 1.0×ATR, TP = 2.0×ATR fixed [trailing/partial ĐÃ BÁC — churn net-âm sau phí R7-PREREG].
- Time-stop: 48 nến H4 = 192h qua POSITION_TIME [F1].
- STOPS_LEVEL clamp trước mọi lệnh [F4]. Budget chỉ trừ khi lệnh thật vào [F2].
- Trend filter: default OFF [PHASE1: filterOFF robust hơn qua 3 regime].
- CẤM vĩnh viễn: DCA/grid/hedge/martingale [Lyapunov II.B], pinbar/engulfing filter, retest-entry,
  wick-count filter, volume filter, cổng ER [tất cả fail kiểm chứng độc lập R7c/d].
### 3.2 Profile SEMI (XAU): như RB_EA_Master_Spec gốc — người vẽ zone + /arm, range sleeve ON,
  budget 1 RANGE_BUY + 1 RANGE_SELL + 1 BREAK/ngày, gap 60', whipsaw-block theo hướng SL.
### 3.3 Profile AUTO (BTC): I_AutoZone=true (Donchian-20 nến đã đóng, cập nhật mỗi nến),
  I_RangeEnabled=false — CHỈ break 2 chiều [R7g validated: +0.119R PF1.19 n=1693, fee-stress ×2 PASS].
  KHÔNG áp MinZoneATR ở auto mode (fidelity với sleeve validated).

## 4. RISK STACK — 4 TẦNG (mapping FTMO)
| Tầng | Ngưỡng EA | Luật FTMO | Đệm | Hành vi khi nổ |
|---|---|---|---|---|
| Per-trade | 0.15-0.20% fixed-$ | — | — | SL cứng mọi lệnh |
| Daily | −3% equity đầu-ngày-server | −5% (CE(S)T) | 2% | NEUTRAL hết ngày, giữ vị thế theo I_CloseOnBreaker |
| Weekly | −8% từ Monday-server | — | dự phòng bậc 2 | NEUTRAL hết tuần |
| **TOTAL** | **−9% từ BALANCE BAN ĐẦU** | **−10% Max Loss** | 1% | **CloseAll + PERM-HALT (persist), cần người reset** [R7e] |
- Sizing: fixed-fractional trên BALANCE — ổn định Lyapunov, breaker kéo về V=0 [framework II].
- MC nền: risk 0.25%/sleeve đơn → P(chết 2y) 4%; cấu hình 2-sleeve 0.15/0.15 → 2.2% [R7e/R7g].

## 5. COMPLIANCE FTMO (bắt buộc trước khi cắm)
- [ ] Loại account: **SWING** (weekend-hold + news OK — bắt buộc vì hold tới 192h). Normal = CẤM DÙNG.
- [ ] EA được phép; chiến lược tự xây (không copy) — OK.
- [ ] Server FTMO = CE(S)T: mốc daily EA khớp; verify công thức daily ($ cố định từ initial) khi audit.
- [ ] Whitelist https://api.telegram.org trong MT5 Tools>Options>Expert Advisors.
- [ ] Payout: rút theo chu kỳ, không giữ lãi tồn (counterparty risk); ghi nhận CPPI-ladder là TÙY CHỌN
      (survival giữ nguyên, mean +0.2-0.3%; median không đổi) — bật sau quý đầu nếu muốn.

## 6. VẬN HÀNH (VPS runbook)
- VPS: MT5 + 2 chart (XAU H4, BTC H4), EA v0.3 compile sẵn, autostart, đồng hồ NTP.
- Telegram: /status /arm /disarm /flat cho từng instance (token chung, chat-id whitelist 1 người).
- Nhật ký: mỗi lần ARM XAU → 1 dòng journal R1 (đo human-alpha song song — mảnh PASS).
- Checklist TUẦN (5'): equity vs initial · số lệnh tuần (kỳ vọng 2-3) · PERM-HALT flag · VPS uptime ·
  đối chiếu 1 lệnh bất kỳ với backtest logic (spot-check).
- Sự cố: mất VPS >4h → mở MT5 mobile kiểm vị thế (SL cứng luôn có — an toàn kể cả EA chết);
  PERM-HALT nổ → KHÔNG reset vội, mở phiên điều tra trước.

## 7. GATES NGHIỆM THU (không được bỏ bậc — Guardian Rules)
| Gate | Nội dung | Tiêu chí đạt |
|---|---|---|
| G1 Compile | MetaEditor 0 error 0 warning | binary chạy |
| G2 Tester | Strategy Tester visual 3 tháng gần, cả 2 profile | không lệnh phi logic; time-stop/breaker hoạt động |
| G3 Audit | ea-code-audit instance TƯƠI trên v0.3 | vá hết finding đỏ; soi 3 flag đã ghi: (a) buy khi giá vượt trigger, (b) lệch 1-vị-thế vs backtest overlap, (c) công thức daily FTMO |
| G4 Demo | VPS demo ≥4 tuần VÀ ≥40 lệnh tổng 2 sleeve | tần suất 10-13 lệnh/tháng (±40%); avgR không âm hệ thống; 0 vi phạm breaker logic |
| G5 Go/No-Go | so demo vs backtest | lệch giải thích được → cắm FTMO Swing với risk 0.15/0.15 |

## 8. KPI SAU KHI LIVE (bảng theo dõi quý)
Số lệnh/tháng (kỳ vọng 10-13) · avgR trượt-12-tháng · khoảng cách tới total-breaker ·
payout đã rút · tháng-quỹ tích lũy · human-alpha (journal R1, n ARM) · phí demo/challenge đã đốt.

## 9. RỦI RO TỒN ĐỌNG (đã biết, chấp nhận có chủ đích)
1. BTC sleeve đoạn 2022-26 yếu (fee-stress ≈ hòa) — demo là phán quyết; nếu BTC demo âm 2 quý → tắt sleeve BTC, quay về đơn-XAU (payout giảm về ~1%, survival tăng).
2. Backtest overlap vs EA 1-vị-thế → tần suất live có thể lệch (đo ở G4).
3. Correlation XAU-BTC có thể tăng trong khủng hoảng thanh khoản (corr đo trong điều kiện thường).
4. Hệ CHƯA từng chạy production một ngày nào — mọi con số là tiền nghiệm cho tới hết G4.
═══════════════════════════════════════════════════════════════════
Phê duyệt thiết kế: Sếp. Thực thi G1-G2: Sếp (cần MetaEditor). G3: phiên Claude tươi. G4-G5: VPS + thời gian.
