#!/usr/bin/env python3
"""
Streamer profiles with bio and social media info
"""

STREAMER_PROFILES = {
    'stake': {
        'name': 'Steak (Ebenezer Jonathan Crait)',
        'bio': '17-year-old YouTuber from Utah. High-energy daily vlogs, challenges, and streams. Brother of Cruz',
        'youtube': '@steak',
        'instagram': None,
        'twitter': None,
        'twitch': 'stake'
    },
    'xqc': {
        'name': 'xQc (Félix Lengyel)',
        'bio': 'Former Overwatch pro, variety streamer. One of the biggest streamers on Twitch',
        'youtube': '@xQcOW',
        'instagram': '@xqcow1',
        'twitter': '@xQc'
    },
    'kaicenat': {
        'name': 'Kai Cenat',
        'bio': 'Comedy/variety streamer, 2023 Streamer of the Year. Known for viral IRL content and celebrity collabs',
        'youtube': '@KaiCenat',
        'instagram': '@kaicenat',
        'twitter': '@KaiCenat'
    },
    'pokimane': {
        'name': 'Pokimane (Imane Anys)',
        'bio': 'Variety streamer and content creator. Co-founder of OfflineTV',
        'youtube': '@pokimane',
        'instagram': '@pokimanelol',
        'twitter': '@pokimanelol'
    },
    'hasanabi': {
        'name': 'HasanAbi (Hasan Piker)',
        'bio': 'Political commentator and variety streamer. Known for news/politics content',
        'youtube': '@HasanAbi',
        'instagram': '@hasandpiker',
        'twitter': '@hasanthehun'
    },
    'ishowspeed': {
        'name': 'IShowSpeed (Darren Watkins Jr.)',
        'bio': 'High-energy gaming/IRL streamer. Known for FIFA, Fortnite, and viral reactions',
        'youtube': '@IShowSpeed',
        'instagram': '@ishowspeed',
        'twitter': '@ishowspeedsui'
    }
}

def get_profile(username):
    """Get streamer profile by username"""
    return STREAMER_PROFILES.get(username.lower())
