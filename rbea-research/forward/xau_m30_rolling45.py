#!/usr/bin/env python3
"""
xau_m30_rolling45.py — Xuất nến XAUUSD M30 cửa sổ trượt 45 ngày từ MT5/VPS → Google Drive.
==========================================================================================
Chạy từ Mac (định kỳ 24h qua cron, hoặc kèm mỗi lần /dong-bo-skills):
  python3 rbea-research/forward/xau_m30_rolling45.py

- SSH tới VPS (password qua Keychain — quant_lab/vps_secrets, KHÔNG hardcode).
- Trên VPS: MetaTrader5 python attach terminal Exness đang chạy (READ-ONLY: copy_rates_range).
- CSV format export chuẩn MT5: Date;Open;High;Low;Close;Volume · datetime "2026.07.24 08:00".
- Ghi đè CÙNG file: QTQ_FABLE_BRIDGE/INBOX_FINDINGS/XAU_M30_rolling45d.csv (Drive hoangminhvu423).
- CHỈ 45 ngày (~150-300KB) — không bao giờ xuất full history.
"""
import sys
from pathlib import Path

WS = Path("/Users/mailien/Downloads/VPS_LIVE_EA")
sys.path.insert(0, str(WS))
import paramiko  # noqa: E402
from quant_lab.vps_secrets import vps_password  # noqa: E402

VPS_HOST, VPS_PORT, VPS_USER = "103.163.219.235", 22, "Administrator"
REMOTE_PY = r"C:\CFO_Bot\python311\python.exe"
DRIVE_OUT = Path.home() / (
    "Library/CloudStorage/GoogleDrive-hoangminhvu423@gmail.com/"
    "Drive của tôi/QTQ_FABLE_BRIDGE/INBOX_FINDINGS/XAU_M30_rolling45d.csv"
)

# Script chạy TRÊN VPS — chỉ đọc dữ liệu, không đụng lệnh/chart.
REMOTE_SCRIPT = r'''
import sys
from datetime import datetime, timedelta, timezone
import MetaTrader5 as mt5

# Attach terminal Exness dang chay (KHONG launch moi neu dang chay; read-only)
if not mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe"):
    print("ERR_INIT:", mt5.last_error()); sys.exit(1)
try:
    # Tim symbol XAU/USD dung ten broker (XAUUSD, XAUUSDm, ...)
    cands = [s.name for s in mt5.symbols_get() if "XAU" in s.name.upper() and "USD" in s.name.upper()]
    if not cands:
        print("ERR_NO_XAU"); sys.exit(1)
    sym = "XAUUSD" if "XAUUSD" in cands else sorted(cands, key=len)[0]
    mt5.symbol_select(sym, True)
    digits = mt5.symbol_info(sym).digits

    end = datetime.now(timezone.utc) + timedelta(days=1)   # dem bien server-time
    start = end - timedelta(days=46)
    rates = mt5.copy_rates_range(sym, mt5.TIMEFRAME_M30, start, end)
    if rates is None or len(rates) == 0:
        print("ERR_NO_RATES:", mt5.last_error()); sys.exit(1)

    # Cat dung cua so truot 45 ngay tinh tu nen cuoi cung
    cutoff = int(rates[-1]["time"]) - 45 * 86400
    rows = [r for r in rates if int(r["time"]) >= cutoff]

    print("CSV_BEGIN")
    print("Date;Open;High;Low;Close;Volume")
    fmt = "%." + str(digits) + "f"
    for r in rows:
        t = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)  # epoch MT5 = server-time
        print("%s;%s;%s;%s;%s;%d" % (
            t.strftime("%Y.%m.%d %H:%M"),
            fmt % r["open"], fmt % r["high"], fmt % r["low"], fmt % r["close"],
            int(r["tick_volume"])))
    print("CSV_END")
    print("META;symbol=%s;digits=%d;rows=%d;first=%s;last=%s" % (
        sym, digits, len(rows),
        datetime.fromtimestamp(int(rows[0]["time"]), tz=timezone.utc).strftime("%Y.%m.%d %H:%M"),
        datetime.fromtimestamp(int(rows[-1]["time"]), tz=timezone.utc).strftime("%Y.%m.%d %H:%M")))
finally:
    mt5.shutdown()
'''


def main() -> int:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=vps_password(), timeout=30)
    try:
        # Day script len temp roi chay (tranh gioi han do dai command line)
        sftp = ssh.open_sftp()
        remote_tmp = "C:/Temp/xau_m30_rolling45_remote.py"
        ssh.exec_command('if not exist "C:\\Temp" mkdir "C:\\Temp"')
        with sftp.open(remote_tmp, "w") as f:
            f.write(REMOTE_SCRIPT)
        sftp.close()
        _i, o, e = ssh.exec_command(f'"{REMOTE_PY}" "{remote_tmp}"', timeout=180)
        out = o.read().decode("utf-8", "ignore").replace("\r\n", "\n")
        err = e.read().decode("utf-8", "ignore").replace("\r\n", "\n")
    finally:
        ssh.close()

    if "CSV_BEGIN" not in out or "CSV_END" not in out:
        print("❌ Export fail.\nSTDOUT:", out[:2000], "\nSTDERR:", err[:2000])
        return 1

    csv_text = out.split("CSV_BEGIN\n", 1)[1].split("CSV_END", 1)[0].strip() + "\n"
    meta = next((l for l in out.splitlines() if l.startswith("META;")), "META;?")
    n_rows = csv_text.count("\n") - 1  # tru header

    if n_rows < 500:  # 45 ngay M30 phai co ~1500+ nen — it hon la co van de
        print(f"❌ Chỉ {n_rows} nến — bất thường, KHÔNG ghi đè file cũ. {meta}")
        return 1

    DRIVE_OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = DRIVE_OUT.with_suffix(".csv.tmp")
    tmp.write_text(csv_text, encoding="utf-8")
    tmp.replace(DRIVE_OUT)  # ghi de nguyen tu — khong bao gio de file cut
    size_kb = DRIVE_OUT.stat().st_size / 1024
    print(f"✅ {DRIVE_OUT.name}: {n_rows} nến, {size_kb:.0f}KB → {DRIVE_OUT.parent}")
    print(f"   {meta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
