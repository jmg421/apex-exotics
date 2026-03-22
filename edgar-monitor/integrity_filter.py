"""
Integrity Filter — Defensive layer against manipulated markets.

Lesson from KSU game-fixing: some participants aren't playing the game
you think they're playing. This module doesn't try to detect manipulation
(that's the SEC/DOJ's job). Instead, it adjusts our behavior when
conditions suggest the price discovery process may be compromised.

Applied to: zone_trader.py, detect_patterns.py, futures_patterns.py
"""
import json
import numpy as np
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def halftime_divergence(first_half_move, second_half_move, threshold=2.5):
    """
    KSU pattern: first half was fixed (down 13), second half was real (competitive).
    In futures: a session's first hour moves hard one way, then fully reverses.
    
    Returns divergence ratio. >threshold suggests the first move was artificial.
    """
    if abs(first_half_move) < 0.01:
        return 0.0
    ratio = abs(second_half_move / first_half_move)
    # Opposite direction AND large reversal = suspicious
    if np.sign(first_half_move) != np.sign(second_half_move) and ratio > threshold:
        return ratio
    return 0.0


def volume_at_stops(price_levels, volume_profile, stop_price, window_pct=0.1):
    """
    Stop hunt detector: unusual volume concentration near common stop levels.
    
    The KSU equivalent: $20K wagered on a narrow spread in a nothing game.
    In futures: volume spikes at round numbers / known stop clusters.
    """
    if not price_levels or not volume_profile:
        return 0.0
    stop_window = abs(stop_price * window_pct / 100)
    near_stop_vol = sum(
        v for p, v in zip(price_levels, volume_profile)
        if abs(p - stop_price) <= stop_window
    )
    total_vol = sum(volume_profile)
    if total_vol == 0:
        return 0.0
    return near_stop_vol / total_vol


def correlation_break(primary_move, correlated_move, historical_corr=0.85):
    """
    If ES moves 2% but NQ doesn't move, something is wrong with one of them.
    
    The KSU equivalent: the team's leading scorer suddenly can't hit shots,
    but the rest of the team plays normally.
    """
    if abs(primary_move) < 0.01:
        return False
    expected = primary_move * historical_corr
    actual_corr = correlated_move / primary_move if primary_move != 0 else 0
    return abs(actual_corr - historical_corr) > 0.4


def assess_session(quotes_now, quotes_prev, stop_price=None):
    """
    Run all integrity checks on current session data.
    Returns risk adjustment factor (1.0 = normal, <1.0 = reduce size).
    """
    flags = []
    adjustment = 1.0

    if len(quotes_now) >= 2 and len(quotes_prev) >= 2:
        # Check for correlation breaks between ES and NQ
        es_now = next((q for q in quotes_now if q['symbol'] in ('ES', '/ES', '/MES')), None)
        nq_now = next((q for q in quotes_now if q['symbol'] in ('NQ', '/NQ', '/MNQ')), None)
        if es_now and nq_now:
            if correlation_break(es_now['change_percent'], nq_now['change_percent']):
                flags.append('CORRELATION_BREAK_ES_NQ')
                adjustment *= 0.5

    # Check volume clustering at stop level
    if stop_price and quotes_now:
        prices = [q.get('price', 0) for q in quotes_now]
        volumes = [q.get('volume', 0) for q in quotes_now]
        stop_ratio = volume_at_stops(prices, volumes, stop_price)
        if stop_ratio > 0.3:
            flags.append(f'STOP_HUNT_RISK_{stop_ratio:.0%}')
            adjustment *= 0.75

    return {
        'adjustment': adjustment,
        'flags': flags,
        'recommendation': 'REDUCE_SIZE' if adjustment < 1.0 else 'NORMAL',
        'timestamp': datetime.now().isoformat()
    }


# ── The philosophical framework ──────────────────────────────────────
#
# You can't eliminate manipulation. You can only:
#
# 1. PREDEFINE RISK — Your $75/trade max means manipulation costs you
#    $75, not your account. The KSU bettors risked $20K on one game.
#
# 2. THINK IN SAMPLES — Any single trade might be manipulated. Over
#    100 trades, your edge either exists or it doesn't. The fixers
#    needed every fixed game to pay off. You don't.
#
# 3. DETECT ANOMALIES — Not to catch the manipulator, but to step
#    aside when conditions are abnormal. The DBSCAN approach in
#    detect_patterns.py is exactly right: if today's price action
#    doesn't cluster with normal behavior, reduce exposure.
#
# 4. TRADE SMALL — 1 MES contract. The manipulation targets are
#    large positions with predictable stops. Nobody is engineering
#    a $75 stop-out on 1 micro contract.
#
# 5. ACCEPT THE TAX — Some percentage of your losses are stop hunts.
#    That's the cost of participating. Build it into your expected
#    win rate. If your edge is 55% and 5% of losses are manipulation,
#    your "real" edge is still positive.
#
# The KSU case proves: manipulation happens in EVERY market where
# money is at stake. The question isn't "is it happening?" — it's
# "does my system survive it?"
#
# Your zone_trader already answers yes:
#   - Fixed risk per trade
#   - Probability-based thinking
#   - Daily loss limits
#   - No single trade matters
# ─────────────────────────────────────────────────────────────────────
