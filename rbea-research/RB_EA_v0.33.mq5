//+------------------------------------------------------------------+
//| RB_EA.mq5 — Range/Break Semi-Auto EA v0.33                       |
//| Spec: RB_EA_MASTER_SPEC_v1.0 + EA_ENGINEERING_PLAN_v1.0          |
//| THAY DOI v0.33 (va finding CAM re-audit v0.32, 2026-07-24):      |
//|  [L1] Chong race login=0: neu OnInit chay khi terminal CHUA ket  |
//|       noi (VPS reboot + autologon) -> HOAN nap state toi tick    |
//|       dau tien (deferred init). Truoc: khoa thanh RBEA2_0_...    |
//|       -> "quen" perm_halt + BTC auto tu re-arm voi khoa sai.     |
//|  [L2] version 0.330 (het warning 68) + dong bo chuoi noi bo      |
//|       v0.33 (I_Comment/StatusText/TG online kem login).          |
//|  [L3] Print khi nap perm_halt=1 tu GlobalVariable (truoc day chi |
//|       log khi nap tu file Common).                               |
//| THAY DOI v0.32 (va G2-FAIL 2026-07-24 — halt-file dung chung):   |
//|  [H1] HaltFile()/GV() them ACCOUNT LOGIN vao khoa ten -> tester, |
//|       live, va 2 account KHAC NHAU khong con chia se file/GV.    |
//|       Truoc: "RBEA2_<sym>_<magic>_halt.bin" -> tester(magic X) + |
//|       chart live(magic X) dung CHUNG file -> perm_halt=1 cua ben |
//|       nay lay sang ben kia -> EA halt ngay OnInit -> 0 lenh mai. |
//|  [H2] Trong Strategy Tester: KHONG doc/ghi FILE_COMMON halt (moi |
//|       run bat dau sach; trang thai trong-run dua vao GV cach ly).|
//|  [H3] Moi lan set perm_halt -> Print ly do + eq + init_bal (de   |
//|       lan sau chan doan duoc, khong "halt am tham").             |
//| THAY DOI v0.31 (va 4 finding DO cua audit G3 ngay 2026-07-24):   |
//|  [D1] AutoZone Donchian doi shift 1->2: box = 20 nen DA DONG     |
//|       LIEN TRUOC nen xac nhan (index 2..21). Ban v0.3 tinh ca    |
//|       nen tin hieu (1..20) -> break bat kha thi, BTC auto 0 lenh.|
//|  [D2] Profile AUTO (I_AutoZone=true): KHONG Friday-disarm (24/7  |
//|       nhu backtest R7g); arm san lan cai dau. /disarm tay van    |
//|       giu nguyen y nguoi (khong tu re-arm de len quyet dinh).    |
//|  [D3] Breaker TUAN latch rieng g_week_halt (persist GV), chi xoa |
//|       tai Monday-reset — day-reset khong con "chua lanh" nua.    |
//|  [D4] Neo breaker tong: input I_InitBalance ($ co dinh, BAT BUOC |
//|       set voi FTMO); perm-halt + init_bal persist ra FILE_COMMON |
//|       (song sot redeploy/doi VPS/GV tu xoa sau 4 tuan).          |
//|  [V1] Daily breaker doi sang dang FTMO-dong-nhat:                |
//|       floor = max(balance0,equity0) - I_MaxDailyDD% x initial    |
//|       -> nghiem hon FTMO(-5%) VO DIEU KIEN ke ca floating loss.  |
//|  [V4] I_RiskPct default 0.25 -> 0.15 (spec muc 2: khoi dau       |
//|       survival-first 0.15/0.15).                                 |
//|  [V5] PERM-HALT van retry dong vi the (moi 5') neu lan dau fail. |
//| GIU NGUYEN tu v0.21/v0.3: C4-fix market entry, F1 time-stop,     |
//|   F2 budget-on-fill, F4 stops clamp, C6 FridayFlat(semi),        |
//|   C7 Monday week reset, AutoZone/RangeEnabled profile BTC.       |
//| FLAG G4 con theo doi: lech tan suat 1-vi-the vs backtest overlap |
//|   (audit flag b — do o demo, khong va code).                     |
//| CHUA COMPILE (G1) / CHUA TESTER (G2) — bat buoc truoc demo.      |
//+------------------------------------------------------------------+
#property copyright "RB_EA v0.33 - QTQ project"
#property version   "0.330"
#property strict
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

CTrade        g_trade;
CPositionInfo g_pos;

//=== INPUTS =========================================================
input group "=== ZONE (nguoi ve) ==="
input bool   I_AutoZone    = false;     // [v0.3] true = box rolling Donchian-20 H4 (full-auto, khong can hline)
input bool   I_RangeEnabled= true;      // [v0.3] false = BREAK-only (profile BTC theo R7g)
input string I_HiLine      = "RB_HI";
input string I_LoLine      = "RB_LO";
input double I_MinZoneATR  = 1.5;

