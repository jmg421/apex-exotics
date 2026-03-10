#!/usr/bin/env python3
"""
RedZone Entertainment Scorer - Ranks headlines by entertainment value
"""

def score_headline_entertainment(headline_text):
    """
    Score headline from 0-100 based on entertainment value
    Higher = more entertaining
    """
    score = 50  # Base score
    headline_lower = headline_text.lower()
    
    # HIGH VALUE: Drama, controversy, records
    drama_words = ['disgust', 'slams', 'rips', 'destroys', 'dominates', 'shocking', 'stunning', 'upset']
    controversy_words = ['trade', 'fired', 'benched', 'suspended', 'fined', 'ejected', 'fight']
    record_words = ['record', 'historic', 'first time', 'ties', 'breaks', 'career-high']
    
    for word in drama_words:
        if word in headline_lower:
            score += 15
    
    for word in controversy_words:
        if word in headline_lower:
            score += 12
    
    for word in record_words:
        if word in headline_lower:
            score += 10
    
    # MEDIUM VALUE: Big names, playoffs, championships
    big_names = ['lebron', 'curry', 'mahomes', 'brady', 'judge', 'ohtani', 'messi', 'ronaldo']
    playoff_words = ['playoff', 'championship', 'finals', 'super bowl', 'world series']
    
    for name in big_names:
        if name in headline_lower:
            score += 8
    
    for word in playoff_words:
        if word in headline_lower:
            score += 7
    
    # BONUS: Numbers (scores, stats)
    import re
    if re.search(r'\d+-\d+', headline_text):  # Score like "129-126"
        score += 5
    
    # PENALTY: Boring words
    boring_words = ['practice', 'injury report', 'preview', 'schedule', 'roster move']
    for word in boring_words:
        if word in headline_lower:
            score -= 20
    
    # PENALTY: Too long (attention span = -5 seconds)
    if len(headline_text) > 100:
        score -= 10
    
    # BONUS: Short and punchy
    if len(headline_text) < 60:
        score += 5
    
    return min(100, max(0, score))  # Clamp to 0-100

def rank_headlines(headlines):
    """
    Rank headlines by entertainment value
    Returns list of (score, headline) tuples, sorted by score
    """
    scored = []
    for h in headlines:
        score = score_headline_entertainment(h['text'])
        scored.append((score, h))
    
    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])
    
    return scored
