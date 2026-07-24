---
name: guardian-rules
description: Cổng an toàn BẮT BUỘC khi thao tác trên VPS MT5 live (Exness demo #413885821, 36-chart). Dùng LUÔN trước mọi thao tác compile/deploy/kill/close trên VPS. Các quy tắc dựng sau sự cố production 2026-06-10.
---

# Guardian Rules — cổng an toàn VPS (KHÔNG NGOẠI LỆ)

> Dựng sau sự cố 2026-06-10 (một agent phá hỏng VPS 36-chart).

## 🔴 NEVER
1. **KHÔNG force-kill MT5** (`taskkill /F /IM terminal64.exe`) khi chưa có user approval rõ ràng — mất chart config + Global Variables trong RAM → vỡ trailing/breaker đang chạy.
2. **KHÔNG MetaEditor `/compile` trực tiếp** — xoá `.ex5` cũ trước khi compile; fail = mất binary. Dùng `safe-compile`.
3. **KHÔNG SFTP push thủ công** — dùng pipeline `deploy-ea`.
4. **KHÔNG kết luận "có bug"** trước khi đọc `SYSTEM_BRIEF.md` + `DECISION_LOG.md` (tại `/Users/mailien/.gemini/antigravity/scratch/TQT/`).
5. **KHÔNG DCA / martingale / grid** — bao giờ.
6. **KHÔNG lộ** password VPS / Telegram token ra UI/log.

## 🟢 ALWAYS
1. **Health-check sau mỗi compile/deploy** (skill `vps-health-check`).
2. **Đọc log MT5 qua PowerShell Unicode** (skill `read-mt5-logs`).
3. **Magic tách biệt** (707001 calendar · 707002 rsi2) tránh đè trade DB.
4. **Sửa vị thế live cần user duyệt** trước khi thực thi (trim/close).
5. **Backtest-validate trước deploy** thay đổi logic.

## Toàn quyền được cấp
- Trên DEMO VPS: tự chủ thao tác, MIỄN không xoá gì trên local Macbook và tuân Guardian trên.
