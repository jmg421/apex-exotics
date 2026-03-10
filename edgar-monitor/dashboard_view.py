#!/usr/bin/env python3
"""Market Dashboard - Combined view of stocks + futures patterns"""
import json
from datetime import datetime

def load_latest(filename):
    """Load latest analysis"""
    try:
        with open(f'data/{filename}', 'r') as f:
            return json.load(f)
    except:
        return None

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

if __name__ == '__main__':
    print("📊 APEX EXOTICS MARKET DASHBOARD")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    
    # Stocks
    print_section("🏢 MICRO-CAP STOCKS")
    
    stock_patterns = load_latest('pattern_detection.json')
    if stock_patterns:
        print(f"Total: {stock_patterns['total_stocks']} stocks")
        print(f"Anomalies: {len(stock_patterns['anomalies'])}")
        print(f"Clusters: {len(stock_patterns['clusters'])}")
        
        print("\n🔥 Top Stock Anomalies:")
        for a in sorted(stock_patterns['anomalies'], 
                       key=lambda x: abs(x['change_percent']), reverse=True)[:3]:
            print(f"  {a['symbol']:6} ${a['price']:7.2f} {a['change_percent']:+6.2f}% | Vol: {a['volume']:,}")
    
    # Futures
    print_section("📈 CME FUTURES")
    
    futures_analysis = load_latest('futures_analysis.json')
    if futures_analysis:
        print(f"Anomalies: {len(futures_analysis['anomalies'])}")
        print(f"Clusters: {len(futures_analysis['clusters'])}")
        
        print("\n🔥 Futures Anomalies:")
        for a in futures_analysis['anomalies']:
            print(f"  {a['symbol']:6} ${a['price']:8.2f} {a['change_percent']:+6.2f}% | Vol: {a['volume']:,}")
        
        if 'jarvis_analysis' in futures_analysis:
            response = futures_analysis['jarvis_analysis'].get('response', '')
            if response:
                # Extract key recommendations
                lines = response.split('\n')
                print("\n🎯 Jarvis Recommendations:")
                in_table = False
                for line in lines:
                    if '| Contract |' in line or '|-------' in line:
                        in_table = True
                        continue
                    if in_table and line.strip().startswith('|'):
                        print(f"  {line.strip()}")
                    if in_table and not line.strip().startswith('|'):
                        break
    
    # Combined insights
    print_section("💡 COMBINED INSIGHTS")
    
    stock_jarvis = load_latest('jarvis_analysis.json')
    if stock_jarvis and 'anthropic' in stock_jarvis:
        response = stock_jarvis['anthropic']
        if isinstance(response, str):
            # Extract priority targets
            if 'Priority targets' in response:
                print("\n📌 Stock Priority Targets:")
                lines = response.split('\n')
                for i, line in enumerate(lines):
                    if 'Priority targets' in line:
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip().startswith(('1.', '2.', '3.')):
                                print(f"  {lines[j].strip()}")
    
    print("\n" + "="*60)
    print("📁 Data files:")
    print("  • data/pattern_detection.json - Stock patterns")
    print("  • data/futures_analysis.json - Futures analysis")
    print("  • data/jarvis_analysis.json - Stock analysis")
    print("="*60)
