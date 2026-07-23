# R7e — MC SURVIVAL cho vai KEEP (FTMO 200k Swing) — 2026-07-23
Chạy Q3 (đã prereg trong LOGIC_FRAMEWORK I.B). Phân phối lệnh khớp PHASE1 fOFF (check: avgR +0.080 vs mục tiêu +0.078;
đuôi béo theo Q2). 60 lệnh/năm, 2 năm, 8k paths/ô, breaker tổng cứng −9% neo BALANCE BAN ĐẦU, risk fixed-$ từ initial.

## BẢNG QUYẾT ĐỊNH (validated edge)
```
risk%   P(chết/2năm)  tháng-quỹ/24   median %/năm   P(scale 10%/4mo)
0.25        3.9%          23.8          +1.08%            1%
0.50       26.5%          20.9          +1.67%           40%
0.75       43.5%          17.5          +0.26%           51%
1.00       54.9%          14.9          −4.50%           46%
```
Degraded (edge/2): 0.25% → chết 5.5% | 0.5% → 31.5%. Zero-edge: 0.25% → chết 7% | 0.5% → 36.5%.

## KẾT LUẬN (cho mục tiêu "sống sót + cầm max quỹ")
1. **Risk 0.25%/lệnh là cấu hình KEEP đúng** — P(chết 2 năm) chỉ 4–7% NGAY CẢ khi edge chết hẳn (zero-edge 7%).
   Risk 0.5% (default cũ) tưởng an toàn nhưng P(chết) 26–37% — gấp ~7 lần, vì đuôi béo + edge mỏng.
2. **"Cầm max quỹ" = NHÂN ACCOUNT, không phải tăng risk.** Tăng 0.25→0.5 để x2 payout làm P(chết) x7.
   2 account 200k @0.25% = cùng payout với 1 account @0.5% nhưng survival từng account vẫn 96%.
   (FTMO cho phép max allocation $400k/trader chuẩn — đúng khớp 2×200k.)
3. **FTMO Scaling Plan (+25%/4 tháng cần +10%/4mo): auto KHÔNG BAO GIỜ tự đạt** (P≈1% @0.25%).
   Scaling chỉ đến từ sleeve NGƯỜI. Auto = giữ sàn nhà, người = xây tầng.
4. Payout kỳ vọng auto-keep @0.25% trên 200k: ~$2–3k/năm (median +1.1%, split 80%) — rỉ giọt đúng vai.

## ĐÃ VÁ VÀO EA v0.22
- I_MaxTotalDD=9.0% neo balance ban đầu → CloseAll + PERM-HALT (trước ngưỡng FTMO 10%). Persist qua restart.
- I_RiskPct default 0.25 (keep-profile).
- Yêu cầu sản phẩm: **FTMO SWING** (giữ weekend + không giới hạn tin — bắt buộc cho H4/time-stop 192h).

## CAVEAT
MC tham số hóa từ summary stats (không phải trade-list gốc); lệnh i.i.d. — thực tế chuỗi âm 8 tháng có clustering
→ P(chết) THẬT có thể cao hơn ở cùng risk% → thêm lý do chọn 0.25%. Chưa mô hình phí attempt/reset.
