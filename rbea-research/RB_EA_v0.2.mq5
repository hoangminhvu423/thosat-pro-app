//+------------------------------------------------------------------+
//| RB_EA.mq5 — Range/Break Semi-Auto EA v0.2                        |
//| Spec: RB_EA_Master_Spec. v0.21 sau cross-val Fable-B 2026-07-23  |
//| THAY DOI v0.21 (chi logic DA CHUNG MINH + va loi audit):        |
//|  [C4-fix] BREAK entry = MARKET NGAY tai nen xac nhan (khop      |
//|       backtest PHASE1 da validate) — khong cho them 1 nen H4.   |
//|       [E1 pending-stop DA RUT: Fable-B doc lap cho thay E1      |
//|       KHONG cai thien baseline -> theo luat "khong so lieu      |
//|       chac chan thi khong them", quay ve entry dung spec.]      |
//|  [F1] time-stop 192h (48 nen H4) qua POSITION_TIME.              |
//|  [F4] clamp SL/TP ngoai STOPS_LEVEL; bo lenh neu qua sat.        |
//|  [F2] budget chi tru khi lenh THAT vao (OnTradeTransaction).     |
//|  [C6] tuy chon Friday-flat (dong vi the truoc weekend).          |
//|  [C7] moc reset tuan theo Monday server (khong lech thu 5 UTC).  |
//|  [R7e/FTMO] breaker TONG I_MaxTotalDD neo BALANCE BAN DAU        |
//|       (permHalt truoc nguong Max Loss 10% cua FTMO) + risk       |
//|       default 0.25% theo MC-survival (P breach 2y ~4% vs 26%).   |
//|  Trend filter DEFAULT OFF (PHASE1: robust hon).                  |
//| BAC (khong dua vao): trailing/partial TP, pinbar/engulfing,      |
//|   retest-limit, wick-structure -> deu fail OOS.                  |
//| CHUA COMPILE / CHUA AUDIT Phase-4 / CHUA DEMO — bat buoc 3 buoc  |
//|   nay truoc tien that. Range absolute chua verify (replica loi). |
//+------------------------------------------------------------------+
#property copyright "RB_EA v0.21 - QTQ project"
#property version   "0.22"
#property strict
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

CTrade        g_trade;
CPositionInfo g_pos;

//=== INPUTS =========================================================
input group "=== ZONE (nguoi ve) ==="
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
input double I_RiskPct        = 0.25;   // [R7e] keep-profile: MC P(breach 2y) 4% @0.25 vs 26% @0.5
input double I_MaxDailyDD     = 3.0;
input double I_MaxWeeklyDD    = 8.0;
input double I_MaxTotalDD     = 9.0;    // [R7e/FTMO] % tu BALANCE BAN DAU -> permHalt (0=tat). FTMO max loss 10%
input bool   I_CloseOnBreaker = false;
input bool   I_FridayCleanup  = true;
input int    I_FridayHour     = 21;
input bool   I_FridayFlat     = false; // [C6] true = dong het vi the truoc weekend (khong chi disarm)

input group "=== TELEGRAM ==="
input string I_TGToken   = "";
input string I_TGChatID  = "";
input int    I_TGPollSec = 5;

input group "=== EXEC ==="
input int    I_Magic     = 20260723;   // [v0.2] magic moi
input int    I_Deviation = 30;
input string I_Comment   = "RB_EA_v02";

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
double   g_day_eq0=0, g_week_eq0=0;
int      g_atr_handle=INVALID_HANDLE, g_sma_handle=INVALID_HANDLE;
datetime g_last_h4_bar=0;
long     g_tg_offset=0;
double   g_init_bal=0;                  // [R7e] balance ban dau (neo breaker tong)
bool     g_perm_halt=false;             // [R7e] halt vinh vien sau breaker tong
string   g_sym;

