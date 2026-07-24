---
name: ea-code-audit
description: Audit đối kháng code EA MQL5 tìm lỗi "âm thầm" làm live ≠ backtest hoặc phá an toàn. Dùng trước khi deploy version mới hoặc khi review EA. Checklist các lỗi đã gặp thật - filling mode, repaint nến, handle-per-tick, sizing/min-lot, circuit-breaker.
---

# EA Code Audit — checklist lỗi âm thầm (MQL5)

## Khi nào dùng
Trước khi deploy EA mới, hoặc khi soi một EA hiện có tìm bug loại "không crash nhưng sai".

## CHECKLIST (đã bắt được lỗi thật)

**🔴 Circuit-breaker / CloseAll**
- `PositionClose` có `SetTypeFillingBySymbol` chưa? US500 chỉ nhận **FOK** (rc=10030 nếu sai) → breaker có thể KHÔNG đóng được lệnh to nhất.
- Có **retry + verify** (`PositionSelectByTicket` sau khi đóng) không? Breaker không được phép thất bại âm thầm.

**🟠 Repaint / look-ahead**
- Tín hiệu đọc nến index 0 (đang hình thành) hay index 1 (đã đóng)? Chiến lược daily PHẢI dùng index 1 + new-bar gating (`iTime(sym,TF,0)` đổi). Index 0 = repaint → live ≠ backtest.

**🟡 Indicator handle**
- Có tạo/huỷ `iATR/iMA/iRSI` mỗi tick không? → cache handle; handle chưa sẵn data → CopyBuffer trả 0 → bỏ lỡ entry.

**🟡 Sizing**
- `lot < volume_min` xử lý sao? Skip âm thầm? Ép min → over-risk? Cần **trần risk cứng/lệnh** + log rõ.
- SL width có được validate (sweep) chưa? SL "một cỡ cho mọi sleeve" thường sai (xem `backtest-validate`).

**🟡 Persist state**
- Mốc max-loss/init-balance/day-baseline lưu `GlobalVariable`/file chưa? Nếu là biến RAM → reset khi restart → guard sai.

**🟡 Daily reset**
- Mốc daily-loss theo SERVER-day (`TimeCurrent`) hay local? Tính cả floating? (chuẩn FTMO).

## Output
Xếp lỗi theo mức 🔴/🟠/🟡, kèm dòng code + cách vá. Không kết luận "có bug" trước khi đọc `SYSTEM_BRIEF.md` + `DECISION_LOG.md`.
