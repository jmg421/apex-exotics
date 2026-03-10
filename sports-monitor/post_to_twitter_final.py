#!/usr/bin/env python3
"""
Auto-post to Twitter using AppleScript (works on macOS!)
"""
import subprocess
import time
from headline_storage import get_unposted_headlines, mark_posted_to_x

posted_urls = set()

def post_tweet_automated(tweet_text):
    """Post a tweet using AppleScript"""
    
    # Copy to clipboard
    subprocess.run(['pbcopy'], input=tweet_text.encode(), check=True)
    print(f"📋 Copied to clipboard")
    
    # Paste
    print(f"⌨️  Pasting...")
    subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'])
    time.sleep(1)
    
    # Post with Cmd+Enter
    print(f"🚀 Posting with Cmd+Enter...")
    subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke return using command down'])
    time.sleep(2)
    
    # Tab to reset cursor to compose box
    print(f"⌨️  Tab to reset cursor...")
    subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke tab'])
    time.sleep(0.5)
    
    print(f"✅ Posted and ready for next tweet!")
    return True

def post_headline(headline_text, source_url):
    """Post a headline to Twitter"""
    # Skip if URL already posted
    if source_url in posted_urls:
        print(f"⏭️  Skipping (duplicate URL): {headline_text[:60]}")
        return False
    
    tweet_text = f"{headline_text}\n\n{source_url}"
    
    print(f"\n📰 {headline_text}")
    print(f"🔗 {source_url}")
    print(f"⏳ Posting in 2 seconds...")
    time.sleep(2)
    
    if post_tweet_automated(tweet_text):
        mark_posted_to_x(headline_text)
        posted_urls.add(source_url)
        return True
    return False

def post_unposted_headlines(limit=1):
    """Post unposted headlines"""
    unposted = get_unposted_headlines()
    
    if not unposted:
        print("No unposted headlines")
        return
    
    # Reverse to get newest first
    unposted = list(reversed(unposted))
    
    posted_count = 0
    for headline in unposted[:limit*3]:  # Check more headlines to find ones with URLs
        if headline.get('source_url') and 'story' in headline['source_url']:
            if post_headline(headline['text'], headline['source_url']):
                posted_count += 1
                if posted_count >= limit:
                    break
                if posted_count < limit:
                    print("\n⏳ Waiting 5 seconds before next tweet...")
                    time.sleep(5)
        else:
            print(f"⏭️  Skipping (no deep link): {headline['text'][:60]}")
    
    print(f"\n📊 Posted {posted_count} of {len(unposted)} unposted headlines")

if __name__ == "__main__":
    import sys
    
    print("🔴 RedZone Auto-Poster (AppleScript)")
    print("=" * 50)
    print("Make sure:")
    print("  1. x.com is open in Safari/Chrome")
    print("  2. Cursor is blinking in compose box")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 1
    
    post_unposted_headlines(limit)
