#!/usr/bin/env python3
"""
Find source URLs for headlines by scraping ESPN's Top Headlines
"""
import requests
import re
import subprocess
import json

def get_sport_from_headline(headline):
    """Determine sport from headline keywords"""
    headline_lower = headline.lower()
    
    if any(word in headline_lower for word in ['nfl', 'football', 'quarterback', 'qb', 'super bowl', 'ravens', 'raiders', 'eagles', 'giants', 'crosby', 'likely', 'linderbaum']):
        return 'nfl'
    elif any(word in headline_lower for word in ['nba', 'basketball', 'cavaliers', 'magic', 'nets', 'grizzlies', 'nuggets', 'thunder', 'rockets', 'jokic']):
        return 'nba'
    elif any(word in headline_lower for word in ['ncaa', 'tournament', 'march madness', 'college basketball', 'uconn', 'villanova']):
        return 'mens-college-basketball'
    elif any(word in headline_lower for word in ['mlb', 'baseball', 'judge', 'wbc', 'world baseball classic']):
        return 'mlb'
    elif any(word in headline_lower for word in ['nhl', 'hockey', 'ice']):
        return 'nhl'
    else:
        return None

def get_article_title(url):
    """Fetch actual article title from URL"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            # Extract title from <title> tag or og:title
            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            if title_match:
                title = title_match.group(1).strip()
                # Clean up ESPN suffix
                title = re.sub(r'\s*-\s*ESPN.*$', '', title)
                return title
    except:
        pass
    return None

def scrape_espn_headlines(sport):
    """Scrape ESPN section page for Top Headlines"""
    if not sport:
        section_url = "https://www.espn.com/"
    else:
        section_url = f"https://www.espn.com/{sport}/"
    
    try:
        response = requests.get(section_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            content = response.text
            
            # Find Top Headlines section
            start = content.find('Top Headlines')
            if start > 0:
                section = content[start:start+3000]
                
                # Extract all headline links
                headlines = re.findall(r'<a[^>]*href=\"(/[^/]+/story/_/id/\d+/[^\"]+)\"[^>]*>([^<]+)</a>', section)
                
                return [(f"https://www.espn.com{url}", title.strip()) for url, title in headlines]
        
        return []
    except Exception as e:
        print(f"Error scraping ESPN: {e}")
        return []

def match_headline_with_kiro(headline, candidates):
    """Use kiro-cli to find best matching article"""
    if not candidates:
        return None
    
    # Build prompt with candidates
    candidate_text = "\n".join([f"{i+1}. {title}" for i, (url, title) in enumerate(candidates)])
    
    prompt = f"""Match this headline to the best candidate article:

Headline: {headline}

Candidates:
{candidate_text}

Return ONLY the number (1-{len(candidates)}) of the best match, or 0 if no good match."""
    
    try:
        result = subprocess.run(
            ['timeout', '15', 'kiro-cli', 'chat', '--no-interactive', '--trust-all-tools', prompt],
            capture_output=True,
            text=True,
            cwd='/Users/apple/apex-exotics/sports-monitor'
        )
        
        output = result.stdout.strip()
        # Remove ANSI codes
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        # Extract number from output
        match = re.search(r'\b([0-9]+)\b', output)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(candidates):
                return candidates[idx][0]
        
        return None
    except Exception as e:
        print(f"Error matching with kiro: {e}")
        return None

def verify_headline_match(ocr_headline, article_url):
    """Verify OCR headline matches actual article content"""
    article_title = get_article_title(article_url)
    
    if not article_title:
        return False, None
    
    # Extract key entities (words > 4 chars, excluding common words)
    common = {'with', 'from', 'that', 'this', 'have', 'been', 'will', 'their', 'about', 'after'}
    
    ocr_words = set(w.lower() for w in ocr_headline.split() if len(w) > 4 and w.lower() not in common)
    article_words = set(w.lower() for w in article_title.split() if len(w) > 4 and w.lower() not in common)
    
    # Calculate overlap
    if not ocr_words or not article_words:
        return False, article_title
    
    overlap = len(ocr_words & article_words) / len(ocr_words)
    
    # Need at least 50% key word overlap
    return overlap >= 0.5, article_title

def find_source_url(headline):
    """Find article URL and verify it matches the headline"""
    try:
        # Step 1: Determine sport
        sport = get_sport_from_headline(headline)
        
        # Step 2: Scrape ESPN section
        candidates = scrape_espn_headlines(sport)
        
        if not candidates:
            return None, None
        
        # Step 3: Use kiro-cli to match
        matched_url = match_headline_with_kiro(headline, candidates)
        
        if matched_url:
            # Step 4: Verify the match
            is_match, article_title = verify_headline_match(headline, matched_url)
            
            if is_match:
                return matched_url, article_title
        
        return None, None
        
    except Exception as e:
        print(f"Error finding source: {e}")
        return None, None
