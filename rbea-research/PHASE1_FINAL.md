# RB_EA — PHASE 1 FINAL: BACKTEST 21 NAM (2004-2025)
Ngay: 2026-07-22 · Engine: Fable-B (da cross-validate voi Fable-A) · Data: XAU_30m_data.csv cua chu du an
Nhanh production: H4PURE / TP=TRAVERSE / budget 3 lenh-ngay / gap 60' / phi $0.35

## KET QUA TONG (243,821 nen M30 -> 32,290 nen H4)

filterON  : n=896  WR=35.4% avgR=+0.099 totR=+89.1 PF=1.14 | 18/22 nam duong
            nam am: 2007(-1.7) 2018(-20.0) 2021(-9.5) 2023(-3.8)
filterOFF : n=1272 WR=31.4% avgR=+0.078 totR=+98.8 PF=1.10

## OUT-OF-SAMPLE THUAN (quyet dinh O1-O3 chot tren 2012-2022, hai doan kia chua tung nhin)

              filterON              filterOFF
2004-2012 OOS +0.122R PF1.18 (319)  +0.077R PF1.10 (438)
2012-2022 DEV +0.101R PF1.14 (443)  +0.074R PF1.10 (629)
2022-2025 OOS +0.039R PF1.06 (134)  +0.089R PF1.12 (205)   <-- DANG CHU Y

## STRESS PHI $0.50: PASS ca hai
filterON  @0.50: avgR=+0.070 PF=1.10
filterOFF @0.50: avgR=+0.044 PF=1.06

## DOI CHIEU TIEU CHI PHASE 0 (preregistered)
[PASS] net avgR >= 0 tren 21y ......... +0.099 (ON) / +0.078 (OFF)
[PASS] PF >= 1.05 ..................... 1.14 / 1.10
[PASS] khong nam nao < -30R ........... worst = -20.0R (2018, filterON)
[PASS] song sot phi $0.50 ............. PF 1.10 / 1.06

## FINDING QUAN TRONG NHAT — TREND FILTER LA REGIME-DEPENDENT
Dung nhu caveat da preregister: filterON thang lon o 2004-2012 (+0.122) nhung
YEU HAN o regime bull 2022-2025 (+0.039), trong khi filterOFF on dinh dang kinh
ngac qua CA BA doan (+0.077/+0.074/+0.089 — gan nhu phang).
=> filterON: ky vong cao hon, phu thuoc regime. filterOFF: ky vong thap hon
   nhung robust hon. Day la quyet dinh TRADE-OFF cua chu du an, khong phai
   quyet dinh ky thuat. De xuat: giu I_TrendFilter lam input, default OFF
   (uu tien robust), bat ON khi chu du an danh gia regime khong phai bull manh.

## LUU Y MAU
~43 lenh/nam (ON) / ~60 lenh/nam (OFF) — dung canh bao "thin trade count":
forward demo can toi thieu 40 lenh (~6-9 thang) truoc khi ket luan.
2022-2025 OOS chi co 134-205 lenh — PF 1.06 cua filterON o doan nay chua du
phan biet voi hoa von. KHONG duoc doc thanh "chac chan co edge o regime moi".

## TRANG THAI: Phase 1 DONG. Con lai truoc demo:
1. v0.2 fix RBEA-F1 (time-stop thieu) + F2 (budget tru khi lot=0)
2. Chu du an quyet: I_TrendFilter default + I_CloseOnBreaker
3. Phase 4 audit instance tuoi -> compile -> VPS demo (Guardian Rules)
