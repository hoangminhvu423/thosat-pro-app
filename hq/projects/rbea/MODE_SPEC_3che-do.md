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

## ✅ ĐÍNH CHÍNH (Sếp đúng — proof là R7h của CHÍNH RB_EA): 15-17%/năm CÓ THẬT
Tôi đã sai 2 lần và xin nhận: (1) trích số KEEP (0.15-0.25% → ~1%/năm) như thể đó là trần của RB_EA;
(2) đổ nhầm 15-17% sang Fund EA (đã khai tử). Sự thật: **15-17%/năm @ DD 25-30% là của CHÍNH RB_EA**,
chỉ khác MỨC RISK — proof có sẵn trên GitHub:

- **`rbea-research/mc_personal.py` (R7h)** + commit `62b2c6d`. MC joint block-bootstrap XAU+BTC (corr 0.024),
  **lãi kép, 5 năm, 8000 paths**, seed cố định (tái lập được). Đọc script: phương pháp sạch, đúng chuẩn.
- **Kết quả R7h (chốt trong commit)**:
  | risk/sleeve | CAGR median | P(DD>30%) |
  |---|---|---|
  | 0.75% | **~14%/năm** | (dưới 50%) |
  | 1.0%  | **~18%/năm** | ~50% |
  → **15-17%/năm ≈ risk 0.85-0.95%/sleeve**, DD budget 25-30%. KHỚP CHÍNH XÁC dải Sếp đặt.

### Vì sao trước tôi thấy "chênh lệch bất thường" — thực ra KHÔNG có gì bất thường
RB_EA là 1 chiến lược với **NÚM RISK**; 2 đầu núm cho 2 con số hoàn toàn khác nhau, cả hai đều ĐÚNG:
- KEEP/prop (R7e/f): 0.15-0.25% → ~1-2%/năm, DD nhỏ — chủ đích SỐNG SÓT qua lằn ranh prop (chạm DD = chết).
- PERSONAL (R7h): 0.75-1.0% → 14-18%/năm, DD 25-30% — không có lằn ranh chết, lãi kép, chịu DD lớn.
→ Đây CHÍNH LÀ cơ chế 3 chế độ Sếp muốn: **mode = một mức risk khác nhau trên cùng 1 EA**. Không mâu thuẫn.

### Lưu ý honest (không giấu): số R7h dựng trên forward/backfill R7g (đóng băng), corr XAU-BTC 0.024,
giả định 2 sleeve chạy song song. CSV nguồn (mret_XAU/BTC) không nằm trong repo (chỉ script) → muốn
CHẠY LẠI tái lập cần đưa 2 file monthly-return đó về, hoặc tái tạo từ forward log (ghi rõ phương pháp).

## Bó tham số PERSONAL (chốt theo R7h)
| | 1) FUND | 2) HUMAN_ALPHA | 3) PERSONAL |
|---|---|---|---|
| Vùng | AUTO | SEMI (/zone) | AUTO |
| Risk/sleeve | 0.15% | 0.20% | **~0.85-0.90%** (mục tiêu 15-17%, R7h) |
| Total DD/perm-halt | 9% | 8% | **28-30%** (đúng DD-budget Sếp) |
| Mục tiêu | giữ quỹ | pass challenge | 15-17%/năm lãi kép |

## Việc làm ngay (nếu Sếp duyệt)
- Build `I_Mode` cho RB_EA v0.5 với 3 bó trên (PERSONAL neo R7h 0.85-0.90% + DD 28-30%).
- Trước tiền thật PERSONAL: (a) đưa mret CSV về chạy lại R7h xác nhận 15-17% @ risk chốt; (b) G1+G2;
  (c) Sếp xác nhận CHẤP NHẬN DD tới ~30% (R7h: risk 1.0% có ~50% khả năng chạm >30% trong 5 năm).