string GV(string k){ return "RBEA2_"+g_sym+"_"+(string)I_Magic+"_"+k; }
void SaveState(){
   GlobalVariableSet(GV("mode"),g_mode);   GlobalVariableSet(GV("armed"),g_armed?1:0);
   GlobalVariableSet(GV("rb"),g_bud_rb);   GlobalVariableSet(GV("rs"),g_bud_rs);
   GlobalVariableSet(GV("bk"),g_bud_bk);   GlobalVariableSet(GV("blk"),g_blocked_dir);
   GlobalVariableSet(GV("lastt"),(double)g_last_trade_t);
   GlobalVariableSet(GV("day"),(double)g_last_day); GlobalVariableSet(GV("deq"),g_day_eq0);
   GlobalVariableSet(GV("week"),(double)g_last_week); GlobalVariableSet(GV("weq"),g_week_eq0);
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
   g_last_week=(long)GlobalVariableGet(GV("week")); g_week_eq0=GlobalVariableGet(GV("weq"));
   g_zone_hi=GlobalVariableGet(GV("zhi")); g_zone_lo=GlobalVariableGet(GV("zlo"));
   g_frozen_hi=GlobalVariableGet(GV("fhi")); g_frozen_lo=GlobalVariableGet(GV("flo"));
   g_tg_offset=(long)GlobalVariableGet(GV("tgoff"));
   g_init_bal=GlobalVariableGet(GV("ibal")); g_perm_halt=GlobalVariableGet(GV("phalt"))>0.5;
}

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
   return StringFormat("RB_EA v0.2 %s\nARMED:%s|MODE:%s\nZone:%.2f-%.2f\nBudget RB/RS/BK:%d/%d/%d\nRisk:%.2f%%|Eq:%.2f",
      g_sym,g_armed?"YES":"no",m,g_zone_lo,g_zone_hi,g_bud_rb,g_bud_rs,g_bud_bk,I_RiskPct,AccountInfoDouble(ACCOUNT_EQUITY)); }
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
int OnInit(){
   g_sym=Symbol();
   g_trade.SetExpertMagicNumber(I_Magic); g_trade.SetDeviationInPoints(I_Deviation);
   g_trade.SetTypeFilling(AutoFill(g_sym));
   g_atr_handle=iATR(g_sym,PERIOD_H4,20);
   g_sma_handle=iMA(g_sym,PERIOD_H4,200,0,MODE_SMA,PRICE_CLOSE);
   if(g_atr_handle==INVALID_HANDLE||g_sma_handle==INVALID_HANDLE) return INIT_FAILED;
   LoadState();
   if(g_init_bal<=0){ g_init_bal=AccountInfoDouble(ACCOUNT_BALANCE); SaveState(); }  // [R7e] neo 1 lan
   EventSetTimer(I_TGPollSec);
   g_last_h4_bar=iTime(g_sym,PERIOD_H4,0);
   TG("RB_EA v0.2 online\n"+StatusText());
   return INIT_SUCCEEDED; }
void OnDeinit(const int r){
   SaveState(); EventKillTimer();
   if(g_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_atr_handle);
   if(g_sma_handle!=INVALID_HANDLE) IndicatorRelease(g_sma_handle); }
void OnTimer(){ TGPoll(); }

