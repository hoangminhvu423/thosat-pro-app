# RB_EA — STATE (2026-07-23, sau R7a-g)
## ĐANG Ở ĐÂU
- Thiết kế production CHỐT: rbea-research/RB_EA_MASTER_SPEC_v1.0.md (2 sleeve: XAU-SEMI + BTC-AUTO, risk 0.15/0.15, FTMO Swing).
- Code: RB_EA_v0.3.mq5 (auto-mode + range-toggle + total-breaker permHalt). CHƯA compile/audit/demo.
- Số đã validate: portfolio XAU+BTC payout 2.3-3.5%/năm @ P(chết 2y) 2-6% (R7g, corr 0.024).
## VIỆC TIẾP THEO (thứ tự)
1. [SẾP] G1 compile MetaEditor + G2 Strategy Tester visual.
2. [PHIÊN MỚI] G3 ea-code-audit v0.3 — 3 flag chờ soi: buy-khi-giá-vượt-trigger · lệch 1-vị-thế-vs-overlap · công thức daily FTMO.
3. [VPS] G4 demo ≥4 tuần/≥40 lệnh (kỳ vọng 10-13 lệnh/tháng ±40%) + journal R1 song song (JOURNAL_R1_schema.md).
4. G5 go/no-go → FTMO Swing.
## ĐÃ CHỐT / ĐÃ BÁC: xem rbea-research/PROJECT_STATE_HANDOFF.md + CROSSVAL_CORRECTION + các PREREG R7c/d/g.
