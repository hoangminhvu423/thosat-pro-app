# BÁO CÁO — Quét phương pháp trên data M1 thật

> Sinh tự động bởi `quant/run_all.py`. dựng lại từ ledger 2026-07-18 23:47

> **Nguyên tắc vàng**: mọi EV OOS dương mặc định là nhiễu/overfit cho tới khi qua được
> validation + cross-symbol. Đa số EV≈0 sau phí là KẾT QUẢ, không phải thất bại.

## 1. Tổng quan
- Số thí nghiệm (method×symbol×khung): **1008**
- Dòng ledger: 3024 | có đủ lệnh OOS để xét: 1007
- OOS EV>0: 79/1007 (7.8%) — kỳ vọng ~50% do nhiễu nếu không có edge
- OOS CI95 không chứa 0 (EV>0): 1/1007
- **SỐNG SÓT (OOS ci_lo>0 + validation>0 + cross-symbol): 0**
- ⚠️ Nếu thuần nhiễu (95% CI, 1 phía) kỳ vọng ~25 con có CI>0 do may rủi; thực tế chỉ **1** → phí kéo âm ÁP ĐẢO cả nhiễu (ít hơn cả mức ăn may).

## 1b. GRADIENT PHÍ THEO KHUNG (phát hiện sắc nhất)
Phí cố định mỗi lệnh (spread+comm+slippage) quy R = phí_giá / độ_rộng_SL. Khung càng nhỏ,
SL càng hẹp → phí quy R càng lớn → giết edge. Số liệu OOS:

| Khung | Trung vị EV_OOS (R) | TB EV_OOS (R) | % config EV>0 | #config |
|---|---|---|---|---|
| M5 | -0.3151 | -0.4302 | 0% | 252 |
| M15 | -0.1722 | -0.2283 | 0% | 252 |
| H1 | -0.0833 | -0.1030 | 2% | 252 |
| H4 | -0.0396 | -0.0434 | 29% | 251 |

→ M5/M15 **không config nào** dương (phí ăn sạch). Chỉ H4 có ~29% dương do phí nhẹ —
nhưng KHÔNG con nào sống qua validation+cross-symbol. Đây là 'nghĩa địa' số hoá: logic
tĩnh công khai không thắng nổi chi phí thực, tệ nhất ở khung thấp.

## 2. Bảng xếp hạng phương pháp (trung vị EV OOS trên mọi symbol×khung)
| Phương pháp | Nhóm | Trung vị EV_OOS (R) | Số cấu hình |
|---|---|---|---|
| ctrl_rsi_diverg | Đối chứng | -0.1113 | 72 |
| smc_premium_disc | SMC/ICT | -0.1197 | 72 |
| ctrl_meanrev_z | Đối chứng | -0.1250 | 72 |
| sd_zone | Supply/Demand | -0.1311 | 72 |
| smc_fvg | SMC/ICT | -0.1382 | 72 |
| smc_liq_sweep | SMC/ICT | -0.1382 | 72 |
| pa_engulfing | PriceAction | -0.1414 | 72 |
| pa_bos | PriceAction | -0.1431 | 72 |
| wyckoff_spring | Wyckoff | -0.1455 | 71 |
| pa_inside_outside | PriceAction | -0.1496 | 72 |
| ctrl_channel_break | Đối chứng | -0.1592 | 72 |
| elliott_zigzag | Elliott | -0.1609 | 72 |
| pa_pinbar | PriceAction | -0.1621 | 72 |
| smc_order_block | SMC/ICT | -0.1651 | 72 |

