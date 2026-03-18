#!/usr/bin/env python3
"""
March Madness integration for sports dashboard
"""
import re

def fuzzy_match_teams(game1, game2):
    """Fuzzy match team names (ignore formatting, Live markers, etc)"""
    # Extract team names only
    def clean(s):
        s = re.sub(r'ᴸᶦᵛᵉ|Live|ᴺᵉʷ|\(.*?\)', '', s)  # Remove markers
        s = re.sub(r'Blue Devils|Tar Heels|Wildcats|Wolfpack|Red Raiders', '', s)  # Remove mascots
        s = re.sub(r'College Basketball\s*:\s*|Tournament\s*:\s*|ACC|Big 12|SEC', '', s)  # Remove prefixes
        s = s.replace('.', '').replace(',', '')  # Remove punctuation
        return s.strip().lower()
    
    c1, c2 = clean(game1), clean(game2)
    
    # Split by vs and check if team names match
    if ' vs ' in c1 and ' vs ' in c2:
        teams1 = [t.strip() for t in c1.split(' vs ')]
        teams2 = [t.strip() for t in c2.split(' vs ')]
        
        # Check if both teams appear in both strings
        matches = sum(1 for t1 in teams1 if any(t1 in t2 or t2 in t1 for t2 in teams2))
        return matches >= 2
    
    return c1 in c2 or c2 in c1

def match_games_to_channels(upset_alerts, epg_programs):
    """Match upset alert games to EPG channels"""
    result = []
    
    for alert in upset_alerts:
        matched = False
        for program in epg_programs:
            if fuzzy_match_teams(alert['Matchup'], program['title']):
                alert['channel'] = program['channel']
                alert['live'] = 'ᴸᶦᵛᵉ' in program['title']
                matched = True
                break
        
        if not matched:
            alert['channel'] = None
            alert['live'] = False
        
        result.append(alert)
    
    return result

def get_upset_alerts():
    """Get current upset predictions matched to live EPG channels"""
    # Mock upset data (will be replaced with real upset_detector.py later)
    mock_upsets = [
        {'Matchup': 'TBA vs Virginia', 'Fav_Rank': 5, 'Dog_Rank': 12, 
         'Fav_EM': '22.3', 'Dog_EM': '16.8', 'Upset_Score': 6, 
         'Flags': 'ACC_TOURNAMENT, UPSET_POTENTIAL'},
        {'Matchup': 'Texas Tech vs TBA', 'Fav_Rank': 3, 'Dog_Rank': 14,
         'Fav_EM': '25.1', 'Dog_EM': '17.4', 'Upset_Score': 7,
         'Flags': 'BIG12_TOURNAMENT, TEMPO_TRAP'}
    ]
    
    # Get live EPG data
    try:
        from epg_parser import fetch_epg, get_current_program, CHANNEL_MAP
        epg = fetch_epg()
        epg_programs = []
        
        for channel_num, epg_id in CHANNEL_MAP.items():
            program = get_current_program(epg, epg_id)
            if program:
                epg_programs.append({
                    'channel': channel_num,
                    'title': program['title']
                })
        
        # Match upsets to channels
        return match_games_to_channels(mock_upsets, epg_programs)
    except Exception as e:
        print(f"EPG matching failed: {e}, using mock data")
        # Fallback to mock with hardcoded channels
        for upset in mock_upsets:
            upset['channel'] = None
            upset['live'] = False
        return mock_upsets

def get_injury_watch_teams():
    """Teams to monitor for injuries"""
    return [
        'Duke', 'Michigan', 'Florida', 'Arizona', 'Houston', 
        'Illinois', 'Iowa St.', 'Purdue', 'Connecticut', 'Michigan St.',
        'Northwestern', 'New Mexico'
    ]

if __name__ == '__main__':
    print("Upset Alerts:", get_upset_alerts())
    print("Injury Watch:", get_injury_watch_teams())
