# PANEL SPEC v0.4 — giao diện chart RB_EA (Sếp PHÊ DUYỆT mockup 2026-07-24)

Bối cảnh: v0.31 KHÔNG có panel chart (StatusText chỉ gửi Telegram). Sếp duyệt mockup
3 trạng thái → đây là YÊU CẦU BẮT BUỘC của P2 (v0.4 module hóa, cùng gói Panel/Logger/Notifier/Watchdog).
Phong cách bám HM0.4 đang chạy live (chữ trắng nền chart, mono, góc trên-trái + nút đỏ HALT).

## Nội dung panel (mọi trạng thái)
```
RB_EA v0.4 — <symbol> <TF>                     ← xám nhạt
ARMED: YES/CHƯA | MODE: NEUTRAL/RANGE/BREAK    ← trạng thái tô màu (xanh=chạy, đỏ=halt)
Zone: <lo> – <hi>   (chưa vẽ → "— (chờ vẽ RB_HI/RB_LO)")
Budget RB/RS/BK: x/y/z
Risk 0.15% | Eq <equity> | vị thế: n (hướng + lot)
ngày -a.a% (dừng -3.0%) | tuần -b.b% (-8.0%)   ← dòng breaker LUÔN hiện
tổng -c.c% (perm-halt -9.0%)
[/arm|/disarm] [HALT ALL]                       ← nút bấm trên chart
```

## Quy tắc trạng thái (khớp logic v0.31 đã audit G3)
1. **Chưa arm (SEMI)**: ARMED đỏ "CHƯA", zone trống, nút `/arm`.
2. **Đang chạy**: ARMED/MODE xanh, hiện vị thế mở, nút `/disarm`.
3. **WEEK-HALT latch (Đ3)**: dòng đỏ "NGHỈ HẾT TUẦN — mở lại Monday-reset",
   hiện % vượt ngưỡng + chữ LATCH. PERM-HALT tương tự (đỏ, ghi "vĩnh viễn — cần /arm tay").

## Ràng buộc kỹ thuật cho R&D
- Panel = OBJ_LABEL/OBJ_BUTTON hoặc Comment() — PHẢI hiện được trong Strategy Tester visual
  (để duyệt giao diện bằng giả lập, không cần cắm live).
- % breaker hiển thị phải lấy TỪ CÙNG BIẾN mà logic breaker dùng để quyết định
  (không tính riêng 2 nơi — bài học panel HM0.4 hiển thị vượt ngưỡng, xem audit 24/07).
- Nút HALT ALL: bấm = đóng hết vị thế + perm-halt latch, có confirm 2 bước.
- Không lộ token/chat-id Telegram lên panel (Guardian NEVER-6).
