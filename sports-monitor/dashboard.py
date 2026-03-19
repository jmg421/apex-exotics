#!/usr/bin/env python3
"""
Sports Stats Monitor - Live NCAA game margins
Shows efficiency stats that predict outcomes before the score does
"""
from flask import Flask, render_template, jsonify, request, Response
from functools import wraps
import requests
from datetime import datetime
import os
import time
from headline_storage import save_headline, get_recent_headlines
from headline_source import find_source_url

app = Flask(__name__)

# Simple in-memory cache to respect API rate limits
_api_cache = {}
def cached(key, ttl):
    """Return cached data if fresh, else None"""
    entry = _api_cache.get(key)
    if entry and time.time() - entry['ts'] < ttl:
        return entry['data']
    return None
def cache_set(key, data):
    _api_cache[key] = {'data': data, 'ts': time.time()}
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Basic auth for private streaming
STREAM_USER = os.getenv('STREAM_USER', 'apex')
STREAM_PASS = os.getenv('STREAM_PASS', 'sports2026')

def check_auth(username, password):
    return username == STREAM_USER and password == STREAM_PASS

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip auth for local/LAN access
        remote = request.remote_addr
        if remote in ('127.0.0.1', '::1') or remote.startswith('192.168.'):
            return f(*args, **kwargs)
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('Access denied', 401, {'WWW-Authenticate': 'Basic realm="Apex Sports"'})
        return f(*args, **kwargs)
    return decorated

NCAA_API = "https://ncaa-api.henrygd.me"
ESPN_API = "http://site.api.espn.com/apis/site/v2/sports"
JARVIS_API = "https://staging.nodes.bio/api/jarvis"
JARVIS_TOKEN = os.getenv('JARVIS_TOKEN', '')

def filter_headlines_with_jarvis(headlines):
    """Filter headlines to only important/interesting ones"""
    # Simple keyword-based filter
    important_keywords = ['trade', 'traded', 'sign', 'signing', 'deal', 'injury', 'injured', 'out for', 'torn', 'return', 'fire', 'hire', 'suspend', 'fine', 'mvp', 'playoff', 'shut down', 'waive', 'release', 'cut', 'retire', 'arrest', 'ban', 'upset', 'buzzer', 'overtime', 'walk-off', 'no-hitter', 'record-breaking', 'scores', 'scored', 'top ', 'beat', 'defeat', 'win ', 'wins ', 'rout', 'clinch', 'eliminate', 'advance', 'double-double', 'triple-double']
    skip_keywords = ['host', 'face', 'play the', 'takes on', 'looks to', 'game preview', 'live updates', 'grades', 'tracker', 'offseason', 'free agency', 'mock draft', 'predictions', 'odds', 'power rankings', 'what to know', 'how to watch', 'preview:', 'picks:', 'best bets', 'game highlights', 'highlights:', 'full highlights', 'recap:', 'records to know', 'streaks:', 'rule change', 'propose', 'all-time', 'history of']
    
    filtered = []
    for h in headlines:
        headline_lower = h['headline'].lower()
        
        # Skip generic game previews
        if any(skip in headline_lower for skip in skip_keywords):
            continue
        
        # Keep if has important keywords or is short/punchy
        if any(keyword in headline_lower for keyword in important_keywords) or len(h['headline']) < 60:
            filtered.append(h)
    
    return filtered if filtered else headlines[:5]

@app.route('/')
@requires_auth
def index():
    return render_template('dashboard.html')

