> ⚠️ **ĐÍNH CHÍNH 2026-07-23:** kết luận trong file này đã bị SỬA sau cross-validation Fable-B.
> Đọc **CROSSVAL_CORRECTION_20260723.md** — N-shape = regime-dependent (không phải all-OOS robust); E1 = KHÔNG cải thiện (đã gỡ khỏi EA, v0.21 dùng market-ngay-tại-xác-nhận).

# N-SHAPE ROBUSTNESS SWEEP (2026-07-23) — chống overfit
Quét IMP{1.0,1.5,2.0,2.5} × pivot-k{1,2,3} × retrace-band{(0.2,0.7),(0.3,0.6),(0.15,0.8)} = 36 cấu hình.
TP=MM, net phí 0.04R, data chuẩn, OOS 3 đoạn.

KẾT QUẢ: **36/36 cấu hình net-dương CẢ 3 OOS** (avgR ALL +0.21→+0.33, PF 1.33–1.60).
=> Edge N-shape KHÔNG phụ thuộc một bộ tham số → bằng chứng mạnh chống overfit.
- k lớn hơn (pivot chặt hơn) và retrace hẹp (0.3-0.6) cho avgR cao hơn chút (ít lệnh hơn).
- OOS-A (2004-12) mạnh nhất (+0.30→+0.52); DEV yếu nhất (+0.08→+0.18) nhưng vẫn dương; OOS-B mạnh (+0.31→+0.49).

CAVEAT: proxy pivot standalone + tick-volume; cross-validate bằng Fable-B engine độc lập (đang chạy).
Chạy: python3 nshape_sweep.py <csv> [cost_R]