//=== CORE ==========================================================
void OnTick(){
   //-- [R7e] breaker TONG: -I_MaxTotalDD% tu balance ban dau -> dong het + halt VINH VIEN
   if(!g_perm_halt && I_MaxTotalDD>0 && g_init_bal>0){
      if(AccountInfoDouble(ACCOUNT_EQUITY) <= g_init_bal*(1.0-I_MaxTotalDD/100.0)){
         g_perm_halt=true; g_armed=false; g_mode=MODE_NEUTRAL;
         CancelAllPending(); CloseAllOurs(); SaveState();
         TG(StringFormat("TOTAL BREAKER -%.1f%% tu initial %.2f — PERM HALT. Can nguoi reset GlobalVariable.",I_MaxTotalDD,g_init_bal));
      }
   }
   if(g_perm_halt) return;
   CheckTimeStop();                                     // [F1] moi tick
   //-- Friday cleanup
   if(I_FridayCleanup){
      MqlDateTime dt; TimeToStruct(TimeCurrent(),dt);
      if(dt.day_of_week==5&&dt.hour>=I_FridayHour&&g_armed){
         g_armed=false; CancelAllPending();
         if(I_FridayFlat) CloseAllOurs();               // [C6]
         SaveState(); TG("Friday cleanup"+(I_FridayFlat?" + FLAT":"")); } }
   //-- Day reset (server day)
   MqlDateTime now; TimeToStruct(TimeCurrent(),now);
   long daykey=now.year*10000+now.mon*100+now.day;
   if(daykey!=g_last_day){
      g_last_day=daykey; g_day_eq0=AccountInfoDouble(ACCOUNT_EQUITY);
      g_bud_rb=1; g_bud_rs=1; g_bud_bk=1; g_blocked_dir=0;
      if(g_mode==MODE_NEUTRAL||g_mode==MODE_BREAK) g_mode=MODE_RANGE;
      SaveState(); }
   //-- [C7] Week reset theo Monday server (khong con lech thu 5 UTC nhu v0.1)
   if(now.day_of_week==1){                              // Monday = moc tuan chuan prop-firm
      long mon_key=now.year*10000+now.mon*100+now.day;
      if(mon_key!=g_last_week){ g_last_week=mon_key; g_week_eq0=AccountInfoDouble(ACCOUNT_EQUITY); SaveState(); } }
   if(g_week_eq0<=0) g_week_eq0=AccountInfoDouble(ACCOUNT_EQUITY);  // khoi tao lan dau

   //-- DD breakers
   double eq=AccountInfoDouble(ACCOUNT_EQUITY); bool breaker=false;
   if(I_MaxDailyDD>0 && g_day_eq0>0 && (eq/g_day_eq0-1)*100 < -I_MaxDailyDD) breaker=true;
   if(I_MaxWeeklyDD>0 && g_week_eq0>0 && (eq/g_week_eq0-1)*100 < -I_MaxWeeklyDD) breaker=true;
   if(breaker && g_mode!=MODE_NEUTRAL){
      g_mode=MODE_NEUTRAL; CancelAllPending();
      if(I_CloseOnBreaker) CloseAllOurs();
      SaveState(); TG("DD BREAKER - NEUTRAL"); }
   if(!g_armed || g_mode==MODE_NEUTRAL) return;

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
         // v0.1 cho them 1 nen (tre 4h) = lech backtest. E1 pending-stop da rut (Fable-B).
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
      //-- RANGE_SELL (F2: tru budget khi MarketIn TRUE)
      if(h1>=bh-I_TouchBufATR*atr && g_bud_rs>0 && (g_blocked_dir&2)==0 && sell_ok){
         double sl=bh+I_RangeSLBuf*atr, tp=bl;
         if(sl-c1>0.05*atr && (c1-tp)/(sl-c1)>=1.0){
            if(MarketIn(-1,sl,tp,"RANGE_SELL")){ g_bud_rs--; SaveState(); } }
      }
      else if(l1<=bl+I_TouchBufATR*atr && g_bud_rb>0 && (g_blocked_dir&1)==0 && buy_ok){
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
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(trans.deal)) return;
   if(HistoryDealGetInteger(trans.deal,DEAL_MAGIC)!=I_Magic) return;
   if(HistoryDealGetString(trans.deal,DEAL_SYMBOL)!=g_sym) return;
   ENUM_DEAL_ENTRY de=(ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   // lenh vao (gom BREAK-stop fill): cap nhat gap-timer. Budget bk da tru luc DAT pending (F2, khong phu thuoc comment).
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
