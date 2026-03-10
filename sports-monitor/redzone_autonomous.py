#!/usr/bin/env python3
"""
RedZone Autonomous Bot - Runs continuously, auto-posts breaking sports news
Posts the MOST ENTERTAINING headline every 5 minutes
"""
import subprocess
import time
import requests
from datetime import datetime
from entertainment_scorer import rank_headlines

DASHBOARD_URL = "http://localhost:5001"
CHECK_INTERVAL = 30  # Check for new headlines every 30 seconds
POST_INTERVAL = 300  # Post best headline every 5 minutes (300 seconds)
MAX_POSTS_PER_HOUR = 12  # 60min / 5min = 12 posts max

last_posted_time = 0
posted_headlines = set()
posts_this_hour = []

def post_tweet(tweet_text):
    """Post a tweet using AppleScript"""
    try:
        subprocess.run(['pbcopy'], input=tweet_text.encode(), check=True)
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'])
        time.sleep(1)
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke return using command down'])
        time.sleep(2)
        # Compose box should auto-clear and be ready for next tweet
        return True
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return False

def should_post_headline(headline_text, source_url):
    """Decide if headline is worth posting"""
    global posts_this_hour
    
    # Clean up old posts from tracking
    current_time = time.time()
    posts_this_hour = [t for t in posts_this_hour if current_time - t < 3600]
    
    # Check hourly limit
    if len(posts_this_hour) >= MAX_POSTS_PER_HOUR:
        return False
    
    # Skip if already posted
    if headline_text in posted_headlines:
        return False
    
    # Skip if no good URL (must have 'story' for deep link)
    if not source_url or 'story' not in source_url:
        return False
    
    # Skip if too soon after last post
    global last_posted_time
    if current_time - last_posted_time < MIN_POST_INTERVAL:
        return False
    
    # Skip if headline is too generic or preview
    generic_terms = ['tonight', 'today', 'tomorrow', 'upcoming', 'preview', 'vs', 'face', 'meet']
    if any(term in headline_text.lower() for term in generic_terms):
        return False
    
    return True

def check_and_post():
    """Check for new headlines and post if worthy"""
    global last_posted_time
    
    try:
        # Get unposted headlines
        response = requests.get(f"{DASHBOARD_URL}/api/headlines/unposted", timeout=5)
        headlines = response.json()
        
        for headline in headlines:
            text = headline.get('text', '')
            url = headline.get('source_url', '')
            
            if should_post_headline(text, url):
                tweet = f"{text}\n\n{url}"
                
                print(f"\n🔴 [{datetime.now().strftime('%H:%M:%S')}] Posting:")
                print(f"   {text[:60]}...")
                
                if post_tweet(tweet):
                    print(f"   ✅ Posted!")
                    posted_headlines.add(text)
                    last_posted_time = time.time()
                    posts_this_hour.append(time.time())
                    
                    # Mark as posted in database
                    requests.post(f"{DASHBOARD_URL}/api/headlines/mark_posted", 
                                json={'headline': text})
                    
                    # Show rate limit status
                    remaining = MAX_POSTS_PER_HOUR - len(posts_this_hour)
                    print(f"   📊 {remaining} posts remaining this hour")
                    
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run autonomous bot"""
    import sys
    test_mode = '--test' in sys.argv
    
    if test_mode:
        print("🧪 RedZone Bot - TEST MODE (no actual posting)")
    else:
        print("🔴 RedZone Autonomous Bot Starting...")
    
    print("=" * 60)
    print(f"Checking for headlines every {CHECK_INTERVAL} seconds")
    print(f"Minimum {MIN_POST_INTERVAL//60} minutes between posts")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    if not test_mode:
        print("⚠️  IMPORTANT: Open x.com and press Cmd+N to open compose box")
        print("   The bot will auto-post when it finds worthy headlines")
        input("\nPress ENTER when ready...")
    else:
        print("Test mode - will show what would be posted\n")
    
    cycle = 0
    while True:
        cycle += 1
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"[{timestamp}] Cycle {cycle}: Checking for headlines...")
        
        if test_mode:
            posted = check_and_post_test()
        else:
            posted = check_and_post()
        
        if not posted:
            print(f"   No worthy headlines to post")
        
        print(f"   Waiting {CHECK_INTERVAL}s...\n")
        time.sleep(CHECK_INTERVAL)

def check_and_post_test():
    """Test mode - show what would be posted without posting"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/headlines/unposted", timeout=5)
        headlines = response.json()
        
        for headline in headlines:
            text = headline.get('text', '')
            url = headline.get('source_url', '')
            
            if should_post_headline(text, url):
                print(f"\n   ✅ WOULD POST:")
                print(f"      {text}")
                print(f"      {url}")
                posted_headlines.add(text)
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 RedZone Bot Stopped")
        print(f"Posted {len(posted_headlines)} headlines total")
