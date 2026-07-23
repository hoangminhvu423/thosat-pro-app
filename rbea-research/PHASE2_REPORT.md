# RB_EA — PHASE 2 REPORT (Fable-B + Stress + Data research + Pre-audit)
Ngay: 2026-07-21 dem muon · Trang thai: Phase 2 PASS, Phase 4 co finding dau tien

## 1. FABLE-B CROSS-VALIDATION: PASS
Engine viet lai DOC LAP tu spec chu (vong lap event-driven, ATR Wilder de quy
tu viet, rolling box bang deque — khong dung pandas nhu Fable-A).
Doi chieu nhanh production H4PURE/TRAV:
  filterOFF: FableB n=629 avgR=+0.074 | FableA n=624 avgR=+0.072 -> dN=0.8%, dAvg=0.002 OK
  filterON : FableB n=440 avgR=+0.102 | FableA n=440 avgR=+0.102 -> TRUNG TUYET DOI
Ket luan: hai engine doc lap hoi tu — logic spec khong mo ho, khong bug 1 phia.

## 2. STRESS PHI $0.50: PASS (tieu chi Phase 0)
  filterON @ $0.50: avgR=+0.074, PF=1.10, totR=+32.7 — VAN DUONG
  filterOFF @ $0.50: avgR=+0.044, PF=1.06 — van duong nhung mong hon
Nhanh production song sot phi tang 43%. (Van tren data 10y — cho 21y de final.)

## 3. DATA REGIME MOI (2022-2026): tim thay nguon, sandbox khong tai duoc
- HuggingFace: ZombitX64/xauusd-gold-price-historical-data-2004-2025 (M15, den 10/2025)
- Kaggle: novandraanugrah/xauusd-gold-price-historical-data-2004-2024 (cap nhat 2026)
Ca hai domain bi chan trong sandbox (chi cho GitHub/PyPI). Duong di:
chu du an tai 1 trong 2 -> zip -> upload chat, HOAC dung XAU_30m_data.csv tren PC.

## 4. PRE-AUDIT RB_EA v0.1 — FINDING DAU TIEN (Phase 4 se soi tiep)
[🔴 RBEA-F1] TIME-STOP KHONG DUOC IMPLEMENT: input I_MaxHoldBars=48 co khai bao
  nhung KHONG co logic dem nen/dong lenh trong EA. Backtest CO time-stop 48 nen
  (~4.6% lenh thoat kieu TIME) -> live se lech backtest: lenh range ket vo thoi han
  neu khong cham SL/TP. Muc do: lam sai expectancy da validate. Fix o v0.2:
  luu bar-count vao GlobalVariable hoac tinh tu POSITION_TIME.
[🟡 RBEA-F2] Budget BREAK bi tru ca khi CalcLot tra 0 (lot < min) — dot dan
  khong no. Fix: chi tru budget khi MarketIn thanh cong.
[🟡 RBEA-F3] Parse JSON Telegram bang StringFind tho — du dung cho lenh don,
  nhung se vo neu message chua ky tu dac biet. Chap nhan duoc v0.1, ghi nhan.

## 5. TRANG THAI PIPELINE
Phase 0 preregister ......... CHO chu du an chot (O4/O6 con mo, tieu chi da de xuat)
Phase 1 backtest final ...... 10y XONG (ma tran 12 nhanh); 21y CHO data
Phase 2 adversarial ......... PASS (muc 1 + 2 tren)
Phase 3 code MQL5 ........... v0.1 XONG, can v0.2 fix F1/F2
Phase 4 audit ............... BAT DAU (3 finding tren); can instance tuoi soi full
Phase 5 demo forward ........ chua — SAU khi v0.2 + audit xong. Guardian Rules ap dung.
Phase 6 go/no-go ............ chua
