#!/Users/apple/apex-exotics/venv/bin/python
"""
Auto Channel Switcher — switches to the most exciting live game.
Uses excitement engine + ESPN broadcast data to find the right HEAT channel.
"""
import time
import json
import requests
from datetime import datetime
from excitement_engine import get_excitement_rankings
from channel_switcher import change_channel

# Network name → HEAT channel number
NETWORK_CHANNELS = {
    # ESPN family
    'ESPN': 809, 'ESPN2': 811, 'ESPNU': 812, 'ESPNews': 814, 'ESPN+': None,
    # Broadcast
    'CBS': 28, 'TBS': 156, 'TNT': 162, 'truTV': 166,
    # Sports networks
    'FS1': 860, 'FS2': 862, 'MLB Network': 815, 'NBA TV': 816,
    'NFL Network': 817, 'Big Ten Network': 807, 'CBS Sports Network': 808,
    'SEC Network': 820, 'Golf Channel': 912,
}

SPORT_PATHS = {
    'NCAA Basketball': 'basketball/mens-college-basketball',
    'NBA': 'basketball/nba',
    'NHL': 'hockey/nhl',
}

# State
MIN_EXCITEMENT = 40
COOLDOWN = 45
STICKINESS = 5
ROTATION_SECONDS = 60  # Time on each game before rotating
PREGAME_MINUTES = 5  # Switch this many minutes before tip-off
CLOCK_STALL_SECONDS = 25  # If game clock unchanged this long, likely commercial

# Pinned teams get excitement boost + longer rotation time
PINNED_TEAMS = {'OSU'}
PINNED_BOOST = 30
PINNED_ROTATION_SECONDS = 120

# Track game clocks for stall detection
_clock_history = {}  # game_id -> (clock_str, timestamp_of_last_change)

def get_broadcasts():
    """Fetch broadcast info for all live games from ESPN."""
    broadcasts = {}
    for sport, path in SPORT_PATHS.items():
        try:
            data = requests.get(
                f'http://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard', timeout=5
            ).json()
            for event in data.get('events', []):
                game_id = event.get('id')
                for comp in event.get('competitions', []):
                    networks = []
                    for b in comp.get('broadcasts', []):
                        networks.extend(b.get('names', []))
                    if networks:
                        broadcasts[game_id] = networks
        except:
            pass
    return broadcasts

def get_upcoming_tips():
    """Find games tipping off soon that we should switch to for pregame."""
    tips = []
    for sport, path in SPORT_PATHS.items():
        try:
            data = requests.get(
                f'http://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard', timeout=5
            ).json()
            for event in data.get('events', []):
                state = event['status']['type'].get('state', '')
                if state != 'pre':
                    continue
                start = event.get('date', '')
                if not start:
                    continue
                from dateutil import parser as dtparser
                tip_time = dtparser.isoparse(start)
                now = datetime.now(tip_time.tzinfo)
                mins_until = (tip_time - now).total_seconds() / 60
                if 0 < mins_until <= PREGAME_MINUTES:
                    networks = []
                    for comp in event.get('competitions', []):
                        for b in comp.get('broadcasts', []):
                            networks.extend(b.get('names', []))
                    ch = resolve_channel(networks)
                    if ch:
                        tips.append({
                            'game_id': event['id'],
                            'name': event.get('shortName', ''),
                            'channel': ch,
                            'networks': networks,
                            'mins_until': mins_until,
                        })
        except:
            pass
    return tips

def resolve_channel(networks):
    """Find the best HEAT channel from a list of broadcast networks."""
    for net in networks:
        for name, ch in NETWORK_CHANNELS.items():
            if ch and name.lower() in net.lower():
                return ch
    return None

def is_clock_stalled(game):
    """Detect if a game's clock has stalled (likely commercial/timeout)."""
    gid = game.get('game_id')
    clock = game.get('status', '')
    now = time.time()
    prev = _clock_history.get(gid)
    if prev is None or prev[0] != clock:
        _clock_history[gid] = (clock, now)
        return False
    return (now - prev[1]) >= CLOCK_STALL_SECONDS


