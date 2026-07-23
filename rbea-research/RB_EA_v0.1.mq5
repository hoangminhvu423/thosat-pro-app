//+------------------------------------------------------------------+
//| RB_EA.mq5 — Range/Break Semi-Auto EA v0.1                        |
//| Spec: RB_EA_Master_Spec (L1-L10 locked)                          |
//| NGUOI ve vung (2 hline RB_HI / RB_LO) — MAY thi hanh ky luat     |
//| State machine: RANGE / BREAK / NEUTRAL                           |
//| Budget/ngay: 1 RANGE_BUY + 1 RANGE_SELL + 1 BREAK, gap >= 60'    |
//| Telegram 2 chieu: /status /arm /disarm /flat /help               |
//| Ke thua bai hoc SC6: fill-mode auto, retry+verify close,         |
//|   persist GlobalVariable, server-day reset, Friday cleanup       |
//| CHUA AUDIT — bat buoc qua Phase 4 (ea-code-audit) truoc demo     |
//| LUU Y: file luu duoi ten .txt tren Drive do su co container —    |
//|   doi ten thanh RB_EA_v0.1.mq5 truoc khi compile                 |
//+------------------------------------------------------------------+
#property copyright "RB_EA v0.1 - QTQ project"
#property version   "0.10"
#property strict
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

CTrade        g_trade;
CPositionInfo g_pos;

//=== INPUTS =========================================================
input group "=== ZONE (nguoi ve) ==="
input string I_HiLine      = "RB_HI";   // ten hline bien tren
input string I_LoLine      = "RB_LO";   // ten hline bien duoi
input double I_MinZoneATR  = 1.5;       // do rong vung toi thieu (xATR H4)

input group "=== STRATEGY (theo backtest 2012-2022) ==="
input double I_TouchBufATR = 0.15;      // vung cham bien (xATR)
input double I_BreakBufATR = 0.25;      // buffer xac nhan pha vo (xATR)
input double I_RangeSLBuf  = 0.50;      // SL ngoai bien (xATR)
input double I_BreakSL_ATR = 1.0;       // SL lenh break (xATR)
input double I_BreakTP_ATR = 2.0;       // TP lenh break (xATR)
input bool   I_TrendFilter = true;      // chan RANGE nguoc SMA200 H4 (O3)
input int    I_MinGapMin   = 60;        // phut toi thieu giua 2 lenh
input int    I_MaxHoldBars = 48;        // time-stop (nen H4)

input group "=== RISK ==="
input double I_RiskPct       = 0.5;     // % balance / lenh
input double I_MaxDailyDD    = 3.0;     // % daily DD -> NEUTRAL het ngay
input double I_MaxWeeklyDD   = 8.0;     // % weekly DD -> NEUTRAL het tuan
input bool   I_CloseOnBreaker= false;   // breaker no: false=giu vi the (co SL), true=dong het
input bool   I_FridayCleanup = true;    // huy pending + disarm truoc weekend
input int    I_FridayHour    = 21;      // gio broker (Exness UTC+3)

input group "=== TELEGRAM ==="
input string I_TGToken   = "";          // bot token (KHONG hardcode - bai hoc TQT)
input string I_TGChatID  = "";          // chat id duy nhat duoc phep dieu khien
input int    I_TGPollSec = 5;           // chu ky poll getUpdates

input group "=== EXEC ==="
input int    I_Magic     = 20260721;
input int    I_Deviation = 30;
input string I_Comment   = "RB_EA_v01";

//=== STATE (persist qua GlobalVariable — bai hoc SC6 RAM-only bug) ==
enum EMode { MODE_RANGE=0, MODE_BREAK=1, MODE_NEUTRAL=2 };
int      g_mode        = MODE_RANGE;
bool     g_armed       = false;
double   g_zone_hi=0, g_zone_lo=0;
double   g_frozen_hi=0, g_frozen_lo=0;
int      g_bud_rb=1, g_bud_rs=1, g_bud_bk=1;
int      g_blocked_dir=0;                // bitmask whipsaw: 1=buy, 2=sell
datetime g_last_trade_t=0;
int      g_pend_break_dir=0;
long     g_last_day=-1, g_last_week=-1;
double   g_day_eq0=0, g_week_eq0=0;
int      g_atr_handle=INVALID_HANDLE, g_sma_handle=INVALID_HANDLE;
datetime g_last_h4_bar=0;
long     g_tg_offset=0;
string   g_sym;

string GV(string k){ return "RBEA_"+g_sym+"_"+(string)I_Magic+"_"+k; }
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
}

