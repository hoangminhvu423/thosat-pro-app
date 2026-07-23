# QTQ HQ — HIẾN PHÁP CÔNG TY (mọi phiên/agent PHẢI đọc trước khi làm việc)
Cập nhật: 2026-07-23 · Chủ tịch: Sếp (donald.walker@ / yz.hoangmaisongvu@)

## LUẬT LÕI (bất biến — vi phạm = dừng việc)
1. **KHÔNG SỐ LIỆU → KHÔNG THÊM.** Mọi thay đổi hệ giao dịch phải có số kèm n + OOS + net phí.
2. **PREREG TRƯỚC, CHẠY SAU.** Giả thuyết khóa dự đoán trước khi thấy kết quả (dùng templates/PREREG_TEMPLATE.md).
3. **KIỂM CHỨNG ĐỘC LẬP** trước khi tuyên bố edge: engine thứ 2 viết từ SPEC, không nhìn code gốc (bài học LESSON-05: 36/36 "robust" vẫn có thể là 1 bug fill chung).
4. **FAIL thì XẾP KHO, không dò thêm ngưỡng trên cùng data** (= mining). Diễn giải hậu nghiệm phải prereg lại vòng sau.
5. **Tiền thật đi sau gates**: compile → tester → audit tươi → demo ≥4 tuần/≥40 lệnh → go/no-go. Không bỏ bậc (Guardian Rules).
6. Backtest có stop/limit fill: luôn kiểm "mức giá còn tồn tại lúc được phép đặt lệnh" + quét LỖ HỔNG THỜI GIAN của data trước khi tin outlier.
7. LESSON-04: finding là thuộc tính (thị trường × payoff × cơ chế vùng) — không chuyển chéo khi chưa đo lại.

## GIAO THỨC PHIÊN (mọi cửa sổ = một phòng ban)
- **MỞ việc**: đọc `hq/INDEX.md` → đọc `hq/projects/<dự-án>/STATE.md` → làm tiếp từ mục "VIỆC TIẾP THEO".
- **ĐÓNG việc**: chạy skill `dong-phien` — cập nhật STATE.md + DECISION_LOG nếu có quyết định mới + push. KHÔNG đóng phiên mà không cập nhật STATE.
- Kết quả quan trọng: lưu GitHub (nguồn chân lý) + Drive (bản cho người đọc, folder RB_EA id 1ieXx8k_QZumVlu5W4Tdv-z3eMf2c1V40).

## PHÂN TẦNG MODEL (tiết kiệm quota)
- Haiku: dọn dẹp, format, tổng hợp log, janitor.
- Sonnet: code thường, vận hành, viết tài liệu.
- Fable/Opus: R&D đối kháng, audit, quyết định kiến trúc, cross-validation.
- Một dòng công việc = một phiên dài (tận dụng cache). Cửa sổ mới chỉ khi chủ đề khác hoặc cần phòng-sạch.

## DANH SÁCH CẤM VĨNH VIỄN (đã fail kiểm chứng — không thử lại trên data cũ)
DCA/grid/hedge/martingale · trailing/partial TP · pinbar/engulfing filter · retest-entry ·
wick-count filter · volume filter (tick-vol) · cổng ER phổ-quát · session-block/time-stop-ngắn cho auto XAU.
