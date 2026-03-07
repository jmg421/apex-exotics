#!/usr/bin/env python3
"""
Sports Stats Monitor - Live NCAA game margins
Shows efficiency stats that predict outcomes before the score does
"""
from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

NCAA_API = "https://ncaa-api.henrygd.me"

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/games')
def get_games():
    """Get today's games"""
    today = datetime.now().strftime('%Y/%m/%d')
    url = f"{NCAA_API}/scoreboard/basketball-men/d1/{today}/all-conf"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        games = []
        for item in data.get('games', []):
            game = item['game']
            games.append({
                'id': game['gameID'],
                'away': game['away']['names']['short'],
                'home': game['home']['names']['short'],
                'away_score': game['away'].get('score', '0'),
                'home_score': game['home'].get('score', '0'),
                'status': game['currentPeriod'],
                'clock': game['contestClock'],
                'state': game['gameState']
            })
        
        return jsonify(games)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/<game_id>/stats')
def get_game_stats(game_id):
    """Get detailed stats for a game"""
    url = f"{NCAA_API}/game/{game_id}/team-stats"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        teams = data.get('teams', [])
        stats = data.get('teamBoxscore', [])
        
        # Handle clock formatting safely
        minutes = data.get('minutes')
        seconds = data.get('seconds')
        if minutes is not None and seconds is not None:
            clock = f"{minutes}:{seconds:02d}"
        else:
            clock = "0:00"
        
        result = {
            'game_id': game_id,
            'period': data.get('period', ''),
            'clock': clock,
            'teams': []
        }
        
        for i, team_data in enumerate(stats):
            team_info = teams[i] if i < len(teams) else {}
            team_stats = team_data.get('teamStats', {})
            
            # Handle None values
            fg_pct = team_stats.get('fieldGoalPercentage') or '0%'
            three_pct = team_stats.get('threePointPercentage') or '0%'
            
            result['teams'].append({
                'name': team_info.get('nameShort', ''),
                'is_home': team_info.get('isHome', False),
                'fg_pct': fg_pct if fg_pct != '-' else '0%',
                'fg_made': team_stats.get('fieldGoalsMade', '0'),
                'fg_att': team_stats.get('fieldGoalsAttempted', '0'),
                'three_pct': three_pct if three_pct != '-' else '0%',
                'three_made': team_stats.get('threePointsMade', '0'),
                'three_att': team_stats.get('threePointsAttempted', '0'),
                'turnovers': team_stats.get('turnovers', '0'),
                'rebounds': team_stats.get('totalRebounds', '0'),
                'assists': team_stats.get('assists', '0'),
                'steals': team_stats.get('steals', '0')
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
