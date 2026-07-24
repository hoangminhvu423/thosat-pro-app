# STATE — RB_EA (cập nhật 2026-07-24 tối — phiên R&D cloud)
## Vị trí hiện tại: v0.33 chờ G1+G2-BTC lại (15'), XAU SEMI visual (Sếp), rồi mới cắm
- **File chuẩn MỚI: `rbea-research/RB_EA_v0.33.mq5`** — vá finding CAM của re-audit v0.32 (race login=0
  khi VPS reboot: deferred init) + version 0.330 (hết warning 68) + log halt từ GV. Hồ sơ đầy đủ:
  `rbea-research/AUDIT_v032_20260724.md` (re-audit v0.32 PASS có điều kiện + điều tra perm_halt).
- **Bí ẩn perm_halt=1 ĐÃ GIẢI**: breaker bắn ĐÚNG THIẾT KẾ khi equity tụt dưới neo 4,600 do Sếp rút
  tiền/lệnh tay −763 (EA không phân biệt rút tiền với thua lỗ). "Âm thầm" vì TG token trống.
  → R3 ÁP NGAY: mọi lần rút tiền phải theo quy trình trong AUDIT_v032 (disarm→rút→chỉnh neo→dọn halt
  có chủ đích→re-arm). R1/R2 (tự nhận cash-flow, I_PropMode) vào backlog v0.4/P2.
- Cửa sổ deploy: việc kế tiếp = pull → compile v0.33 (kỳ vọng 0 error 0 warning) → G2 BTC AUTO headless
  lại → cập nhật profile RBEA sang v0.33 → chờ XAU SEMI visual (Sếp, theo G2_KIT trỏ v0.33) → checklist
  điều kiện 1-5 trong AUDIT_v032 mục cuối → mới attach + bật algo.

## [Lịch sử chiều 24/07 — cửa sổ deploy]
- **File chuẩn MỚI: `rbea-research/RB_EA_v0.32.mq5`** (vá H1/H2/H3 halt-file; G1 0-error; BTC AUTO
  3 tháng 7 lệnh / 18 tháng 13 lệnh PF 2.24, risk cap đúng 0.15%). Chi tiết: G2_FINDINGS_20260724.md.
- Còn: (1) Sếp chạy XAU SEMI visual theo G2_KIT (đã trỏ v0.32); (2) sau đó mới bàn cắm live.
- Bal account 265921030 = 3,909: Sếp XÁC NHẬN là RÚT TIỀN (không phải lỗ). Khi cắm RB_EA:
  I_InitBalance chốt theo số dư tại ngày cắm (~3,900).
- Hạ tầng VPS đã rà + fix 24/07 (watchdog vá + 5 task mồ côi/mìn disable + cờ bảo trì): hq/VPS_HATANG_20260724.md.
  Chờ Sếp quyết: autologon sau reboot (lỗ hổng EA chết im lặng), bot Telegram riêng cho RB_EA, terminal FTMO.
- Cũ (đã xử lý): ⛔ G2 FAIL sáng 24/07 do halt-file dùng chung — gốc đã vá trong v0.32:
- G2 (2026-07-24): BTC AUTO headless 0 lệnh cả cửa sổ 3 tháng LẪN 18 tháng (tham số đúng, history 100%).
  NGUYÊN NHÂN: file halt Common `RBEA2_BTCUSD_20260724_halt.bin` perm_halt=1 → EA halt ngay OnInit → 0 lệnh.
  Sharp-edge re-audit đã cảnh báo (halt-file chung symbol+magic, tester+live+2acc đè nhau). Hồ sơ:
  `G2_FINDINGS_20260724.md` (+ Drive INBOX_FINDINGS). Đề xuất vá cho v0.4 (thêm login vào tên file + log lý do halt).
- ⚠️ RB_EA đang gắn 2 chart LIVE nhưng perm_halt=1 → bật Algo cũng KHÔNG trade. CHƯA gỡ (chờ Sếp quyết).
- CẤM xoá file halt để chữa rồi deploy khi chưa hiểu vì sao perm_halt=1 (Guardian).
- G1: compile VPS 0 error / 1 warning (warning 68 — format chuỗi version, metadata thuần).
  **Sếp PHÊ DUYỆT chấp nhận warning 24/07** → G1 đạt. Hồ sơ: G1_ERRORS.md. Nhắc R&D: v0.4 sửa
  `#property version "0.310"` cho sạch 0/0 (1 dòng, gộp vào P2 module hóa).
- G2: mọi thứ đã dựng sẵn — `.ex5` ở staging + 2 set-file trong Presets terminal Exness.
  **Sếp làm theo `G2_KIT.md`** (RDP 15': 2 run visual + checklist mắt người).
- Sau G2 đạt: cửa sổ deploy soạn checklist cắm live; bước attach chart + AutoTrading do Sếp bấm.
  Account 4,600 USD ĐÃ XÁC ĐỊNH: Exness REAL #265921030 "botea" (terminal Program Files) —
  Sếp đã gỡ HM0.4 khỏi chart 24/07 09:07, account phẳng 0 vị thế, eq 4,673.28 → sẵn sàng nhận RB_EA sau G2.
- PANEL v0.4: Sếp PHÊ DUYỆT mockup 24/07 → spec bắt buộc cho P2: `PANEL_SPEC_v04.md`.
- Audit HM0.4 (panel "vượt breaker"): breaker ĐÚNG, chỉ 2 finding hiển thị (V-A day-baseline đóng băng
  khi halt, V-B emoji ⛔ render thành □) — hồ sơ Drive INBOX_FINDINGS/AUDIT_HM04_PANEL_20260724.md.
- Terminal FTMO trên VPS: Authorization failed + 0 EA gắn — chạy rỗng, chờ Sếp xử lý account.
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
