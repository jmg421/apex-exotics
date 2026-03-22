#!/usr/bin/env python3
"""
Excitement Engine - Scores live games for auto-switching
March Madness optimized
"""
import requests
from datetime import datetime

ESPN_NCAA_API = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
ESPN_NHL_API = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
ESPN_NBA_API = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"


def load_tossup_boosts():
    """Load toss-up priority boosts from r1_schedule.json"""
    import json, os
    path = os.path.join(os.path.dirname(__file__), 'data', 'r1_schedule.json')
    try:
        with open(path) as f:
            data = json.load(f)
        boosts = {}
        for g in data['games']:
            if g.get('tossup'):
                # Key by both team names (lowercase) for matching
                for team in [g['away'], g['home']]:
                    key = team.lower().replace('.', '').replace("'", '').strip()
                    boosts[key] = 25 if g.get('priority') == 'highest' else 15
        return boosts
    except Exception:
        return {}

_tossup_boosts = None

def get_tossup_boost(team_abbr):
    """Get toss-up excitement boost for a team abbreviation."""
    global _tossup_boosts
    if _tossup_boosts is None:
        _tossup_boosts = load_tossup_boosts()
    key = team_abbr.lower().replace('.', '').replace("'", '').strip()
    return _tossup_boosts.get(key, 0)

def calculate_excitement(game):
    """Calculate excitement score (0-100) for a game"""
    score = 0
    
    comp = game['competitions'][0]
    status = game['status']['type']
    
    # Skip if not in progress
    if status['state'] != 'in':
        return 0
    
    # Get scores
    home = comp['competitors'][0]
    away = comp['competitors'][1]
    home_score = int(home['score'])
    away_score = int(away['score'])
    margin = abs(home_score - away_score)
    
    # Score margin (closer = more exciting)
    if margin <= 3:
        score += 50
    elif margin <= 7:
        score += 35
    elif margin <= 10:
        score += 20
    elif margin <= 15:
        score += 10
    
    # Time remaining (final minutes = more exciting)
    if 'displayClock' in status:
        clock = status['displayClock']
        period = status.get('period', 2)
        
        # Second half / OT
        if period >= 2:
            score += 20
            
            # Final 5 minutes
            if ':' in clock:
                mins = int(clock.split(':')[0])
                if mins <= 5:
                    score += 30
    
    # Tournament game bonus
    if game.get('season', {}).get('type') == 3:  # Postseason
        score += 20
    
    return min(score, 100)

def get_excitement_rankings():
    """Get all live games ranked by excitement across all sports"""
    all_games = []
    
    # Check NCAA Basketball
    try:
        resp = requests.get(ESPN_NCAA_API, timeout=5)
        data = resp.json()
        for event in data.get('events', []):
            excitement = calculate_excitement(event)
            if excitement > 0:
                comp = event['competitions'][0]
                home = comp['competitors'][0]['team']
                away = comp['competitors'][1]['team']
                
                # Apply toss-up boost for NCAA
                boost = max(get_tossup_boost(home['abbreviation']),
                            get_tossup_boost(home.get('displayName', '')),
                            get_tossup_boost(away['abbreviation']),
                            get_tossup_boost(away.get('displayName', '')))
                excitement = min(excitement + boost, 100)
                
                # Get players on court
                players = get_players_in_game(event['id'], 'basketball/mens-college-basketball')
                
                all_games.append({
                    'game_id': event['id'],
                    'excitement': excitement,
                    'home': home['abbreviation'],
                    'away': away['abbreviation'],
                    'home_score': comp['competitors'][0]['score'],
                    'away_score': comp['competitors'][1]['score'],
                    'status': event['status']['type']['detail'],
                    'sport': 'NCAA Basketball',
                    'channel': None,
                    'players': players,
                    'home_full': home.get('displayName', home['abbreviation']),
                    'away_full': away.get('displayName', away['abbreviation']),
                    'home_id': home.get('id'),
                    'away_id': away.get('id'),
                })
    except Exception as e:
        print(f"Error fetching NCAA: {e}")
    
    # Check NHL
    try:
        resp = requests.get(ESPN_NHL_API, timeout=5)
        data = resp.json()
        for event in data.get('events', []):
            excitement = calculate_excitement(event)
            if excitement > 0:
                comp = event['competitions'][0]
                home = comp['competitors'][0]['team']
                away = comp['competitors'][1]['team']
                
                # Get players on ice
                players = get_players_in_game(event['id'], 'hockey/nhl')
                
                all_games.append({
                    'game_id': event['id'],
                    'excitement': excitement,
                    'home': home['abbreviation'],
                    'away': away['abbreviation'],
                    'home_score': comp['competitors'][0]['score'],
                    'away_score': comp['competitors'][1]['score'],
                    'status': event['status']['type']['detail'],
                    'sport': 'NHL',
                    'channel': None,
                    'players': players,
                    'home_id': home.get('id'),
                    'away_id': away.get('id'),
                })
    except Exception as e:
        print(f"Error fetching NHL: {e}")
    
    # Check NBA
    try:
        resp = requests.get(ESPN_NBA_API, timeout=5)
        data = resp.json()
        for event in data.get('events', []):
            excitement = calculate_excitement(event)
            if excitement > 0:
                comp = event['competitions'][0]
                home = comp['competitors'][0]['team']
                away = comp['competitors'][1]['team']
                
                # Get players on court
                players = get_players_in_game(event['id'], 'basketball/nba')
                
                all_games.append({
                    'game_id': event['id'],
                    'excitement': excitement,
                    'home': home['abbreviation'],
                    'away': away['abbreviation'],
                    'home_score': comp['competitors'][0]['score'],
                    'away_score': comp['competitors'][1]['score'],
                    'status': event['status']['type']['detail'],
                    'sport': 'NBA',
                    'channel': None,
                    'players': players,
                    'home_id': home.get('id'),
                    'away_id': away.get('id'),
                })
    except Exception as e:
        print(f"Error fetching NBA: {e}")
    
    # Sort by excitement
    all_games.sort(key=lambda x: x['excitement'], reverse=True)
    return all_games

