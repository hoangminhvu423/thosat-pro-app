# SETUP-DECAY STUDY — Hieu luc setup intraday theo thoi gian (2026-07-22)
Data: XAU M30 2004-2025 · Proxy: vung snapshot DAU NGAY (nhu ve buoi sang), theo doi ca ngay tren M30
Config study YEU HON production co y (khong break-mode, khong budget, moi cu cham deu danh,
khong filter) -> avgR tuyet doi am; GIA TRI nam o pattern TUONG DOI. 1,453 ngay-vung, 1,782 cu cham.

## A. EDGE THEO THOI GIAN CHO (vung ve -> cu cham)
  0-2h: -0.188 | 2-4h: -0.243 | 4-8h: -0.265 | 8-12h: -0.276 | 12-24h: -0.060
KHONG PHAI decay don dieu — cham muon TOT HON cham som/giua.

## A2. KHU NHIEU PHIEN (gio broker cua cu cham) — day moi la bien that
  Asia 00-08h: -0.248 | London 08-14h: -0.226 | NY 14-20h: -0.066 | Late 20-24h: -0.035
"Cho 8-12h" xau vi no TRUNG gio London breakout, khong phai vi vung "cu".

## B. SO LAN CHAM (cung vung cung ngay cung huong) — don dieu tang
  Lan 1: -0.201 (n=1036) | Lan 2: -0.146 (n=462) | Lan 3+: +0.016 (n=284)
Vung MAY ve: cham dau nguy hiem nhat (lan nhieu vung sap vo); vung song sot 2+ cham
la vung tu chung minh. NGUOC voi loi khuyen "first touch is best" — voi vung co hoc.

## A3. KET HOP (exploratory, can xac nhan): vung da cham 3+ VA cham trong 12-24h:
  **+0.198R (n=209)** — duong manh ngay ca trong config bi tuoc het filter.
  Cung vung do cham som 4-12h: -0.472. => Vung sang song sot qua London roi
  quay lai trong phien My/late = cohort tot nhat toan study.

## C. TIME-STOP lenh dang mo (ky vong R CON LAI neu giu tiep)
  sau 4h: -0.099 | 8h: -0.051 | 16h: +0.042 | 24h: +0.030 | 48h: -0.100
Phi tuyen: 8h dau la vung chop (gia tri am), 16-24h duong (lenh song qua chop
thuong dang di dung), sau 48h thanh xac song. p50 tuoi tho lenh = 6.5h.

## KET LUAN HANH DONG
1. HUY SETUP THEO SU KIEN, KHONG THEO GIO: chi huy khi (a) nen H4 dong ngoai bien
   (da co trong L3/L4), (b) sang ngay moi chua kich hoat -> VE LAI. Khong huy chi vi
   "cho lau" — vung sang chua cham den chieu la cohort TOT, khong phai hong.
2. Hieu luc thuc te: trong pham vi 1 ngay giao dich (~24h). Qua ngay -> redraw.
3. Cham dau tien trong gio Asia/London tren vung CHUA chung minh: bo qua hoac
   giam size. Diem vao dep nhat: cham lan 2-3, phien My.
4. TIME-STOP: giu toi thieu 16-24h (dung cat trong vung chop), cat cung ~48h.
   => v0.2 doi I_MaxHoldBars tu 48 nen H4 (192h — qua dai) xuong 12 nen (48h).

## CAVEAT
- A3 la lat cat exploratory sau khi nhin A+B (khong preregistered) -> can vong
  xac nhan truoc khi code cung vao EA. A/B/C la preregistered.
- Vung nguoi ve (co cau truc) co the khac vung may: "cham dau" cua nguoi co the
  tot hon — CHUA DO DUOC, se do bang journal forward.
- Gio phien theo broker GMT+2/3; 1 thi truong (gold) — chua test cross-market.