@app.route('/api/current_channel')
def get_current_channel():
    """Get currently playing VSeeBox channel"""
    import json
    try:
        with open('data/current_channel.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'channel': 'UNKNOWN', 'timestamp': None, 'peer_count': 0})
    except Exception as e:
        print(f"Error reading channel state: {e}")
        return jsonify({'channel': 'ERROR', 'timestamp': None, 'peer_count': 0})

@app.route('/api/stream_source')
def get_stream_source():
    """Return the current active m3u8 filename for direct HLS access"""
    import glob
    movies_dir = os.path.expanduser('/Users/apple/Movies')
    m3u8_files = sorted(glob.glob(f'{movies_dir}/*.m3u8'), key=os.path.getmtime, reverse=True)
    for m in m3u8_files:
        basename = os.path.splitext(os.path.basename(m))[0]
        if glob.glob(f'{movies_dir}/{basename}*.ts'):
            return jsonify({'filename': os.path.basename(m)})
    return jsonify({'filename': ''})

@app.route('/stream.m3u8')
@requires_auth
def get_stream():
    """Proxy HLS - use remote quality if requested"""
    import glob
    import os
    from flask import make_response

    remote = request.args.get('quality') == 'remote'
    
    if remote:
        remote_m3u8 = os.path.expanduser('/Users/apple/Movies/remote/stream.m3u8')
        if os.path.exists(remote_m3u8):
            with open(remote_m3u8, 'r') as f:
                content = f.read()
            lines = []
            for line in content.splitlines():
                if line and not line.startswith('#'):
                    lines.append(f'/stream/remote/{line}')
                else:
                    lines.append(line)
            response = make_response('\n'.join(lines))
            response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    movies_dir = os.path.expanduser('/Users/apple/Movies')
    m3u8_files = glob.glob(f'{movies_dir}/*.m3u8')

    if not m3u8_files:
        return "No stream available", 404

    m3u8_files.sort(key=os.path.getmtime, reverse=True)
    for m3u8 in m3u8_files:
        basename = os.path.splitext(os.path.basename(m3u8))[0]
        if glob.glob(f'{movies_dir}/{basename}*.ts'):
            # Read and rewrite m3u8 to use relative /stream/ paths
            with open(m3u8, 'r') as f:
                content = f.read()
            # Replace bare filenames with /stream/ prefix
            lines = []
            for line in content.splitlines():
                if line and not line.startswith('#'):
                    lines.append(f'/stream/{line}')
                else:
                    lines.append(line)
            response = make_response('\n'.join(lines))
            response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    return "No stream with segments available", 404


@app.route('/stream/remote/<path:filename>')
@requires_auth
def get_remote_segment(filename):
    """Serve low-bitrate remote HLS segments"""
    from flask import send_file
    import os
    file_path = os.path.join('/Users/apple/Movies/remote', filename)
    if os.path.exists(file_path):
        mimetype = 'application/vnd.apple.mpegurl' if filename.endswith('.m3u8') else 'video/mp2t'
        response = send_file(file_path, mimetype=mimetype)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'no-cache'
        return response
    return f"Segment not found: {filename}", 404

@app.route('/stream/<path:filename>')
@requires_auth
def get_stream_segment(filename):
    """Serve HLS segments"""
    from flask import send_file
    import os
    
    movies_dir = os.path.expanduser('/Users/apple/Movies')
    file_path = os.path.join(movies_dir, filename)
    
    if os.path.exists(file_path):
        mimetype = 'application/vnd.apple.mpegurl' if filename.endswith('.m3u8') else 'video/mp2t'
        response = send_file(file_path, mimetype=mimetype)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'no-cache' if filename.endswith('.m3u8') else 'public, max-age=60'
        return response
    return f"Segment not found: {filename}", 404

@app.route('/api/team_roster/<team_name>')
def get_team_roster(team_name):
    """Scrape team roster from ESPN"""
    try:
        # Search for team on ESPN
        search_url = f"https://www.espn.com/mens-college-basketball/teams"
        
        # For now, return placeholder data
        # Real scraping would require finding team ID, then roster page
        return jsonify({
            'team': team_name,
            'players': [
                f'Player 1 - {team_name}',
                f'Player 2 - {team_name}',
                f'Player 3 - {team_name}',
                f'Player 4 - {team_name}',
                f'Player 5 - {team_name}'
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e), 'players': []})

@app.route('/api/espn_game')
def get_espn_game():
    """Find which game is currently LIVE on ESPN"""
    try:
        # Check NCAA basketball
        resp = requests.get(f'{ESPN_API}/basketball/mens-college-basketball/scoreboard', timeout=5)
        data = resp.json()
        
        for event in data.get('events', []):
            # Only check live games
            status = event.get('competitions', [{}])[0].get('status', {})
            if status.get('type', {}).get('state') != 'in':
                continue
                
            broadcasts = event.get('competitions', [{}])[0].get('broadcasts', [])
            for broadcast in broadcasts:
                if 'ESPN' in broadcast.get('names', []):
                    # This game is LIVE on ESPN
                    return jsonify({
                        'id': event.get('id'),
                        'name': event.get('name'),
                        'sport': 'ncaa-basketball'
                    })
        
        # Check NBA
        resp = requests.get(f'{ESPN_API}/basketball/nba/scoreboard', timeout=5)
        data = resp.json()
        
        for event in data.get('events', []):
            status = event.get('competitions', [{}])[0].get('status', {})
            if status.get('type', {}).get('state') != 'in':
                continue
                
            broadcasts = event.get('competitions', [{}])[0].get('broadcasts', [])
            for broadcast in broadcasts:
                if 'ESPN' in broadcast.get('names', []):
                    return jsonify({
                        'id': event.get('id'),
                        'name': event.get('name'),
                        'sport': 'nba'
                    })
        
        return jsonify({'id': None, 'name': 'No live ESPN game found'})
        
    except Exception as e:
        return jsonify({'id': None, 'error': str(e)})

SCORE_DELAY_SECONDS = 150 # remote: IPTV delay + transcode + CDN
SCORE_DELAY_LAN = 45     # IPTV broadcast runs behind real-time
SCORE_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'score_history.json')

