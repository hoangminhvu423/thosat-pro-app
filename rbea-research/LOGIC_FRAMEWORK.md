# 05_EA_LOGIC_FRAMEWORK.md — Khung logic EA tu dong & ban tu dong + nen tang Lyapunov
Ban hanh 2026-07-22 · Tong hop tu 10 bao cao 21-22/07 · Trang thai: phan II la TOAN CHINH XAC,
phan I.B la EMPIRICAL-QUEUE (preregistered, cho compute), phan III la spec tong hop da kiem chung.

=====================================================================
PHAN I — MO XE RB_EA
=====================================================================
## I.A — Da chung minh (nguon: PHASE1_FINAL, PHASE2, V02_CONTROL_RUN)
1. Edge +0.099R/lenh (fON) / +0.078R (fOFF), PF 1.14/1.10, 21 nam, OOS 2 phia deu duong,
   song phi $0.50. Hai engine doc lap trung so.
2. Cau truc edge da biet: sleeve BREAK la nguon chinh (gross +0.084..+0.146 moi config);
   RANGE sleeves ~hoa gross, am net o TF thap. => RB_EA ban chat la HE BAT BREAKOUT
   co lop range bao ve budget, khong phai he range thuan.
3. Edge KHONG cai thien duoc bang session-block/time-stop-ngan (control run V02) —
   baseline da toi uu noi sinh nho rolling box.
4. Phan phoi thang: median ~0R, 50% thang am, chuoi am toi da 8 thang, mean +0.35R/thang.
   => Tang auto = khung gam + bao hiem, KHONG phai nguon thu nhap.

## I.B — EMPIRICAL-QUEUE (preregister TRUOC, chay khi co compute — phien moi hoac Claude Code)
Q1. Bootstrap 95% CI cua avgR (n=896, 10k resample).
    DU DOAN: CI ~ [+0.02, +0.18], P(edge<=0) ~ 1-3%. NGUONG HANH DONG: neu P>10%
    => edge chua phan biet duoc voi 0, ha cap ky vong xuong "khung gam thuan".
Q2. Tap trung duoi: % totR tu top 5%/10% lenh.
    DU DOAN: top 10% lenh chiem >80% totR (dong dang ho so FTMO cua Sep — edge o duoi).
    HE QUA neu dung: moi co che cat som lenh thang (trailing chat, TP gan) la cam ky.
Q3. Monte Carlo 10k duong equity (risk 0.5%/lenh, 60 lenh/nam, 5 nam):
    DU DOAN: median maxDD ~8-12%, p95 maxDD ~18-25%, P(cham daily+weekly breaker
    it nhat 1 lan/nam) > 80% — breaker la BO PHAN VAN HANH thuong xuyen, khong phai su co.
Q4. Doi dau thang/thua (runs test): DU DOAN ~50% (doc lap) — neu <45% co chuoi
    => co the them logic "nghi sau N thua" (counterfactual FTMO cua Sep goi y co).

=====================================================================
PHAN II — NEN TANG LYAPUNOV (toan chinh xac, khong can mo phong)
=====================================================================
## II.A — Thiet lap
He: equity E_t, quy tac sizing s_t (rui ro $ cua lenh t). Nhieu: ket qua lenh
X_t in {-1, +m} (thua 1R / thang m R, m~2-4). Dong luc: E_{t+1} = E_t + s_t * X_t.
Cau hoi Lyapunov: nhieu loan (chuoi thua) bi TIEU TAN hay TICH LUY?
Chon ham V_t = s_t / E_t (ty le phoi bay — exposure ratio).

## II.B — Ba che do sizing, ba so phan (chung minh)
1. FIXED-FRACTIONAL (RB_EA): s_t = f * E_t => V_t = f hang so.
   Sau k lenh thua lien tiep: E giam theo (1-f)^k — co so mu < 1, HOI TU.
   Khoang thua chiu duoc vo han ve mat toan (khong bao gio am von);
   thuc te bi chan boi breaker (xem II.C). V̇ = 0, he o bien on dinh,
   breaker keo ve V=0 (NEUTRAL) => asymptotically stable co dieu khien.
2. MARTINGALE (nhan d sau thua): s_{t+1} = d*s_t khi thua, E_{t+1} = E_t - s_t.
   V_{t+1}/V_t = d * E_t/(E_t - s_t) > d >= 2. V tang it nhat theo d^k trong khi
   E giam => ton tai k* huu han: s_{k*} > E_{k*} (chay margin). Voi d=2, s_0=1%E_0:
   k* <= 7 (vi 2^7 = 128% > 100% - ton that tich luy 127%... chinh xac: tong
   ton that sau k thua = (2^k - 1)*s_0; cham 100% khi k=7). PHAN KY TAT DINH —
   khong phai xac suat, la dinh menh khi chuoi du dai. P(chuoi 7 thua voi WR 50%)
   = 1/128 moi cua so 7 lenh => voi 397 lenh/tuan (bot TikTok): gan nhu chac chan
   trong vai tuan. DD 110% quan sat duoc = dung diem k* nay.
