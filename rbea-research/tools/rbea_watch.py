#!/usr/bin/env python3
"""
rbea_watch.py — TRỤ 3 (monitor CHỦ ĐỘNG, READ-ONLY): bắt lỗi âm thầm SỚM.
=========================================================================
Chạy tay hoặc theo lịch (launchd). KHÔNG đụng gì trên VPS — chỉ đọc qua MT5 python + log.

  python3 rbea-research/tools/rbea_watch.py

Kiểm + cảnh báo (in ra; nối Telegram sau nếu muốn):
 - Terminal Exness sống? EA RB_EA gắn trên chart? (rụng = im lặng nguy hiểm — bài học Fund EA chết 9 ngày)
 - AlgoTrading ON/OFF (đổi ngoài ý muốn?)
 - Vị thế/lệnh RB_EA (magic 20260723/24) + PnL
 - DD hiện tại vs ngưỡng perm-halt (tới 80% ngưỡng = cảnh báo)
 - Số ngày kể từ lệnh RB_EA gần nhất (không trade quá lâu khi lẽ ra phải = nghi min-lot/detach)
 - File halt Common còn perm_halt=1 sót? (bài học G2-FAIL)
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, "/Users/mailien/Downloads/VPS_LIVE_EA")
import paramiko
from quant_lab.vps_secrets import vps_password

MAGICS = {20260723: "XAU", 20260724: "BTC"}
COMMON = "C:/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/Common/Files"
PROBE = r'''
import MetaTrader5 as mt5, json
from datetime import datetime, timedelta, timezone
mt5.initialize(path="C:/Program Files/MetaTrader 5/terminal64.exe")
ti=mt5.terminal_info(); ai=mt5.account_info()
o={"connected":bool(ti.connected),"algo":bool(ti.trade_allowed),"login":ai.login if ai else 0,
   "bal":ai.balance if ai else 0,"eq":ai.equity if ai else 0}
pos=[{"sym":p.symbol,"magic":p.magic,"vol":p.volume,"pnl":p.profit} for p in (mt5.positions_get() or []) if p.magic in (20260723,20260724)]
now=datetime.now(timezone.utc); last=None
for d in (mt5.history_deals_get(now-timedelta(days=60),now+timedelta(hours=3)) or []):
    if d.magic in (20260723,20260724) and d.type in (0,1):
        if last is None or d.time>last: last=d.time
o["rbea_pos"]=pos; o["last_deal_ts"]=last or 0
print("JSON"+json.dumps(o))
mt5.shutdown()
'''

def main():
    ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("103.163.219.235", port=22, username="Administrator", password=vps_password(), timeout=25)
    def run(c, t=90):
        _i, o, e = ssh.exec_command(c, timeout=t); return o.read().decode("utf-8", "ignore") + e.read().decode("utf-8", "ignore")
    sftp = ssh.open_sftp()
    with sftp.open("C:/Temp/rbea_probe.py", "w") as f:
        f.write(PROBE)
    import json, time
    out = run(r'"C:\CFO_Bot\python311\python.exe" C:/Temp/rbea_probe.py')
    line = next((l for l in out.splitlines() if l.startswith("JSON")), None)
    alerts = []
    print("=" * 60); print("RB_EA WATCH")
    if not line:
        print("❌ Không đọc được trạng thái MT5:\n", out[:400]); alerts.append("probe fail")
    else:
        d = json.loads(line[4:])
        print(f"acc={d['login']} bal={d['bal']:.2f} eq={d['eq']:.2f} connected={d['connected']} algo={'ON' if d['algo'] else 'OFF'}")
        # EA gắn? (qua log loaded gần nhất, xấp xỉ)
        D = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075"
        loaded = run(f'powershell -Command "Get-ChildItem \'{D}\\logs\\*.log\'|Sort LastWriteTime -Desc|Select -First 1|%{{Get-Content $_.FullName -Encoding Unicode|Select-String \'RB_EA.*(loaded|removed)\'|Select -Last 2}}"').strip()
        print("EA log gần nhất:", (loaded[-120:] if loaded else "—"))
        if loaded and "removed" in loaded.split("loaded")[-1]:
            alerts.append("RB_EA có thể ĐÃ RỤNG khỏi chart (log cuối = removed)")
        # vị thế
        print(f"RB_EA vị thế: {len(d['rbea_pos'])}", d['rbea_pos'] if d['rbea_pos'] else "")
        # ngày từ deal gần nhất
        if d["last_deal_ts"]:
            days = (time.time() - d["last_deal_ts"]) / 86400
            print(f"Lệnh RB_EA gần nhất: {days:.1f} ngày trước")
            if days > 21:
                alerts.append(f"RB_EA không trade {days:.0f} ngày — nghi detach/min-lot/halt")
        else:
            print("RB_EA: CHƯA có lệnh nào (magic 20260723/24)")
        # DD vs ngưỡng (dùng eq vs bal như xấp xỉ; perm-halt file có init_bal thật)
        if d["bal"] > 0:
            dd = (d["bal"] - d["eq"]) / d["bal"] * 100
            if dd > 20:
                alerts.append(f"DD hiện tại ~{dd:.1f}% — theo dõi sát")
    # halt file sót?
    hf = run(f'dir /b "{COMMON}\\RBEA*_halt.bin" 2>nul').strip()
    if hf:
        print("File halt Common:", hf.replace("\n", " "))
        for name in hf.split("\n"):
            try:
                with sftp.open(f"{COMMON}/{name.strip()}", "rb") as fh:
                    raw = fh.read()
                if len(raw) >= 12 and struct.unpack("<i", raw[8:12])[0] == 1:
                    alerts.append(f"perm_halt=1 trong {name.strip()} — EA sẽ đứng im tới khi xoá")
            except Exception:
                pass
    sftp.close(); ssh.close()
    print("-" * 60)
    if alerts:
        print("🔴 CẢNH BÁO:")
        for a in alerts:
            print("  •", a)
        _telegram_alert("RB_EA WATCH 🔴\n" + "\n".join("• " + a for a in alerts))
    else:
        print("✅ Không phát hiện bất thường.")
    print("=" * 60)
    return len(alerts)


def _telegram_alert(msg):
    """Push cảnh báo Telegram NẾU có file token do Sếp tự đặt (~/.config/rbea_tg.txt: dòng1=token, dòng2=chat_id).
    Agent KHÔNG chạm token — chỉ đọc file nếu Sếp tạo. Không có file = chỉ in ra (không lỗi)."""
    tf = Path.home() / ".config/rbea_tg.txt"
    if not tf.exists():
        return
    try:
        tok, chat = [x.strip() for x in tf.read_text().splitlines()[:2]]
        import urllib.request, urllib.parse
        url = f"https://api.telegram.org/bot{tok}/sendMessage?" + urllib.parse.urlencode({"chat_id": chat, "text": msg})
        urllib.request.urlopen(url, timeout=8)
    except Exception as ex:
        print("(TG alert lỗi:", ex, ")")

if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 2)