def run():
    """Main loop with round-robin rotation across exciting games."""
    # Read current channel from disk so we don't switch on startup
    try:
        import json as _json
        with open('data/current_channel.json') as f:
            current_channel = _json.load(f).get('channel')
    except Exception:
        current_channel = None
    last_switch = time.time()
    rotation_index = -1

    print(f"🎯 Auto-Switcher started at {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Networks mapped: {len([v for v in NETWORK_CHANNELS.values() if v])}")
    print(f"   Rotation: {ROTATION_SECONDS}s per game, cooldown: {COOLDOWN}s, pinned: {PINNED_TEAMS} ({PINNED_ROTATION_SECONDS}s +{PINNED_BOOST})")

    while True:
        now = time.time()
        games = get_excitement_rankings()
        broadcasts = get_broadcasts()

        # Check for upcoming tip-offs first
        tips = get_upcoming_tips()
        if tips and (now - last_switch) > COOLDOWN:
            tip = tips[0]
            if tip['channel'] != current_channel:
                print(f"\n🏀 PREGAME: {tip['name']} tips off in {tip['mins_until']:.0f}m — switching to ch {tip['channel']}")
                change_channel(tip['channel'])
                current_channel = tip['channel']
                last_switch = now
                time.sleep(15)
                continue

        # Attach channel info
        for g in games:
            nets = broadcasts.get(g['game_id'], [])
            g['networks'] = nets
            g['channel'] = resolve_channel(nets)

        switchable = [g for g in games if g['channel'] and g['excitement'] >= MIN_EXCITEMENT]
        # Boost pinned teams
        for g in switchable:
            if g.get('home') in PINNED_TEAMS or g.get('away') in PINNED_TEAMS:
                g['excitement'] = min(g['excitement'] + PINNED_BOOST, 100)
                g['pinned'] = True
            else:
                g['pinned'] = False
        switchable.sort(key=lambda g: g['excitement'], reverse=True)

        # Log top games
        ts = datetime.now().strftime('%H:%M:%S')
        for g in switchable[:6]:
            marker = '★' if g['channel'] == current_channel else ' '
            print(f"  [{ts}] {marker} {g['excitement']:3d} {g['away']:5} vs {g['home']:5} | {g['status'][:25]:25} | ch:{g['channel']} {g['networks'][:2]}")

        if not switchable:
            print(f"  [{ts}] No switchable games above {MIN_EXCITEMENT}")
            time.sleep(15)
            continue

        # Tag stalled games
        for g in switchable:
            g['stalled'] = is_clock_stalled(g)

        current_game = next((g for g in switchable if g['channel'] == current_channel), None)
        current_stalled = current_game['stalled'] if current_game else False
        current_pinned = current_game.get('pinned', False) if current_game else False
        rot_time = PINNED_ROTATION_SECONDS if current_pinned else ROTATION_SECONDS
        time_on_current = now - last_switch

        if current_stalled and not current_pinned and len(switchable) >= 2:
            # Commercial/timeout — jump to next live game after broadcast delay
            live_games = [g for g in switchable if not g['stalled'] and g['channel'] != current_channel]
            if live_games:
                target = live_games[0]
                print(f"\n📺 COMMERCIAL SKIP → ch {target['channel']}: "
                      f"{target['away']} vs {target['home']} ({target['away_score']}-{target['home_score']}) — excitement {target['excitement']}"
                      f" (waiting 20s for broadcast)")
                time.sleep(20)  # let broadcast catch up to API
                change_channel(target['channel'])
                current_channel = target['channel']
                last_switch = now
                rotation_index = switchable.index(target) if target in switchable else 0
        elif len(switchable) >= 2 and time_on_current >= rot_time:
            # Rotate — but only to a game worth switching to
            rotation_index = (rotation_index + 1) % len(switchable)
            target = switchable[rotation_index]
            current_exc = current_game['excitement'] if current_game else 0
            if (target['channel'] != current_channel
                    and not target['stalled']
                    and target['excitement'] >= current_exc - 20):
                print(f"\n🔄 ROTATE [{rotation_index+1}/{len(switchable)}] → ch {target['channel']}: "
                      f"{target['away']} vs {target['home']} ({target['away_score']}-{target['home_score']}) — excitement {target['excitement']}")
                change_channel(target['channel'])
                current_channel = target['channel']
                last_switch = now
        elif len(switchable) == 1:
            # Only one game — just switch to it
            best = switchable[0]
            if best['channel'] != current_channel and time_on_current > COOLDOWN:
                print(f"\n🔄 SWITCHING to ch {best['channel']}: {best['away']} vs {best['home']} ({best['away_score']}-{best['home_score']}) — excitement {best['excitement']}")
                change_channel(best['channel'])
                current_channel = best['channel']
                last_switch = now
                rotation_index = 0

        time.sleep(15)

if __name__ == '__main__':
    run()
