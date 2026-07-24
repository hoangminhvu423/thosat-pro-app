# STATE — RB_EA (cập nhật 2026-07-24 chiều — cửa sổ deploy)
## Vị trí hiện tại: G1 ĐẠT (phê duyệt) → chờ Sếp chạy G2 theo G2_KIT.md (~15 phút)
- G1: compile VPS 0 error / 1 warning (warning 68 — format chuỗi version, metadata thuần).
  **Sếp PHÊ DUYỆT chấp nhận warning 24/07** → G1 đạt. Hồ sơ: G1_ERRORS.md. Nhắc R&D: v0.4 sửa
  `#property version "0.310"` cho sạch 0/0 (1 dòng, gộp vào P2 module hóa).
- G2: mọi thứ đã dựng sẵn — `.ex5` ở staging + 2 set-file trong Presets terminal Exness.
  **Sếp làm theo `G2_KIT.md`** (RDP 15': 2 run visual + checklist mắt người).
- Sau G2 đạt: cửa sổ deploy soạn checklist cắm live; bước attach chart + AutoTrading do Sếp bấm.
  CÒN THIẾU: account 4,600 USD nằm ở terminal nào (Exness tree hay cài mới?) — Sếp cho biết khi G2 xong.
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

## QUYẾT ĐỊNH MỚI (Sếp, 2026-07-24 sáng): deploy sớm lên account CÁ NHÂN ~4,600 USD
- Sếp chấp nhận rút gọn: KHÔNG chờ G4 demo 4 tuần cho account cá nhân này (tiền cá nhân, không phải quỹ).
- **G1 + G2 vẫn BẮT BUỘC** trước khi cắm (đã thống nhất — 2 gate này gần như miễn phí, ~1 giờ).
- Chốt an toàn khi cắm: I_InitBalance=4600 · I_RiskPct=0.15 · Telegram alert verify trước khi rời máy ·
  tuần đầu checklist HẰNG NGÀY · mọi số liệu 4 tuần đầu coi như G4-trả-phí-thật, đối chiếu shadow như thường.
- Nếu G1 ra lỗi compile: KHÔNG tự sửa logic ở cửa sổ deploy — báo lỗi về repo (commit message hoặc file
  hq/projects/rbea/G1_ERRORS.md) để phiên R&D vá theo vòng audit.
