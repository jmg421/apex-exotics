#!/usr/bin/env python3
"""
Heartbeat — Pre-trade connection health gate.
Checks quote feed (REST), platform status, and account readiness.

Usage:
  python heartbeat.py              # One-shot check
  python heartbeat.py --watch      # Continuous (30s interval)
  python heartbeat.py --json       # Machine-readable

As module:
  from heartbeat import check_health, get_session
  session = get_session()
  result = await check_health(session)
  if result["ok"]: ...
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from tastytrade import Session, Account
from tastytrade.market_data import get_market_data_by_type

DATA_DIR = Path(__file__).parent / "data"
STATE_PATH = DATA_DIR / "heartbeat.json"
CONFIG_PATH = Path(__file__).parent / "config" / "zone.json"

SYMBOL = "/MESM6"
STATUS_URL = "https://status.tastytrade.com/feed.atom"
STALE_SEC = 120  # quote older than this = degraded


def load_config():
    return json.loads(CONFIG_PATH.read_text())


def get_session():
    env = {}
    for line in (Path(__file__).parent / ".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return Session(
        env["TASTYTRADE_CLIENT_SECRET"],
        env["TASTYTRADE_REFRESH_TOKEN"],
        is_test=env.get("TASTYTRADE_ENV") == "sandbox",
    )


async def check_platform_status():
    """Scrape Atom feed for unresolved incidents affecting Futures or Quotes."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(STATUS_URL)
            entries = resp.text.split("<entry>")[1:]
            for entry in entries:
                if "Resolved" not in entry:
                    title = entry.split("<title")[1].split("]]>")[0].split("CDATA[")[-1] if "CDATA" in entry else "Unknown"
                    if any(k in entry for k in ["Futures", "Quotes", "All"]):
                        return {"ok": False, "incident": title.strip()}
            return {"ok": True, "incident": None}
    except Exception as e:
        return {"ok": True, "incident": None, "warning": str(e)}


async def check_account(session, account_number="5WI49746"):
    """Check account is funded and futures-enabled."""
    try:
        acct = await Account.get(session, account_number)
        bal = await acct.get_balances(session)
        status = await session._get(f"/accounts/{account_number}/trading-status")
        return {
            "funded": float(bal.net_liquidating_value) > 0,
            "futures_enabled": status.get("is-futures-enabled", False),
            "frozen": status.get("is-frozen", False),
            "closing_only": status.get("is-futures-closing-only", False),
            "net_liq": float(bal.net_liquidating_value),
            "buying_power": float(bal.equity_buying_power),
        }
    except Exception as e:
        return {"funded": False, "futures_enabled": False, "error": str(e)}


async def check_quotes(session, symbol=SYMBOL):
    """Fetch quote via REST market data endpoint."""
    try:
        data = await get_market_data_by_type(session, futures=[symbol])
        if not data:
            return {"status": "DOWN", "error": "No data returned"}
        d = data[0]
        now = datetime.now(timezone.utc)
        age = (now - d.updated_at).total_seconds() if d.updated_at else 999

        result = {
            "bid": float(d.bid) if d.bid else None,
            "ask": float(d.ask) if d.ask else None,
            "last": float(d.last) if d.last else None,
            "open": float(d.open) if d.open else None,
            "day_high": float(d.day_high_price) if d.day_high_price else None,
            "day_low": float(d.day_low_price) if d.day_low_price else None,
            "volume": float(d.volume) if d.volume else None,
            "mark": float(d.mark) if d.mark else None,
            "prev_close": float(d.prev_close) if d.prev_close else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            "age_sec": round(age, 1),
            "error": None,
        }

        if result["bid"] and result["ask"]:
            result["spread"] = round(result["ask"] - result["bid"], 2)

        if age > STALE_SEC:
            result["status"] = "DEGRADED"
            result["error"] = f"Quote is {age:.0f}s old"
        elif not result["bid"] or not result["ask"]:
            result["status"] = "DEGRADED"
            result["error"] = "Missing bid/ask"
        else:
            result["status"] = "CONNECTED"

        return result
    except Exception as e:
        return {"status": "DOWN", "error": str(e)}


async def check_health(session, symbol=SYMBOL):
    """Full health check. Returns combined status dict."""
    platform, account, quotes = await asyncio.gather(
        check_platform_status(),
        check_account(session),
        check_quotes(session, symbol),
    )

    ok = (
        quotes.get("status") == "CONNECTED"
        and platform.get("ok", False)
        and account.get("futures_enabled", False)
        and not account.get("frozen", False)
        and not account.get("closing_only", False)
    )

    result = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "quotes": quotes,
        "platform": platform,
        "account": account,
    }

    DATA_DIR.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(result, indent=2))
    return result


def print_result(r):
    icons = {"CONNECTED": "🟢", "DEGRADED": "🟡", "DOWN": "🔴"}
    qs = r["quotes"]
    print(f"\n{'='*50}")
    print(f"HEARTBEAT — {r['symbol']}")
    print(f"{'='*50}")

    qi = icons.get(qs.get("status"), "❓")
    print(f"  Quotes:   {qi} {qs.get('status')} (age={qs.get('age_sec', '?')}s)")
    if qs.get("bid"):
        print(f"            {qs['bid']} / {qs['ask']}  spread={qs.get('spread')}")
        print(f"            last={qs['last']}  vol={qs.get('volume', 0):,.0f}")
        print(f"            range={qs.get('day_low')}-{qs.get('day_high')}")
    if qs.get("error"):
        print(f"            ⚠ {qs['error']}")

    p = r["platform"]
    print(f"  Platform: {'🟢' if p.get('ok') else '🔴'} {'OK' if p.get('ok') else p.get('incident', 'ISSUE')}")

    a = r["account"]
    print(f"  Account:  {'🟢' if a.get('futures_enabled') else '🔴'} futures={'enabled' if a.get('futures_enabled') else 'disabled'}")
    print(f"            net_liq=${a.get('net_liq', 0):,.2f}  bp=${a.get('buying_power', 0):,.2f}")
    if a.get("frozen"):
        print(f"            🔴 FROZEN")

    gate = "✅ OPEN — clear to trade" if r["ok"] else "❌ CLOSED — do not trade"
    print(f"\n  Gate: {gate}")
    print(f"{'='*50}")


async def main():
    session = get_session()
    if "--watch" in sys.argv:
        while True:
            r = await check_health(session)
            print_result(r)
            await asyncio.sleep(30)
    else:
        r = await check_health(session)
        if "--json" in sys.argv:
            print(json.dumps(r, indent=2))
        else:
            print_result(r)
        sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
