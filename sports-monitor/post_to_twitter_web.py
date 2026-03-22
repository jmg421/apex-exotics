#!/usr/bin/env python3
"""
Post to Twitter using web GraphQL endpoint (no API key needed!)
Requires: auth_token and ct0 (CSRF token) from browser cookies
"""
import requests
import json
import os
from headline_storage import get_unposted_headlines, mark_posted_to_x

# Get these from your browser cookies after logging into x.com
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '2869860b14f8187aad2044056bcd5fb24aadf28c')
CSRF_TOKEN = os.getenv('TWITTER_CSRF_TOKEN', '3bdad6e1d8b3e29fd77be78e0e53d72122dd590112c1d66fdb4c55ecae71c278c1a556699646be8097d9fa1c4f25054410fcc77a0a4d0bfa75bacd95b6dcbec222e97acb5cb079aefc32e71e5e3e19b4')

GRAPHQL_ENDPOINT = "https://x.com/i/api/graphql/SwEFc8z18gL1ahel3VSIow/CreateTweet"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

def post_tweet(text):
    """Post a tweet using Twitter's web GraphQL endpoint"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'x-csrf-token': CSRF_TOKEN,
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-active-user': 'yes',
        'Cookie': f'auth_token={AUTH_TOKEN}; ct0={CSRF_TOKEN}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15',
        'Referer': 'https://x.com/home',
        'Origin': 'https://x.com'
    }
    
    payload = {
        "variables": {
            "tweet_text": text,
            "media": {
                "media_entities": [],
                "possibly_sensitive": False
            },
            "semantic_annotation_ids": [],
            "disallowed_reply_options": None
        },
        "features": {
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        },
        "queryId": "SwEFc8z18gL1ahel3VSIow"
    }
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
            
            # Try to extract tweet ID
            try:
                tweet_id = data['data']['create_tweet']['tweet_results']['result']['rest_id']
            except (KeyError, TypeError):
                try:
                    tweet_id = data['data']['create_tweet']['tweet_results']['result']['legacy']['id_str']
                except (KeyError, TypeError):
                    print("Could not extract tweet ID from response")
                    return None
            
            print(f"✅ Posted successfully!")
            print(f"   Tweet ID: {tweet_id}")
            print(f"   URL: https://x.com/JonIsGold/status/{tweet_id}")
            return tweet_id
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def post_headline(headline_text, source_url):
    """Post a headline to Twitter"""
    tweet_text = f"{headline_text}\n\n{source_url}"
    
    tweet_id = post_tweet(tweet_text)
    
    if tweet_id:
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
            print(f"\n📰 Posting: {headline['text'][:60]}...")
            if post_headline(headline['text'], headline['source_url']):
                posted_count += 1
        else:
            print(f"⏭️  Skipping (no URL): {headline['text'][:60]}")
    
    print(f"\n📊 Posted {posted_count} of {len(unposted)} unposted headlines")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 1
    
    post_unposted_headlines(limit)
