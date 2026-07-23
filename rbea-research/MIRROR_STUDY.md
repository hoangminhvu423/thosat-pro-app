# MIRROR STUDY — 3 lat cat cho entry MOMENTUM kieu SC6 (2026-07-22)
Cung data (XAU 2004-2025), cung vung H4 dau ngay. Entry: M30 dong ngoai bien
+0.25*ATR, than nen thuan huong. SL=1*ATR, TP=3*ATR. n=726 cu pha xac nhan.
Du doan preregistered: phien DAO DAU (dung) | tested-count: khong du doan | giu keo dai duong (SAI).

## A2. PHIEN — DAO DAU HOAN HAO so voi range
              RANGE (short-vol)   BREAKOUT (long-vol)
Asia 00-08h        -0.248              +0.096  (yeu nhat — thanh khoan mong, pha de gia)
London 08-14h      -0.226              +0.229  (MANH NHAT — doi xung gan nhu guong: -0.226 vs +0.229)
NY 14-20h          -0.066              +0.168
Late 20-24h        -0.035              +0.178
=> Cung mot ban do volatility, hai chien luoc doc nguoc dau. Filter "tranh London"
la thuoc bo cua RB_EA nhung la thuoc DOC cua SC6. LESSON-04 xac nhan bang so.

## B'. BIEN BI THU TRUOC KHI VO — cung DAO so voi touch-count cua range
0 lan (vo tho): +0.229 (n=166) | 1 lan: +0.183 (n=344) | 2+ lan: +0.112 (n=216)
Range: cham cang nhieu cang tot (+survivorship). Breakout: vo THO tot nhat —
bien chua tung duoc phong thu ma vo = xung luc that; bien bi thu nhieu lan =
dong mean-revert manh dang hap thu, pha xong de bi day nguoc.
(Nguoc voi sach TA pho thong "test nhieu = level yeu = break sach".)

## C. GIA TRI GIU TIEP — du doan cua Fable SAI
sau 8h: +0.078 (72% con mo) | sau 24h: -0.159 (48%) | sau 48h: -0.124 (33%)
Du doan: trend giu cang lau cang duong. THUC TE: momentum HET HAN NHANH HON range
(range duong den 24h, cat 48h; momentum duong den ~8h, am tu 24h).
Ly giai: luan de breakout la TIEP DIEN NGAY LAP TUC — khong tiep dien trong 1 ngay
= luan de fail; lenh "con mo sau 24h" voi TP=3ATR la nhom tu-chon-loc-xau (chua
du luc cham TP = ket). Caveat: hinh dang C mot phan la artifact cua TP cap 3ATR;
voi he KHONG TP (trend-following thuan) can do rieng — CHUA DO.
=> Time-stop de xuat: momentum-co-TP ~24h; range ~48h. NGUOC voi truc giac.

## Tong quat (LESSON-04, da them vao 02_META_LESSONS):
Cac finding vi cau truc KHONG phai thuoc tinh cua thi truong — chung la thuoc tinh
cua CAP (thi truong x loai payoff). Session, tested-count, hold-time DEU dao dau
hoac doi hinh dang khi chuyen tu short-vol sang long-vol. Chuyen finding giua
hai chien luoc khac payoff ma khong do lai = loi look-ahead mem.
Ghi chu them: breakout XAU duong o MOI phien (+0.10..+0.23 truoc filter) —
nhat quan voi viec sleeve BREAK la sleeve khoe nhat cua RB_EA va voi ho so
FTMO cua Sep (edge nam o duoi phai, RRR cao).
