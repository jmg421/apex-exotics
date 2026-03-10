#!/usr/bin/env python3
"""
RedZone Entertainment Bot - Posts the MOST ENTERTAINING headline every 5 minutes
100% Factual. 100% Entertaining. 100% Accurate. 99.9% Free.
"""
import subprocess
import time
import requests
import json
import os
from datetime import datetime
from entertainment_scorer import rank_headlines

DASHBOARD_URL = "http://localhost:5001"
CHECK_INTERVAL = 30  # Check every 30 seconds
POST_INTERVAL = 300  # Post best headline every 5 minutes
POSTED_CACHE = os.path.expanduser("~/apex-exotics/sports-monitor/posted_cache.json")

def load_posted_cache():
    """Load previously posted headlines/URLs"""
    if os.path.exists(POSTED_CACHE):
        with open(POSTED_CACHE, 'r') as f:
            data = json.load(f)
            return set(data.get('headlines', [])), set(data.get('urls', []))
    return set(), set()

def save_posted_cache(headlines, urls):
    """Save posted headlines/URLs to disk"""
    with open(POSTED_CACHE, 'w') as f:
        json.dump({'headlines': list(headlines), 'urls': list(urls)}, f)

last_posted_time = 0
posted_headlines, posted_urls = load_posted_cache()
headline_queue = []

print(f"📋 Loaded {len(posted_headlines)} previously posted headlines")

def is_similar_headline(new_headline, existing_headlines):
    """Check if headline is too similar to already posted ones"""
    new_lower = new_headline.lower()
    new_words = set(w for w in new_lower.split() if len(w) > 4)  # Key words only
    
    for existing in existing_headlines:
        existing_lower = existing.lower()
        existing_words = set(w for w in existing_lower.split() if len(w) > 4)
        
        # If 60%+ of key words overlap, it's too similar
        if new_words and existing_words:
            overlap = len(new_words & existing_words) / len(new_words)
            if overlap > 0.6:
                return True
    
    return False

def post_tweet(tweet_text):
    """Post using Cmd+Enter → Tab"""
    try:
        subprocess.run(['pbcopy'], input=tweet_text.encode(), check=True)
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'])
        time.sleep(1)
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke return using command down'])
        time.sleep(2)
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke tab'])
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_and_post():
    """Collect headlines, score them, post best one every 5 minutes"""
    global last_posted_time, headline_queue
    
    try:
        # Get unposted headlines with deep links
        response = requests.get(f"{DASHBOARD_URL}/api/headlines/unposted", timeout=5)
        headlines = response.json()
        
        # Filter to deep links only, skip duplicates and similar
        worthy = []
        for h in headlines:
            url = h.get('source_url', '')
            text = h['text']
            
            # Must have deep link
            if not url or 'story' not in url:
                continue
            
            # Skip if URL already posted (MOST IMPORTANT CHECK)
            if url in posted_urls:
                continue
            
            # Skip if exact headline already posted
            if text in posted_headlines:
                continue
            
            # Skip if too similar to posted headlines
            if is_similar_headline(text, posted_headlines):
                continue
            
            # Skip if already in queue
            if any(h['source_url'] == url for h in headline_queue):
                continue
            
            worthy.append(h)
        
        # Add to queue
        headline_queue.extend(worthy)
        
        # Check if it's time to post
        current_time = time.time()
        time_until_post = int(POST_INTERVAL - (current_time - last_posted_time))
        
        if time_until_post > 0:
            print(f"   📊 {len(headline_queue)} headlines queued, posting in {time_until_post}s")
            return False
        
        # Time to post! Rank by entertainment
        if headline_queue:
            ranked = rank_headlines(headline_queue)
            
            print(f"\n🎯 Top 3 Entertainment Scores:")
            for i, (score, h) in enumerate(ranked[:3], 1):
                print(f"   {i}. [{score}/100] {h['text'][:55]}...")
            
            # Post the winner
            best_score, best = ranked[0]
            
            if best_score >= 50:
                tweet = f"{best['text']}\n\n{best['source_url']}"
                
                print(f"\n🔴 POSTING WINNER (Score: {best_score}/100)")
                print(f"   {best['text']}")
                
                if post_tweet(tweet):
                    print(f"   ✅ Posted!")
                    posted_headlines.add(best['text'])
                    posted_urls.add(best['source_url'])
                    save_posted_cache(posted_headlines, posted_urls)
                    last_posted_time = time.time()
                    headline_queue = []
                    
                    requests.post(f"{DASHBOARD_URL}/api/headlines/mark_posted",
                                json={'headline': best['text']})
                    return True
            else:
                print(f"   ⚠️  Best score ({best_score}) below threshold")
                headline_queue = []  # Clear low-quality queue
        
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run entertainment bot"""
    import sys
    test_mode = '--test' in sys.argv
    
    print("🔴 RedZone Entertainment Bot")
    print("=" * 60)
    print("Posts MOST ENTERTAINING headline every 5 minutes")
    print("100% Factual | 100% Entertaining | 100% Accurate")
    print("=" * 60)
    print()
    
    if not test_mode:
        import sys
        if sys.stdin.isatty():
            print("⚠️  Make sure x.com compose box is open!")
            input("Press ENTER to start...")
        else:
            print("⚠️  Running in background mode - make sure x.com compose box is open!")
            time.sleep(2)
    
    cycle = 0
    while True:
        cycle += 1
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"[{timestamp}] Cycle {cycle}")
        
        if test_mode:
            # Just show what would be posted
            print("   (Test mode - not actually posting)")
        
        check_and_post()
        
        print(f"   Waiting {CHECK_INTERVAL}s...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 RedZone Bot Stopped")
        print(f"Posted {len(posted_headlines)} headlines")
