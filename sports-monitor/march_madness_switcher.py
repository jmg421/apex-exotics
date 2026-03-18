#!/usr/bin/env python3
"""
March Madness Auto-Switcher
Switches TV to the most exciting live tournament game.
"""
import time
import json
import logging
import re
from datetime import datetime

from excitement_engine import get_excitement_rankings
from channel_switcher import change_channel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('march_madness_switcher.log'),
    ]
)
log = logging.getLogger(__name__)

# VSeeBox channel numbers for March Madness networks
MM_CHANNELS = {'CBS': 28, 'TBS': 156, 'TNT': 162, 'truTV': 166}

# Switching parameters
MIN_EXCITEMENT = 40
STICKINESS_BONUS = 10
COOLDOWN_SECONDS = 120
MANUAL_OVERRIDE_SECONDS = 300
POLL_INTERVAL = 30


def resolve_channel(game, epg_games=None):
    """Match an ESPN game to a VSeeBox channel via EPG data."""
    if epg_games is None:
        try:
            from epg_parser import fetch_epg, get_march_madness_now
            epg_games = get_march_madness_now()
        except Exception as e:
            log.warning(f"EPG fetch failed: {e}")
            epg_games = []

    home = game.get('home_full', game['home']).lower()
    away = game.get('away_full', game['away']).lower()

    for epg in epg_games:
        title = epg['title'].lower()
        # Check if both team abbreviations or names appear in EPG title
        home_match = game['home'].lower() in title or home in title
        away_match = game['away'].lower() in title or away in title
        if home_match or away_match:
            return epg['channel']

    return None


def load_state():
    """Load current channel and override state."""
    try:
        with open('data/switcher_state.json') as f:
            return json.load(f)
    except Exception:
        return {'current_channel': None, 'last_switch': 0, 'manual_override_until': 0}


def save_state(state):
    """Persist switcher state."""
    with open('data/switcher_state.json', 'w') as f:
        json.dump(state, f)


def run(dry_run=False):
    """Main auto-switch loop."""
    state = load_state()
    log.info(f"🏀 March Madness Auto-Switcher started (dry_run={dry_run})")
    log.info(f"   Channels: {MM_CHANNELS}")
    log.info(f"   Min excitement: {MIN_EXCITEMENT}, Stickiness: {STICKINESS_BONUS}, Cooldown: {COOLDOWN_SECONDS}s")

    while True:
        now = time.time()

        # Check manual override
        if now < state.get('manual_override_until', 0):
            remaining = int(state['manual_override_until'] - now)
            log.debug(f"Manual override active ({remaining}s remaining)")
            time.sleep(POLL_INTERVAL)
            continue

        # Get live games ranked by excitement
        games = get_excitement_rankings()
        ncaa_games = [g for g in games if g['sport'] == 'NCAA Basketball']

        if not ncaa_games:
            log.info("No live NCAA games")
            time.sleep(POLL_INTERVAL)
            continue

        # Resolve channels via EPG (one fetch for all games)
        try:
            from epg_parser import fetch_epg, get_march_madness_now
            epg_games = get_march_madness_now()
        except Exception:
            epg_games = []

        for g in ncaa_games:
            g['channel'] = resolve_channel(g, epg_games)

        # Apply stickiness to current channel
        current = state.get('current_channel')
        for g in ncaa_games:
            if g['channel'] == current:
                g['excitement'] = min(g['excitement'] + STICKINESS_BONUS, 100)

        # Pick best game that has a channel
        switchable = [g for g in ncaa_games if g['channel'] is not None and g['excitement'] >= MIN_EXCITEMENT]
        switchable.sort(key=lambda g: g['excitement'], reverse=True)

        # Log all games
        for g in ncaa_games[:6]:
            marker = "📺" if g.get('channel') else "  "
            stick = " (sticky)" if g.get('channel') == current else ""
            log.info(f"  {marker} [{g['excitement']:3d}] {g['away']} vs {g['home']} — {g['status']} ch:{g.get('channel')}{stick}")

        if not switchable:
            log.info("No switchable games above threshold")
            time.sleep(POLL_INTERVAL)
            continue

        best = switchable[0]
        target = best['channel']

        # Check if we need to switch
        if target == current:
            time.sleep(POLL_INTERVAL)
            continue

        # Check cooldown
        since_last = now - state.get('last_switch', 0)
        if since_last < COOLDOWN_SECONDS:
            log.info(f"⏳ Cooldown ({int(COOLDOWN_SECONDS - since_last)}s remaining)")
            time.sleep(POLL_INTERVAL)
            continue

        # Switch!
        log.info(f"🔄 SWITCHING to ch {target}: {best['away']} vs {best['home']} "
                 f"({best['away_score']}-{best['home_score']}) — excitement {best['excitement']}")

        if not dry_run:
            try:
                change_channel(target)
            except Exception as e:
                log.error(f"Channel switch failed: {e}")
                time.sleep(POLL_INTERVAL)
                continue

        state['current_channel'] = target
        state['last_switch'] = now
        save_state(state)

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='March Madness Auto-Switcher')
    parser.add_argument('--dry-run', action='store_true', help='Log decisions without sending IR')
    parser.add_argument('--channel', type=int, help='Set starting channel')
    args = parser.parse_args()

    if args.channel:
        state = load_state()
        state['current_channel'] = args.channel
        save_state(state)

    run(dry_run=args.dry_run)