//=== FILL MODE AUTO (SC6 v3.7-A: khong hardcode FOK) ================
ENUM_ORDER_TYPE_FILLING AutoFill(string sym){
   long fm=SymbolInfoInteger(sym,SYMBOL_FILLING_MODE);
   if((fm&SYMBOL_FILLING_FOK)!=0) return ORDER_FILLING_FOK;
   if((fm&SYMBOL_FILLING_IOC)!=0) return ORDER_FILLING_IOC;
   return ORDER_FILLING_RETURN;
}
//=== CLOSE retry+verify (bai hoc QTQ v1) ============================
bool ClosePositionVerified(ulong ticket){
   for(int a=0;a<3;a++){
      g_trade.SetTypeFillingBySymbol(g_sym);
      if(g_trade.PositionClose(ticket)){
         if(!PositionSelectByTicket(ticket)) return true;
      }
      Sleep(300);
   }
   PrintFormat("[RBEA-ERR] Close #%d FAILED sau 3 retry rc=%d",(int)ticket,g_trade.ResultRetcode());
   TG("CANH BAO: CLOSE FAIL #"+(string)ticket+" rc="+(string)g_trade.ResultRetcode());
   return false;
}

//=== TELEGRAM =======================================================
string UrlEnc(string s){
   string r=""; uchar b[]; StringToCharArray(s,b,0,WHOLE_ARRAY,CP_UTF8);
   for(int i=0;i<ArraySize(b)-1;i++){
      uchar c=b[i];
      if((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='-'||c=='_'||c=='.') r+=CharToString(c);
      else r+=StringFormat("%%%02X",c);
   }
   return r;
}
void TG(string msg){
   if(I_TGToken=="") return;
   string url="https://api.telegram.org/bot"+I_TGToken+"/sendMessage?chat_id="+I_TGChatID+"&text="+UrlEnc(msg);
   char post[],res[]; string hdr;
   WebRequest("GET",url,"",3000,post,res,hdr);  // nho whitelist api.telegram.org trong MT5
}
string StatusText(){
   string m = g_mode==MODE_RANGE?"RANGE":(g_mode==MODE_BREAK?"BREAK":"NEUTRAL");
   return StringFormat("RB_EA %s\nARMED: %s | MODE: %s\nZone: %.2f - %.2f\nBudget RB/RS/BK: %d/%d/%d\nRisk: %.2f%% | Eq: %.2f",
      g_sym, g_armed?"YES":"no", m, g_zone_lo, g_zone_hi, g_bud_rb,g_bud_rs,g_bud_bk,
      I_RiskPct, AccountInfoDouble(ACCOUNT_EQUITY));
}
void TGPoll(){
   if(I_TGToken=="") return;
   string url="https://api.telegram.org/bot"+I_TGToken+"/getUpdates?timeout=0&offset="+(string)(g_tg_offset+1);
   char post[],res[]; string hdr;
   if(WebRequest("GET",url,"",3000,post,res,hdr)!=200) return;
   string body=CharArrayToString(res,0,WHOLE_ARRAY,CP_UTF8);
   int p=0;
   while((p=StringFind(body,"\"update_id\":",p))>=0){
      p+=12;
      long uid=StringToInteger(StringSubstr(body,p,12));
      if(uid>g_tg_offset) g_tg_offset=uid;
      int cp=StringFind(body,"\"chat\":{\"id\":",p);
      int tp=StringFind(body,"\"text\":\"",p);
      if(cp<0||tp<0) break;
      string chat=StringSubstr(body,cp+13,20);
      int comma=StringFind(chat,","); if(comma>0) chat=StringSubstr(chat,0,comma);
      tp+=8; int te=StringFind(body,"\"",tp);
      string cmd=StringSubstr(body,tp,te-tp);
      if(chat==I_TGChatID) HandleCmd(cmd);          // whitelist 1 chat id
      else PrintFormat("[RBEA-SEC] Tu choi lenh tu chat la: %s",chat);
   }
   SaveState();
}
void HandleCmd(string cmd){
   StringToLower(cmd);
   if(StringFind(cmd,"/status")==0){ TG(StatusText()); }
   else if(StringFind(cmd,"/arm")==0 && StringFind(cmd,"/disarm")!=0){
      if(ReadZone(true)){ g_armed=true; g_mode=MODE_RANGE; TG("ARMED OK\n"+StatusText()); }
      else TG("ARM FAIL: vung khong hop le (can 2 hline RB_HI>RB_LO, rong >= "+DoubleToString(I_MinZoneATR,1)+"xATR)");
   }
   else if(StringFind(cmd,"/disarm")==0){ g_armed=false; CancelAllPending(); TG("DISARMED (vi the mo van giu SL)"); }
   else if(StringFind(cmd,"/flat")==0){ g_armed=false; CancelAllPending(); CloseAllOurs(); TG("FLAT-ALL xong"); }
   else if(StringFind(cmd,"/help")==0){ TG("/status /arm /disarm /flat"); }
   SaveState();
}

//=== ZONE INPUT =====================================================
bool ReadZone(bool announce){
   if(ObjectFind(0,I_HiLine)<0 || ObjectFind(0,I_LoLine)<0) return false;
   double hi=ObjectGetDouble(0,I_HiLine,OBJPROP_PRICE);
   double lo=ObjectGetDouble(0,I_LoLine,OBJPROP_PRICE);
   if(hi<=lo) return false;
   double atr=ATRv(); if(atr<=0) return false;
   if(hi-lo < I_MinZoneATR*atr){
      if(announce) PrintFormat("[RBEA] Vung qua hep: %.2f < %.1fxATR(%.2f)",hi-lo,I_MinZoneATR,atr);
      return false;
   }
   g_zone_hi=hi; g_zone_lo=lo;
   return true;
}

//=== INDICATORS (cache handle — checklist audit) ====================
double ATRv(){
   double b[]; ArraySetAsSeries(b,true);
   if(CopyBuffer(g_atr_handle,0,1,1,b)<1) return 0;
   return b[0];
}
double SMAv(){
   double b[]; ArraySetAsSeries(b,true);
   if(CopyBuffer(g_sma_handle,0,1,1,b)<1) return 0;
   return b[0];
}

//=== HELPERS ========================================================
bool OursOpen(){
   for(int i=PositionsTotal()-1;i>=0;i--)
      if(g_pos.SelectByIndex(i)&&g_pos.Symbol()==g_sym&&g_pos.Magic()==I_Magic) return true;
   return false;
}
void CloseAllOurs(){
   for(int i=PositionsTotal()-1;i>=0;i--)
      if(g_pos.SelectByIndex(i)&&g_pos.Symbol()==g_sym&&g_pos.Magic()==I_Magic)
         ClosePositionVerified(g_pos.Ticket());
}
void CancelAllPending(){
   for(int i=OrdersTotal()-1;i>=0;i--){
      ulong t=OrderGetTicket(i);
      if(OrderGetString(ORDER_SYMBOL)==g_sym&&OrderGetInteger(ORDER_MAGIC)==I_Magic)
         g_trade.OrderDelete(t);
   }
   g_pend_break_dir=0;
}
double CalcLot(double entry,double sl){
   double risk_amt=AccountInfoDouble(ACCOUNT_BALANCE)*I_RiskPct/100.0;
   double tick_val=SymbolInfoDouble(g_sym,SYMBOL_TRADE_TICK_VALUE);
   double tick_sz =SymbolInfoDouble(g_sym,SYMBOL_TRADE_TICK_SIZE);
   double dist=MathAbs(entry-sl); if(dist<=0||tick_val<=0||tick_sz<=0) return 0;
   double lot=risk_amt/(dist/tick_sz*tick_val);
   double minl=SymbolInfoDouble(g_sym,SYMBOL_VOLUME_MIN);
   double stp =SymbolInfoDouble(g_sym,SYMBOL_VOLUME_STEP);
   lot=MathFloor(lot/stp)*stp;
   if(lot<minl){                                  // KHONG ep min-lot am tham
      PrintFormat("[RBEA-SKIP] lot %.2f < min %.2f — bo lenh (khong over-risk)",lot,minl);
      return 0;
   }
   return lot;
}
void MarketIn(int dir,double sl,double tp,string tag){
   double px = dir>0?SymbolInfoDouble(g_sym,SYMBOL_ASK):SymbolInfoDouble(g_sym,SYMBOL_BID);
   double lot=CalcLot(px,sl); if(lot<=0) return;
   g_trade.SetTypeFillingBySymbol(g_sym);
   bool ok = dir>0 ? g_trade.Buy(lot,g_sym,0,sl,tp,I_Comment+"_"+tag)
                   : g_trade.Sell(lot,g_sym,0,sl,tp,I_Comment+"_"+tag);
   if(ok){
      g_last_trade_t=TimeCurrent();
      PrintFormat("[RBEA-ENTRY] %s %s lot=%.2f sl=%.2f tp=%.2f",tag,dir>0?"BUY":"SELL",lot,sl,tp);
      TG(StringFormat("ENTRY %s %s %s | lot %.2f | SL %.2f | TP %.2f",g_sym,tag,dir>0?"BUY":"SELL",lot,sl,tp));
   } else PrintFormat("[RBEA-FAIL] %s rc=%d",tag,g_trade.ResultRetcode());
}

//=== INIT ===========================================================
int OnInit(){
   g_sym=Symbol();
   g_trade.SetExpertMagicNumber(I_Magic);
   g_trade.SetDeviationInPoints(I_Deviation);
   g_trade.SetTypeFilling(AutoFill(g_sym));
   g_atr_handle=iATR(g_sym,PERIOD_H4,20);
   g_sma_handle=iMA(g_sym,PERIOD_H4,200,0,MODE_SMA,PRICE_CLOSE);
   if(g_atr_handle==INVALID_HANDLE||g_sma_handle==INVALID_HANDLE) return INIT_FAILED;
   LoadState();
   EventSetTimer(I_TGPollSec);
   g_last_h4_bar=iTime(g_sym,PERIOD_H4,0);
   Print("[RBEA] v0.1 init. ",StatusText());
   TG("RB_EA v0.1 online\n"+StatusText());
   return INIT_SUCCEEDED;
}
void OnDeinit(const int r){
   SaveState(); EventKillTimer();
   if(g_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_atr_handle);
   if(g_sma_handle!=INVALID_HANDLE) IndicatorRelease(g_sma_handle);
}
void OnTimer(){ TGPoll(); }

//=== CORE ===========================================================
void OnTick(){
   //-- Friday cleanup (SC6 Fix-M: chan weekend gap-fill)
   if(I_FridayCleanup){
      MqlDateTime dt; TimeToStruct(TimeCurrent(),dt);
      if(dt.day_of_week==5&&dt.hour>=I_FridayHour&&g_armed){
         g_armed=false; CancelAllPending(); SaveState();
         TG("Friday cleanup: DISARM + huy pending");
      }
   }
   //-- Day/Week reset (SERVER day — chuan FTMO)
   MqlDateTime now; TimeToStruct(TimeCurrent(),now);
   long daykey=now.year*10000+now.mon*100+now.day;
   if(daykey!=g_last_day){
      g_last_day=daykey; g_day_eq0=AccountInfoDouble(ACCOUNT_EQUITY);
      g_bud_rb=1; g_bud_rs=1; g_bud_bk=1; g_blocked_dir=0;
      if(g_mode==MODE_NEUTRAL||g_mode==MODE_BREAK) g_mode=MODE_RANGE;  // ngay moi: nguoi ve lai
      SaveState();
   }
   long wk=(long)((TimeCurrent()+3*86400)/(7*86400));
   if(wk!=g_last_week){ g_last_week=wk; g_week_eq0=AccountInfoDouble(ACCOUNT_EQUITY); SaveState(); }

   //-- DD breakers (tinh ca floating)
   double eq=AccountInfoDouble(ACCOUNT_EQUITY);
   bool breaker=false;
   if(I_MaxDailyDD>0 && g_day_eq0>0 && (eq/g_day_eq0-1)*100 < -I_MaxDailyDD) breaker=true;
   if(I_MaxWeeklyDD>0 && g_week_eq0>0 && (eq/g_week_eq0-1)*100 < -I_MaxWeeklyDD) breaker=true;
   if(breaker && g_mode!=MODE_NEUTRAL){
      g_mode=MODE_NEUTRAL; CancelAllPending();
      if(I_CloseOnBreaker) CloseAllOurs();
      SaveState();
      TG("DD BREAKER — NEUTRAL. "+(I_CloseOnBreaker?"Da dong het vi the.":"Vi the mo giu SL cung."));
   }
   if(!g_armed || g_mode==MODE_NEUTRAL) return;

   //-- Chi hanh dong khi nen H4 MOI dong (index 1 — chong repaint)
   datetime cur_bar=iTime(g_sym,PERIOD_H4,0);
   if(cur_bar==g_last_h4_bar) return;
   g_last_h4_bar=cur_bar;
   OnNewH4();
}

void OnNewH4(){
   double atr=ATRv(); if(atr<=0) return;
   double c1=iClose(g_sym,PERIOD_H4,1);
   double h1=iHigh (g_sym,PERIOD_H4,1);
   double l1=iLow  (g_sym,PERIOD_H4,1);
   bool gap_ok=(TimeCurrent()-g_last_trade_t)>=I_MinGapMin*60;

   //-- Vao lenh BREAK da hen tu nen truoc
   if(g_pend_break_dir!=0 && !OursOpen()){
      int d=g_pend_break_dir;
      double px=d>0?SymbolInfoDouble(g_sym,SYMBOL_ASK):SymbolInfoDouble(g_sym,SYMBOL_BID);
      double sl=px-d*I_BreakSL_ATR*atr, tp=px+d*I_BreakTP_ATR*atr;
      MarketIn(d,sl,tp,"BREAK"); g_bud_bk--;
      g_pend_break_dir=0; SaveState(); return;
   }
   g_pend_break_dir=0;

   if(g_mode==MODE_RANGE){
      if(!ReadZone(false)){ Print("[RBEA] Mat hline vung — cho nguoi ve lai"); return; }
      double bh=g_zone_hi, bl=g_zone_lo;
      //-- Pha vo xac nhan bang CLOSE + buffer (L3)
      if(c1>bh+I_BreakBufATR*atr || c1<bl-I_BreakBufATR*atr){
         int d = c1>bh ? 1 : -1;
         g_frozen_hi=bh; g_frozen_lo=bl; g_mode=MODE_BREAK;
         TG(StringFormat("BREAK %s xac nhan @ %.2f",d>0?"UP":"DOWN",c1));
         if(g_bud_bk>0 && gap_ok && !OursOpen()) g_pend_break_dir=d;
         SaveState(); return;
      }
      if(OursOpen()||!gap_ok) return;
      double sma=SMAv();
      bool sell_ok = !(I_TrendFilter && sma>0 && c1>sma);
      bool buy_ok  = !(I_TrendFilter && sma>0 && c1<sma);
      //-- RANGE_SELL: cham bien tren
      if(h1>=bh-I_TouchBufATR*atr && g_bud_rs>0 && (g_blocked_dir&2)==0 && sell_ok){
         double sl=bh+I_RangeSLBuf*atr, tp=bl;                 // TP=TRAV (O2)
         if(sl-c1>0.05*atr && (c1-tp)/(sl-c1)>=1.0){
            MarketIn(-1,sl,tp,"RANGE_SELL"); g_bud_rs--; SaveState();
         }
      }
      //-- RANGE_BUY: cham bien duoi
      else if(l1<=bl+I_TouchBufATR*atr && g_bud_rb>0 && (g_blocked_dir&1)==0 && buy_ok){
         double sl=bl-I_RangeSLBuf*atr, tp=bh;
         if(c1-sl>0.05*atr && (tp-c1)/(c1-sl)>=1.0){
            MarketIn(1,sl,tp,"RANGE_BUY"); g_bud_rb--; SaveState();
         }
      }
   }
   else if(g_mode==MODE_BREAK){
      //-- False break: dong nguoc vao trong box -> NEUTRAL het ngay (L4)
      if(c1<g_frozen_hi && c1>g_frozen_lo){
         g_mode=MODE_NEUTRAL; g_pend_break_dir=0; SaveState();
         TG("FALSE BREAK — NEUTRAL het ngay, ve lai vung ngay mai");
      }
   }
}

//=== Whipsaw guard: ghi nhan SL cua lenh RANGE ======================
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &req, const MqlTradeResult &res){
   if(trans.type!=TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(trans.deal)) return;
   if(HistoryDealGetInteger(trans.deal,DEAL_MAGIC)!=I_Magic) return;
   if(HistoryDealGetString(trans.deal,DEAL_SYMBOL)!=g_sym) return;
   if((ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal,DEAL_ENTRY)!=DEAL_ENTRY_OUT) return;
   double profit=HistoryDealGetDouble(trans.deal,DEAL_PROFIT);
   ENUM_DEAL_REASON rs=(ENUM_DEAL_REASON)HistoryDealGetInteger(trans.deal,DEAL_REASON);
   if(rs==DEAL_REASON_SL && profit<0){
      long dtype=HistoryDealGetInteger(trans.deal,DEAL_TYPE);
      if(dtype==DEAL_TYPE_SELL) g_blocked_dir|=1;   // BUY vua SL -> block RANGE_BUY
      else                      g_blocked_dir|=2;
      SaveState();
   }
   TG(StringFormat("CLOSE %s P&L %+.2f (%s)",g_sym,profit,EnumToString(rs)));
}
//+------------------------------------------------------------------+