## 3. Top 20 cấu hình theo EV OOS (⚠️ đỉnh bảng MẶC ĐỊNH là nhiễu multiple-testing)
| # | Phương pháp | Symbol | Khung | N | EV_OOS | win% | PF | CI95_OOS | IS→OOS | Sống? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wyckoff_spring | eurgbp | H4 | 151 | +0.1714 | 50.3 | 1.348 | [-0.016,+0.357] | -0.055→+0.171 |  |
| 2 | wyckoff_spring | gbpusd | H4 | 161 | +0.1196 | 47.2 | 1.225 | [-0.060,+0.305] | +0.070→+0.120 |  |
| 3 | pa_engulfing | gbpusd | H4 | 706 | +0.0947 | 44.9 | 1.173 | [+0.008,+0.182] | -0.031→+0.095 |  |
| 4 | wyckoff_spring | usdcad | H4 | 174 | +0.0904 | 46.0 | 1.168 | [-0.085,+0.269] | +0.048→+0.090 |  |
| 5 | smc_order_block | nzdjpy | H4 | 306 | +0.0892 | 46.4 | 1.165 | [-0.047,+0.223] | +0.018→+0.089 |  |
| 6 | smc_order_block | usdchf | H4 | 382 | +0.0882 | 45.8 | 1.164 | [-0.033,+0.207] | -0.050→+0.088 |  |
| 7 | ctrl_rsi_diverg | eurusd | H1 | 158 | +0.0869 | 44.9 | 1.169 | [-0.107,+0.272] | -0.046→+0.087 |  |
| 8 | ctrl_channel_break | eurjpy | H4 | 506 | +0.0855 | 46.8 | 1.158 | [-0.020,+0.197] | +0.047→+0.085 |  |
| 9 | pa_bos | eurusd | H4 | 87 | +0.0723 | 44.8 | 1.128 | [-0.176,+0.318] | +0.007→+0.072 |  |
| 10 | smc_order_block | audjpy | H4 | 379 | +0.0705 | 45.9 | 1.127 | [-0.058,+0.196] | +0.054→+0.070 |  |
| 11 | wyckoff_spring | eurcad | H4 | 182 | +0.0679 | 46.1 | 1.124 | [-0.106,+0.231] | +0.113→+0.068 |  |
| 12 | ctrl_channel_break | usdjpy | H4 | 550 | +0.0654 | 44.5 | 1.119 | [-0.033,+0.172] | -0.029→+0.065 |  |
| 13 | smc_order_block | gbpusd | H4 | 376 | +0.0642 | 43.6 | 1.118 | [-0.057,+0.185] | -0.086→+0.064 |  |
| 14 | pa_bos | chfjpy | H4 | 719 | +0.0636 | 46.0 | 1.119 | [-0.024,+0.146] | -0.006→+0.064 |  |
| 15 | elliott_zigzag | nzdusd | H4 | 572 | +0.0598 | 44.1 | 1.108 | [-0.040,+0.158] | -0.026→+0.060 |  |
| 16 | smc_fvg | gbpjpy | H4 | 893 | +0.0587 | 44.2 | 1.107 | [-0.018,+0.140] | +0.042→+0.059 |  |
| 17 | elliott_zigzag | gbpjpy | H4 | 597 | +0.0575 | 45.4 | 1.105 | [-0.034,+0.154] | -0.027→+0.058 |  |
| 18 | pa_inside_outside | usdcad | H4 | 632 | +0.0570 | 44.9 | 1.103 | [-0.036,+0.150] | -0.000→+0.057 |  |
| 19 | ctrl_rsi_diverg | eurcad | H4 | 377 | +0.0559 | 44.6 | 1.102 | [-0.060,+0.183] | -0.036→+0.056 |  |
| 20 | ctrl_channel_break | gbpjpy | H4 | 542 | +0.0548 | 44.5 | 1.099 | [-0.045,+0.154] | +0.079→+0.055 |  |

## 4. Con SỐNG SÓT (qua cả validation + cross-symbol)
**KHÔNG có phương pháp nào sống sót.** Đúng như luận đề: logic tĩnh công khai bị
arbitrage cạn — không con nào vượt được phí + walk-forward + cross-symbol trên data thật.

## 5. Mức overfit (khoảng cách IS ↔ OOS)
- Trung vị (EV_IS − EV_OOS) = **+0.0280R** (>0 = IS đẹp hơn OOS = overfit điển hình).
- IS dương nhưng OOS âm (lật dấu): 33 cấu hình — minh hoạ sống của 'đường cong đẹp trên IS lật trên OOS'.

## 6. Nhận định trung thực
- **Data**: đọc `data/GHI-CHU.md`. Symbol cụt (eurusd, chfjpy, xauusd) đã gắn cờ ở cột ghi_chu.
- **Giả định phí**: bảng `engine_np.COST_PRICE` (Exness Pro ~2026). Chỉnh số đó nếu có bảng chuẩn hơn.
- **CHƯA mô hình swap qua đêm** — lệnh giữ nhiều nến/ngày sẽ tệ hơn số ở đây (báo cáo này là cận TRÊN lạc quan về phí).
- **Mỗi phương pháp là MỘT cách số hoá** (nhất là Elliott/Wyckoff/SMC). EV xấu = bản code này chết, không phủ định phương pháp gốc.
- Kết quả này để **số hoá nghĩa địa**, không phải tìm chén thánh. EV≈0 sau phí là dữ liệu quý.
- **Đối chứng độc lập**: một bản scanner thứ 2 (stdlib, mô hình phí khác) chạy riêng trên H4
  cũng ra **0 con sống sót** — xem `quant/xcheck_cloud/KET-QUA-DOI-CHUNG.md`. Kết luận bền với lỗi code.
