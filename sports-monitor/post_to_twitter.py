#!/usr/bin/env python3
"""
Twitter/X posting for @JonIsGold
Requires: pip install tweepy
"""
import tweepy
import os
from headline_storage import get_unposted_headlines, mark_posted_to_x

# Twitter API credentials (set these as environment variables)
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

def init_twitter_client():
    """Initialize Twitter API client using OAuth 1.0a"""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        raise Exception("Twitter credentials not set. Set environment variables: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")
    
    # Use OAuth 1.0a authentication
    auth = tweepy.OAuth1UserHandler(
        API_KEY, API_SECRET,
        ACCESS_TOKEN, ACCESS_SECRET
    )
    
    api = tweepy.API(auth)
    
    return api

def format_tweet(headline, source_url):
    """Format headline and URL into tweet"""
    # Twitter allows 280 chars, URLs count as 23 chars
    max_headline_length = 280 - 23 - 3  # 3 for newline and space
    
    if len(headline) > max_headline_length:
        headline = headline[:max_headline_length-3] + "..."
    
    tweet = f"{headline}\n\n{source_url}"
    return tweet

def post_headline(headline_text, source_url):
    """Post a single headline to Twitter using v1.1 API"""
    try:
        api = init_twitter_client()
        tweet = format_tweet(headline_text, source_url)
        
        # Try v1.1 statuses/update endpoint directly
        response = api.update_status(status=tweet)
        
        print(f"✅ Posted: {headline_text}")
        print(f"   Tweet ID: {response.id}")
        print(f"   URL: https://twitter.com/user/status/{response.id}")
        
        # Mark as posted
        mark_posted_to_x(headline_text)
        
        return True
    except Exception as e:
        print(f"❌ Error posting: {e}")
        import traceback
        traceback.print_exc()
        return False

def post_unposted_headlines(limit=1):
    """Post unposted headlines (default: 1 at a time)"""
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
            print(f"⏭️  Skipping (no URL): {headline['text']}")
    
    print(f"\n📊 Posted {posted_count} of {len(unposted)} unposted headlines")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 1
    
    post_unposted_headlines(limit)
