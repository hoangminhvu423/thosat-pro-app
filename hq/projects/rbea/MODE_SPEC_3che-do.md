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

## 🔴 CẢNH BÁO KHẢ THI — chế độ 3 (PERSONAL 15-17%/năm)
Bằng chứng từ chính backtest đã kiểm chứng (R7g, G2 v0.32):
- BTC AUTO 18 tháng @ risk 0.15% = **+48,62 USD trên vốn 4600 ≈ +1,06% / 18 tháng ≈ 0,7%/năm**.
- Tần suất ~0,7 lệnh/tháng (rất thưa).
→ Để từ 0,7%/năm lên 15-17%/năm cần **~20 lần** — KHÔNG đạt được bằng tăng risk đơn thuần:
  risk phải lên ~3%+ mà DD sẽ vượt xa 30%, và chỉ ~8 lệnh/18 tháng thì variance khổng lồ.
- **Kết luận thẳng**: mục tiêu 15-17%/năm KHÔNG khả thi với 1 edge BTC-AUTO hiện có ở bất kỳ mức risk
  an toàn nào. Ép risk để chạm mục tiêu = cách cháy tài khoản (đúng thứ Guardian + LUẬT LÕI cấm).

### Đường đi đúng cho chế độ 3 (cần Sếp chọn, KHÔNG bịa số)
1. **Thêm sleeve/instrument** để tăng số lệnh (XAU + BTC + FX majors đã bác ở break; cần R&D thêm rổ).
2. HOẶC hạ mục tiêu về mức edge thật đỡ (vd 3-5%/năm) — bền, không ép.
3. HOẶC backtest sweep risk×DD để tìm điểm risk cao nhất mà DD 18 tháng vẫn ≤ 25% → xem đạt được %/năm
   bao nhiêu (prereg trước khi test, theo giao thức quant). Con số ra được mới chốt vào bó PERSONAL.

## Việc làm ngay (nếu Sếp duyệt)
- Build I_Mode + bó FUND & HUMAN_ALPHA (số chắc chắn) → G1 + G2.
- PERSONAL: để `risk = CHỜ CHỐT`, chạy backtest sweep (mục 3 trên) → báo cáo %/năm thực đạt ở DD 25%,
  Sếp chốt rồi mới điền. KHÔNG deploy PERSONAL với số bịa.