input group "=== STRATEGY ==="
input double I_TouchBufATR = 0.15;
input double I_BreakBufATR = 0.25;
input double I_RangeSLBuf  = 0.50;
input double I_BreakSL_ATR = 1.0;
input double I_BreakTP_ATR = 2.0;      // fixed-R (trailing DA BAC)
input bool   I_TrendFilter = false;    // [v0.2] DEFAULT OFF (PHASE1)
input int    I_MinGapMin   = 60;
input int    I_MaxHoldBars = 48;       // [F1] time-stop 48 nen H4 = 192h

input group "=== RISK ==="
input double I_RiskPct        = 0.15;   // [V4] spec muc 2: khoi dau 0.15 (nang 0.20 sau quy dau sach)
input double I_InitBalance    = 0;      // [D4] $ ban dau account (FTMO: BAT BUOC set, vd 200000). 0 = tu neo balance
input double I_MaxDailyDD     = 3.0;    // [V1] % cua initial, floor = max(bal0,eq0) - 3%xinitial (FTMO-dong-nhat)
input double I_MaxWeeklyDD    = 8.0;
input double I_MaxTotalDD     = 9.0;    // [R7e/FTMO] % tu balance ban dau -> permHalt (0=tat). FTMO max loss 10%
input bool   I_CloseOnBreaker = false;
input bool   I_FridayCleanup  = true;   // [D2] chi ap dung profile SEMI (I_AutoZone=false)
input int    I_FridayHour     = 21;
input bool   I_FridayFlat     = false; // [C6] true = dong het vi the truoc weekend (khong chi disarm)

input group "=== TELEGRAM ==="
input string I_TGToken   = "";
input string I_TGChatID  = "";
input int    I_TGPollSec = 5;

input group "=== EXEC ==="
input int    I_Magic     = 20260723;   // XAU semi 20260723 | BTC auto 20260724 (spec muc 2)
input int    I_Deviation = 30;
input string I_Comment   = "RB_EA_v033";

//=== STATE ==========================================================
enum EMode { MODE_RANGE=0, MODE_BREAK=1, MODE_NEUTRAL=2 };
int      g_mode        = MODE_RANGE;
bool     g_armed       = false;
double   g_zone_hi=0, g_zone_lo=0;
double   g_frozen_hi=0, g_frozen_lo=0;
int      g_bud_rb=1, g_bud_rs=1, g_bud_bk=1;
int      g_blocked_dir=0;
datetime g_last_trade_t=0;
long     g_last_day=-1, g_last_week=-1;
double   g_day_eq0=0, g_day_bal0=0;     // [V1] equity + balance dau ngay (floor FTMO-dong-nhat)
double   g_week_eq0=0;
bool     g_week_halt=false;             // [D3] latch breaker tuan, chi xoa tai Monday-reset
int      g_atr_handle=INVALID_HANDLE, g_sma_handle=INVALID_HANDLE;
datetime g_last_h4_bar=0;
long     g_tg_offset=0;
double   g_init_bal=0;                  // [R7e] balance ban dau (neo breaker tong)
bool     g_perm_halt=false;             // [R7e] halt vinh vien sau breaker tong
string   g_sym;

