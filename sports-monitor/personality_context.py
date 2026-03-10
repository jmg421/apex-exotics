#!/usr/bin/env python3
"""
Sports personality Twitter feeds for context
"""

# Map of personalities to their Twitter handles
PERSONALITIES = {
    'stephen a': 'stephenasmith',
    'stephen a smith': 'stephenasmith',
    'shaq': 'SHAQ',
    'shaquille': 'SHAQ',
    'charles barkley': 'NBAonTNT',
    'skip bayless': 'RealSkipBayless',
    'shannon sharpe': 'ShannonSharpe',
    'lebron': 'KingJames',
    'kd': 'KDTrey5',
    'kevin durant': 'KDTrey5',
    'giannis': 'Giannis_An34',
    'steph curry': 'StephenCurry30',
    'patrick mahomes': 'PatrickMahomes',
    'tom brady': 'TomBrady',
}

def get_personality_handle(headline_text):
    """Extract personality Twitter handle from headline"""
    headline_lower = headline_text.lower()
    
    for name, handle in PERSONALITIES.items():
        if name in headline_lower:
            return handle, name.title()
    
    return None, None

def get_recent_tweet_context(handle, topic_keywords):
    """
    Get recent tweet from personality about the topic
    For now, returns a placeholder - would need Twitter API or scraping
    """
    # TODO: Implement Twitter API call or web scraping
    # For now, just return the handle so we can tag them
    return f"@{handle}"

def enhance_headline_with_context(headline_text, source_url):
    """Add personality context to headline if relevant"""
    handle, name = get_personality_handle(headline_text)
    
    if handle:
        # Add the personality's handle for engagement
        return f"{headline_text}\n\n{source_url}\n\n(via @{handle})"
    
    return f"{headline_text}\n\n{source_url}"
