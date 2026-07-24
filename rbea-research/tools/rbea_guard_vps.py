# -*- coding: utf-8 -*-
"""
rbea_guard_vps.py — NGUOI GAC 24/7 CHAY TREN VPS (khong phu thuoc MacBook).
===========================================================================
Schtasks moi 5'. Theo PLAYBOOK_van-hanh.md — quyen 1 CHIEU AN TOAN duy nhat:
khi cham RED-LINE (Sep phe duyet 2026-07-24) -> FLATTEN vi the RB_EA + ghi halt-file
(EA v0.51 doc file moi 60s -> tu perm-halt). KHONG bao gio mo lenh / arm / doi param.

RED-LINES (Sep chot):
  R1: DD tong >= 28% tu init_bal          -> flatten + halt + bao
  R2: mat ket noi broker > 15' KHI co vi the RB_EA -> bao lien tuc (flatten khi noi lai neu van hở + Sep chua xu ly)
  R3: EA rung khoi chart + vi the ho > 10' -> flatten + halt + bao
Bao thuong: heartbeat 6h/lan "guard song"; moi canh bao khac gui 1 lan/loai/6h (chong spam).

Telegram: doc C:\\qtq\\tg_secret.txt (2 dong: token, chat_id — Sep tao truoc, script KHONG chua token).
State: C:\\qtq\\rbea_guard_state.json. Log: C:\\qtq\\rbea_guard.log.
"""
import json, os, struct, time, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

TERM = "C:/Program Files/MetaTrader 5/terminal64.exe"
LOGDIR = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\logs"
COMMON = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
QTQ = r"C:\qtq"
STATE_F = os.path.join(QTQ, "rbea_guard_state.json")
LOG_F = os.path.join(QTQ, "rbea_guard.log")
SECRET = os.path.join(QTQ, "tg_secret.txt")
MAGICS = {20260723: "XAUUSD", 20260724: "BTCUSD"}
INIT_BAL_FALLBACK = 3909.0
DD_LIMIT = 0.28          # R1
CONN_GRACE_MIN = 15      # R2
EA_DEAD_GRACE_MIN = 10   # R3
ALERT_COOLDOWN_H = 6

def log(msg):
    line = "%s %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    try:
        with open(LOG_F, "a", encoding="utf-8") as f: f.write(line + "\n")
    except Exception: pass

def tg(msg):
    try:
        if not os.path.exists(SECRET): return
        tok, chat = [x.strip() for x in open(SECRET, encoding="utf-8-sig").read().splitlines()[:2]]
        url = "https://api.telegram.org/bot%s/sendMessage?%s" % (tok, urllib.parse.urlencode({"chat_id": chat, "text": msg}))
        urllib.request.urlopen(url, timeout=10)
    except Exception as e:
        log("TG fail: %r" % e)

def load_state():
    try: return json.load(open(STATE_F))
    except Exception: return {}

def save_state(s):
    try: json.dump(s, open(STATE_F, "w"))
    except Exception: pass

def should_alert(state, key):
    last = state.get("alert_" + key, 0)
    if time.time() - last > ALERT_COOLDOWN_H * 3600:
        state["alert_" + key] = time.time(); return True
    return False

def ea_attached():
    """Doc log MT5 hom nay (UTF-16): dong RB_EA loaded/removed cuoi cung."""
    try:
        p = os.path.join(LOGDIR, datetime.now().strftime("%Y%m%d") + ".log")
        if not os.path.exists(p): return None
        txt = open(p, "r", encoding="utf-16-le", errors="ignore").read()
        last = None
        for ln in txt.splitlines():
            if "RB_EA" in ln and ("loaded" in ln or "removed" in ln):
                last = ln
        if last is None: return None
        return "loaded" in last
    except Exception:
        return None

def write_halt(login, sym, magic, init_bal):
    try:
        p = os.path.join(COMMON, "RBEA2_%d_%s_%d_halt.bin" % (login, sym, magic))
        with open(p, "wb") as f:
            f.write(struct.pack("<d", init_bal)); f.write(struct.pack("<i", 1))
        log("halt-file ghi: %s" % p)
    except Exception as e:
        log("halt-file fail %s: %r" % (sym, e))

def flatten(mt5, positions):
    """Dong toan bo vi the RB_EA (1 chieu an toan). Retry 3 lan."""
    closed = []
    for p in positions:
        for _ in range(3):
            tick = mt5.symbol_info_tick(p.symbol)
            if tick is None: break
            req = dict(action=mt5.TRADE_ACTION_DEAL, symbol=p.symbol, volume=p.volume,
                       type=mt5.ORDER_TYPE_SELL if p.type == 0 else mt5.ORDER_TYPE_BUY,
                       position=p.ticket, price=tick.bid if p.type == 0 else tick.ask,
                       deviation=50, magic=p.magic, comment="GUARD_HALT",
                       type_filling=mt5.ORDER_FILLING_FOK)
            r = mt5.order_send(req)
            if r and r.retcode == mt5.TRADE_RETCODE_DONE:
                closed.append(p.ticket); break
            req["type_filling"] = mt5.ORDER_FILLING_IOC
            r = mt5.order_send(req)
            if r and r.retcode == mt5.TRADE_RETCODE_DONE:
                closed.append(p.ticket); break
            time.sleep(1)
    # huy pending RB_EA
    for o in (mt5.orders_get() or []):
        if o.magic in MAGICS:
            mt5.order_send(dict(action=mt5.TRADE_ACTION_REMOVE, order=o.ticket))
    return closed