3. ANTI-MARTINGALE (tang sau thang): V co dieu kien — on dinh khi thua (co exposure)
   nhung V tang trong chuoi thang => rui ro tra lai loi nhuan o cu dao chieu.
   On dinh tiem can co dieu kien; can chan tren V_max.

## II.C — Ban kinh hap dan cua RB_EA (tinh dong)
Voi f = 0.5%/lenh, daily breaker 3%: hap thu toi da floor(3/0.5) = 6 SL/ngay
(budget 3 lenh/ngay lam tran thuc te = 3 SL/ngay => breaker daily gan nhu
chi kich hoat khi slippage/gap, day la du phong bac 2). Weekly 8% = 16 SL —
voi ~1-5 lenh/ngay, khong the cham bang SL sach => weekly breaker = phong gap/loi he.
KET LUAN: RB_EA co V̇ <= 0 tren moi quy dao + 2 tang keo ve NEUTRAL.
Muon pha vo on dinh nay chi co 3 cua: (i) bug lam sizing sai (=> audit F1-F5),
(ii) gap qua SL (=> Friday cleanup + news manual), (iii) NGUOI override.
=> Moi rui ro ton tai cua he nam NGOAI logic — dung noi audit phai soi.

## II.D — Lambda cuc bo (MC-003, da OOS-validated)
lambda_24h = mean continuation(6h) cua cac soc (range>=2.5xATR_M30) trong 24h truoc.
Vung trung tinh [-0.3..+0.2] tot nhat cho range-touch (OOS spread +0.218R vs khuech dai).
Vi tri trong khung: chi bao MOI TRUONG cho tang nguoi, KHONG phai tin hieu.
=====================================================================
PHAN III — KHUNG LOGIC HOP NHAT (auto + ban tu dong)
=====================================================================
Kien truc 4 tang, moi tang co bang chung rieng:

T1. TANG ON DINH (bat bien — Lyapunov, II.B/II.C):
    fixed-fractional + SL cung moi lenh + budget/ngay + breaker 2 cap + cam DCA/grid.
    Day la tang KHONG BAO GIO nhuong cho toi uu loi nhuan. Moi de xuat lam V̇>0
    o bat ky nhanh nao = tu choi truoc khi backtest.
T2. TANG CO HOI (may — da dong bang): state machine RANGE/BREAK/NEUTRAL,
    box hop le <=4xATR, break = close + 0.25xATR, TP traverse, time-stop 192h.
    San +0.099R da chung minh. CAM cay them finding tang khac vao day
    khi chua qua control-run kieu V02.
T3. TANG PHAN LOAI (nguoi — noi edge tang truong): ve vung theo cau truc (Wyckoff),
    quyet dinh ARM/khong-ARM dung: lambda_24h (trung tinh?), phien, so lan cham,
    lich tin. Moi input tang nay la ADVISORY hien thi luc /arm — nguoi quyet.
    Do luong bat buoc: journal moi lan ARM (R1) — day la tang duy nhat chua co so.
T4. TANG DO LUONG (meta): moi finding vao the MC 4-truc; moi thay doi T2 phai qua
    (preregister -> control run -> Fable doc lap); du doan sai ghi vao lich su the.

CHE DO VAN HANH:
- FULL-AUTO = T1 + T2 (rolling box thay nguoi ve): ky vong +0.35R/thang, median 0,
  vai tro khung gam/benchmark. Da du dieu kien build (gate-check PASS).
- SEMI-AUTO = T1 + T2(zone nguoi) + T3: ky vong = san may + human-alpha(chua do)
  + thue-so-hai thu hoi (prior manh nhat: RRR 4.82 vs 1.95). Day la san pham chinh.
- Hai che do chay SONG SONG cung thoi gian = thi nghiem doi chung tu nhien do
  human-alpha truc tiep (khac biet PnL tren cung ky = dong gop cua nguoi).

VIEC TIEP THEO (thu tu): v0.2 (F1 192h, F2, F4 STOPS_LEVEL, F5 handle-alert,
lambda display luc /arm, journal schema) -> audit instance tuoi -> demo song song
2 che do -> Q1-Q4 khi co compute.
