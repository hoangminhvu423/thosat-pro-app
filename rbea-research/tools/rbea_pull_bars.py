#!/usr/bin/env python3
"""rbea_pull_bars.py — kéo BTCUSD+XAUUSD H4 từ VPS (bridge) về rbea-research/data/. READ-ONLY."""
import sys
from pathlib import Path
sys.path.insert(0, "/Users/mailien/Downloads/VPS_LIVE_EA")
import paramiko
from quant_lab.vps_secrets import vps_password

DATA = Path(__file__).resolve().parents[2] / "rbea-research/data"
EXPORTER = r'''
import MetaTrader5 as mt5, csv
from datetime import datetime, timezone
mt5.initialize(path="C:/Program Files/MetaTrader 5/terminal64.exe")
start=datetime(2023,1,1,tzinfo=timezone.utc); end=datetime(2030,1,1,tzinfo=timezone.utc)
for want in ["BTCUSD","XAUUSD"]:
    cands=[s.name for s in mt5.symbols_get() if want[:3] in s.name.upper() and "USD" in s.name.upper()]
    sym=want if want in cands else (sorted(cands,key=len)[0] if cands else None)
    if not sym: print("NO_SYM",want); continue
    mt5.symbol_select(sym,True)
    r=mt5.copy_rates_range(sym, mt5.TIMEFRAME_H4, start, end)
    if r is None or len(r)==0: print("NO_RATES",sym); continue
    with open(f"C:/Temp/bars_{want}_H4.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["time","open","high","low","close","tickvol"])
        for x in r: w.writerow([datetime.fromtimestamp(int(x["time"]),tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),x["open"],x["high"],x["low"],x["close"],int(x["tick_volume"])])
    print(f"OK {want} {len(r)} bars")
mt5.shutdown()
'''

def main():
    ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("103.163.219.235", port=22, username="Administrator", password=vps_password(), timeout=25)
    sftp = ssh.open_sftp()
    with sftp.open("C:/Temp/bar_export.py", "w") as f:
        f.write(EXPORTER)
    _i, o, e = ssh.exec_command(r'"C:\CFO_Bot\python311\python.exe" C:/Temp/bar_export.py', timeout=240)
    print(o.read().decode("utf-8", "ignore") + e.read().decode("utf-8", "ignore"))
    DATA.mkdir(parents=True, exist_ok=True)
    for want in ["BTCUSD", "XAUUSD"]:
        try:
            sftp.get(f"C:/Temp/bars_{want}_H4.csv", str(DATA / f"bars_{want}_H4.csv"))
            print("pulled", want)
        except Exception as ex:
            print("pull fail", want, ex)
    sftp.close(); ssh.close()

if __name__ == "__main__":
    main()
