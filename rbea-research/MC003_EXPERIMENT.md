# MC003_EXPERIMENT — Shock Absorption Regime (2026-07-22)
Data: XAU M30 2004-2025. Soc = nen M30 range >= 2.5xATR(20). n=8,443 (~607/nam).
CONTINUATION(N) = dich chuyen sau N nen theo huong soc / bien do soc.
Preregistered: P1 soc London tiep dien > phien muon/Asia | P2 phien muon hap thu |
P3 cham range ngay lambda am > ngay lambda duong. KET QUA: 0/3 DUNG CHI TIET.

## P1+P2 — CA HAI DAO NGUOC
phien          n     N=4 mean/med    N=12 mean/med   N=24 mean/med
Asia 00-08    603   +0.011/-0.048   +0.011/-0.034   +0.135/-0.019
London 08-14 1361   +0.025/-0.013   +0.000/-0.042   -0.052/-0.121  <- HAP THU MANH NHAT
NY 14-20     6020   +0.016/-0.004   +0.013/-0.006   +0.005/-0.014
Late 20-24    459   +0.066/+0.011   +0.085/+0.108   +0.145/+0.169  <- KHUECH DAI MANH NHAT
Soc gio London bi PHAI (median -0.121 sau 12h); soc phien muon CHAY TIEP (+0.169).

## Doi chieu tuong phan voi MIRROR_STUDY (London breakout tot nhat +0.229):
KHONG mau thuan — hai doi tuong khac nhau:
- Mirror: pha vo BIEN CAU TRUC (mep box H4) xac nhan bang close -> London tot nhat
- MC003: nen soc THO bat ky vi tri (phan lon giua range, spike tin) -> London fade manh nhat
=> GIA THUYET SUA DOI (interpretive, chua prereg): so phan cu soc = VI TRI so voi
cau truc x DO SAU thanh khoan. Thanh khoan sau (London) fade soc vo cau truc nhung
day tiep soc pha cau truc; thanh khoan mong (late) de soc chay bat ke cau truc.
Day la tang co che sau hon cua MC-001/MC-002 — hop nhat duoc ca 3 the.

## P3 — KHONG DON DIEU (bat ngo lon nhat)
Cham range vung-sang theo tercile lambda-24h-truoc (n=1,454 + 328 khong soc):
  HAP THU manh  [-4.79..-0.32]: avgR=-0.157 WR=21.3%
  TRUNG TINH    [-0.32..+0.21]: avgR=-0.027 WR=22.3%   <- TOT NHAT
  KHUECH DAI    [+0.21..+4.74]: avgR=-0.233 WR=20.4%   <- TE NHAT
  KHONG CO SOC 24h            : avgR=-0.211 WR=19.2%   <- cung te (tape chet)
Du doan "hap thu = tot cho range" SAI: moi truong tot cho range la TRUNG TINH
(dong chay 2 chieu co trat tu). Hap thu du doi = whipsaw quet SL; khuech dai =
trend can; tape chet = vung vo nghia. Spread 0.21R giua trung tinh va khuech dai
la QUAN SAT DUOC TRUOC KHI VAO LENH -> co gia tri cho workflow nguoi ve vung sang.

## HANH DONG
1. The MC-003 cap nhat: co che goc SAI, thay bang "vi tri-vs-cau truc x do sau
   thanh khoan"; trang thai TESTED, du doan moi can prereg vong sau (R7b):
   tach soc THEO vi tri (trong range vs tai bien) du doan London se dao dau giua 2 nhom.
2. Ung dung tang NGUOI (khong dua vao auto — theo bai hoc V02): chi bao lambda-24h
   hien thi luc ARM buoi sang; uu tien ARM range khi lambda trung tinh [-0.3..+0.2].
3. Ghi vao lich su du doan MC-003: Fable 0/3 — co che can dai tu, khong phai data can them.
