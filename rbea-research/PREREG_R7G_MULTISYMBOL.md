# PREREG R7g — ĐA THỊ TRƯỜNG cho KEEP-SLEEVE (khóa 2026-07-23, TRƯỚC khi lấy data/chạy)
Đề bài (Sếp giao): nâng auto payout keep lên ~2-2.5%/năm bằng TẦN SUẤT (nhiều thị trường ít tương quan),
KHÔNG tăng risk/lệnh, survival giữ tương đương flat-0.25% đơn-symbol.

## PHẠM VI TEST (đóng băng)
- Sleeve test = **BREAK sleeve Donchian-20 H4** (baseline entry, SL 1×ATR, TP 2×ATR, fresh-cross, 2 chiều,
  net 0.04R) trên **engine Fable-B** — vì framework I.A.2 đã xác định BREAK là nguồn edge chính của hệ;
  RANGE sleeve cần zone-người nên không test tự động được. Tham số KHÔNG chỉnh theo symbol (LESSON-04 test
  tính chuyển được của CƠ CHẾ, không phải tối ưu per-symbol).
- Ứng viên symbol (theo PROP_MC R4): FX majors (EURUSD, GBPUSD), kim loại 2 (XAG nếu có), chỉ số (US500/DAX
  nếu có), crypto (BTC — đã có data). Tối đa 5 symbol test (chống mining: ghi số symbol thử).

## TIÊU CHÍ DATA (như R7d): TF ≤ H1, OHLC đủ, kiểm mốc giá lịch sử, quét lỗ hổng thời gian >12h ngoài weekend/lễ.

## TIÊU CHÍ PASS per-symbol (khóa trước)
1. Net avgR > 0 toàn kỳ VÀ dương ≥ 2/3 đoạn thời gian (chia 3 đều theo năm data có).
2. n ≥ 100 lệnh toàn kỳ.
3. PF ≥ 1.03 toàn kỳ.
(Chuẩn này CHỦ Ý thấp — mục tiêu là "sàn không âm" cộng dồn tần suất, không phải tìm edge mạnh.)

## PORTFOLIO (chỉ chạy với symbol PASS)
- MC danh mục: mỗi symbol risk 0.15%/lệnh (tổng exposure ≤ ~0.5% khi trùng), breaker −9% chung.
- Tương quan giữa các stream: đo bằng chuỗi lợi nhuận THÁNG của backtest từng symbol (đoạn trùng thời gian).
- Metric: P(chết/2y), median payout %/năm — so với flat-0.25% XAU đơn (P 4.1%, median ~1.0-1.2%).

## DỰ ĐOÁN KHÓA TRƯỚC (chấm sau)
- P1: BTC PASS tiêu chí (Fable-B đã chạy: +0.022 toàn kỳ, PF1.03 — sát mép; long-only +0.087). tin TB.
- P2: ≤ 2/5 symbol PASS — breakout H4 KHÔNG phải tính chất phổ quát mọi thị trường (FX majors range nhiều). tin TB.
- P3: Nếu ≥2 symbol PASS: portfolio 3-stream @0.15% cho median payout 1.6-2.2%/năm @ P(chết/2y) ≤ 8%. tin TB-THẤP.
- P4: Tương quan tháng giữa XAU-BTC < 0.3 (thị trường khác nhau). tin TB.
- CAM KẾT: symbol FAIL thì loại — không chỉnh tham số để cứu. Nếu <2 symbol PASS → kết luận trung thực:
  đa-symbol không khả thi với cơ chế hiện tại, target 2-4% quay về cấu trúc auto+human.

## KẾT QUẢ (chạy 2026-07-23, engine Fable-B nguyên bản, net 0.04R)
### Per-symbol (Donchian-20 BREAK, tham số đóng băng, 3 đoạn đều):
- XAU  2004-2025: +0.022 PF1.03 n=1887, 3/3 đoạn dương → **PASS**
- BTC  2012-2026: **+0.119 PF1.19 n=1693, 3/3 đoạn dương → PASS mạnh** (~117 lệnh/năm vì 24/7)
  - Stress phí ×2 (0.08R): vẫn +0.079 PF1.12 → PASS (robust chi phí)
- EURUSD −0.077 / GBPUSD −0.017 / USDJPY −0.050 → **FAIL cả 3, loại không cứu** (đúng cam kết)

### Tương quan & Portfolio (joint block-bootstrap tháng từ data thật, 163 tháng trùng, 8k paths × 24 tháng)
- **Corr tháng XAU-BTC = +0.024 ≈ KHÔNG tương quan** (P4 ✓)
```
wXAU  wBTC   P(chết 2y)  median payout/năm
0.25   —        2.0%        0.27%   (break-XAU đơn — đối chiếu)
0.15  0.15      2.2%        2.31%   ← survival-first
0.20  0.20      5.8%        3.46%   ← balanced, GIỮA target 2-4%
0.25  0.25     12.4%        4.66%   (quá nóng — bác)
```
### CHẤM DỰ ĐOÁN: P1 ✓ (BTC pass) · P2 ✓ (đúng 2/5) · P3 ✓ VƯỢT (2.3-3.5% vs dự 1.6-2.2%) · P4 ✓ (corr 0.024)

## VERDICT R7g
**Đa-symbol XAU+BTC ĐẠT target payout 2-4%/năm ở survival 2-6%** — bằng TẦN SUẤT + tương quan ≈0, đúng thiết kế.
Cấu hình đề xuất: **0.15/0.15 (an toàn) hoặc 0.20/0.20 (balanced)**.

## CAVEAT & VIỆC PHẢI LÀM TRƯỚC KHI TIN HẲN
1. Bootstrap từ lịch sử backtest — BTC đoạn gần (2022-26) yếu hơn mean (+0.037; fee-stress ≈ 0) → tương lai giống S3 thì median thấp hơn. Forward demo là phán quyết.
2. Portfolio = BREAK-sleeve-only cả 2 bên → XAU thật (full EA) sẽ TỐT hơn số này (floor bảo thủ). NHƯNG BTC cần
   **EA mode FULL-AUTO (rolling Donchian box)** — v0.21 hiện là human-zone → deliverable v0.3 (framework đã gate-check PASS từ trước).
3. FTMO Swing có BTCUSD CFD; phí thật cần đo ở demo (stress 0.08R đã cover một phần).
4. Thứ tự: build v0.3 auto-mode → audit → demo song song XAU(zone)+BTC(auto) ≥4 tuần → go/no-go.
