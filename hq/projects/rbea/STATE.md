# STATE — RB_EA (cập nhật 2026-07-24 đêm)
## Vị trí hiện tại: P1 XONG → chờ P3 (G1/G2 của Sếp)
- **File chuẩn: `rbea-research/RB_EA_v0.31.mq5`** (v0.3 đã deprecated — có banner, KHÔNG dùng).
- Audit G3: v0.3 có 4 lỗi đỏ (nặng nhất: Donchian shift làm BTC auto 0 lệnh) → vá hết trong v0.31 →
  re-audit độc lập PASS. Hồ sơ: `AUDIT_G3_v03_20260724.md`.
- Phương án kỹ thuật đã duyệt: `EA_ENGINEERING_PLAN_v1.0.md` (P1✓ → P2 v0.4 module hóa → P3 G1/G2 Sếp
  → P4 verify_ea_log → P5 demo → P6 go/no-go).
- FTMO set-file cần nhớ: I_InitBalance BẮT BUỘC set ($ account); XAU semi magic 20260723 risk 0.15;
  BTC auto magic 20260724, I_AutoZone=true, I_RangeEnabled=false, I_FridayCleanup vô hiệu với AUTO.
## Forward monitoring đang chạy
- BTC shadow: routine đêm 20:00 UTC. XAUT proxy: feed GitHub Actions 4h/lần (nhánh data-gold) +
  xaut_shadow.py chạy trong phiên bất kỳ. XAU CFD: chờ Sếp export MT5 (~2 tuần/lần) → đo tracking-error.
## Việc kế tiếp
1. Sếp: compile v0.31 (G1) + Strategy Tester visual 3 tháng 2 profile (G2).
2. Claude: P2 — v0.4 module hóa + Panel/Logger/Notifier/Watchdog (diff logic = 0), sau khi G1/G2 sạch.
3. Version sau nhớ 2 ghi chú vàng của re-audit: halt-file thêm login; note /arm khi đè GV cũ.
