#!/usr/bin/env python3
"""
Zone Trader — Single gateway for all trades.
Enforces Mark Douglas's 7 principles. No bypasses.

Usage:
  python zone_trader.py long 5850 breakout       # Open long on signal
  python zone_trader.py short 5860 reversal       # Open short on signal
  python zone_trader.py check 5855                # Check position targets/stops
  python zone_trader.py status                    # Daily report
  python zone_trader.py close 5855                # Manual close at price
"""

import json
import sys
import time
from datetime import datetime, date
from pathlib import Path
from trading_psychology import (
    RiskAcceptance, RuleAdherence, EmotionalStateMonitor,
    ConsistencyMetrics, TradeJournal, ProbabilityFramework, validate_trade
)
from integrity_filter import assess_session

DATA_DIR = Path(__file__).parent / "data"
CONFIG_PATH = Path(__file__).parent / "config" / "zone.json"
STATE_PATH = DATA_DIR / "zone_state.json"
JOURNAL_PATH = DATA_DIR / "zone_journal.jsonl"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {
        "balance": 100000,
        "position": None,
        "today_trades": [],
        "today_pnl": 0,
        "total_pnl": 0,
        "all_trades": []
    }


def save_state(state):
    DATA_DIR.mkdir(exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def reset_daily(state):
    """Reset daily counters if new day."""
    today = date.today().isoformat()
    if state.get("last_trade_date") != today:
        state["today_trades"] = []
        state["today_pnl"] = 0
        state["last_trade_date"] = today
    return state


def get_recent_monitor_trades(state):
    """Convert stored trades to format EmotionalStateMonitor expects."""
    out = []
    for t in state.get("all_trades", [])[-20:]:
        out.append({
            "entry_time": t.get("entry_time_ts", 0),
            "exit_time": t.get("exit_time_ts", 0),
            "outcome": t.get("outcome", "OPEN"),
            "exit_reason": t.get("exit_reason"),
            "position_value": t.get("contracts", 0) * t.get("entry_price", 0) * t.get("point_value", 50)
        })
    return out


# ── PRINCIPLE 1: Objectively identify edges ──────────────────────────

def check_edge(signal, config):
    if not signal:
        return False, "No entry signal provided"
    if signal not in config["approved_signals"]:
        return False, f"Signal '{signal}' not in approved list: {config['approved_signals']}"
    return True, f"Edge identified: {signal}"


# ── PRINCIPLE 2: Predefine risk ──────────────────────────────────────

def calculate_risk(entry_price, side, config):
    stop_pts = config["stop_points"]
    contracts = config["contracts"]
    pv = config["point_value"]

    if side == "LONG":
        stop_price = entry_price - stop_pts
        targets = [entry_price + t for t in config["targets"]]
    else:
        stop_price = entry_price + stop_pts
        targets = [entry_price - t for t in config["targets"]]

    total_risk = stop_pts * pv * contracts

    return {
        "stop_price": stop_price,
        "targets": targets,
        "scale_out": config["scale_out"],
        "total_risk": total_risk,
        "risk_per_contract": stop_pts * pv,
        "contracts": contracts
    }


# ── PRINCIPLE 3: Accept risk or let go ───────────────────────────────

def accept_risk(risk_info, state, config):
    # Daily loss limit
    if state["today_pnl"] < 0 and abs(state["today_pnl"]) + risk_info["total_risk"] > config["max_daily_loss"]:
        return False, f"Would exceed daily loss limit (${config['max_daily_loss']})"

    # Account risk %
    risk_pct = (risk_info["total_risk"] / state["balance"]) * 100
    if risk_pct > 2.0:
        return False, f"Risk {risk_pct:.2f}% exceeds 2% limit"

    return True, f"Risk accepted: ${risk_info['total_risk']} ({risk_pct:.2f}%)"


# ── PRINCIPLE 4: Act without hesitation (auto-execute) ───────────────

def execute_entry(side, entry_price, risk_info, signal, state, config):
    now = datetime.now()
    position = {
        "instrument": config["instrument"],
        "side": side,
        "entry_price": entry_price,
        "contracts": risk_info["contracts"],
        "remaining": risk_info["contracts"],
        "stop_price": risk_info["stop_price"],
        "targets": risk_info["targets"],
        "scale_out": list(risk_info["scale_out"]),
        "signal": signal,
        "entry_time": now.isoformat(),
        "entry_time_ts": now.timestamp(),
        "point_value": config["point_value"],
        "partial_pnl": 0,
        "targets_hit": 0
    }
    state["position"] = position
    state["today_trades"].append({"signal": signal, "time": now.isoformat(), "side": side})
    save_state(state)

    print(f"\n{'='*60}")
    print(f"✓ ZONE TRADE EXECUTED")
    print(f"{'='*60}")
    print(f"  {side} {risk_info['contracts']} {config['instrument']} @ ${entry_price:.2f}")
    print(f"  Signal: {signal}")
    print(f"  Stop: ${risk_info['stop_price']:.2f} (risk: ${risk_info['total_risk']})")
    for i, target in enumerate(risk_info['targets']):
        lots = config['scale_out'][i] if i < len(config['scale_out']) else 'runner'
        print(f"  Target {i+1}: ${target:.2f} (+{config['targets'][i]}pts) → close {lots}")
    print(f"{'='*60}")


# ── PRINCIPLE 5: Pay yourself ────────────────────────────────────────

def check_position(current_price, state, config):
    pos = state.get("position")
    if not pos:
        print("No open position.")
        return

    pv = pos["point_value"]
    side = pos["side"]
    entry = pos["entry_price"]
    remaining = pos["remaining"]

    if side == "LONG":
        pnl_pts = current_price - entry
    else:
        pnl_pts = entry - current_price

    current_pnl = pnl_pts * pv * remaining + pos["partial_pnl"]

    print(f"\n📊 {side} {remaining}/{pos['contracts']} {pos['instrument']} @ ${entry:.2f}")
    print(f"   Current: ${current_price:.2f}  P&L: ${current_pnl:+.2f}  ({pnl_pts:+.1f} pts)")
    print(f"   Stop: ${pos['stop_price']:.2f}")

    # Check stop
    stop_hit = (side == "LONG" and current_price <= pos["stop_price"]) or \
               (side == "SHORT" and current_price >= pos["stop_price"])

    if stop_hit:
        close_position(pos["stop_price"], state, config, "STOP")
        return

    # Check targets (scale out)
    for i, target in enumerate(pos["targets"]):
        if i < pos["targets_hit"]:
            print(f"   Target {i+1}: ${target:.2f} ✓ HIT")
            continue

        target_hit = (side == "LONG" and current_price >= target) or \
                     (side == "SHORT" and current_price <= target)

        if target_hit and pos["remaining"] > 0:
            lots = min(pos["scale_out"][i], pos["remaining"])
            partial = abs(target - entry) * pv * lots
            pos["partial_pnl"] += partial
            pos["remaining"] -= lots
            pos["targets_hit"] = i + 1

            # Move stop to breakeven after first target
            if i == 0:
                pos["stop_price"] = entry
            elif i == 1:
                pos["stop_price"] = pos["targets"][0]  # Move stop to target 1

            print(f"   🎯 TARGET {i+1} HIT — closed {lots} @ ${target:.2f} (+${partial:.2f})")
            print(f"   Stop moved to ${pos['stop_price']:.2f}")

            if pos["remaining"] == 0:
                close_position(target, state, config, "TARGET")
                return
        else:
            print(f"   Target {i+1}: ${target:.2f} ...")

    save_state(state)


def close_position(exit_price, state, config, reason):
    pos = state["position"]
    pv = pos["point_value"]
    side = pos["side"]
    entry = pos["entry_price"]
    remaining = pos["remaining"]

    if side == "LONG":
        final_pnl = (exit_price - entry) * pv * remaining
    else:
        final_pnl = (entry - exit_price) * pv * remaining

    total_pnl = final_pnl + pos["partial_pnl"]
    outcome = "WIN" if total_pnl > 0 else "LOSS"
    now = datetime.now()

    # Record completed trade
    trade_record = {
        "instrument": pos["instrument"],
        "side": side,
        "entry_price": entry,
        "exit_price": exit_price,
        "contracts": pos["contracts"],
        "signal": pos["signal"],
        "pnl": total_pnl,
        "outcome": outcome,
        "exit_reason": reason,
        "entry_time": pos["entry_time"],
        "exit_time": now.isoformat(),
        "entry_time_ts": pos["entry_time_ts"],
        "exit_time_ts": now.timestamp(),
        "targets_hit": pos["targets_hit"],
        "point_value": pv
    }

    state["all_trades"].append(trade_record)
    state["today_pnl"] += total_pnl
    state["total_pnl"] += total_pnl
    state["balance"] += total_pnl
    state["position"] = None
    save_state(state)

    # Journal with psychology data
    journal = TradeJournal(journal_path=str(JOURNAL_PATH))
    monitor_trades = get_recent_monitor_trades(state)
    emotion = EmotionalStateMonitor()
    emo_state, _ = emotion.check_state(monitor_trades)
    consistency = ConsistencyMetrics()

    journal_trades = []
    for t in state["all_trades"]:
        journal_trades.append({
            "followed_plan": t["exit_reason"] in ("STOP", "TARGET"),
            "stop_honored": t["exit_reason"] == "STOP" if t["outcome"] == "LOSS" else True,
            "position_value": t["contracts"] * t["entry_price"] * t["point_value"]
        })

    score = consistency.calculate_consistency_score(journal_trades)

    journal.log_trade(trade_record, {
        "risk_accepted": True,
        "adherence_score": 100 if reason in ("STOP", "TARGET") else 80,
        "violations": [] if reason in ("STOP", "TARGET") else ["manual_close"],
        "emotional_state": emo_state,
        "followed_plan": reason in ("STOP", "TARGET")
    })

    icon = "🎯" if outcome == "WIN" else "🛑"
    print(f"\n{icon} POSITION CLOSED — {reason}")
    print(f"   P&L: ${total_pnl:+.2f} ({outcome})")
    print(f"   Targets hit: {pos['targets_hit']}/{len(pos['targets'])}")
    print(f"   Today P&L: ${state['today_pnl']:+.2f}")
    print(f"   Consistency: {score['consistency_score']}/100 ({score['grade']})")


# ── PRINCIPLE 6: Monitor errors ──────────────────────────────────────

def daily_status(state):
    config = load_config()
    today_count = len(state["today_trades"])
    all_trades = state["all_trades"]

    print(f"\n{'═'*60}")
    print(f"ZONE TRADING REPORT — {date.today().isoformat()}")
    print(f"Instrument: {config['instrument']} | Contracts: {config['contracts']} per trade")
    print(f"{'═'*60}")

    print(f"\nBalance: ${state['balance']:,.2f}")
    print(f"Trades today: {today_count}/{config['max_daily_trades']}")
    print(f"Today P&L: ${state['today_pnl']:+.2f}")
    print(f"Total P&L: ${state['total_pnl']:+.2f}")

    if state.get("position"):
        pos = state["position"]
        print(f"\nOPEN: {pos['side']} {pos['remaining']}/{pos['contracts']} @ ${pos['entry_price']:.2f}")
        print(f"  Stop: ${pos['stop_price']:.2f} | Targets hit: {pos['targets_hit']}")

    # Consistency
    if all_trades:
        journal_trades = [{
            "followed_plan": t["exit_reason"] in ("STOP", "TARGET"),
            "stop_honored": t["exit_reason"] == "STOP" if t["outcome"] == "LOSS" else True,
            "position_value": t["contracts"] * t["entry_price"] * t["point_value"]
        } for t in all_trades]

        cm = ConsistencyMetrics()
        score = cm.calculate_consistency_score(journal_trades)
        wins = sum(1 for t in all_trades if t["outcome"] == "WIN")

        print(f"\nCONSISTENCY: {score['consistency_score']}/100 ({score['grade']})")
        for k, v in score["breakdown"].items():
            print(f"  {k}: {v:.1f}%")
        print(f"Win rate: {wins}/{len(all_trades)} ({wins/len(all_trades)*100:.0f}%)")

    # Emotional state
    monitor_trades = get_recent_monitor_trades(state)
    emo = EmotionalStateMonitor()
    emo_state, warnings = emo.check_state(monitor_trades)
    print(f"\nEmotional State: {emo_state}")
    for w in warnings:
        print(f"  ⚠️  {w}")

    print(f"\n{'═'*60}")
    print("THE QUESTION: Did I follow my rules?")
    plan_trades = [t for t in all_trades if t["exit_reason"] in ("STOP", "TARGET")]
    if all_trades:
        print(f"  {len(plan_trades)}/{len(all_trades)} trades followed the plan")
    print(f"{'═'*60}")


# ── PRINCIPLE 7: Never violate ───────────────────────────────────────

def open_trade(side, entry_price, signal):
    """The single gateway. All 7 checks in sequence."""
    config = load_config()
    state = load_state()
    state = reset_daily(state)

    # Already in a position?
    if state.get("position"):
        print("❌ Already in a position. Manage it or close it first.")
        return

    # 1. Edge
    ok, msg = check_edge(signal, config)
    if not ok:
        print(f"❌ P1 EDGE: {msg}")
        return
    print(f"✓ P1 Edge: {msg}")

    # 1b. Probability check
    pf = ProbabilityFramework()
    prob_result = pf.evaluate_setup(signal)
    if prob_result["recommendation"] == "PASS":
        print(f"❌ P1b PROBABILITY: {signal} win_prob={prob_result['win_probability']:.3f} < threshold. PASS.")
        return
    print(f"✓ P1b Probability: {prob_result['win_probability']:.3f} edge={prob_result['edge']:+.3f}")

    # 1c. Integrity check — are market conditions normal?
    try:
        prev_path = DATA_DIR / "prev_quotes.json"
        curr_path = DATA_DIR / "futures_snapshot.json"
        if prev_path.exists() and curr_path.exists():
            import json as _json
            prev_q = _json.loads(prev_path.read_text()).get('quotes', [])
            curr_q = _json.loads(curr_path.read_text()).get('quotes', [])
            integrity = assess_session(curr_q, prev_q, stop_price=entry_price - config['stop_points'] if side == 'LONG' else entry_price + config['stop_points'])
            if integrity['flags']:
                print(f"⚠️  P1c Integrity: {integrity['flags']} — adjustment {integrity['adjustment']:.0%}")
            else:
                print(f"✓ P1c Integrity: CLEAR")
        else:
            integrity = {'adjustment': 1.0, 'flags': []}
            print(f"✓ P1c Integrity: no prior data, skipping")
    except Exception as e:
        integrity = {'adjustment': 1.0, 'flags': []}
        print(f"✓ P1c Integrity: check skipped ({e})")

    # 2. Risk
    risk_info = calculate_risk(entry_price, side, config)
    print(f"✓ P2 Risk: ${risk_info['total_risk']} ({risk_info['contracts']}×{config['stop_points']}pts×${config['point_value']})")

    # 3. Accept
    ok, msg = accept_risk(risk_info, state, config)
    if not ok:
        print(f"❌ P3 ACCEPT: {msg}")
        return
    print(f"✓ P3 Accept: {msg}")

    # 4+5+6: Psychology gate (rules, emotion, daily limit)
    trade_plan = {
        "symbol": config["instrument"],
        "entry_price": entry_price,
        "stop_loss": risk_info["stop_price"],
        "shares": risk_info["contracts"],
        "entry_signal": signal,
        "direction": side
    }
    monitor_trades = get_recent_monitor_trades(state)

    # Daily limit
    if len(state["today_trades"]) >= config["max_daily_trades"]:
        print(f"❌ P6 LIMIT: {len(state['today_trades'])}/{config['max_daily_trades']} trades today. Done.")
        return
    print(f"✓ P4 Rules: {len(state['today_trades'])}/{config['max_daily_trades']} trades today")

    # Emotional state
    emo = EmotionalStateMonitor()
    emo_state, warnings = emo.check_state(monitor_trades)
    if emo_state == "TILT":
        print(f"❌ P6 TILT: {warnings}. Done for the day.")
        return
    if emo_state == "CAUTION":
        print(f"⚠️  P6 Caution: {warnings}")
    else:
        print(f"✓ P6 State: CLEAR")

    # Revenge check
    adherence = RuleAdherence()
    adherence_data = adherence.check_trade(trade_plan, monitor_trades, state["balance"])
    if not adherence_data["followed_plan"]:
        print(f"❌ P7 VIOLATIONS: {adherence_data['violations']}")
        return
    print(f"✓ P7 Adherence: {adherence_data['adherence_score']}%")

    # All clear — execute (Principle 4: no hesitation)
    execute_entry(side, entry_price, risk_info, signal, state, config)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("ZONE TRADER — One instrument. Fixed size. Follow the rules.")
        print("="*60)
        config = load_config()
        print(f"\nInstrument: {config['instrument']}")
        print(f"Contracts: {config['contracts']}")
        print(f"Risk/trade: ${config['stop_points'] * config['point_value'] * config['contracts']}")
        print(f"Targets: {config['targets']} pts")
        print(f"\nCommands:")
        print(f"  python zone_trader.py long 5850 breakout")
        print(f"  python zone_trader.py short 5860 reversal")
        print(f"  python zone_trader.py check 5855")
        print(f"  python zone_trader.py close 5855")
        print(f"  python zone_trader.py status")
        print(f"\nApproved signals: {config['approved_signals']}")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        state = load_state()
        state = reset_daily(state)
        daily_status(state)

    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: python zone_trader.py check PRICE")
            sys.exit(1)
        state = load_state()
        config = load_config()
        check_position(float(sys.argv[2]), state, config)

    elif cmd == "close":
        if len(sys.argv) < 3:
            print("Usage: python zone_trader.py close PRICE")
            sys.exit(1)
        state = load_state()
        config = load_config()
        if not state.get("position"):
            print("No open position.")
        else:
            close_position(float(sys.argv[2]), state, config, "MANUAL")

    elif cmd in ("long", "short"):
        if len(sys.argv) < 4:
            print(f"Usage: python zone_trader.py {cmd} PRICE SIGNAL")
            print(f"Signals: {load_config()['approved_signals']}")
            sys.exit(1)
        entry_price = float(sys.argv[2])
        signal = sys.argv[3].lower()
        open_trade(cmd.upper(), entry_price, signal)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
