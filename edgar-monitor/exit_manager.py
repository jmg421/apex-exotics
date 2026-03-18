"""
Exit Manager — systematic exit logic for open positions.

Three modes (configured in config/exits.json):
  hard_stop  — honor the stop, no exceptions
  trailing   — move stop to breakeven after 1R, trail at 1.5R
  scaled     — take 1/3 at 1R, 1/3 at 2R, let 1/3 run with trail
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config" / "exits.json"


def _load_config():
    return json.loads(CONFIG_PATH.read_text())


def r_multiple(entry, stop, current, direction="LONG"):
    """How many R the current price represents."""
    risk = abs(entry - stop)
    if risk == 0:
        return 0
    move = (current - entry) if direction == "LONG" else (entry - current)
    return move / risk


def check_exit(position, current_price):
    """
    Given an open position dict and current price, return exit instructions.

    position keys: entry_price, stop_loss, direction, shares, mode (optional)
    Returns: {"action": "HOLD"|"EXIT"|"PARTIAL", "reason": str, ...}
    """
    cfg = _load_config()
    entry = position["entry_price"]
    stop = position["stop_loss"]
    direction = position.get("direction", "LONG")
    shares = position.get("shares", 1)
    mode = position.get("mode", cfg["default_mode"])
    already_exited = position.get("shares_exited", 0)

    rm = r_multiple(entry, stop, current_price, direction)

    # Hard stop hit — universal across all modes
    if (direction == "LONG" and current_price <= stop) or \
       (direction == "SHORT" and current_price >= stop):
        return {"action": "EXIT", "shares": shares - already_exited,
                "reason": "Stop hit", "r_multiple": rm}

    if mode == "hard_stop":
        return {"action": "HOLD", "r_multiple": rm}

    if mode == "trailing":
        tcfg = cfg["modes"]["trailing"]
        new_stop = stop  # default: no change

        if rm >= tcfg["trail_at_r"]:
            # Trail: stop moves to entry + (rm - trail_r) * risk
            risk = abs(entry - stop)
            trail_offset = (rm - tcfg["trail_at_r"]) * risk
            new_stop = (entry + trail_offset) if direction == "LONG" else (entry - trail_offset)
        elif rm >= tcfg["breakeven_at_r"]:
            new_stop = entry  # breakeven

        return {"action": "HOLD", "r_multiple": rm, "new_stop": round(new_stop, 2)}

    if mode == "scaled":
        exits = cfg["modes"]["scaled"]["exits"]
        remaining = shares - already_exited

        for ex in exits:
            target_r = ex["at_r"]
            if target_r is None:
                continue  # runner leg — handled by trail
            frac_shares = round(shares * ex["fraction"])
            cumulative_needed = frac_shares  # simplified: check if this tranche is due

            if rm >= target_r and already_exited < (shares - remaining + frac_shares):
                exit_shares = min(frac_shares, remaining)
                if exit_shares > 0:
                    return {"action": "PARTIAL", "shares": exit_shares,
                            "reason": f"Scaled exit at {target_r}R", "r_multiple": rm}

        # Runner leg — trail stop
        runner = [e for e in exits if e["at_r"] is None]
        if runner and remaining > 0:
            trail_r = runner[0].get("trail_r", 1.5)
            risk = abs(entry - stop)
            if rm >= trail_r:
                trail_offset = (rm - trail_r) * risk
                new_stop = (entry + trail_offset) if direction == "LONG" else (entry - trail_offset)
                return {"action": "HOLD", "r_multiple": rm, "new_stop": round(new_stop, 2)}

        return {"action": "HOLD", "r_multiple": rm}

    return {"action": "HOLD", "r_multiple": rm}


if __name__ == "__main__":
    # Demo
    pos = {"entry_price": 100, "stop_loss": 95, "direction": "LONG", "shares": 3}
    for price in [94, 97, 100, 105, 110, 115]:
        result = check_exit(pos, price)
        print(f"  Price ${price}: {result}")
