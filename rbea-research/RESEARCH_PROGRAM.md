# 04_RESEARCH_PROGRAM.md — Chuong trinh nghien cuu co che (cho agent local + subagent)
Ban hanh 2026-07-22 · Chu du an: Sep · Dieu phoi: agent local MacBook goi subagent theo phan vai duoi day
Nguyen tac toi cao: CO CHE DI TRUOC, PHEP DO DI SAU. Chi do o nao co du doan viet
truoc. Moi vong: preregister -> chay -> ghi the MC -> Fable-B doc lap doi chieu neu
ket qua se duoc dua vao EA. Chong data-mining: khong quet luoi o; du doan sai = ghi
vao Lich su du doan cua the, khong xoa.

## A. TAI SAN HIEN CO (input cho moi subagent — doc truoc khi lam gi)
- Data: XAU_30m_data.csv 2004-2025 (243k nen M30, tren may Sep + da dung o cloud)
- Engine: fableB_independent.py / final_21y.py (pure stdlib, da cross-validate),
  setup_decay.py, decay_multitf.py, mirror_sc6.py (Sep co the xin lai code tu chat log)
- Docs: 01_PROJECT_STATE, 02_META_LESSONS (L01-L04), 03_MECHANISM_CARDS (template
  + MC-001/002), INBOX_FINDINGS/* (5 bao cao 21-22/07)
- He dang phat trien: RB_EA v0.1 (INBOX, can v0.2 fix F1: time-stop 48 NEN H4 =192h
  dung backtest, KHONG PHAI 48h; F2: budget khi lot=0) + SC6 v3.97/3.98

## B. HUONG NGHIEN CUU (uu tien giam dan, moi item = 1 subagent 1 phien)
R1. [MC-001/P1] Do vung NGUOI ve: dung journal forward cua Sep (ARM log cua RB_EA
    + ghi chu tich luy/phan phoi). Output: nguoi-ve nam dau giua snapshot (-0.23)
    va rolling (+0.51). Can ~50 vung. KHONG lam duoc bang backtest — day la data
    chi forward moi sinh ra. Khoi luong: setup log 1 buoi + cho mau.
R2. [MC-002/P1] Test artifact TP-cap: chay mirror study voi he KHONG TP (trailing
    theo cau truc hoac exit cuoi tuan). Du doan viet truoc: hold-value se duong
    keo dai qua 48h. Khoi luong: 1 script ~1h, data san.
R3. [MC-002/P2] Port 3 gia thuyet sang SC6 THAT trong Strategy Tester MT5
    (session boost / POI trinh / time-stop 24h) — tren logic SC6 nguyen ban,
    khong dung proxy. Khoi luong: 3 run tester + doc bao cao, 1-2 buoi.
R4. [MC-001/P2] Cross-market: chay setup_decay tren 1 thi truong 24h (BTC) va
    1 thi truong co gio dong cua (DAX/US500 CFD). Du doan: hieu ung phien yeu di
    o BTC, manh len o DAX. Can data — Sep export tu MT5. Khoi luong: 1 buoi/thi truong.
R5. [MC-001/P3] Ngay tin lon: gan lich FOMC/NFP (public) vao setup_decay, tach
    cohort ngay-tin vs ngay-thuong. Du doan: ngay tin lam vung sang chet nhanh hon.
    Khoi luong: 1 script + lich su kien, 1 buoi.
R6. Vong xac nhan A3 (cohort vang) dung chuan prereg — vi A3 goc la exploratory:
    chia doi mau theo thoi gian, prereg nguong +0.10R tren nua chua nhin. 30 phut.

## C. HUONG TRIEN KHAI (song song, khong cho nghien cuu xong)
D1. RB_EA v0.2: fix F1 (192h dung backtest) + F2 + Telegram soft-warning khi ARM
    gio London (nhac, khong chan — theo V02_CONTROL_RUN). -> Phase 4 audit boi
    instance tuoi -> compile -> VPS demo magic moi. Guardian Rules toan trinh.
D2. Journal schema cho R1: moi lan ARM ghi (ts, zone_hi/lo, nhan dinh acc/dist,
    phien, cham thu may) — EA tu ghi phan may, Sep them 1 dong nhan dinh.
D3. FTMO thang truoc (68 lenh): khi nao tien, export tu MetriX de doi chieu voi
    baseline n=51 thang 4 (do do on dinh edge chon keo). Khong gap.
D4. KHONG trien khai gi tu decay/mirror vao logic AUTO cua RB_EA (da chung minh
    khong cai thien — V02_CONTROL_RUN). Dia chi ap dung: playbook NGUOI + SC6 sau R3.

## D. PHAN VAI SUBAGENT (goi y cho agent local)
- Fable-Research (1 instance/1 huong R): chay study, viet the MC, KHONG duoc sua
  co che giua chung — du doan sai thi ghi sai.
- Fable-Adversary (instance TUOI, khong doc ket qua Research truoc): tai lap doc
  lap bat ky ket qua nao sap vao EA; nguong lech >5% n hoac >0.02 avgR = dieu tra.
- Fable-Scribe: cap nhat 02_META_LESSONS + 03_MECHANISM_CARDS sau moi vong;
  moi finding thieu toa do 4 truc = tra ve.
- Sep (chu du an): duy nhat co quyen (i) chot du doan truoc khi chay, (ii) quyet
  dua gi vao EA, (iii) cung cap data moi/journal. Khong ai duoc thay Sep lam (ii).

## E. TIEU CHI THANH CONG CUA CHUONG TRINH (6-8 tuan)
- MC-001 dat CROSS-VALIDATED (>=2 trong P1-P3 co ket qua, du doan dung/sai deu tinh)
- RB_EA v0.2 qua audit + chay demo >=4 tuan khong lech backtest
- Journal R1 dat >=50 vung co nhan dinh
- KHONG co finding nao duoc trich dan thieu the MC — do bang cach Fable-Scribe audit ngau nhien
