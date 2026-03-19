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
COOLDOWN = 120
STICKINESS = 10
PREGAME_MINUTES = 5  # Switch this many minutes before tip-off

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

def run():
    """Main loop."""
    current_channel = None
    last_switch = 0

    print(f"🎯 Auto-Switcher started at {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Networks mapped: {len([v for v in NETWORK_CHANNELS.values() if v])}")

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
                time.sleep(30)
                continue

        # Attach channel info
        for g in games:
            nets = broadcasts.get(g['game_id'], [])
            g['networks'] = nets
            g['channel'] = resolve_channel(nets)
            # Stickiness bonus
            if g['channel'] == current_channel:
                g['excitement'] = min(g['excitement'] + STICKINESS, 100)

        switchable = [g for g in games if g['channel'] and g['excitement'] >= MIN_EXCITEMENT]
        switchable.sort(key=lambda g: g['excitement'], reverse=True)

        # Log top games
        ts = datetime.now().strftime('%H:%M:%S')
        for g in switchable[:5]:
            stick = ' ★' if g['channel'] == current_channel else ''
            print(f"  [{ts}] {g['excitement']:3d} {g['away']:5} vs {g['home']:5} | {g['status'][:25]:25} | ch:{g['channel']} {g['networks'][:2]}{stick}")

        if not switchable:
            print(f"  [{ts}] No switchable games above {MIN_EXCITEMENT}")
            time.sleep(30)
            continue

        best = switchable[0]
        if best['channel'] != current_channel and (now - last_switch) > COOLDOWN:
            print(f"\n🔄 SWITCHING to ch {best['channel']}: {best['away']} vs {best['home']} ({best['away_score']}-{best['home_score']}) — excitement {best['excitement']}")
            change_channel(best['channel'])
            current_channel = best['channel']
            last_switch = now
            print()

        time.sleep(30)

if __name__ == '__main__':
    run()
