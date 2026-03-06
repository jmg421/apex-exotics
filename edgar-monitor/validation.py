#!/usr/bin/env python3
"""
Validation framework for ENIS + LLM recommendations.
Measures hit rate, alpha generation, and prompt effectiveness.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def load_reports():
    """Load all LLM analysis reports."""
    reports_file = Path(__file__).parent / 'data' / 'llm_reports.json'
    if not reports_file.exists():
        return {}
    
    with open(reports_file) as f:
        return json.load(f)

def load_historical_prices():
    """Load historical price data from cache or mock."""
    cache_file = Path(__file__).parent / 'data' / 'price_cache.json'
    
    # Try to load from cache
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                cache = json.load(f)
            
            # Convert ticker-based cache to CIK-based
            scores_file = Path(__file__).parent / 'data' / 'enis_scores.json'
            if scores_file.exists():
                with open(scores_file) as f:
                    scores = json.load(f)
                
                prices_by_cik = {}
                for company in scores:
                    ticker = company.get('ticker')
                    cik = company.get('cik')
                    if ticker in cache and cik:
                        prices_by_cik[cik] = cache[ticker].get('prices', {})
                
                if prices_by_cik:
                    return prices_by_cik
        except:
            pass
    
    # Fallback to mock data
    return {
        '0001822523': {  # AFCG
            '2026-03-06': 10.0,
            '2026-04-06': 8.5,  # -15% (correct short)
            '2026-05-06': 7.0,  # -30% (correct short)
        },
        '0001279704': {  # CLRB
            '2026-03-06': 5.0,
            '2026-04-06': 5.2,  # +4%
            '2026-05-06': 4.8,  # -4%
        }
    }

def calculate_return(cik, start_date, end_date, prices):
    """Calculate return for a CIK between two dates."""
    if cik not in prices:
        return None
    
    if start_date not in prices[cik] or end_date not in prices[cik]:
        return None
    
    start_price = prices[cik][start_date]
    end_price = prices[cik][end_date]
    
    return (end_price - start_price) / start_price

def calculate_hit_rate(reports, prices, horizon_days=30):
    """Calculate hit rate: % of correct recommendations."""
    results = {
        'total': 0,
        'correct': 0,
        'by_type': defaultdict(lambda: {'total': 0, 'correct': 0}),
        'by_conviction': defaultdict(lambda: {'total': 0, 'correct': 0})
    }
    
    for cik, report in reports.items():
        rec = report.get('recommendation', '').upper()
        conviction = report.get('conviction', 'UNKNOWN').upper()
        analysis_date = report.get('analysis_date', '').split('T')[0]
        
        if not analysis_date or rec not in ['BUY', 'SHORT', 'AVOID']:
            continue
        
        # Calculate future date
        try:
            start = datetime.fromisoformat(analysis_date)
            end = start + timedelta(days=horizon_days)
            end_date = end.strftime('%Y-%m-%d')
        except:
            continue
        
        ret = calculate_return(cik, analysis_date, end_date, prices)
        if ret is None:
            continue
        
        results['total'] += 1
        
        # Check if recommendation was correct
        correct = False
        if rec == 'BUY' and ret > 0:
            correct = True
        elif rec in ['SHORT', 'AVOID'] and ret < 0:
            correct = True
        
        if correct:
            results['correct'] += 1
        
        # Track by type
        results['by_type'][rec]['total'] += 1
        if correct:
            results['by_type'][rec]['correct'] += 1
        
        # Track by conviction
        results['by_conviction'][conviction]['total'] += 1
        if correct:
            results['by_conviction'][conviction]['correct'] += 1
    
    # Calculate percentages
    if results['total'] > 0:
        results['hit_rate'] = results['correct'] / results['total']
    else:
        results['hit_rate'] = 0.0
    
    for rec_type in results['by_type']:
        total = results['by_type'][rec_type]['total']
        if total > 0:
            results['by_type'][rec_type]['hit_rate'] = \
                results['by_type'][rec_type]['correct'] / total
    
    for conviction in results['by_conviction']:
        total = results['by_conviction'][conviction]['total']
        if total > 0:
            results['by_conviction'][conviction]['hit_rate'] = \
                results['by_conviction'][conviction]['correct'] / total
    
    return results

def calculate_alpha(reports, prices, sp500_return=0.08, horizon_days=30):
    """Calculate alpha vs S&P 500."""
    portfolio_returns = []
    
    for cik, report in reports.items():
        rec = report.get('recommendation', '').upper()
        analysis_date = report.get('analysis_date', '').split('T')[0]
        
        if not analysis_date or rec not in ['BUY', 'SHORT', 'AVOID']:
            continue
        
        try:
            start = datetime.fromisoformat(analysis_date)
            end = start + timedelta(days=horizon_days)
            end_date = end.strftime('%Y-%m-%d')
        except:
            continue
        
        ret = calculate_return(cik, analysis_date, end_date, prices)
        if ret is None:
            continue
        
        # Adjust for short positions
        if rec in ['SHORT', 'AVOID']:
            ret = -ret
        
        portfolio_returns.append(ret)
    
    if not portfolio_returns:
        return None
    
    avg_return = sum(portfolio_returns) / len(portfolio_returns)
    alpha = avg_return - (sp500_return * horizon_days / 365)
    
    return {
        'portfolio_return': avg_return,
        'sp500_return': sp500_return * horizon_days / 365,
        'alpha': alpha,
        'num_positions': len(portfolio_returns)
    }

def analyze_prompt_effectiveness(reports):
    """Analyze which analysis types perform best."""
    by_type = defaultdict(lambda: {
        'count': 0,
        'recommendations': defaultdict(int),
        'avg_conviction': []
    })
    
    for report in reports.values():
        analysis_type = report.get('analysis_type', 'unknown')
        rec = report.get('recommendation', 'UNKNOWN')
        conviction = report.get('conviction', '')
        
        by_type[analysis_type]['count'] += 1
        by_type[analysis_type]['recommendations'][rec] += 1
        
        # Map conviction to numeric
        conv_map = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        if conviction.upper() in conv_map:
            by_type[analysis_type]['avg_conviction'].append(
                conv_map[conviction.upper()]
            )
    
    # Calculate averages
    for analysis_type in by_type:
        convictions = by_type[analysis_type]['avg_conviction']
        if convictions:
            by_type[analysis_type]['avg_conviction'] = sum(convictions) / len(convictions)
        else:
            by_type[analysis_type]['avg_conviction'] = 0
    
    return dict(by_type)

def generate_validation_report():
    """Generate full validation report."""
    reports = load_reports()
    prices = load_historical_prices()
    
    print("="*60)
    print("ENIS + LLM Validation Report")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Reports: {len(reports)}")
    print()
    
    # Hit rate analysis
    print("Hit Rate Analysis (30-day horizon)")
    print("-"*60)
    hit_rate = calculate_hit_rate(reports, prices)
    print(f"Overall Hit Rate: {hit_rate['hit_rate']:.1%} ({hit_rate['correct']}/{hit_rate['total']})")
    print()
    
    if hit_rate['by_type']:
        print("By Recommendation Type:")
        for rec_type, stats in hit_rate['by_type'].items():
            hr = stats.get('hit_rate', 0)
            print(f"  {rec_type}: {hr:.1%} ({stats['correct']}/{stats['total']})")
        print()
    
    if hit_rate['by_conviction']:
        print("By Conviction Level:")
        for conviction, stats in hit_rate['by_conviction'].items():
            hr = stats.get('hit_rate', 0)
            print(f"  {conviction}: {hr:.1%} ({stats['correct']}/{stats['total']})")
        print()
    
    # Alpha analysis
    print("Alpha Analysis")
    print("-"*60)
    alpha = calculate_alpha(reports, prices)
    if alpha:
        print(f"Portfolio Return: {alpha['portfolio_return']:.1%}")
        print(f"S&P 500 Return: {alpha['sp500_return']:.1%}")
        print(f"Alpha: {alpha['alpha']:.1%}")
        print(f"Positions: {alpha['num_positions']}")
    else:
        print("Insufficient data for alpha calculation")
    print()
    
    # Prompt effectiveness
    print("Prompt Effectiveness")
    print("-"*60)
    prompt_stats = analyze_prompt_effectiveness(reports)
    for analysis_type, stats in prompt_stats.items():
        print(f"{analysis_type}:")
        print(f"  Count: {stats['count']}")
        print(f"  Avg Conviction: {stats['avg_conviction']:.1f}/3")
        print(f"  Recommendations: {dict(stats['recommendations'])}")
        print()

if __name__ == '__main__':
    generate_validation_report()
