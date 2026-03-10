#!/usr/bin/env python3
"""
Ohio Sports Hub - All Ohio teams in one place
Cavs, Browns, Bengals, Reds, Guardians, Blue Jackets, Buckeyes
"""
from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

ESPN_API = "http://site.api.espn.com/apis/site/v2/sports"

OHIO_TEAMS = {
    'nba': ['CLE'],
    'nfl': ['CLE', 'CIN'],
    'mlb': ['CLE', 'CIN'],
    'nhl': ['CBJ'],
    'ncaa-football': ['OHIO'],
    'ncaa-basketball': ['OHIO']
}

@app.route('/')
def index():
    return render_template('ohio_dashboard.html')

@app.route('/api/ohio-games')
def get_ohio_games():
    """Get all Ohio team games across all sports"""
    all_games = []
    
    # NBA
    nba_games = fetch_espn_games('basketball/nba', 'nba')
    all_games.extend([g for g in nba_games if g['away'] in OHIO_TEAMS['nba'] or g['home'] in OHIO_TEAMS['nba']])
    
    # NFL
    nfl_games = fetch_espn_games('football/nfl', 'nfl')
    all_games.extend([g for g in nfl_games if g['away'] in OHIO_TEAMS['nfl'] or g['home'] in OHIO_TEAMS['nfl']])
    
    # MLB - detect split squad games
    mlb_games = fetch_espn_games('baseball/mlb', 'mlb')
    ohio_mlb = [g for g in mlb_games if g['away'] in OHIO_TEAMS['mlb'] or g['home'] in OHIO_TEAMS['mlb']]
    
    # Mark split squad games
    team_game_count = {}
    for game in ohio_mlb:
        for team in [game['away'], game['home']]:
            if team in OHIO_TEAMS['mlb']:
                team_game_count[team] = team_game_count.get(team, 0) + 1
    
    for game in ohio_mlb:
        for team in [game['away'], game['home']]:
            if team in OHIO_TEAMS['mlb'] and team_game_count[team] > 1:
                game['split_squad'] = True
                break
    
    all_games.extend(ohio_mlb)
    
    # NHL
    nhl_games = fetch_espn_games('hockey/nhl', 'nhl')
    all_games.extend([g for g in nhl_games if g['away'] in OHIO_TEAMS['nhl'] or g['home'] in OHIO_TEAMS['nhl']])
    
    # NCAA Football
    ncaa_fb_games = fetch_espn_games('football/college-football', 'ncaa-football')
    all_games.extend([g for g in ncaa_fb_games if 'OHIO' in g['away'] or 'OHIO' in g['home']])
    
    # NCAA Basketball
    ncaa_bb_games = fetch_espn_games('basketball/mens-college-basketball', 'ncaa-basketball')
    all_games.extend([g for g in ncaa_bb_games if 'OHIO' in g['away'] or 'OHIO' in g['home']])
    
    # Sort: live first, then by start time
    all_games.sort(key=lambda x: (x['state'] != 'in' and x['state'] != 'live', x.get('start_time', '')))
    
    return jsonify(all_games)

def fetch_espn_games(sport_path, sport_key):
    """Fetch games from ESPN API"""
    url = f"{ESPN_API}/{sport_path}/scoreboard"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        events = data.get('events', [])
        games = []
        
        for event in events:
            comp = event.get('competitions', [{}])[0]
            teams = comp.get('competitors', [])
            status = event.get('status', {})
            
            if len(teams) < 2:
                continue
            
            away = next((t for t in teams if t.get('homeAway') == 'away'), teams[0])
            home = next((t for t in teams if t.get('homeAway') == 'home'), teams[1])
            
            games.append({
                'id': event.get('id'),
                'sport': sport_key,
                'away': away.get('team', {}).get('abbreviation', ''),
                'home': home.get('team', {}).get('abbreviation', ''),
                'away_score': away.get('score', '0'),
                'home_score': home.get('score', '0'),
                'status': status.get('type', {}).get('shortDetail', ''),
                'state': status.get('type', {}).get('state', ''),
                'start_time': event.get('date', '')
            })
        
        return games
    except Exception as e:
        print(f"Error fetching {sport_path}: {e}")
        return []

@app.route('/api/game/<sport>/<game_id>/stats')
def get_game_stats(sport, game_id):
    """Get detailed stats for a specific game"""
    sport_map = {
        'nba': 'basketball/nba',
        'nfl': 'football/nfl',
        'mlb': 'baseball/mlb',
        'nhl': 'hockey/nhl',
        'ncaa-football': 'football/college-football',
        'ncaa-basketball': 'basketball/mens-college-basketball'
    }
    
    sport_path = sport_map.get(sport)
    if not sport_path:
        return jsonify({'error': 'Invalid sport'}), 400
    
    url = f"{ESPN_API}/{sport_path}/summary?event={game_id}"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        # Return raw data for now - can parse specific stats later
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
