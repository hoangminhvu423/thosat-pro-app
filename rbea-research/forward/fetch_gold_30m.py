#!/usr/bin/env python3
"""GOLD PROXY FEED — keo nen 30m vang token-hoa tu API public cac san (chay tren GitHub Actions runner,
KHONG chay duoc trong sandbox Claude vi network policy chan API san).
- XAUT (Tether Gold, ~1 oz): OKX XAUT-USDT (uu tien) -> Gate.io XAUT_USDT (du phong)
- PAXG (Paxos Gold,  ~1 oz): Binance data-api (data-api.binance.vision, mirror public)
Ghi: xaut_30m.csv + paxg_30m.csv (ts_utc,open,high,low,close,volume,source), dedupe theo ts, chi giu nen DA DONG.
Backfill lan dau: OKX history-candles ~2000 nen (~40 ngay). Chay lai bao nhieu lan cung idempotent.
LUU Y (LESSON-04): XAUT/PAXG la vang token-hoa 24/7, KHONG phai XAUUSD CFD (dong cua weekend, spread khac).
Day la PROXY de doi chieu doc lap — ground truth cua sleeve XAU van la MT5/VPS demo.
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timezone

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
UA = {"User-Agent": "gold-feed/1.0"}

def get(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if k == tries - 1:
                print(f"[feed] FAIL {url.split('?')[0]} : {e}")
                return None
            time.sleep(2 * (k + 1))

def now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def okx_xaut(backfill):
    rows = []
    if backfill:  # history-candles: 100 nen/call, phan trang 'after' (cu hon)
        after = ""
        for _ in range(20):
            j = get(f"https://www.okx.com/api/v5/market/history-candles?instId=XAUT-USDT&bar=30m&limit=100{after}")
            if not j or j.get("code") != "0" or not j.get("data"):
                break
            rows += j["data"]
            after = f"&after={j['data'][-1][0]}"
            time.sleep(0.25)
    j = get("https://www.okx.com/api/v5/market/candles?instId=XAUT-USDT&bar=30m&limit=300")
    if j and j.get("code") == "0":
        rows += j.get("data", [])
    out = []
    for r in rows:  # [ts,o,h,l,c,vol,...,confirm] — confirm=1 la nen da dong
        if len(r) >= 9 and r[8] != "1":
            continue
        out.append((int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), "okx"))
    return out

def gate_xaut():
    j = get("https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair=XAUT_USDT&interval=30m&limit=300")
    if not isinstance(j, list):
        return []
    out = []
    for r in j:  # [t, vol_quote, close, high, low, open, vol_base, closed]
        if len(r) >= 8 and str(r[7]).lower() != "true":
            continue
        out.append((int(r[0]) * 1000, float(r[5]), float(r[3]), float(r[4]), float(r[2]), float(r[6]), "gate"))
    return out

def binance_paxg():
    j = get("https://data-api.binance.vision/api/v3/klines?symbol=PAXGUSDT&interval=30m&limit=1000")
    if not isinstance(j, list):
        return []
    out = []
    for r in j:  # [openTime,o,h,l,c,vol,closeTime,...]
        if int(r[6]) > now_ms():  # nen chua dong
            continue
        out.append((int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), "binance"))
    return out

def append_csv(path, rows):
    seen = {}
    if os.path.exists(path):
        with open(path) as f:
            f.readline()
            for line in f:
                p = line.strip().split(",")
                if len(p) >= 6:
                    seen[p[0]] = line.strip()
    added = 0
    for ts, o, h, l, c, v, src in rows:
        k = datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")
        if k not in seen:
            seen[k] = f"{k},{o},{h},{l},{c},{v},{src}"
            added += 1
    with open(path, "w") as f:
        f.write("ts_utc,open,high,low,close,volume,source\n")
        for k in sorted(seen):
            f.write(seen[k] + "\n")
    print(f"[feed] {os.path.basename(path)}: +{added} nen moi, tong {len(seen)}")
    return added

def main():
    os.makedirs(OUT, exist_ok=True)
    xaut_path = os.path.join(OUT, "xaut_30m.csv")
    backfill = not os.path.exists(xaut_path) or sum(1 for _ in open(xaut_path)) < 500
    xaut = okx_xaut(backfill)
    if not xaut:
        print("[feed] OKX fail -> thu Gate.io")
        xaut = gate_xaut()
    if xaut:
        append_csv(xaut_path, xaut)
    paxg = binance_paxg()
    if paxg:
        append_csv(os.path.join(OUT, "paxg_30m.csv"), paxg)
    if not xaut and not paxg:
        sys.exit(1)  # ca 3 nguon fail -> workflow do, de con thay tren tab Actions

if __name__ == "__main__":
    main()
