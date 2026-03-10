#!/usr/bin/env python3
"""
Auto-post to Twitter by finding and clicking the compose box
"""
import pyautogui
import pyperclip
import time
from headline_storage import get_unposted_headlines, mark_posted_to_x

pyautogui.FAILSAFE = True

def post_tweet_automated(tweet_text):
    """Post a tweet by clicking current mouse position"""
    
    print(f"📋 Copying tweet to clipboard...")
    pyperclip.copy(tweet_text)
    
    print(f"🖱️  Clicking compose box (wherever your mouse is)...")
    time.sleep(1)
    pyautogui.click()
    time.sleep(0.5)
    
    print(f"⌨️  Pasting tweet...")
    pyautogui.hotkey('command', 'v')
    time.sleep(1)
    
    print(f"🚀 Posting in 2 seconds...")
    time.sleep(2)
    
    # Press Cmd+Enter to post
    pyautogui.hotkey('command', 'return')
    
    print(f"✅ Tweet posted!")
    time.sleep(2)
    
    return True

def post_headline(headline_text, source_url):
    """Post a headline to Twitter"""
    tweet_text = f"{headline_text}\n\n{source_url}"
    
    print(f"\n📰 {headline_text[:60]}...")
    print(f"🔗 {source_url}")
    
    input("\n⏸️  Press ENTER to post (move mouse to corner to abort)...")
    
    if post_tweet_automated(tweet_text):
        mark_posted_to_x(headline_text)
        return True
    return False

def post_unposted_headlines(limit=1):
    """Post unposted headlines"""
    unposted = get_unposted_headlines()
    
    if not unposted:
        print("No unposted headlines")
        return
    
    posted_count = 0
    for headline in unposted[:limit]:
        if headline.get('source_url'):
            if post_headline(headline['text'], headline['source_url']):
                posted_count += 1
        else:
            print(f"⏭️  Skipping (no URL): {headline['text'][:60]}")
    
    print(f"\n📊 Posted {posted_count} of {len(unposted)} unposted headlines")

if __name__ == "__main__":
    import sys
    
    print("🔴 RedZone Auto-Poster v2")
    print("=" * 50)
    print("Will automatically find and click compose box")
    print("Move mouse to corner to abort")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 1
    
    post_unposted_headlines(limit)
