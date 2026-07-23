# JOURNAL R1 — đo HUMAN-ALPHA (tầng người / vế PASS)
Mục đích: tách "alpha chọn kèo của NGƯỜI" khỏi "premium giữ exit của MÁY". Đây là mảnh CHẶN đường vế semi-auto/pass.
Nguyên tắc: máy giữ exit (không chốt tay); người chỉ chọn kèo + vẽ vùng. Mỗi lần ARM ghi 1 dòng TRƯỚC khi biết kết quả.

## Cột (CSV, ghi lúc ARM — trước outcome)
| cột | ý nghĩa |
|---|---|
| ts | thời điểm ARM (server time) |
| symbol | XAUUSD... |
| setup | loại: WICK_RETEST (Setup A) / WICK_CLOSE (Setup B) / ZONE_SD / OTHER |
| dir | buy/sell |
| zone_hi, zone_lo | vùng người vẽ |
| entry_plan | giá dự định vào |
| sl_struct | SL theo cấu trúc M15/M30 (giá) |
| tp_target | TP = đỉnh/đáy đích (measured-move / swing) |
| R_planned | (tp-entry)/(entry-sl) — R kỳ vọng |
| conviction | 1-3 (tự chấm độ tự tin) |
| session | Asia/London/NY/Late |
| lambda24 | trạng thái lambda_24h lúc ARM: HAP_THU / TRUNG_TINH / KHUECH_DAI (MC-003) |
| touch_count | số lần vùng đã bị chạm trước đó |
| news_near | có tin lớn ±2h? y/n |
| note | ghi chú người |

## Cột outcome (điền sau khi máy đóng lệnh)
| cột | ý nghĩa |
|---|---|
| filled | lệnh có vào không (retest có chạm không) y/n |
| R_actual | kết quả R thực (máy giữ exit) |
| exit_reason | TP / SL / TIME / MANUAL_HALT |
| bars_held | số nến H4 giữ |

## Cách tính human-alpha (sau ≥50 dòng)
1. **Baseline máy đối chứng:** cùng thời điểm ARM, chạy RB_EA AUTO (rolling-box) trên cùng khung → R_auto.
2. **Human-alpha = mean(R_actual người) − mean(R_auto) trên cùng cửa sổ.** >0 có ý nghĩa (t-test / bootstrap) → người thêm giá trị.
3. **Tách nguồn:** so R_planned (chọn kèo) vs R_actual (máy giữ exit) → phần nào của alpha là "chọn" vs "giữ".
4. **Chấm theo setup:** WICK_RETEST vs WICK_CLOSE vs ZONE_SD — cái nào có alpha thật (nhớ: study cho thấy 2 setup wick HIẾM nhưng R cao khi trúng → cần đủ mẫu).
5. **Gate:** chỉ tuyên "semi-auto > auto" khi human-alpha > 0 với n≥50 và qua bootstrap. Trước đó, semi-auto chỉ là giả thuyết (đúng như framework ghi).

## Lưu ý khớp với study 2026-07-23
- 2 setup wick của Sếp trên proxy: quá hiếm (12-18 lần/21y) cho AUTO → đúng chỗ để NGƯỜI khai thác (discretionary, high-conviction).
- Gợi ý mạnh nhất từ data: TP measured-move (đích lớn) > TP 2R cho các cú hiếm-xịn (PF 1.7-2.0, mẫu nhỏ) → journal ghi tp_target theo đích, đừng cắt 2R.
- lambda24 TRUNG_TINH [-0.3..+0.2] là môi trường tốt nhất cho range-touch (MC-003 OOS +0.218R) → ưu tiên ARM khi trung tính.