def _save_score_snapshot(games):
    """Append score snapshot to shared file cache"""
    import json
    try:
        try:
            with open(SCORE_CACHE_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []
        now = time.time()
        history.append({'t': now, 'games': games})
        # Keep 3 minutes
        history = [h for h in history if h['t'] > now - 180]
        with open(SCORE_CACHE_FILE, 'w') as f:
            json.dump(history, f)
    except:
        pass

def _get_delayed_scores(delay_seconds):
    """Get scores from N seconds ago"""
    import json
    try:
        with open(SCORE_CACHE_FILE, 'r') as f:
            history = json.load(f)
        if not history:
            return None
        target = time.time() - delay_seconds
        best = history[0]['games']
        for h in history:
            if h['t'] <= target:
                best = h['games']
            else:
                break
        return best
    except:
        return None

@app.route('/api/excitement')
def get_excitement():
    """Get excitement scores for all live games"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    sport = request.args.get('sport', 'ncaa-basketball')
    is_remote = request.args.get('remote', 'false').lower() == 'true'
    
    try:
        from excitement_engine import get_excitement_rankings
        c = cached('excitement_rankings', 15)
        games = c if c is not None else get_excitement_rankings()
        if c is None:
            cache_set('excitement_rankings', games)
        
        # Map sport names to filter
        sport_map = {
            'ncaa-basketball': 'NCAA',
            'nba': 'NBA',
            'nhl': 'NHL',
            'mlb': 'MLB'
        }
        
        # Filter by sport
        if sport == 'all':
            filtered_games = games
        else:
            sport_filter = sport_map.get(sport, 'NCAA')
            filtered_games = [g for g in games if sport_filter.upper() in g.get('sport', '').upper()]
        
        # Add channel info from auto_channel broadcasts
        try:
            from auto_channel import get_broadcasts, resolve_channel
            broadcasts = get_broadcasts()
            for g in filtered_games:
                nets = broadcasts.get(g['game_id'], [])
                g['network'] = ', '.join(nets) if nets else ''
                g['channel'] = resolve_channel(nets)
        except:
            pass
        
        # Store snapshot for delayed serving
        _save_score_snapshot(filtered_games)
        
        # LAN viewers get slightly delayed scores
        if not is_remote:
            delayed = _get_delayed_scores(SCORE_DELAY_LAN)
            return jsonify(delayed if delayed else filtered_games)

        # Remote viewers get delayed scores
        delayed = _get_delayed_scores(SCORE_DELAY_SECONDS)
        if delayed:
            return jsonify(delayed)
        
        return jsonify(filtered_games)
    except Exception as e:
        return jsonify([])

_jokes_cache = {'data': [], 'ts': 0}

def _refresh_jokes_background():
    """Background thread that refreshes jokes/trivia every 2 minutes"""
    import html as htmlmod
    while True:
        items = []
        try:
            r = requests.get('https://icanhazdadjoke.com/', headers={'Accept': 'application/json'}, timeout=3)
            items.append('😂 ' + r.json().get('joke', ''))
        except:
            pass
        try:
            data = requests.get('http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard', timeout=5).json()
            for e in data.get('events', []):
                if e['status']['type'].get('state') != 'in':
                    continue
                for c in e['competitions'][0]['competitors']:
                    t = c['team']
                    records = [r['summary'] for r in c.get('records', [])]
                    record = records[0] if records else ''
                    seed = c.get('curatedRank', {}).get('current', 0)
                    name = t['displayName']
                    if record:
                        items.append(f'🏀 {name} are {record} this season')
                    if seed and seed <= 16:
                        items.append(f'🏀 {name} are a #{seed} seed in the tournament')
                    if int(c.get('score', 0)) > 0:
                        for l in c.get('leaders', [])[:1]:
                            for a in l.get('leaders', [])[:1]:
                                stat = l.get('displayName', 'points').lower()
                                ath = a['athlete']
                                jersey = ath.get('jersey', '')
                                num = f'#{jersey} ' if jersey else ''
                                items.append(f'🏀 {num}{ath.get("displayName","?")} leads {t["shortDisplayName"]} with {a["displayValue"]} {stat}')
        except:
            pass
        try:
            r = requests.get('https://opentdb.com/api.php?amount=2&category=21&type=multiple', timeout=3)
            for q in r.json().get('results', []):
                question = htmlmod.unescape(q['question'])
                answer = htmlmod.unescape(q['correct_answer'])
                items.append(f'🧠 {question} → {answer}')
        except:
            pass
        if items:
            _jokes_cache['data'] = items
            _jokes_cache['ts'] = time.time()
        time.sleep(120)

import threading
threading.Thread(target=_refresh_jokes_background, daemon=True).start()

@app.route('/api/dad_jokes')
def get_dad_jokes():
    """Return pre-computed jokes/trivia — instant response"""
    return jsonify(_jokes_cache['data'])

@app.route('/api/tension')
def get_tension():
    """Real-time margin for tension bar — matches current channel's game"""
    try:
        from excitement_engine import get_excitement_rankings
        from auto_channel import get_broadcasts, resolve_channel
        import json as j
        games = get_excitement_rankings()
        if not games:
            return jsonify({'margin': 30})
        # Match current channel to a game
        try:
            with open('data/current_channel.json', 'r') as f:
                current_ch = j.load(f).get('channel')
            broadcasts = get_broadcasts()
            for g in games:
                if g.get('status') in ('Final', 'Final/OT'):
                    continue
                nets = broadcasts.get(g['game_id'], [])
                if resolve_channel(nets) == current_ch:
                    return jsonify({'margin': abs(int(g.get('home_score', 0)) - int(g.get('away_score', 0)))})
        except:
            pass
        # No matching live game — no glow
        return jsonify({'margin': 30})
    except:
        return jsonify({'margin': 30})

@app.route('/api/final_scores')
def get_final_scores():
    """Get today's final scores across sports"""
    c = cached('final_scores', 60)
    if c is not None:
        return jsonify(c)
    finals = []
    try:
        for path in ['basketball/mens-college-basketball', 'basketball/nba', 'hockey/nhl']:
            data = requests.get(f'http://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard', timeout=5).json()
            for e in data.get('events', []):
                if e['status']['type'].get('state') == 'post':
                    c = e['competitions'][0]['competitors']
                    away = next(t for t in c if t['homeAway'] == 'away')
                    home = next(t for t in c if t['homeAway'] == 'home')
                    finals.append({
                        'away': away['team']['shortDisplayName'],
                        'home': home['team']['shortDisplayName'],
                        'away_score': int(away.get('score', 0)),
                        'home_score': int(home.get('score', 0)),
                    })
    except:
        pass
    cache_set('final_scores', finals)
    return jsonify(finals)

@app.route('/api/espn_headlines')
def get_espn_headlines():
    """Get ESPN top headlines filtered by Jarvis"""
    try:
        # Collect headlines
        headlines = []
        for sport in ['basketball/nba', 'hockey/nhl', 'basketball/mens-college-basketball']:
            resp = requests.get(f'http://site.api.espn.com/apis/site/v2/sports/{sport}/news', timeout=3)
            data = resp.json()
            
            for article in data.get('articles', [])[:5]:
                headlines.append({
                    'headline': article.get('headline', 'No headline'),
                    'description': article.get('description', '')[:120]
                })
            
            if len(headlines) >= 15:
                break
        
        # Filter with Jarvis
        filtered = filter_headlines_with_jarvis(headlines)
        return jsonify(filtered[:10])
    except Exception as e:
        return jsonify([{'headline': 'Error loading headlines', 'description': str(e)}])

@app.route('/api/streamer_feed')
def get_streamer_feed():
    """Get top streamer activity from Twitch API with social stats"""
    try:
        from streamer_profiles import get_profile
        
        # Get Twitch OAuth token
        client_id = os.getenv('TWITCH_CLIENT_ID', '')
        client_secret = os.getenv('TWITCH_CLIENT_SECRET', '')
        
        if not client_id or not client_secret:
            # Try to get top streams from public endpoint
            try:
                # Get top 10 live streams
                resp = requests.post('https://gql.twitch.tv/gql', 
                    headers={
                        'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'query': '''
                        {
                            streams(first: 10, options: {sort: VIEWER_COUNT}) {
                                edges {
                                    node {
                                        broadcaster {
                                            login
                                            displayName
                                        }
                                        viewersCount
                                        game {
                                            displayName
                                        }
                                        createdAt
                                    }
                                }
                            }
                        }
                        '''
                    },
                    timeout=5
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = []
                    
                    for edge in data.get('data', {}).get('streams', {}).get('edges', [])[:10]:
                        node = edge['node']
                        broadcaster = node['broadcaster']
                        channel = broadcaster['login']
                        name = broadcaster['displayName']
                        viewers = f"{node['viewersCount']:,}"
                        game = node.get('game', {}).get('displayName', 'Unknown')
                        
                        items.append({
                            'headline': f'{name} is LIVE',
                            'description': f'Playing {game} • {viewers} viewers',
                            'viewers': node['viewersCount']
                        })
                    
                    return jsonify(items)
            except Exception as e:
                print(f"Twitch API error: {e}")
            
            # Fallback to hardcoded list
            streamers = ['stake', 'xqc', 'kaicenat', 'pokimane', 'hasanabi', 'ishowspeed']
            items = []
            live_count = 0
            
            for streamer in streamers:
                profile = get_profile(streamer)
                
                try:
                    # Try to get stream info from public endpoint
                    resp = requests.get(f'https://decapi.me/twitch/uptime/{streamer}', timeout=3)
                    uptime = resp.text.strip()
                    
                    if 'offline' not in uptime.lower() and uptime:
                        live_count += 1
                        # Get game info
                        game_resp = requests.get(f'https://decapi.me/twitch/game/{streamer}', timeout=3)
                        game = game_resp.text.strip()
                        
                        # Get viewer count
                        viewers_resp = requests.get(f'https://decapi.me/twitch/viewercount/{streamer}', timeout=3)
                        viewers = viewers_resp.text.strip()
                        
                        try:
                            viewer_count = int(viewers.replace(',', ''))
                        except:
                            viewer_count = 0
                        
                        items.append({
                            'headline': f'{profile["name"]} is LIVE',
                            'description': f'Playing {game} • {viewers} viewers • {uptime}',
                            'viewers': viewer_count
                        })
                except:
                    continue
            
            # Sort live streams by viewer count (highest first)
            items.sort(key=lambda x: x.get('viewers', 0), reverse=True)
            
            # Remove viewer count from response (only used for sorting)
            for item in items:
                item.pop('viewers', None)
            
            # If no one is live, show profiles with stats
            if live_count == 0:
                for streamer in streamers:
                    profile = get_profile(streamer)
                    
                    try:
                        followers_resp = requests.get(f'https://decapi.me/twitch/followcount/{streamer}', timeout=3)
                        followers = followers_resp.text.strip()
                        
                        # Format with commas
                        try:
                            followers_formatted = f"{int(followers):,}"
                        except:
                            followers_formatted = followers
                        
                        # Build social links
                        socials = []
                        if profile.get('youtube'):
                            socials.append(f'YT: {profile["youtube"]}')
                        if profile.get('instagram'):
                            socials.append(f'IG: {profile["instagram"]}')
                        
                        social_str = ' • '.join(socials) if socials else ''
                        
                        items.append({
                            'headline': f'{profile["name"]} - {followers_formatted} followers',
                            'description': f'{profile["bio"]} • {social_str}' if social_str else profile["bio"]
                        })
                    except:
                        continue
            
            return jsonify(items if items else [{'headline': 'No streamer data available', 'description': ''}])
        
        # If we have credentials, use official Twitch API
        # (implement later if needed)
        return jsonify([{'headline': 'Twitch API not configured', 'description': 'Set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET'}])
        
    except Exception as e:
        return jsonify([{'headline': 'Error loading streamer feed', 'description': str(e)}])

@app.route('/api/personalized_feed')
def get_personalized_feed():
    """Get personalized news feed based on user interests"""
    try:
        from user_profile import get_personalized_prompt
        
        # Get Reddit LivestreamFail for viral moments
        items = []
        
        try:
            resp = requests.get('https://www.reddit.com/r/LivestreamFail/hot.json?limit=10', 
                              headers={'User-Agent': 'SportsMonitor/1.0'},
                              timeout=5)
            data = resp.json()
            
            for post in data.get('data', {}).get('children', [])[:5]:
                post_data = post.get('data', {})
                items.append({
                    'headline': post_data.get('title', 'No title')[:80],
                    'description': f"👍 {post_data.get('ups', 0)} upvotes • r/LivestreamFail"
                })
        except:
            pass
        
        return jsonify(items if items else [{'headline': 'No personalized content available', 'description': ''}])
        
    except Exception as e:
        return jsonify([{'headline': 'Error loading feed', 'description': str(e)}])

@app.route('/api/viral_videos')
def get_viral_videos():
    """Get viral videos from tracked creators - bypass YouTube algorithm"""
    try:
        from streamer_profiles import STREAMER_PROFILES
        import xml.etree.ElementTree as ET
        
        videos = []
        
        # Get videos from tracked creators' YouTube RSS feeds
        creators_with_youtube = [
            (username, profile['youtube'], profile['name']) 
            for username, profile in STREAMER_PROFILES.items() 
            if profile.get('youtube')
        ]
        
        for username, youtube_handle, creator_name in creators_with_youtube[:3]:  # Limit API calls
            try:
                # YouTube RSS feed format
                channel_handle = youtube_handle.replace('@', '')
                rss_url = f'https://www.youtube.com/feeds/videos.xml?user={channel_handle}'
                
                resp = requests.get(rss_url, timeout=5)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    
                    # Parse first video from feed
                    ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 
                          'media': 'http://search.yahoo.com/mrss/',
                          'atom': 'http://www.w3.org/2005/Atom'}
                    
                    for entry in root.findall('atom:entry', ns)[:1]:  # Get latest video
                        video_id = entry.find('yt:videoId', ns)
                        title = entry.find('atom:title', ns)
                        published = entry.find('atom:published', ns)
                        
                        if video_id is not None and title is not None:
                            videos.append({
                                'creator': creator_name,
                                'title': title.text[:80],
                                'youtube_handle': f'https://www.youtube.com/watch?v={video_id.text}',
                                'views': 'Latest',
                                'uploaded': published.text[:10] if published is not None else 'Recent'
                            })
            except Exception as e:
                print(f"Error fetching {creator_name}: {e}")
                continue
        
        # Add Reddit viral videos
        try:
            resp = requests.get('https://www.reddit.com/r/videos/hot.json?limit=5',
                              headers={'User-Agent': 'SportsMonitor/1.0'},
                              timeout=5)
            data = resp.json()
            
            for post in data.get('data', {}).get('children', [])[:3]:
                post_data = post.get('data', {})
                url = post_data.get('url', '')
                if 'youtube.com' in url or 'youtu.be' in url:
                    videos.append({
                        'creator': 'Reddit Trending',
                        'title': post_data.get('title', '')[:80],
                        'youtube_handle': url,
                        'views': f"{post_data.get('ups', 0)} upvotes",
                        'uploaded': 'Trending'
                    })
        except:
            pass
        
        return jsonify(videos if videos else [{'creator': 'No videos', 'title': 'Check back later', 'youtube_handle': '', 'views': '', 'uploaded': ''}])
        
    except Exception as e:
        return jsonify([{'creator': 'Error', 'title': str(e), 'youtube_handle': '', 'views': '', 'uploaded': ''}])

@app.route('/api/headlines/unposted')
def get_unposted_headlines():
    """Get headlines not yet posted to X"""
    try:
        from headline_storage import get_unposted_headlines
        headlines = get_unposted_headlines()
        return jsonify(headlines)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/headlines/mark_posted', methods=['POST'])
def mark_headline_posted():
    """Mark a headline as posted to X"""
    try:
        from headline_storage import mark_posted_to_x
        data = request.json
        headline_text = data.get('headline')
        if headline_text:
            mark_posted_to_x(headline_text)
            return jsonify({'success': True})
        return jsonify({'error': 'No headline provided'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/headlines')
def get_headlines():
    """Get all stored headlines"""
    try:
        limit = request.args.get('limit', 50, type=int)
        headlines = get_recent_headlines(limit)
        return jsonify(headlines)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/stream_ocr')
def get_stream_ocr():
    """Extract game info from video stream using OCR"""
    try:
        from lower_third_ocr import get_live_game_info
        
        game_info = get_live_game_info()
        
        if game_info:
            # Save headline to persistent storage with source URL
            if 'next_game' in game_info and game_info['next_game']:
                headline_text = game_info['next_game'].replace('📰 ', '')
                source_url, verified_title = find_source_url(headline_text)
                
                # Only save if we have a verified match
                if source_url and verified_title:
                    save_headline(verified_title, source_url)  # Save the verified article title
                else:
                    print(f"⚠️  No verified match for: {headline_text[:60]}...")
            
            return jsonify({
                'success': True,
                'game_info': game_info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not extract game info'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/commercial_check')
def check_commercial():
    """Check if stream is currently showing commercials"""
    try:
        from commercial_integration import check_commercial_break
        
        # Will auto-capture main content area
        result = check_commercial_break()
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/smart_commercial_switch', methods=['POST'])
def smart_commercial_switch():
    """Detect commercial and auto-switch to best game"""
    try:
        from smart_commercial_handler import handle_commercial_break
        
        result = handle_commercial_break()
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
        
        # If we have credentials, use official Twitch API
        # (implement later if needed)
        return jsonify([{'headline': 'Twitch API not configured', 'description': 'Set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET'}])
        
    except Exception as e:
        return jsonify([{'headline': 'Error loading streamer feed', 'description': str(e)}])

@app.route('/api/pinned_games', methods=['GET', 'POST', 'DELETE'])
def pinned_games():
    """Manage pinned games"""
    import json
    import os
    
    pinned_file = 'data/pinned_games.json'
    
    # Ensure file exists
    if not os.path.exists(pinned_file):
        with open(pinned_file, 'w') as f:
            json.dump([], f)
    
    if request.method == 'GET':
        with open(pinned_file, 'r') as f:
            return jsonify(json.load(f))
    
    elif request.method == 'POST':
        game = request.json
        with open(pinned_file, 'r') as f:
            pinned = json.load(f)
        
        # Check if already pinned
        if not any(g['id'] == game['id'] for g in pinned):
            pinned.append(game)
            with open(pinned_file, 'w') as f:
                json.dump(pinned, f, indent=2)
        
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        game_id = request.args.get('id')
        with open(pinned_file, 'r') as f:
            pinned = json.load(f)
        
        pinned = [g for g in pinned if g['id'] != game_id]
        
        with open(pinned_file, 'w') as f:
            json.dump(pinned, f, indent=2)
        
        return jsonify({'success': True})

@app.route('/api/games')
def get_games():
    """Get today's games"""
    sport = request.args.get('sport', 'ncaa-basketball')
    
    if sport == 'nhl':
        return get_nhl_games()
    elif sport == 'nba':
        return get_nba_games()
    elif sport == 'mlb':
        return get_mlb_games()
    else:
        return get_ncaa_games()

@app.route('/api/upcoming_games')
def get_upcoming_games():
    """Get upcoming games with predicted excitement"""
    sport = request.args.get('sport', 'nba')
    
    try:
        if sport == 'nba':
            resp = requests.get(f'{ESPN_API}/basketball/nba/scoreboard', timeout=5)
        elif sport == 'nhl':
            resp = requests.get(f'{ESPN_API}/hockey/nhl/scoreboard', timeout=5)
        elif sport == 'mlb':
            resp = requests.get(f'{ESPN_API}/baseball/mlb/scoreboard', timeout=5)
        elif sport == 'ncaa-basketball':
            resp = requests.get(f'{ESPN_API}/basketball/mens-college-basketball/scoreboard', timeout=5)
        else:
            return jsonify([])
        
        data = resp.json()
        upcoming = []
        
        for event in data.get('events', [])[:20]:
            competition = event.get('competitions', [{}])[0]
            status = competition.get('status', {})
            
            # Only show scheduled games (not live or final)
            if status.get('type', {}).get('state') != 'pre':
                continue
            
            competitors = competition.get('competitors', [])
            if len(competitors) < 2:
                continue
            
            away = competitors[0] if competitors[0].get('homeAway') == 'away' else competitors[1]
            home = competitors[1] if competitors[1].get('homeAway') == 'home' else competitors[0]
            
            # Calculate excitement based on team records
            away_record = away.get('records', [{}])[0].get('summary', '0-0') if away.get('records') else '0-0'
            home_record = home.get('records', [{}])[0].get('summary', '0-0') if home.get('records') else '0-0'
            
            # For NCAA, also check rankings
            away_rank = away.get('curatedRank', {}).get('current', 0) if away.get('curatedRank') else 0
            home_rank = home.get('curatedRank', {}).get('current', 0) if home.get('curatedRank') else 0
            
            try:
                away_wins, away_losses = map(int, away_record.split('-')[:2])
                home_wins, home_losses = map(int, home_record.split('-')[:2])
                
                # Win percentage
                away_pct = away_wins / (away_wins + away_losses) if (away_wins + away_losses) > 0 else 0.5
                home_pct = home_wins / (home_wins + home_losses) if (home_wins + home_losses) > 0 else 0.5
                
                # Base excitement: both teams good = high excitement
                quality = (away_pct + home_pct) * 50
                
                # Matchup closeness: evenly matched = more exciting
                closeness = (1 - abs(away_pct - home_pct)) * 30
                
                # Playoff implications: winning teams = higher stakes
                stakes = min(away_wins, home_wins) * 0.5
                
                # Ranking bonus for NCAA (ranked matchups are huge)
                ranking_bonus = 0
                if away_rank > 0 and home_rank > 0:
                    ranking_bonus = 30  # Both ranked = March Madness preview
                elif away_rank > 0 or home_rank > 0:
                    ranking_bonus = 15  # One ranked = upset potential
                
                excitement = int(quality + closeness + stakes + ranking_bonus)
                excitement = min(100, max(20, excitement))
            except:
                excitement = 50
            
            # Format team names with rankings
            away_name = away.get('team', {}).get('displayName', 'TBD')
            home_name = home.get('team', {}).get('displayName', 'TBD')
            if away_rank > 0:
                away_name = f"#{away_rank} {away_name}"
            if home_rank > 0:
                home_name = f"#{home_rank} {home_name}"
            
            upcoming.append({
                'id': event.get('id'),
                'away_team': away_name,
                'home_team': home_name,
                'start_time': status.get('type', {}).get('shortDetail', 'TBD'),
                'excitement': excitement,
                'away_record': away_record,
                'home_record': home_record
            })
        
        # Sort by excitement
        upcoming.sort(key=lambda x: x['excitement'], reverse=True)
        return jsonify(upcoming[:5])
        
    except Exception as e:
        return jsonify([])


@app.route('/api/recent_games')
def get_recent_games():
    """Get recent completed games from multiple sports"""
    sport = request.args.get('sport', 'nba')
    
    try:
        all_recent = []
        
        # Fetch from multiple sports
        sports_apis = [
            ('nba', f'{ESPN_API}/basketball/nba/scoreboard'),
            ('ncaa', f'{ESPN_API}/basketball/mens-college-basketball/scoreboard'),
            ('nhl', f'{ESPN_API}/hockey/nhl/scoreboard'),
            ('mlb', f'{ESPN_API}/baseball/mlb/scoreboard'),
            ('mls', f'{ESPN_API}/soccer/usa.1/scoreboard')
        ]
        
        for sport_name, url in sports_apis:
            try:
                resp = requests.get(url, timeout=3)
                data = resp.json()
                
                for event in data.get('events', [])[:5]:
                    competition = event.get('competitions', [{}])[0]
                    status = competition.get('status', {})
                    
                    # Only show completed games
                    if status.get('type', {}).get('state') != 'post':
                        continue
                    
                    competitors = competition.get('competitors', [])
                    if len(competitors) < 2:
                        continue
                    
                    away = competitors[0] if competitors[0].get('homeAway') == 'away' else competitors[1]
                    home = competitors[1] if competitors[1].get('homeAway') == 'home' else competitors[0]
                    
                    all_recent.append({
                        'id': event.get('id'),
                        'sport': sport_name.upper(),
                        'away_team': away.get('team', {}).get('abbreviation', 'TBD'),
                        'home_team': home.get('team', {}).get('abbreviation', 'TBD'),
                        'away_score': away.get('score', '0'),
                        'home_score': home.get('score', '0')
                    })
            except:
                continue
        
        return jsonify(all_recent[:15])
        
    except Exception as e:
        return jsonify([])


def get_ncaa_games():
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

def get_nba_games():
    """Get NBA games from ESPN API"""
    url = f"{ESPN_API}/basketball/nba/scoreboard"
    
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
                'away': away.get('team', {}).get('abbreviation', ''),
                'home': home.get('team', {}).get('abbreviation', ''),
                'away_score': away.get('score', '0'),
                'home_score': home.get('score', '0'),
                'status': status.get('type', {}).get('shortDetail', ''),
                'clock': status.get('displayClock', '12:00'),
                'state': status.get('type', {}).get('state', '')
            })
        
        return jsonify(games)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_mlb_games():
    """Get MLB games from ESPN API"""
    url = f"{ESPN_API}/baseball/mlb/scoreboard"
    
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
                'away': away.get('team', {}).get('abbreviation', ''),
                'home': home.get('team', {}).get('abbreviation', ''),
                'away_score': away.get('score', '0'),
                'home_score': home.get('score', '0'),
                'status': status.get('type', {}).get('shortDetail', ''),
                'clock': status.get('displayClock', 'Top 1st'),
                'state': status.get('type', {}).get('state', '')
            })
        
        return jsonify(games)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_nhl_games():
    """Get NHL games from ESPN API"""
    url = f"{ESPN_API}/hockey/nhl/scoreboard"
    
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
                'away': away.get('team', {}).get('abbreviation', ''),
                'home': home.get('team', {}).get('abbreviation', ''),
                'away_score': away.get('score', '0'),
                'home_score': home.get('score', '0'),
                'status': status.get('type', {}).get('shortDetail', ''),
                'clock': status.get('displayClock', '20:00'),
                'state': status.get('type', {}).get('state', '')
            })
        
        return jsonify(games)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/<game_id>/stats')
def get_game_stats(game_id):
    """Get detailed stats for a game"""
    sport = request.args.get('sport', 'ncaa-basketball')
    
    if sport == 'nhl':
        return get_nhl_stats(game_id)
    elif sport == 'nba':
        return get_nba_stats(game_id)
    else:
        return get_ncaa_stats(game_id)

def get_nba_stats(game_id):
    """Get NBA game stats from ESPN"""
    url = f"{ESPN_API}/basketball/nba/summary?event={game_id}"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        boxscore = data.get('boxscore', {})
        teams_data = boxscore.get('teams', [])
        players_data = boxscore.get('players', [])
        header = data.get('header', {})
        competitions = header.get('competitions', [{}])[0]
        status = competitions.get('status', {})
        
        result = {
            'game_id': game_id,
            'period': status.get('period', 1),
            'clock': status.get('displayClock', '12:00'),
            'teams': [],
            'top_players': []
        }
        
        for team_data in teams_data:
            team_info = team_data.get('team', {})
            stats_list = team_data.get('statistics', [])
            
            stats_dict = {s.get('name'): s.get('displayValue', '0') for s in stats_list}
            
            result['teams'].append({
                'name': team_info.get('abbreviation', ''),
                'is_home': team_data.get('homeAway') == 'home',
                'fg_pct': stats_dict.get('fieldGoalPct', '0%'),
                'fg_made': stats_dict.get('fieldGoalsMade', '0'),
                'fg_att': stats_dict.get('fieldGoalsAttempted', '0'),
                'three_pct': stats_dict.get('threePointPct', '0%'),
                'three_made': stats_dict.get('threePointFieldGoalsMade', '0'),
                'three_att': stats_dict.get('threePointFieldGoalsAttempted', '0'),
                'turnovers': stats_dict.get('turnovers', '0'),
                'rebounds': stats_dict.get('totalRebounds', '0'),
                'assists': stats_dict.get('assists', '0'),
                'steals': stats_dict.get('steals', '0'),
                'personalFouls': stats_dict.get('fouls', '0')
            })
        
        # Extract top players by minutes
        for team_players in players_data:
            team_abbr = team_players.get('team', {}).get('abbreviation', '')
            stats_categories = team_players.get('statistics', [])
            
            for category in stats_categories:
                athletes = category.get('athletes', [])
                for player in athletes:
                    athlete = player.get('athlete', {})
                    stats = player.get('stats', [])
                    
                    if len(stats) >= 1:
                        minutes = stats[0] if len(stats) > 0 else '0'
                        points = stats[1] if len(stats) > 1 else '0'
                        plus_minus = stats[12] if len(stats) > 12 else '0'
                        jersey = athlete.get('jersey', '')
                        
                        # Convert minutes to seconds for sorting
                        try:
                            if ':' in str(minutes):
                                parts = str(minutes).split(':')
                                min_seconds = int(parts[0]) * 60 + int(parts[1])
                            else:
                                min_seconds = int(float(minutes) * 60)
                        except:
                            min_seconds = 0
                        
                        result['top_players'].append({
                            'name': athlete.get('displayName', ''),
                            'jersey': jersey,
                            'minutes': minutes,
                            'min_seconds': min_seconds,
                            'points': points,
                            'plus_minus': plus_minus,
                            'team': team_abbr
                        })
        
        # Sort by minutes and take top 6
        result['top_players'].sort(key=lambda x: x['min_seconds'], reverse=True)
        result['top_players'] = result['top_players'][:6]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_nhl_stats(game_id):
    """Get NHL game stats from ESPN"""
    url = f"{ESPN_API}/hockey/nhl/summary?event={game_id}"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        boxscore = data.get('boxscore', {})
        teams_data = boxscore.get('teams', [])
        players_data = boxscore.get('players', [])
        on_ice_data = data.get('onIce', [])
        header = data.get('header', {})
        competitions = header.get('competitions', [{}])[0]
        
        result = {
            'game_id': game_id,
            'period': header.get('period', 1),
            'clock': competitions.get('status', {}).get('displayClock', '20:00'),
            'teams': [],
            'top_players': [],
            'on_ice': []
        }
        
        # Build player lookup map with jersey numbers
        player_map = {}
        for team_players in players_data:
            for category in team_players.get('statistics', []):
                for player in category.get('athletes', []):
                    athlete = player.get('athlete', {})
                    player_id = str(athlete.get('id', ''))
                    player_map[player_id] = {
                        'name': athlete.get('displayName', ''),
                        'jersey': athlete.get('jersey', '')
                    }
        
        # Get players currently on ice
        for team_on_ice in on_ice_data:
            team_id = team_on_ice.get('teamId', '')
            entries = team_on_ice.get('entries', [])
            
            # Find team abbreviation
            team_abbr = ''
            for team_data in teams_data:
                if str(team_data.get('team', {}).get('id', '')) == str(team_id):
                    team_abbr = team_data.get('team', {}).get('abbreviation', '')
                    break
            
            players_on_ice = []
            for entry in entries:
                athlete_id = entry.get('athleteid', '')
                player_info = player_map.get(athlete_id, {'name': 'Unknown', 'jersey': ''})
                player_name = player_info['name']
                jersey = player_info['jersey']
                
                # Format as "#24 Player Name" if jersey available
                if jersey:
                    players_on_ice.append(f"#{jersey} {player_name}")
                else:
                    players_on_ice.append(player_name)
            
            result['on_ice'].append({
                'team': team_abbr,
                'players': players_on_ice
            })
        
        for team_data in teams_data:
            team_info = team_data.get('team', {})
            stats_list = team_data.get('statistics', [])
            
            # Extract stats
            stats_dict = {s.get('name'): s.get('displayValue', '0') for s in stats_list}
            
            result['teams'].append({
                'name': team_info.get('abbreviation', ''),
                'is_home': team_data.get('homeAway') == 'home',
                'shots': stats_dict.get('shotsTotal', '0'),
                'blocked_shots': stats_dict.get('blockedShots', '0'),
                'hits': stats_dict.get('hits', '0'),
                'faceoff_pct': stats_dict.get('faceoffPercent', '0') + '%',
                'powerplay': stats_dict.get('powerPlayGoals', '0/0'),
                'penalty_minutes': stats_dict.get('penaltyMinutes', '0')
            })
        
        # Extract top players by ice time
        for team_players in players_data:
            team_abbr = team_players.get('team', {}).get('abbreviation', '')
            stats_categories = team_players.get('statistics', [])
            
            all_players = []
            for category in stats_categories:
                if category.get('type') in ['', None]:  # Skaters only
                    athletes = category.get('athletes', [])
                    for player in athletes:
                        athlete = player.get('athlete', {})
                        stats = player.get('stats', [])
                        
                        if len(stats) >= 18:
                            # Parse stats: [G, A, PTS, +/-, TOI, ...]
                            ice_time = stats[4] if len(stats) > 4 else '0:00'
                            plus_minus = stats[3] if len(stats) > 3 else '0'
                            goals = stats[0] if len(stats) > 0 else '0'
                            
                            # Convert ice time to seconds for sorting
                            try:
                                parts = ice_time.split(':')
                                ice_seconds = int(parts[0]) * 60 + int(parts[1])
                            except:
                                ice_seconds = 0
                            
                            all_players.append({
                                'name': athlete.get('displayName', ''),
                                'ice_time': ice_time,
                                'ice_seconds': ice_seconds,
                                'plus_minus': plus_minus,
                                'goals': goals,
                                'team': team_abbr
                            })
            
            # Sort by ice time and take top 3
            all_players.sort(key=lambda x: x['ice_seconds'], reverse=True)
            result['top_players'].extend(all_players[:3])
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_ncaa_stats(game_id):
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
                'steals': team_stats.get('steals', '0'),
                'personalFouls': team_stats.get('fouls', '0')
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change_channel', methods=['POST'])
def change_channel():
    """Change TV channel via Broadlink IR"""
    try:
        data = request.get_json()
        channel = data.get('channel')
        
        if not channel:
            return jsonify({'success': False, 'error': 'No channel specified'}), 400
        
        # Run channel switcher
        from channel_switcher import change_channel as switch_channel
        switch_channel(int(channel))
        return jsonify({'success': True, 'channel': channel})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/espn_epg')
def get_espn_epg():
    """Get current ESPN programming from EPG"""
    try:
        from epg_parser import fetch_epg, get_current_program, CHANNEL_MAP
        import json
        
        epg = fetch_epg()
        programs = []
        
        # Get current channel
        current_channel = None
        try:
            with open('data/current_channel.json', 'r') as f:
                current_channel = json.load(f).get('channel')
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error reading channel state: {e}")
        
        for channel_num, epg_id in CHANNEL_MAP.items():
            program = get_current_program(epg, epg_id)
            channel_name = epg_id.replace('.us', '').replace('ESPN', 'ESPN ')
            
            if program:
                programs.append({
                    'channel': channel_num,
                    'name': channel_name,
                    'title': program['title'],
                    'description': program['description'],
                    'start': program['start'],
                    'end': program['end'],
                    'is_live': 'ᴸᶦᵛᵉ' in program['title'],
                    'is_current': channel_num == current_channel
                })
        
        return jsonify({'success': True, 'programs': programs, 'current_channel': current_channel})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/save_clip', methods=['POST'])
def save_clip():
    """Save last 5 minutes of video"""
    try:
        import subprocess
        result = subprocess.run(
            ['./venv/bin/python3', '-c', '''
import os, shutil, time
from pathlib import Path
movies = Path.home() / "Movies"
saved = Path("~/apex-exotics/sports-monitor/saved_clips").expanduser()
saved.mkdir(exist_ok=True)

# Get last 60 segments (5 min at 5 sec each)
segments = sorted(movies.glob("*.ts"), key=lambda x: x.stat().st_mtime, reverse=True)[:60]
timestamp = time.strftime("%Y%m%d_%H%M%S")

for i, seg in enumerate(reversed(segments)):
    shutil.copy(seg, saved / f"clip_{timestamp}_{i:03d}.ts")

print(f"{len(segments)},{len(segments)*5/60:.1f}")
'''],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            count, duration = result.stdout.strip().split(',')
            return jsonify({'success': True, 'segments': count, 'duration': duration})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/march_madness')
def march_madness():
    """Get March Madness upset alerts and injury watch"""
    try:
        from march_madness_integration import get_upset_alerts, get_injury_watch_teams
        return jsonify({
            'upsets': get_upset_alerts(),
            'injury_watch': get_injury_watch_teams()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auto_switch_check')
def auto_switch_check():
    """Check if auto-switching should occur"""
    from auto_switcher import check_and_switch
    import json
    
    # Get current channel
    current_channel = None
    try:
        with open('data/current_channel.json', 'r') as f:
            current_channel = json.load(f).get('channel')
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error reading channel state: {e}")
    
    # Check auto-switch setting (default: disabled for safety)
    auto_enabled = request.args.get('enabled', 'false').lower() == 'true'
    
    result = check_and_switch(current_channel, auto_enabled)
    return jsonify(result)


@app.route('/api/upcoming_tip')
def upcoming_tip():
    """Check for upcoming game tips and return channel switch info"""
    from datetime import datetime, timezone, timedelta
    from espn_channels import get_channel
    import requests as req

    try:
        data = req.get(ESPN_API + '/basketball/mens-college-basketball/scoreboard', timeout=10).json()
        now = datetime.now(timezone.utc)
        lead_minutes = int(request.args.get('lead', 3))

        for event in data.get('events', []):
            comp = event['competitions'][0]
            status = comp['status']['type']['name']
            if status != 'STATUS_SCHEDULED':
                continue

            game_time = datetime.fromisoformat(comp['date'].replace('Z', '+00:00'))
            minutes_until = (game_time - now).total_seconds() / 60

            if 0 < minutes_until <= lead_minutes:
                broadcasts = []
                for b in comp.get('broadcasts', []):
                    broadcasts.extend(b.get('names', []))
                network = broadcasts[0] if broadcasts else None
                channel = get_channel(network) if network else None
                teams = [t['team']['shortDisplayName'] for t in comp['competitors']]

                return jsonify({
                    'switch': True,
                    'channel': channel,
                    'network': network,
                    'game': f'{teams[0]} vs {teams[1]}',
                    'minutes_until': round(minutes_until, 1)
                })

        return jsonify({'switch': False})
    except Exception as e:
        return jsonify({'switch': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=True, threaded=True)
