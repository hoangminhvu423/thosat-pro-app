# RB_EA — 3 CHẾ ĐỘ TÀI KHOẢN qua 1 công tắc I_Mode (Sếp nêu 2026-07-24)

Mục tiêu: bỏ việc chỉnh tay 28 tham số mỗi account (nguồn rủi ro vận hành). Chọn 1 dropdown → EA
tự nạp đúng bó tham số. Deploy-time (chọn 1 lần khi gắn/account), KHÔNG gạt runtime (tránh nhầm).

## Thiết kế cơ chế (an toàn, làm được ngay)
- Thêm input `I_Mode` enum: `CUSTOM | FUND | HUMAN_ALPHA | PERSONAL`.
- OnInit: nếu ≠ CUSTOM → ghi đè các biến làm việc (g_risk, g_maxDaily, g_maxWeekly, g_maxTotal,
  g_autoZone, g_rangeEnabled) theo bó của mode; Print rõ bó đã nạp lên log + panel hiển thị tên mode.
- CUSTOM = dùng input lẻ như hiện tại (tương thích ngược).
- Code chuyển I_RiskPct/I_MaxDailyDD/... → g_* để mode ghi đè được (input MQL5 không sửa runtime).

## Bó tham số đề xuất

| Tham số | 1) FUND (giữ quỹ) | 2) HUMAN_ALPHA (pass quỹ) | 3) PERSONAL (auto cá nhân) |
|---|---|---|---|
| Vùng | AUTO (hands-off) | SEMI — người /zone | AUTO |
| Risk/lệnh | 0.15% | 0.20% | **CHỜ CHỐT (xem cảnh báo)** |
| Daily DD | 3% | 3% | ~8% `// TẠM` |
| Weekly DD | 6% | 6% | ~15% `// TẠM` |
| Total/perm-halt | 9% | 8% | **25%** (trong ngưỡng Sếp 25-30) |
| Mục tiêu | bảo toàn, 0 vi phạm | pass challenge | **15-17%/năm** |
| Cơ sở | FTMO 5%/10% có biên | FTMO + alpha người | Sếp cấp mục tiêu+DD |

FUND & HUMAN_ALPHA: số neo theo luật FTMO (5% daily / 10% max) trừ biên an toàn → chắc chắn, làm được.

## ✅ ĐÍNH CHÍNH (Sếp đúng): backtest 15-17%/năm ĐÃ CÓ — ở QTQ Fund EA, KHÔNG phải RB_EA
Kết luận "không khả thi" ở bản trước là do tôi phân tích nhầm sang edge RB_EA (Range/Break) — vốn là
sleeve GIỮ QUỸ thiết kế "rỉ giọt" ~1%/năm (R7f: trần ~1,2%/năm @0.25%). Đó là chủ đích của RB_EA.
Mục tiêu 15-17%/năm @ DD 25-30% của Sếp lấy từ **QTQ Fund EA (calendar + rsi2)** — chiến lược KHÁC,
đã có sẵn enum 3 chế độ và risk-curve kiểm chứng:

- `projects/Fund_EA/QTQ_Fund_EA.mq5:85` — **`enum EMode { MODE_FUNDED, MODE_PASS, MODE_PERSONAL, MODE_MANUAL }`
  ĐÃ TỒN TẠI** (v3.92, đang deploy). ApplyMode() set risk/daily/max/cap theo mode; breaker CAP DD cứng.
- **Risk-curve (WORKLOG cal+rsi2)**: 1×→1,5%/DD2,5% · 3×→4,6%/7,4% (FTMO an toàn) · 5×→7,7%/12% ·
  **10×→15,5% CAGR / DD 24%**. → 15-17%/năm @ DD~25% ≈ hệ số **~10×**. Đúng dải Sếp đặt.
- Preset đã cài: FUNDED(2×,~5-7%/DD≤8%) · PASS(3×,~10%/DD≤9%) · **PERSONAL(8×, stop 12/30, ~20-27%/DD~24%)**.

### ⚠️ Lưu ý HONEST vs LẠC QUAN (phải nói rõ trước khi tiền thật)
- Risk-curve trên là bản proxy. **Sim v2 HONEST** (vá look-ahead + min-lot + swap, `scratch/simv2_report_20260703.md`):
  **PERSONAL 8× = CAGR +9,73% / maxDD −24,56%**, có **1 ngày HALT** thật (2026-06-09, −12,43%).
- Swap ăn −0,31%/năm; deflated Sharpe forward ~1,0-1,2 (không phải 1,5 gross).
- Nghĩa là: 15-17% "honest" cần đẩy ~10-13× → DD chạm/vượt mép 30%. **Đạt được nhưng ở rìa aggressive**;
  8× honest chỉ ~9,7%. Chốt con số cuối cần Sếp xác nhận chấp nhận DD tới ~30% + HALT-day.

## CÂU HỎI CỐT LÕI cần Sếp chốt: PERSONAL chạy EA NÀO?
Có 2 EA khác nhau trong hệ:
- **RB_EA** (Range/Break) — cái đang deploy hôm nay. Edge ~1%/năm (giữ quỹ). KHÔNG hợp mục tiêu 15-17%.
- **QTQ Fund EA** (cal+rsi2) — đã có 3-mode + backtest ra 15-17% @ ~10×. Đây mới là "động cơ" PERSONAL.

→ Vậy 3 chế độ Sếp muốn là gắn cho **Fund EA** (đã có sẵn, chỉ cần chốt hệ số PERSONAL + deploy)?
Hay muốn RB_EA cũng mang khung 3-mode (thì mode PERSONAL của RB_EA phải hiểu là "giữ quỹ tích luỹ",
không phải 15%)? Đây là quyết định nghề — tôi không tự gộp.

## Việc làm ngay (theo lựa chọn của Sếp)
- Nếu PERSONAL = **Fund EA**: nó đã có enum + preset. Chỉ cần chốt hệ số (8× honest ~9,7% hay ~10-12×
  để chạm 15% chấp nhận DD~28-30%) → re-verify sim → deploy. KHÔNG cần build lại từ đầu.
- Nếu muốn hợp nhất khung 3-mode cho RB_EA: build I_Mode như thiết kế trên, nhưng PERSONAL của RB_EA
  ghi rõ mục tiêu thực (giữ quỹ ~1-3%), không phải 15%.
