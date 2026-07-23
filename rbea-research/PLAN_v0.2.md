# KẾ HOẠCH hoàn thiện logic đã chứng minh → EA thành phẩm v0.2 (làm khi Sếp ngủ)
Ngày: 2026-07-23 · Nguyên tắc: CHỈ đưa vào EA thứ đã net-dương OOS. Không tô hồng. Reliable > đẹp.

## Logic ĐÃ CHỨNG MINH (net, data chuẩn) — được phép vào EA
- E1 continuation entry (vào STOP tại đỉnh/đáy nến break) — net+ cả 3 đoạn trên proxy M30. VỪA sửa C4 VỪA nâng edge.
- Trend filter default OFF (PHASE1: robust hơn, filterON tụt regime bull).
- Fixed-R TP (KHÔNG trailing/partial — đã bác: churn net-âm sau phí).

## Logic BỊ BÁC — cấm vào EA auto
- pinbar/engulfing (E4/E5): fail OOS-B nặng.
- trailing/partial TP: net-âm OOS.
- retest-limit E2: DEV chết.
- wick-structure N≥2: fail OOS.
- 2 setup wick của Sếp: quá hiếm cho auto → chuyển TẦNG NGƯỜI (journal R1).

## Lỗi audit phải vá trong v0.2 (đã xác nhận)
C2/F1 time-stop 192h · C3/F4 STOPS_LEVEL clamp · C4 (E1 giải quyết) · C5/F2 budget-chỉ-trừ-khi-khớp · C6 Friday-flat option · C7 mốc tuần chuẩn.

## CÁC BƯỚC (tuần tự, tự làm)
1. [ ] Dựng REPLICA production (Python) rolling-box full-auto — sanity: tái tạo ~+0.078R filterOFF (PHASE1). Nếu lệch xa → báo trung thực, chỉ dùng cho A/B tương đối.
2. [ ] A/B trên replica: baseline v0.1-entry VS v0.2-entry(E1)+timestop, OOS 3 đoạn, net phí. Xác nhận E1 giữ +.
3. [ ] Tách sleeve BREAK riêng (A/B sạch — RANGE giống nhau nên hiệu số = tác dụng E1).
4. [ ] Chốt SPEC v0.2 (chỉ proven).
5. [ ] Viết RB_EA_v0.2.mq5 hoàn chỉnh (E1 + F1 + F4 + F2 + C6 + C7).
6. [ ] Journal R1 schema (đo human-alpha cho 2 setup wick + tầng người).
7. [ ] Đóng gói + báo cáo tin cậy.

## Tiêu chí "tin cậy" (tự ràng buộc)
- Mọi số kèm n, OOS, net phí. E1 chỉ được tuyên "giữ" nếu net-dương ≥2/3 đoạn VÀ không âm nặng đoạn còn lại.
- Nếu replica không tái tạo được PHASE1 → nói rõ, hạ tuyên bố xuống "A/B tương đối".
- Code EA: comment rõ dòng nào vá lỗi nào; KHÔNG thêm logic chưa chứng minh.