// [H1] khoa state theo LOGIN+symbol+magic -> khong dung chung giua cac account.
// [H2] tester co GV cach ly san theo tung run -> khong dinh trang thai live.
long   g_login=0;
bool   g_pending_init=false;   // [L1] true = OnInit chay khi login=0, cho tick dau de nap state
bool   InTester(){ return (bool)MQLInfoInteger(MQL_TESTER); }
string GV(string k){ return "RBEA2_"+(string)g_login+"_"+g_sym+"_"+(string)I_Magic+"_"+k; }
void SaveState(){
   GlobalVariableSet(GV("mode"),g_mode);   GlobalVariableSet(GV("armed"),g_armed?1:0);
   GlobalVariableSet(GV("rb"),g_bud_rb);   GlobalVariableSet(GV("rs"),g_bud_rs);
   GlobalVariableSet(GV("bk"),g_bud_bk);   GlobalVariableSet(GV("blk"),g_blocked_dir);
   GlobalVariableSet(GV("lastt"),(double)g_last_trade_t);
   GlobalVariableSet(GV("day"),(double)g_last_day); GlobalVariableSet(GV("deq"),g_day_eq0);
   GlobalVariableSet(GV("dbal"),g_day_bal0);                                     // [V1]
   GlobalVariableSet(GV("week"),(double)g_last_week); GlobalVariableSet(GV("weq"),g_week_eq0);
   GlobalVariableSet(GV("whalt"),g_week_halt?1:0);                               // [D3]
   GlobalVariableSet(GV("zhi"),g_zone_hi); GlobalVariableSet(GV("zlo"),g_zone_lo);
   GlobalVariableSet(GV("fhi"),g_frozen_hi); GlobalVariableSet(GV("flo"),g_frozen_lo);
   GlobalVariableSet(GV("tgoff"),(double)g_tg_offset);
   GlobalVariableSet(GV("ibal"),g_init_bal); GlobalVariableSet(GV("phalt"),g_perm_halt?1:0);
}
void LoadState(){
   if(!GlobalVariableCheck(GV("mode"))) return;
   g_mode=(int)GlobalVariableGet(GV("mode")); g_armed=GlobalVariableGet(GV("armed"))>0.5;
   g_bud_rb=(int)GlobalVariableGet(GV("rb")); g_bud_rs=(int)GlobalVariableGet(GV("rs"));
   g_bud_bk=(int)GlobalVariableGet(GV("bk")); g_blocked_dir=(int)GlobalVariableGet(GV("blk"));
   g_last_trade_t=(datetime)GlobalVariableGet(GV("lastt"));
   g_last_day=(long)GlobalVariableGet(GV("day")); g_day_eq0=GlobalVariableGet(GV("deq"));
   g_day_bal0=GlobalVariableGet(GV("dbal"));                                     // [V1]
   g_last_week=(long)GlobalVariableGet(GV("week")); g_week_eq0=GlobalVariableGet(GV("weq"));
   g_week_halt=GlobalVariableGet(GV("whalt"))>0.5;                               // [D3]
   g_zone_hi=GlobalVariableGet(GV("zhi")); g_zone_lo=GlobalVariableGet(GV("zlo"));
   g_frozen_hi=GlobalVariableGet(GV("fhi")); g_frozen_lo=GlobalVariableGet(GV("flo"));
   g_tg_offset=(long)GlobalVariableGet(GV("tgoff"));
   g_init_bal=GlobalVariableGet(GV("ibal")); g_perm_halt=GlobalVariableGet(GV("phalt"))>0.5;
   if(g_perm_halt) Print("[RBEA-HALT] nap perm_halt=1 tu GlobalVariable — EA se dung im. Xoa GV + file halt de reset."); // [L3]
}

// [D4] perm-halt + init_bal persist ra file COMMON — song sot redeploy/doi VPS/GV tu xoa sau 4 tuan.
// [H1] ten file co LOGIN -> 2 account khac nhau tren cung may KHONG chia se file halt.
string HaltFile(){ return "RBEA2_"+(string)g_login+"_"+g_sym+"_"+(string)I_Magic+"_halt.bin"; }
void SaveHalt(){
   if(InTester()) return;                        // [H2] tester khong ghi file live
   int h=FileOpen(HaltFile(),FILE_WRITE|FILE_BIN|FILE_COMMON);
   if(h==INVALID_HANDLE){ PrintFormat("[RBEA-ERR] SaveHalt fail err=%d",GetLastError()); return; }
   FileWriteDouble(h,g_init_bal); FileWriteInteger(h,g_perm_halt?1:0); FileClose(h); }
void LoadHalt(){
   if(InTester()) return;                        // [H2] tester bat dau sach, khong doc halt live cu
   if(!FileIsExist(HaltFile(),FILE_COMMON)) return;
   int h=FileOpen(HaltFile(),FILE_READ|FILE_BIN|FILE_COMMON);
   if(h==INVALID_HANDLE) return;
   double ib=FileReadDouble(h); int ph=FileReadInteger(h); FileClose(h);
   if(ib>0 && g_init_bal<=0) g_init_bal=ib;
   if(ph==1){ g_perm_halt=true;
      PrintFormat("[RBEA-HALT] nap perm_halt=1 tu %s (init_bal=%.2f) — EA se dung im. Xoa file + GV de reset.",HaltFile(),g_init_bal); } }

//=== FILL MODE AUTO =================================================
ENUM_ORDER_TYPE_FILLING AutoFill(string sym){
   long fm=SymbolInfoInteger(sym,SYMBOL_FILLING_MODE);
   if((fm&SYMBOL_FILLING_FOK)!=0) return ORDER_FILLING_FOK;
   if((fm&SYMBOL_FILLING_IOC)!=0) return ORDER_FILLING_IOC;
   return ORDER_FILLING_RETURN;
}
bool ClosePositionVerified(ulong ticket){
   for(int a=0;a<3;a++){
      g_trade.SetTypeFillingBySymbol(g_sym);
      if(g_trade.PositionClose(ticket)){ if(!PositionSelectByTicket(ticket)) return true; }
      Sleep(300);
   }
   PrintFormat("[RBEA-ERR] Close #%d FAILED rc=%d",(int)ticket,g_trade.ResultRetcode());
   TG("CANH BAO: CLOSE FAIL #"+(string)ticket+" rc="+(string)g_trade.ResultRetcode());
   return false;
}

