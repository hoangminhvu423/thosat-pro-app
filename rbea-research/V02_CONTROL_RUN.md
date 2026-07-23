# V02_UPGRADE_CONTROL_RUN — Ket qua AM quan trong (2026-07-22)
Preregister: cay 2 finding tu decay/mirror study vao production RB_EA
(chan RANGE gio London 08-14 + time-stop tach sleeve 48h/24h). Ky vong: cai thien.

## KET QUA: CA HAI DEU KHONG CAI THIEN — MOT CAI PHA HOAI NANG
                                  n     avgR    totR    PF  worstYr
fOFF BASELINE                  1272   +0.078   +98.8  1.10   -16.1
fOFF +chan London range        1136   +0.026   +29.3  1.04   -18.4   <- TE HAN
fOFF +timestop 48h/24h         1340   +0.051   +68.6  1.08   -20.4   <- te hon
fON  BASELINE                   896   +0.099   +89.1  1.14   -20.0
fON  +chan London range         856   +0.101   +86.3  1.15   -16.5   (hoa, DD dep hon chut)
fON  +CA HAI                    871   +0.095   +82.7  1.17   -14.1   (hoa, PF/DD dep hon chut)

Soc nhat: 136 lenh RANGE gio London bi chan trong fOFF dong gop +0.51R/lenh —
gio London voi PRODUCTION la lenh TOT, nguoc 180 do voi study!

## VI SAO — LESSON-04 can chinh minh
Study dung vung SNAPSHOT DAU NGAY + entry M30 (proxy cua workflow NGUOI ve tay).
Production dung vung ROLLING 20-nen H4 cap nhat lien tuc + entry tai close H4.
Cham gio London vao vung-sang-da-cu = dung chan lu (study, -0.23).
Cham gio London vao vung-rolling-vua-cap-nhat = vung tuoi phan anh gia moi (production, +0.51).
=> Finding khong chuyen duoc NGAY CA trong cung mot chien luoc khi config vung khac nhau.
LESSON-04 mo rong: finding la thuoc tinh cua (thi truong x payoff x CO CHE XAY VUNG).

## QUYET DINH CHO v0.2 (chot)
1. KHONG dua session-block va time-stop-ngan vao logic auto cua RB_EA.
2. v0.2 chi fix F1 dung nhu da validate: implement time-stop 48 NEN H4 (192h)
   y het backtest (khong phai 48 GIO). + F2 (budget khi lot=0).
3. Cac finding decay/mirror van SONG — nhung dia chi ap dung cua chung la
   TANG NGUOI cua he ban tu dong (nguoi ve vung buoi sang, vao lenh intraday):
   - Playbook nguoi: than trong cham dau gio London tren vung sang chua chung minh;
     cham lan 2-3 phien My = cohort vang; vung qua ngay -> ve lai.
   - EA co the gui Telegram WARNING mem khi ARM vung trong gio London (khong chan).
4. Cho SC6: cac gia thuyet (uu tien break London/NY, POI trinh, time-stop 24h)
   giu nguyen trang thai GIA THUYET — bat buoc test tren chinh logic SC6 trong
   Strategy Tester truoc khi dung. Lesson-04 da chung minh 2 lan trong 1 ngay.