def get_players_in_game(event_id, sport):
    """Get players currently in play for a game"""
    try:
        resp = requests.get(f'http://site.api.espn.com/apis/site/v2/sports/{sport}/summary?event={event_id}', timeout=5)
        data = resp.json()
        
        players = {'home': [], 'away': []}
        
        # Build team ID to homeAway mapping
        team_map = {}
        if 'header' in data and 'competitions' in data['header']:
            for competitor in data['header']['competitions'][0]['competitors']:
                team_id = str(competitor['team']['id'])
                team_map[team_id] = competitor.get('homeAway', 'away')
        
        if 'onIce' in data:  # NHL
            for team_data in data['onIce']:
                team_id = str(team_data.get('teamId'))
                for entry in team_data.get('entries', []):
                    if entry.get('whereabouts', {}).get('description') == 'In Play':
                        athlete_id = entry.get('athleteid')
                        # Find athlete name in boxscore
                        if 'boxscore' in data and 'players' in data['boxscore']:
                            for team in data['boxscore']['players']:
                                if str(team['team']['id']) == team_id:
                                    for stat_group in team.get('statistics', []):
                                        for athlete in stat_group.get('athletes', []):
                                            if str(athlete['athlete']['id']) == str(athlete_id):
                                                name = athlete['athlete'].get('displayName', 'Unknown')
                                                jersey = athlete['athlete'].get('jersey', '')
                                                side = team_map.get(team_id, 'away')
                                                players[side].append(f"#{jersey} {name}")
        
        return players
    except Exception as e:
        print(f"Error fetching players for {event_id}: {e}")
        return {'home': [], 'away': []}

if __name__ == "__main__":
    print("March Madness Excitement Rankings\n")
    games = get_excitement_rankings()
    
    if not games:
        print("No live games right now")
    else:
        for i, game in enumerate(games, 1):
            print(f"{i}. [{game['excitement']:3d}] {game['away']} @ {game['home']} - {game['status']}")
            print(f"   Score: {game['away_score']}-{game['home_score']}")
            print()

        # Cross-system market signals
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
            from signal_bridge import sports_event_to_market_signal
            signals = []
            for game in games:
                signals.extend(sports_event_to_market_signal(game))
            if signals:
                print("📊 MARKET SIGNALS")
                print("-" * 60)
                for s in signals:
                    print(f"  [{s['urgency']}] {s['type']}: {s['reason']}")
                    print(f"         Tickers: {', '.join(s['tickers'][:5])}")
        except ImportError:
            pass