//=== TELEGRAM (giu nguyen v0.1) ====================================
string UrlEnc(string s){
   string r=""; uchar b[]; StringToCharArray(s,b,0,WHOLE_ARRAY,CP_UTF8);
   for(int i=0;i<ArraySize(b)-1;i++){ uchar c=b[i];
      if((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='-'||c=='_'||c=='.') r+=CharToString(c);
      else r+=StringFormat("%%%02X",c); }
   return r; }
void TG(string msg){
   if(I_TGToken=="") return;
   string url="https://api.telegram.org/bot"+I_TGToken+"/sendMessage?chat_id="+I_TGChatID+"&text="+UrlEnc(msg);
   char post[],res[]; string hdr; WebRequest("GET",url,"",3000,post,res,hdr); }
string StatusText(){
   string m = g_mode==MODE_RANGE?"RANGE":(g_mode==MODE_BREAK?"BREAK":"NEUTRAL");
   return StringFormat("RB_EA v0.33 %s\nARMED:%s|MODE:%s%s\nZone:%.2f-%.2f\nBudget RB/RS/BK:%d/%d/%d\nRisk:%.2f%%|Eq:%.2f",
      g_sym,g_armed?"YES":"no",m,g_week_halt?"|WEEK-HALT":"",g_zone_lo,g_zone_hi,g_bud_rb,g_bud_rs,g_bud_bk,I_RiskPct,AccountInfoDouble(ACCOUNT_EQUITY)); }
void TGPoll(){
   if(I_TGToken=="") return;
   string url="https://api.telegram.org/bot"+I_TGToken+"/getUpdates?timeout=0&offset="+(string)(g_tg_offset+1);
   char post[],res[]; string hdr;
   if(WebRequest("GET",url,"",3000,post,res,hdr)!=200) return;
   string body=CharArrayToString(res,0,WHOLE_ARRAY,CP_UTF8); int p=0;
   while((p=StringFind(body,"\"update_id\":",p))>=0){
      p+=12; long uid=StringToInteger(StringSubstr(body,p,12)); if(uid>g_tg_offset) g_tg_offset=uid;
      int cp=StringFind(body,"\"chat\":{\"id\":",p); int tp=StringFind(body,"\"text\":\"",p);
      if(cp<0||tp<0) break;
      string chat=StringSubstr(body,cp+13,20); int comma=StringFind(chat,","); if(comma>0) chat=StringSubstr(chat,0,comma);
      tp+=8; int te=StringFind(body,"\"",tp); string cmd=StringSubstr(body,tp,te-tp);
      if(chat==I_TGChatID) HandleCmd(cmd); else PrintFormat("[RBEA-SEC] Tu choi chat: %s",chat);
   }
   SaveState(); }
void HandleCmd(string cmd){
   StringToLower(cmd);
   if(StringFind(cmd,"/status")==0){ TG(StatusText()); }
   else if(StringFind(cmd,"/arm")==0 && StringFind(cmd,"/disarm")!=0){
      if(ReadZone(true)){ g_armed=true; g_mode=MODE_RANGE; TG("ARMED OK\n"+StatusText()); }
      else TG("ARM FAIL: vung khong hop le"); }
   else if(StringFind(cmd,"/disarm")==0){ g_armed=false; CancelAllPending(); TG("DISARMED"); }
   else if(StringFind(cmd,"/flat")==0){ g_armed=false; CancelAllPending(); CloseAllOurs(); TG("FLAT-ALL xong"); }
   else if(StringFind(cmd,"/help")==0){ TG("/status /arm /disarm /flat"); }
   SaveState(); }

//=== ZONE / INDICATORS =============================================
bool ReadZone(bool announce){
   if(I_AutoZone){
      // [D1] box = 20 nen DA DONG LIEN TRUOC nen xac nhan (index 2..21).
      // v0.3 dung start=1 (1..20) tinh ca nen tin hieu -> close khong the vuot high chinh no
      // + buffer -> break bat kha thi -> sleeve auto 0 lenh. Backtest R7g: box = h[i-20..i-1], tin hieu = h[i].
      int ih=iHighest(g_sym,PERIOD_H4,MODE_HIGH,20,2);
      int il=iLowest (g_sym,PERIOD_H4,MODE_LOW ,20,2);
      if(ih<0||il<0) return false;
      g_zone_hi=iHigh(g_sym,PERIOD_H4,ih); g_zone_lo=iLow(g_sym,PERIOD_H4,il);
      return (g_zone_hi>g_zone_lo);                    // khong ap MinZone (fidelity voi sleeve validated)
   }
   if(ObjectFind(0,I_HiLine)<0 || ObjectFind(0,I_LoLine)<0) return false;
   double hi=ObjectGetDouble(0,I_HiLine,OBJPROP_PRICE), lo=ObjectGetDouble(0,I_LoLine,OBJPROP_PRICE);
   if(hi<=lo) return false;
   double atr=ATRv(); if(atr<=0) return false;
   if(hi-lo < I_MinZoneATR*atr){ if(announce) PrintFormat("[RBEA] Vung hep %.2f",hi-lo); return false; }
   g_zone_hi=hi; g_zone_lo=lo; return true; }
double ATRv(){ double b[]; ArraySetAsSeries(b,true); if(CopyBuffer(g_atr_handle,0,1,1,b)<1) return 0; return b[0]; }
double SMAv(){ double b[]; ArraySetAsSeries(b,true); if(CopyBuffer(g_sma_handle,0,1,1,b)<1) return 0; return b[0]; }

//=== HELPERS =======================================================
bool OursOpen(){
   for(int i=PositionsTotal()-1;i>=0;i--)
      if(g_pos.SelectByIndex(i)&&g_pos.Symbol()==g_sym&&g_pos.Magic()==I_Magic) return true;
   return false; }
void CloseAllOurs(){
   for(int i=PositionsTotal()-1;i>=0;i--)
      if(g_pos.SelectByIndex(i)&&g_pos.Symbol()==g_sym&&g_pos.Magic()==I_Magic)
         ClosePositionVerified(g_pos.Ticket()); }
void CancelAllPending(){
   for(int i=OrdersTotal()-1;i>=0;i--){ ulong t=OrderGetTicket(i);
      if(OrderGetString(ORDER_SYMBOL)==g_sym&&OrderGetInteger(ORDER_MAGIC)==I_Magic) g_trade.OrderDelete(t); } }

// [F4] khoang cach dung toi thieu (stops level + spread)
double MinStopDist(){
   double point=SymbolInfoDouble(g_sym,SYMBOL_POINT);
   long   sl_lv=SymbolInfoInteger(g_sym,SYMBOL_TRADE_STOPS_LEVEL);
   double spread=(SymbolInfoDouble(g_sym,SYMBOL_ASK)-SymbolInfoDouble(g_sym,SYMBOL_BID));
   return MathMax((double)sl_lv*point, spread) ; }

double CalcLot(double entry,double sl){
   double risk_amt=AccountInfoDouble(ACCOUNT_BALANCE)*I_RiskPct/100.0;
   double tv=SymbolInfoDouble(g_sym,SYMBOL_TRADE_TICK_VALUE), tsz=SymbolInfoDouble(g_sym,SYMBOL_TRADE_TICK_SIZE);
   double dist=MathAbs(entry-sl); if(dist<=0||tv<=0||tsz<=0) return 0;
   double lot=risk_amt/(dist/tsz*tv);
   double minl=SymbolInfoDouble(g_sym,SYMBOL_VOLUME_MIN), stp=SymbolInfoDouble(g_sym,SYMBOL_VOLUME_STEP);
   lot=MathFloor(lot/stp)*stp;
   if(lot<minl){ PrintFormat("[RBEA-SKIP] lot %.2f < min %.2f",lot,minl); return 0; }  // khong ep min-lot
   return lot; }

// [F4] tra false neu SL/TP qua sat -> nen goi tao lenh KHONG dat
bool StopsOK(double px,double sl,double tp){
   double md=MinStopDist();
   if(MathAbs(px-sl) < md){ PrintFormat("[RBEA-F4] SL qua sat (%.5f < %.5f) - bo lenh",MathAbs(px-sl),md); return false; }
   if(tp!=0 && MathAbs(px-tp) < md){ PrintFormat("[RBEA-F4] TP qua sat - bo lenh"); return false; }
   return true; }

// RANGE market entry (F2: tra bool, noi goi tu tru budget khi TRUE)
bool MarketIn(int dir,double sl,double tp,string tag){
   double px = dir>0?SymbolInfoDouble(g_sym,SYMBOL_ASK):SymbolInfoDouble(g_sym,SYMBOL_BID);
   if(!StopsOK(px,sl,tp)) return false;                 // [F4]
   double lot=CalcLot(px,sl); if(lot<=0) return false;
   g_trade.SetTypeFillingBySymbol(g_sym);
   bool ok = dir>0 ? g_trade.Buy(lot,g_sym,0,sl,tp,I_Comment+"_"+tag)
                   : g_trade.Sell(lot,g_sym,0,sl,tp,I_Comment+"_"+tag);
   if(ok){ g_last_trade_t=TimeCurrent();
      TG(StringFormat("ENTRY %s %s %s|lot %.2f|SL %.2f|TP %.2f",g_sym,tag,dir>0?"BUY":"SELL",lot,sl,tp)); }
   else PrintFormat("[RBEA-FAIL] %s rc=%d",tag,g_trade.ResultRetcode());
   return ok; }

// [F1] time-stop: dong vi the giu qua I_MaxHoldBars nen H4
void CheckTimeStop(){
   long maxsec=(long)I_MaxHoldBars*PeriodSeconds(PERIOD_H4);
   for(int i=PositionsTotal()-1;i>=0;i--){
      if(g_pos.SelectByIndex(i)&&g_pos.Symbol()==g_sym&&g_pos.Magic()==I_Magic){
         if(TimeCurrent()-(datetime)g_pos.Time() >= maxsec){
            TG("TIME-STOP #"+(string)g_pos.Ticket()+" (>"+(string)I_MaxHoldBars+" nen H4)");
            ClosePositionVerified(g_pos.Ticket()); } } } }

//=== INIT ==========================================================
// [L1] nap state MOT lan khi DA co login dung — tach rieng de hoan duoc (deferred init)
void StateInit(){
   bool fresh=!GlobalVariableCheck(GV("mode"));         // [D2] truoc khi LoadState/SaveState
   LoadState();
   LoadHalt();                                          // [D4] file COMMON ghi de/gop voi GV
   if(I_InitBalance>0) g_init_bal=I_InitBalance;        // [D4] input la neo TOI CAO (FTMO: bat buoc set)
   else if(g_init_bal<=0){
      g_init_bal=AccountInfoDouble(ACCOUNT_BALANCE);
      PrintFormat("[RBEA-WARN] I_InitBalance=0 -> tu neo %.2f. Voi FTMO PHAI set I_InitBalance de neo khong troi khi redeploy.",g_init_bal); }
   if(I_AutoZone && fresh) g_armed=true;                // [D2] full-auto: arm ngay lan cai dau (/disarm tay van sticky)
   SaveHalt(); SaveState();
   TG("RB_EA v0.33 online (login "+(string)g_login+")\n"+StatusText());
}
int OnInit(){
   g_sym=Symbol();
   g_login=AccountInfoInteger(ACCOUNT_LOGIN);           // [H1] khoa state/halt theo account, dat TRUOC GV()/LoadState
   g_trade.SetExpertMagicNumber(I_Magic); g_trade.SetDeviationInPoints(I_Deviation);
   g_trade.SetTypeFilling(AutoFill(g_sym));
   g_atr_handle=iATR(g_sym,PERIOD_H4,20);
   g_sma_handle=iMA(g_sym,PERIOD_H4,200,0,MODE_SMA,PRICE_CLOSE);
   if(g_atr_handle==INVALID_HANDLE||g_sma_handle==INVALID_HANDLE) return INIT_FAILED;
   if(g_login<=0 && !InTester()){
      // [L1] terminal chua ket noi (VPS vua reboot, autologon dang chay): KHONG nap state voi khoa
      // login=0 (se "quen" perm_halt + tu re-arm sai — finding cam re-audit v0.32). Hoan toi tick dau.
      g_pending_init=true;
      Print("[RBEA-WARN] ACCOUNT_LOGIN=0 (chua ket noi) -> hoan nap state toi tick dau tien co login.");
   } else StateInit();
   EventSetTimer(I_TGPollSec);
   g_last_h4_bar=iTime(g_sym,PERIOD_H4,0);
   return INIT_SUCCEEDED; }
void OnDeinit(const int r){
   if(!g_pending_init) SaveState();                    // [L1] khong ghi GV voi khoa login=0
   EventKillTimer();
   if(g_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_atr_handle);
   if(g_sma_handle!=INVALID_HANDLE) IndicatorRelease(g_sma_handle); }
void OnTimer(){ if(g_pending_init) return; TGPoll(); }  // [L1]

//=== CORE ==========================================================
void OnTick(){
   // [L1] deferred init: tick chi den khi DA ket noi -> login chac chan hop le
   if(g_pending_init){
      g_login=AccountInfoInteger(ACCOUNT_LOGIN);
      if(g_login<=0) return;
      g_pending_init=false; StateInit();
   }
   //-- [R7e] breaker TONG: -I_MaxTotalDD% tu balance ban dau -> dong het + halt VINH VIEN
   if(!g_perm_halt && I_MaxTotalDD>0 && g_init_bal>0){
      if(AccountInfoDouble(ACCOUNT_EQUITY) <= g_init_bal*(1.0-I_MaxTotalDD/100.0)){
         g_perm_halt=true; g_armed=false; g_mode=MODE_NEUTRAL;
         CancelAllPending(); CloseAllOurs(); SaveHalt(); SaveState();   // [D4] persist file truoc
         // [H3] log ly do de lan sau chan doan duoc (khong halt am tham)
         PrintFormat("[RBEA-HALT] SET perm_halt: eq=%.2f <= init_bal=%.2f x (1-%.1f%%)=%.2f",
            AccountInfoDouble(ACCOUNT_EQUITY),g_init_bal,I_MaxTotalDD,g_init_bal*(1.0-I_MaxTotalDD/100.0));
         TG(StringFormat("TOTAL BREAKER -%.1f%% tu initial %.2f — PERM HALT. Can nguoi xoa file halt + GV de reset.",I_MaxTotalDD,g_init_bal));
      }
   }
   if(g_perm_halt){
      // [V5] neu lan dau dong fail (vd market closed) -> van retry moi 5 phut, khong bo mac vi the
      static datetime s_last_try=0;
      if(OursOpen() && TimeCurrent()-s_last_try>=300){
         s_last_try=TimeCurrent(); CancelAllPending(); CloseAllOurs(); }
      return; }
   CheckTimeStop();                                     // [F1] moi tick
   //-- Friday cleanup — [D2] CHI profile SEMI: profile AUTO chay 24/7 nhu backtest R7g, khong disarm weekend
   if(I_FridayCleanup && !I_AutoZone){
      MqlDateTime dt; TimeToStruct(TimeCurrent(),dt);
      if(dt.day_of_week==5&&dt.hour>=I_FridayHour&&g_armed){
         g_armed=false; CancelAllPending();
         if(I_FridayFlat) CloseAllOurs();               // [C6]
         SaveState(); TG("Friday cleanup"+(I_FridayFlat?" + FLAT":"")); } }
   //-- Day reset (server day)
   MqlDateTime now; TimeToStruct(TimeCurrent(),now);
   long daykey=now.year*10000+now.mon*100+now.day;
   if(daykey!=g_last_day){
      g_last_day=daykey;
      g_day_eq0=AccountInfoDouble(ACCOUNT_EQUITY);
      g_day_bal0=AccountInfoDouble(ACCOUNT_BALANCE);    // [V1] floor can ca balance dau ngay
      g_bud_rb=1; g_bud_rs=1; g_bud_bk=1; g_blocked_dir=0;
      if(g_mode==MODE_NEUTRAL||g_mode==MODE_BREAK) g_mode=MODE_RANGE;
      SaveState(); }
   //-- [C7] Week reset theo Monday server (khong con lech thu 5 UTC nhu v0.1)
   if(now.day_of_week==1){                              // Monday = moc tuan chuan prop-firm
      long mon_key=now.year*10000+now.mon*100+now.day;
      if(mon_key!=g_last_week){
         g_last_week=mon_key; g_week_eq0=AccountInfoDouble(ACCOUNT_EQUITY);
         g_week_halt=false;                             // [D3] latch tuan CHI xoa o day
         SaveState(); } }
   if(g_week_eq0<=0) g_week_eq0=AccountInfoDouble(ACCOUNT_EQUITY);  // khoi tao lan dau

   //-- DD breakers
   double eq=AccountInfoDouble(ACCOUNT_EQUITY); bool brk_d=false, brk_w=false;
   // [V1] daily FTMO-dong-nhat: floor = max(balance0,equity0) - I_MaxDailyDD% x initial ($ co dinh)
   //      -> nghiem hon FTMO (-5% x initial) vo dieu kien, ke ca khi qua dem om floating loss.
   if(I_MaxDailyDD>0 && g_init_bal>0 && (g_day_eq0>0||g_day_bal0>0)){
      double floorD=MathMax(g_day_bal0,g_day_eq0) - I_MaxDailyDD/100.0*g_init_bal;
      if(eq<=floorD) brk_d=true; }
   if(I_MaxWeeklyDD>0 && g_week_eq0>0 && (eq/g_week_eq0-1)*100 < -I_MaxWeeklyDD) brk_w=true;
   if(brk_w && !g_week_halt){ g_week_halt=true; SaveState(); }       // [D3] latch den het tuan
   if((brk_d||brk_w) && g_mode!=MODE_NEUTRAL){
      g_mode=MODE_NEUTRAL; CancelAllPending();
      if(I_CloseOnBreaker) CloseAllOurs();
      SaveState(); TG(brk_w?"WEEKLY BREAKER - NEUTRAL het tuan":"DAILY BREAKER - NEUTRAL het ngay"); }
   if(!g_armed || g_mode==MODE_NEUTRAL || g_week_halt) return;       // [D3] tuan halt chan ca khi day-reset

   datetime cur=iTime(g_sym,PERIOD_H4,0);
   if(cur==g_last_h4_bar) return;
   g_last_h4_bar=cur; OnNewH4(); }

void OnNewH4(){
   double atr=ATRv(); if(atr<=0) return;
   double c1=iClose(g_sym,PERIOD_H4,1), h1=iHigh(g_sym,PERIOD_H4,1), l1=iLow(g_sym,PERIOD_H4,1);
   bool gap_ok=(TimeCurrent()-g_last_trade_t)>=I_MinGapMin*60;

   if(g_mode==MODE_RANGE){
      if(!ReadZone(false)){ Print("[RBEA] Mat hline vung"); return; }
      double bh=g_zone_hi, bl=g_zone_lo;
      //-- Pha vo xac nhan bang CLOSE + buffer
      if(c1>bh+I_BreakBufATR*atr || c1<bl-I_BreakBufATR*atr){
         int d = c1>bh ? 1 : -1;
         g_frozen_hi=bh; g_frozen_lo=bl; g_mode=MODE_BREAK;
         TG(StringFormat("BREAK %s xac nhan @ %.2f",d>0?"UP":"DOWN",c1));
         // [C4-fix] vao MARKET NGAY tai nen xac nhan (khop backtest PHASE1).
         if(g_bud_bk>0 && gap_ok && !OursOpen()){
            double px = d>0?SymbolInfoDouble(g_sym,SYMBOL_ASK):SymbolInfoDouble(g_sym,SYMBOL_BID);
            double sl = px - d*I_BreakSL_ATR*atr, tp = px + d*I_BreakTP_ATR*atr;
            if(MarketIn(d,sl,tp,"BREAK")){ g_bud_bk--; }        // [F2] tru khi THAT vao
         }
         SaveState(); return;
      }
      if(OursOpen()||!gap_ok) return;
      double sma=SMAv();
      bool sell_ok = !(I_TrendFilter && sma>0 && c1>sma);
      bool buy_ok  = !(I_TrendFilter && sma>0 && c1<sma);
      //-- RANGE_SELL (F2: tru budget khi MarketIn TRUE) — [v0.3] tat duoc cho profile break-only
      if(I_RangeEnabled && h1>=bh-I_TouchBufATR*atr && g_bud_rs>0 && (g_blocked_dir&2)==0 && sell_ok){
         double sl=bh+I_RangeSLBuf*atr, tp=bl;
         if(sl-c1>0.05*atr && (c1-tp)/(sl-c1)>=1.0){
            if(MarketIn(-1,sl,tp,"RANGE_SELL")){ g_bud_rs--; SaveState(); } }
      }
      else if(I_RangeEnabled && l1<=bl+I_TouchBufATR*atr && g_bud_rb>0 && (g_blocked_dir&1)==0 && buy_ok){
         double sl=bl-I_RangeSLBuf*atr, tp=bh;
         if(c1-sl>0.05*atr && (tp-c1)/(c1-sl)>=1.0){
            if(MarketIn(1,sl,tp,"RANGE_BUY")){ g_bud_rb--; SaveState(); } }
      }
   }
   else if(g_mode==MODE_BREAK){
      //-- False break: dong nguoc vao trong box -> NEUTRAL
      if(c1<g_frozen_hi && c1>g_frozen_lo){
         g_mode=MODE_NEUTRAL;
         SaveState(); TG("FALSE BREAK - NEUTRAL, ve lai vung ngay mai"); }
   }
}

//=== Whipsaw guard + [F2] budget BREAK tru khi FILL ================
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &req, const MqlTradeResult &res){
   if(g_pending_init) return;                           // [L1]
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(trans.deal)) return;
   if(HistoryDealGetInteger(trans.deal,DEAL_MAGIC)!=I_Magic) return;
   if(HistoryDealGetString(trans.deal,DEAL_SYMBOL)!=g_sym) return;
   ENUM_DEAL_ENTRY de=(ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   // lenh vao: cap nhat gap-timer. Budget da tru tai noi goi MarketIn (F2). [v0.31: xoa di tich E1 pending]
   if(de==DEAL_ENTRY_IN){ g_last_trade_t=TimeCurrent(); SaveState(); }
   if(de!=DEAL_ENTRY_OUT) return;
   double profit=HistoryDealGetDouble(trans.deal,DEAL_PROFIT);
   ENUM_DEAL_REASON rs=(ENUM_DEAL_REASON)HistoryDealGetInteger(trans.deal,DEAL_REASON);
   if(rs==DEAL_REASON_SL && profit<0){
      long dtype=HistoryDealGetInteger(trans.deal,DEAL_TYPE);
      if(dtype==DEAL_TYPE_SELL) g_blocked_dir|=1; else g_blocked_dir|=2;
      SaveState();
   }
   TG(StringFormat("CLOSE %s P&L %+.2f (%s)",g_sym,profit,EnumToString(rs)));
}
//+------------------------------------------------------------------+
