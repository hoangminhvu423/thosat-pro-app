#!/usr/bin/env python3
"""XAU SHADOW-RUN (doc lap voi MT5-execution; data = MT5 export cua Sep, bat ky TF<=H1) (forward paper-trade, moi dem) — sleeve BREAK Donchian-20 DONG BANG (R7g).
Chay: python3 xau_shadow.py <mt5_csv_export> [log_csv]  (format: Date;O;H;L;C;V, Y.m.d H:M)
- Data: ff137/bitstamp-btcusd-minute-data updates file (unix ts, 2025-01 -> nay, tu cap nhat daily).
- Chi ghi lenh DA DONG (SL/TP cham). Lenh dang mo se duoc ghi o dem sau khi dong.
- Idempotent: dedupe theo (entry_ts,dir) — chay lai khong trung dong.
- GOLIVE 2026-07-23: dong truoc do la backfill (danh dau B), sau do la forward (F).
"""
import sys, os
from datetime import datetime
FEE=0.04; GOLIVE=datetime(2026,7,23)
LOG=sys.argv[2] if len(sys.argv)>2 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"xau_shadow_log.csv")

def load_1min(p):
    m30={}; order=[]
    with open(p) as f:
        f.readline()
        for line in f:
            parts=line.strip().split(';')
            if len(parts)<5: continue
            try:
                dt=datetime.strptime(parts[0],"%Y.%m.%d %H:%M")
                o,h,l,c=float(parts[1]),float(parts[2]),float(parts[3]),float(parts[4])
            except: continue
            k=dt.replace(minute=(dt.minute//30)*30,second=0)
            if k not in m30:
                m30[k]=[o,h,l,c]; order.append(k)
            else:
                b=m30[k]; b[1]=max(b[1],h); b[2]=min(b[2],l); b[3]=c
    order.sort()
    return [(k,)+tuple(m30[k]) for k in order]

def run(rows):
    # H4 + m-index ranges
    h=[]; hm0=[]; hm1=[]; cur=None
    for i,(dt,o,hh,ll,c) in enumerate(rows):
        k=dt.replace(hour=(dt.hour//4)*4,minute=0)
        if cur!=k:
            h.append([k,o,hh,ll,c]); hm0.append(i); hm1.append(i); cur=k
        else:
            h[-1][2]=max(h[-1][2],hh); h[-1][3]=min(h[-1][3],ll); h[-1][4]=c; hm1[-1]=i
    nH=len(h); P=20
    tr=[h[0][2]-h[0][3]]+[max(h[i][2]-h[i][3],abs(h[i][2]-h[i-1][4]),abs(h[i][3]-h[i-1][4])) for i in range(1,nH)]
    atr=[None]*nH
    if nH<=P: return [],0
    atr[P-1]=sum(tr[:P])/P
    for i in range(P,nH): atr[i]=(atr[i-1]*(P-1)+tr[i])/P
    from datetime import timedelta
    gap_after=set()
    for gi in range(len(rows)-1):
        d1,d2=rows[gi][0],rows[gi+1][0]
        if (d2-d1)>timedelta(hours=12) and not(d1.weekday()==4 and d2.weekday() in (0,6)):
            gap_after.add(gi)
    trades=[]; open_ct=0; skipped_hole=0; prevc=0
    for i in range(P,nH-1):
        a=atr[i]
        if not a or a<=0: prevc=0; continue
        bh=max(h[k][2] for k in range(i-P,i)); bl=min(h[k][3] for k in range(i-P,i))
        c=h[i][4]
        cond=1 if c>bh+0.25*a else (-1 if c<bl-0.25*a else 0)
        fresh=(cond!=0 and cond!=prevc); prevc=cond
        if not fresh: continue
        d=cond; mj=hm0[i+1]; ep=rows[mj][1]
        sl=ep-d*a; tp=ep+d*2*a
        x=None; xt=None
        for j in range(mj,len(rows)):
            _,o,hh,ll,cc=rows[j]
            if d==1:
                if ll<=sl: x=(o if o<sl else sl); xt=rows[j][0]; break
                if hh>=tp: x=(o if o>tp else tp); xt=rows[j][0]; break
            else:
                if hh>=sl: x=(o if o>sl else sl); xt=rows[j][0]; break
                if ll<=tp: x=(o if o<tp else tp); xt=rows[j][0]; break
        if x is None: open_ct+=1; continue          # lenh dang mo -> dem sau
        # HOLE-GUARD: duong di entry->exit xuyen lo hong data -> fill khong tin duoc, bo
        xj=next((jj for jj in range(mj,len(rows)) if rows[jj][0]==xt),len(rows)-1)
        if any(g in gap_after for g in range(mj,xj)): skipped_hole+=1; continue
        trades.append((rows[mj][0], d, round(d*(x-ep)/a-FEE,3), xt))
    print(f"[shadow] bo vi xuyen lo hong data: {skipped_hole}")
    return trades, open_ct

def main():
    rows=load_1min(sys.argv[1])
    if not rows: print("[shadow] khong co data"); return
    trades,open_ct=run(rows)
    seen=set()
    if os.path.exists(LOG):
        for l in open(LOG):
            p=l.strip().split(',')
            if len(p)>=2 and not l.startswith('#'): seen.add((p[0],p[1]))
    new=[]
    for et,d,r,xt in trades:
        key=(et.strftime('%Y-%m-%d %H:%M'),str(d))
        if key not in seen:
            tag='F' if et>=GOLIVE else 'B'
            new.append(f"{key[0]},{d},{r},{xt:%Y-%m-%d %H:%M},{tag}")
    mode='a' if os.path.exists(LOG) else 'w'
    with open(LOG,mode) as f:
        if mode=='w': f.write("# entry_ts,dir,netR,exit_ts,tag(B=backfill,F=forward) | sleeve BREAK Donchian-20 dong bang R7g | golive 2026-07-23\n")
        for l in new: f.write(l+"\n")
    fwd=[l for l in open(LOG) if l.strip().endswith(',F')]
    fr=[float(l.split(',')[2]) for l in fwd]
    print(f"[shadow] data den {rows[-1][0]:%Y-%m-%d %H:%M} | moi ghi: {len(new)} | dang mo: {open_ct}")
    print(f"[shadow] FORWARD tich luy: n={len(fr)} totR={sum(fr):+.2f} avgR={(sum(fr)/len(fr)) if fr else 0:+.3f}")
if __name__=='__main__': main()
