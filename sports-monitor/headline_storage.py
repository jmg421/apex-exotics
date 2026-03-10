import json
import os
from datetime import datetime

HEADLINES_FILE = os.path.expanduser('~/apex-exotics/sports-monitor/headlines.json')

def save_headline(headline, source_url=None):
    """Save a headline with timestamp and optional source URL"""
    headlines = load_headlines()
    
    # Check for duplicates
    for h in headlines:
        if h['text'].lower() == headline.lower():
            return False
    
    headlines.append({
        'text': headline,
        'timestamp': datetime.now().isoformat(),
        'source': 'ESPN Lower Third',
        'source_url': source_url,
        'posted_to_x': False
    })
    
    with open(HEADLINES_FILE, 'w') as f:
        json.dump(headlines, f, indent=2)
    
    return True

def mark_posted_to_x(headline_text):
    """Mark a headline as posted to X"""
    headlines = load_headlines()
    
    for h in headlines:
        if h['text'] == headline_text:
            h['posted_to_x'] = True
            break
    
    with open(HEADLINES_FILE, 'w') as f:
        json.dump(headlines, f, indent=2)

def load_headlines():
    """Load all headlines"""
    if not os.path.exists(HEADLINES_FILE):
        return []
    
    try:
        with open(HEADLINES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def get_recent_headlines(limit=50):
    """Get most recent headlines"""
    headlines = load_headlines()
    return headlines[-limit:][::-1]  # Most recent first

def get_unposted_headlines():
    """Get headlines not yet posted to X"""
    headlines = load_headlines()
    return [h for h in headlines if not h.get('posted_to_x', False)]
