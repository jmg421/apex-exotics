#!/usr/bin/env python3
"""
Personalized news feed based on user interests
"""

USER_INTERESTS = {
    'content_creators': ['steak', 'ishowspeed', 'kaicenat', 'xqc', 'pokimane', 'hasanabi'],
    'topics': [
        'viral videos',
        'youtube trends',
        'twitch drama',
        'gaming news',
        'content creator collabs',
        'irl streams',
        'challenge videos'
    ],
    'sports': ['nfl', 'nba', 'nhl', 'ncaa basketball'],
    'age_demo': 'gen_z_millennial'  # High-energy, viral content
}

def get_personalized_prompt():
    """Generate a prompt for personalized news"""
    creators = ', '.join(USER_INTERESTS['content_creators'])
    topics = ', '.join(USER_INTERESTS['topics'])
    
    return f"""Generate 5-7 brief news items that would interest someone who follows: {creators}

Focus on:
- {topics}
- Recent viral moments or controversies
- Upcoming streams/collabs
- Gaming/sports crossover content

Format as: Headline - Brief description (1 sentence max)"""

def get_feed_sources():
    """Get relevant RSS/API sources for personalized feed"""
    return {
        'youtube_trending': 'https://www.youtube.com/feed/trending',
        'reddit_livestreamfail': 'https://www.reddit.com/r/LivestreamFail/.json',
        'reddit_youtube': 'https://www.reddit.com/r/youtube/.json',
        'esports': 'https://www.espn.com/esports/'
    }
