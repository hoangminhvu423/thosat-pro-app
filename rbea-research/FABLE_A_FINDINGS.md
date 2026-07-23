# RB_EA — FABLE-A FINDINGS + SPEC RESOLUTION v1.0-draft
Ngay: 2026-07-21 (phien dem) · Agent: Fable-A (Claude) · Trang thai: cho chu du an duyet

## 1. MA TRAN 12 NHANH (preregistered, data XAUUSD 2012-05 -> 2022-03, phi $0.35/lenh)

ARCH   TP   FILT |     n   WR%    avgR    totR    PF worstYr   yr+
------------------------------------------------------------------
H4PURE TRAV OFF  |   624  30.9  +0.072   +44.9  1.10   -14.2  5/11   <- nhanh goc, TAI LAP OK (vong truoc 629/+0.074)
H4PURE TRAV ON   |   440  34.5  +0.102   +45.0  1.15   -20.0  8/11   <- THANG
H4PURE MID  OFF  |   612  33.8  -0.029   -17.7  0.96   -16.2  3/11
H4PURE MID  ON   |   419  36.5  +0.030   +12.4  1.04   -17.7  7/11
H4PURE R2   OFF  |   652  35.1  -0.015   -10.0  0.98   -25.3  5/11
H4PURE R2   ON   |   450  36.4  +0.029   +13.0  1.04   -17.4  7/11
H4M15  TRAV OFF  |   680  26.9  +0.002    +1.7  1.00   -14.8  5/11
H4M15  TRAV ON   |   478  31.6  +0.078   +37.4  1.11   -10.7  6/11   <- a hau (worst-year tot nhat)
H4M15  MID  OFF  |   753  33.3  -0.051   -38.2  0.93   -17.6  3/11
H4M15  MID  ON   |   488  35.0  -0.012    -6.0  0.98   -10.4  4/11
H4M15  R2   OFF  |   759  35.6  -0.009    -7.1  0.99   -12.8  7/11
H4M15  R2   ON   |   492  37.2  +0.043   +21.3  1.06   -10.8  6/11

## 2. GIAI QUYET CAC MUC MO
- O1 (kien truc): CHON H4 THUAN. M15-trigger khong tang avgR (0.078 vs 0.102),
  chi giam worst-year. Giu M15-trigger lam OPTION giai doan 2, khong phai core.
- O2 (TP): CHON TRAVERSE (bien doi dien). Thang MID va 2R o ca 2 kien truc.
- O3 (trend filter): BAT — SMA200 H4, chan RANGE_SELL khi close>SMA, chan
  RANGE_BUY khi close<SMA. Cai thien NHAT QUAN o ca 6 cap so sanh (khong phai
  may man 1 nhanh). Luu y: data 10y la uptrend -> hieu ung filter co the la
  regime-dependence, PHAI xac nhan lai tren 21y (O8).
- O5 (UX): 2 hline RB_HI / RB_LO keo tha tren chart (lam duoc tu MT5 mobile)
  + lenh Telegram /arm de kich hoat vung. Da implement trong EA v0.1.
- O7 (breaker): default daily 3% / weekly 8%, input I_CloseOnBreaker de chu
  du an CHON dong-het hay giu-vi-the-voi-SL (cau hoi mo tu QTQ v1, gio la
  input ro rang thay vi mo ho).

## 3. NO CON LAI (blocker truoc Phase 3 hoan tat)
- [ ] Stress phi $0.50: script bi mat khi container sap — CHUA CHAY. Phai chay
      lai truoc khi dong spec (tieu chi Phase 0 yeu cau song sot phi 0.50).
- [ ] O8: chay lai toan bo ma tran tren XAU_30m_data.csv 21 nam (user zip+upload).
      Data 10y KET THUC 3/2022 — regime vang 2023-26 hoan toan chua test.
- [ ] O4: session filter theo gio — chua test.
- [ ] O6: vong doi vung (het han khi nao) — dang tam: het ngay hoac user xoa hline.
- [ ] Fable-B doc lap: chua co engine thu 2 doi chieu (moi co replication noi bo).

## 4. DA GIAO (dem 21/7)
- RB_EA_v0.1.mq5.txt (cung folder nay — DOI TEN bo .txt truoc khi compile):
  state machine + budget 3 lenh/ngay + gap 60' + whipsaw guard + DD breaker
  + Friday cleanup + persist GlobalVariable + Telegram 2 chieu
  (/status /arm /disarm /flat, whitelist 1 chat id, token qua input).
  CHUA COMPILE, CHUA AUDIT — bat buoc Phase 4 truoc khi len VPS demo.
  VPS: nho whitelist https://api.telegram.org trong Tools>Options>Expert Advisors.
- Trong chat (da present): trades_rangebreak.csv, backtest_rangebreak.py,
  backtest_multitf.py, RB_EA_Master_Spec_v0.1.md.

## 5. CHECKLIST SANG MAI CHO CHU DU AN (theo thu tu)
1. Duyet muc 2 (O1/O2/O3/O5/O7) -> chot spec v1.0 hoac veto
2. Zip XAU_30m_data.csv (Drive) -> upload vao chat -> chay O8 + stress 0.50
3. Quyet I_CloseOnBreaker (true/false) — cau hoi risk quan trong nhat con lai
4. Neu 1-3 xong: mo phien moi cho vai Fable-B (engine doc lap) roi moi compile
