# N-SHAPE STUDY — Phân tách chính xác hình thái chữ N + kết quả (2026-07-23)
Data: XAU_30m_data.csv chuẩn (243,821 M30 → 32,290 H4, 2004-2025). Net phí 0.04R. Path M30. Look-ahead ĐÃ VÁ.
Nguồn cảm hứng: bài X của 1 trader TQ (N-model) — CHỈ tham khảo; mọi thứ dưới đây là ĐO ĐƯỢC, không tin theo.

## ĐỊNH NGHĨA CHÍNH XÁC hình thái chữ N (up; down đối xứng)
1. **L0** = pivot low (fractal k=2).
2. **Leg1 (impulse)** = L0 → **H1** (pivot high), với (H1−L0) ≥ 1.5×ATR(H4). (đợt tăng mạnh = chân đứng 1)
3. **Pullback (đường chéo)** = H1 → **L1** (pivot low), với L1 > L0 (higher-low) và retrace (H1−L1)/(H1−L0) ∈ [0.2, 0.7].
4. **Leg2 (continuation)** = giá PHÁ lên trên H1 (đỉnh trước) → **TRIGGER vào lệnh** tại mức H1.
5. **SL** = L1 − 0.2×ATR (cấu trúc — dưới higher-low). **TP** = 2R / 5R / MM(=chiều cao leg1).
- [FIX] pivot cuối (L1) chỉ xác nhận sau k=2 nến → CHỈ vào từ nến i2+3 (chống look-ahead).

## KẾT QUẢ (net 0.04R)
```
TP=MM   seg     n    WR%   avgR    totR   PF
N all  OOS-A   380  49.2  +0.432  +164.2 1.82
N all  DEV     504  40.5  +0.135   +67.9 1.22
N all  OOS-B   199  49.2  +0.403   +80.1 1.77
N all  ALL    1083  45.2  +0.288  +312.2 1.51
(2R: ALL +0.235 PF1.39 | 5R: ALL +0.340 PF1.43)
```
→ Net-dương CẢ 3 OOS, mọi TP. avgR gấp 2–5× edge production (+0.078). Đây là kết quả MẠNH NHẤT của điều tra.

## PHÁT HIỆN
1. **N-shape là edge THẬT, bền** (all-OOS+, PF 1.39–1.51). Hình thức hóa "đỉnh cao dần/đáy cao dần" + chân-2 chữ N + E1, mạnh hơn breakout thô nhờ ngữ cảnh impulse+pullback + SL cấu trúc.
2. **Volume real/fake: KHÔNG xác nhận** trên tick-volume XAU (sau vá look-ahead, fake ≥ real ở nhiều cut). KHÔNG thêm volume filter. (Caveat: tick-volume ≠ volume sàn thật.)
3. **Freshness: N vốn tươi** (fresh2+ n=12) → cấu trúc N tự lọc, không cần filter riêng. Khớp MIRROR (vỡ tươi tốt).
4. **TP MM/5R > 2R** → để chạy tới đích (đo leg1) hợp lý cho setup cấu trúc; khớp RR≥1:5.

## TRIỂN VỌNG (chưa chốt — cần xác nhận)
- N-shape là ứng viên **sleeve mới** hoặc thay logic BREAK của RB_EA (mạnh hơn hẳn). Ưu tiên cao.
- Cần: (a) chạy lại trên **Fable engine** (vào hồ sơ chính thức, thay proxy pivot); (b) test độ nhạy IMP (1.0–2.5) & retrace band & pivot-k; (c) prereg trước khi code vào EA (governance).
- Kết hợp với E1 đã proven: E1 = chân-2 đơn giản; N-shape = chân-2 CÓ ngữ cảnh (impulse+pullback). Có thể N-shape là "phiên bản đầy đủ" của E1.
- TP: cân nhắc MM cho sleeve này thay fixed-2R.

## CAVEAT (đọc trước khi tin)
Detector pivot STANDALONE (chưa tích hợp state machine/zone RB_EA); tick-volume proxy; 3 TP mode (multiple-testing nhẹ, nhưng đều +); 1 nguồn data; look-ahead đã vá nhưng pivot fractal vẫn cần audit kỹ khi cấy vào EA (không được dùng bar tương lai lúc live).