def main():
    if not os.path.isdir(QTQ): os.makedirs(QTQ)
    state = load_state()
    import MetaTrader5 as mt5
    if not mt5.initialize(path=TERM):
        if should_alert(state, "mt5init"):
            tg("RBEA GUARD: KHONG attach duoc MT5 (%s) — terminal chet? Watchdog se tu keo." % str(mt5.last_error()))
        save_state(state); return
    try:
        ti = mt5.terminal_info(); ai = mt5.account_info()
        pos = [p for p in (mt5.positions_get() or []) if p.magic in MAGICS]
        eq = ai.equity if ai else 0.0; login = ai.login if ai else 0
        # init_bal: doc tu halt-file neu co, fallback config
        init_bal = INIT_BAL_FALLBACK
        try:
            for f in os.listdir(COMMON):
                if f.startswith("RBEA2_%d_" % login) and f.endswith("_halt.bin"):
                    raw = open(os.path.join(COMMON, f), "rb").read()
                    v = struct.unpack("<d", raw[:8])[0]
                    if v > 0: init_bal = v; break
        except Exception: pass

        alerts = []; do_flatten = False; reason = ""
        # R1: DD tong
        if init_bal > 0 and eq > 0 and (init_bal - eq) / init_bal >= DD_LIMIT:
            do_flatten = True; reason = "R1 DD tong %.1f%% >= %.0f%%" % (100*(init_bal-eq)/init_bal, DD_LIMIT*100)
        # R2: mat ket noi + vi the
        if not ti.connected and pos:
            t0 = state.get("disconn_since", 0) or time.time()
            state["disconn_since"] = t0
            mins = (time.time() - t0) / 60
            if mins > CONN_GRACE_MIN and should_alert(state, "r2"):
                alerts.append("R2: MAT KET NOI %d' + %d vi the RB_EA ho — khong dong duoc khi offline, se flatten ngay khi noi lai. KIEM TRA GAP." % (mins, len(pos)))
        else:
            if state.get("disconn_since") and ti.connected and pos and \
               (time.time() - state["disconn_since"]) / 60 > CONN_GRACE_MIN:
                do_flatten = True; reason = "R2 noi lai sau >%d' mat ket noi, vi the van ho" % CONN_GRACE_MIN
            state["disconn_since"] = 0
        # R3: EA rung + vi the ho
        att = ea_attached()
        if att is False and pos:
            t0 = state.get("eadead_since", 0) or time.time()
            state["eadead_since"] = t0
            if (time.time() - t0) / 60 > EA_DEAD_GRACE_MIN:
                do_flatten = True; reason = "R3 EA rung khoi chart >%d' + %d vi the ho" % (EA_DEAD_GRACE_MIN, len(pos))
        else:
            state["eadead_since"] = 0
            if att is False and should_alert(state, "earemoved"):
                alerts.append("EA RB_EA co ve DA RUNG khoi chart (log cuoi=removed), khong co vi the ho.")

        if do_flatten and pos:
            closed = flatten(mt5, pos)
            for m, s in MAGICS.items(): write_halt(login, s, m, init_bal)
            tg("RBEA GUARD >> RED-LINE: %s\nDa FLATTEN %d/%d vi the + ghi perm-halt. Eq=%.2f. Can Sep hau kiem truoc khi reset." % (reason, len(closed), len(pos), eq))
            log("RED-LINE %s -> flatten %s" % (reason, closed))
        elif do_flatten:
            for m, s in MAGICS.items(): write_halt(login, s, m, init_bal)
            if should_alert(state, "redline_nopos"):
                tg("RBEA GUARD >> RED-LINE: %s (khong co vi the ho). Da ghi perm-halt." % reason)
        for a in alerts: tg("RBEA GUARD: " + a); log(a)
        # heartbeat 6h
        if should_alert(state, "heartbeat"):
            tg("RBEA GUARD ok: eq=%.2f dd=%.1f%% pos=%d algo=%s ea=%s" % (
                eq, 100*(init_bal-eq)/init_bal if init_bal else 0, len(pos),
                "ON" if ti.trade_allowed else "OFF",
                {True: "attached", False: "REMOVED", None: "?"}[att]))
    finally:
        mt5.shutdown(); save_state(state)

if __name__ == "__main__":
    main()
