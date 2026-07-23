# 02_META_LESSONS — Bai hoc phuong phap luan (moi agent PHAI doc, cap nhat 2026-07-22)

## LESSON-01: Pipeline kiem chung KHONG tu sinh cau hoi
Toan bo bo may (2 engine doc lap, ma tran preregistered, stress phi, cross-val)
chi TRA LOI cau hoi duoc dua vao — khong DE ra cau hoi. Cau hoi "setup hieu luc
bao lau" (Sep hoi 22/07, nghe tam thuong) phoi ra khoang cach 0.67R/lenh giua
cohort tot nhat va te nhat — GAP 4 LAN edge cua ca he thong (+0.15R gross).
=> Quy tac: moi cau phan cua spec deu la GIA DINH cho den khi co vong do rieng,
ke ca cau phan trong hien nhien nhat. Cac gia dinh CHUA tung bi do trong RB_EA:
buffer 0.25xATR, gap 60', box 20 nen, TOUCH 0.15xATR.
Nguon cau hoi tot nhat: trai nghiem ngoi canh setup that cua NGUOI (sot ruot,
kho chiu, thoi quen) — may khong co trai nghiem nay. Phan vai dung cua he
ban-tu-dong lap lai o tang meta: nguoi hoi, may do.

## LESSON-02: Selection effect la co che thong nhat cua ca 3 phat hien setup-decay
(1) Cham dau te nhat vi mau la ro tron vung-that + vung-sap-vo chua phan loai;
den cham 3+ thi vung gia da tu loai khoi mau (survivorship trong ngay).
(2) Phien quyet dinh, khong phai gio cho: range trade = short vol, vol khong
rai deu trong ngay; cham gio London = ban bao hiem truoc bao co lich.
(3) Time-stop phi tuyen = 2 selection effect nguoc chieu: song qua chop 8h dau
= lenh tot tu chung minh (+); qua 48h = luan de goc het han (-).
=> Truc giac trader lay mau theo DO DANG NHO; thong ke lay mau theo TAN SUAT.
Loi khuyen sach vo ("first touch is best", "vung nguoi la vung yeu") sai voi
vung co hoc — kiem chung voi vung nguoi ve bang journal forward.

## LESSON-03: Cau truc vung co NGUONG KICH THUOC toi thieu (do 22/07, 3 khung)
Vung M30 (box 10h): moi pattern BIEN MAT — cham 1/2/3+ deu ~-0.34 phang liet,
A3 golden cohort chet (-0.354). Vung M30 la hinh chu nhat nhieu, khong mang tin.
Vung H1 (box 20h): cau truc XUAT HIEN — cham monotonic -0.243/-0.076/+0.031,
gradient phien sach (Asia -0.26 -> Late +0.11), A3 = +0.128 (n=467).
Vung H4 (box 80h): manh nhat per-trade — A3 = +0.198 (n=209).
=> Nguong ~1 chu ky ngay day du (>=20h): vung phai duoc CA 3 phien thu thach
it nhat 1 lan moi mang thong tin. Vung nho hon chua tung bi test boi day du
cac loai flow -> chua phan loai duoc that/gia.
H1 dang chu y: avgR/lenh thap hon H4 nhung mau GAP DOI -> tong co hoi tuong
duong (H1: 467x0.128=~60R vs H4: 209x0.198=~41R tren 21 nam). H1 co the la
diem ngot cho intraday: du cau truc + du tan suat.
Time-stop khac nhau theo khung: H4 cat ~48h; H1 gia tri giu van duong o 48h
(+0.165, n=100 — mau mong, can xac nhan).

## Tham chieu du lieu goc
INBOX_FINDINGS/SETUP_DECAY_STUDY_20260722.md (study goc H4 + caveat prereg)
Data: XAU_30m_data.csv 2004-2025. Config study yeu hon production co y —
pattern tuong doi la doi tuong, khong phai muc tuyet doi.
