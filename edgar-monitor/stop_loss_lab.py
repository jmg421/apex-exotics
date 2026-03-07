#!/usr/bin/env python3
"""Find historical stop-loss scenarios from your current holdings."""

import yfinance as yf
from paper_trading import load_portfolio
from datetime import datetime, timedelta
import pandas as pd

def analyze_drawdowns(ticker, period="1y"):
    """Find significant drawdowns and what caused them."""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {ticker}")
    print(f"{'='*80}")
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get historical data
        hist = stock.history(period=period)
        
        if hist.empty:
            print(f"No data available for {ticker}")
            return
        
        # Calculate rolling max and drawdown
        hist['RollingMax'] = hist['Close'].expanding().max()
        hist['Drawdown'] = (hist['Close'] - hist['RollingMax']) / hist['RollingMax'] * 100
        
        # Find significant drawdowns (>15%)
        significant = hist[hist['Drawdown'] < -15].copy()
        
        if significant.empty:
            print(f"✓ No major drawdowns (>15%) in the past year")
            print(f"  Current price: ${hist['Close'].iloc[-1]:.2f}")
            print(f"  52-week high: ${hist['Close'].max():.2f}")
            print(f"  Max drawdown: {hist['Drawdown'].min():.1f}%")
            return
        
        print(f"\n🚨 FOUND {len(significant)} DAYS WITH >15% DRAWDOWN")
        print(f"\nWorst drawdown: {significant['Drawdown'].min():.1f}%")
        print(f"Occurred on: {significant['Drawdown'].idxmin().strftime('%Y-%m-%d')}")
        
        # Group consecutive drawdown days into events
        significant['DateDiff'] = significant.index.to_series().diff().dt.days
        significant['Event'] = (significant['DateDiff'] > 7).cumsum()
        
        events = significant.groupby('Event').agg({
            'Drawdown': 'min',
            'Close': ['first', 'min', 'last']
        })
        
        print(f"\nDrawdown events (>7 days apart):")
        for i, (idx, row) in enumerate(events.iterrows(), 1):
            dates = significant[significant['Event'] == idx].index
            start_date = dates[0].strftime('%Y-%m-%d')
            end_date = dates[-1].strftime('%Y-%m-%d')
            worst_dd = row[('Drawdown', 'min')]
            
            print(f"\n  Event {i}: {start_date} to {end_date}")
            print(f"    Worst drawdown: {worst_dd:.1f}%")
            print(f"    Price range: ${row[('Close', 'min')]:.2f} - ${row[('Close', 'first')]:.2f}")
            
            # Check if it recovered
            current_price = hist['Close'].iloc[-1]
            peak_before = hist.loc[:dates[0]]['Close'].max()
            recovery = (current_price / peak_before - 1) * 100
            
            if recovery >= 0:
                print(f"    ✓ Recovered: Now {recovery:.1f}% above pre-event peak")
            else:
                print(f"    ✗ Not recovered: Still {recovery:.1f}% below pre-event peak")
        
        # Stop-loss analysis
        print(f"\n{'='*80}")
        print("STOP-LOSS SCENARIOS:")
        print(f"{'='*80}")
        
        portfolio = load_portfolio()
        if ticker in portfolio['positions']:
            entry_price = portfolio['positions'][ticker]['avg_price']
            current_price = hist['Close'].iloc[-1]
            
            print(f"\nYour position:")
            print(f"  Entry price: ${entry_price:.2f}")
            print(f"  Current price: ${current_price:.2f}")
            print(f"  Current P&L: {((current_price/entry_price - 1) * 100):.1f}%")
            
            # Simulate different stop-loss levels
            for stop_pct in [5, 10, 15, 20]:
                stop_price = entry_price * (1 - stop_pct/100)
                would_trigger = hist[hist['Close'] <= stop_price]
                
                if not would_trigger.empty:
                    trigger_date = would_trigger.index[0].strftime('%Y-%m-%d')
                    trigger_price = would_trigger['Close'].iloc[0]
                    
                    # What would have happened if you held?
                    held_return = ((current_price / entry_price) - 1) * 100
                    stopped_return = ((trigger_price / entry_price) - 1) * 100
                    
                    print(f"\n  {stop_pct}% stop-loss @ ${stop_price:.2f}:")
                    print(f"    Would trigger: {trigger_date} @ ${trigger_price:.2f}")
                    print(f"    Stopped loss: {stopped_return:.1f}%")
                    print(f"    If held instead: {held_return:.1f}%")
                    
                    if held_return > stopped_return:
                        print(f"    ❌ Stop-loss would have cost you {held_return - stopped_return:.1f}%")
                    else:
                        print(f"    ✓ Stop-loss would have saved you {stopped_return - held_return:.1f}%")
                else:
                    print(f"\n  {stop_pct}% stop-loss @ ${stop_price:.2f}: Never triggered")
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")

def main():
    portfolio = load_portfolio()
    
    print("\n" + "="*80)
    print("STOP-LOSS LEARNING LAB")
    print("="*80)
    print("\nAnalyzing your 7 holdings for historical drawdown scenarios...")
    
    for ticker in portfolio['positions'].keys():
        analyze_drawdowns(ticker)
    
    print("\n" + "="*80)
    print("KEY LESSONS:")
    print("="*80)
    print("""
1. Small-caps are volatile - 15%+ drawdowns are normal
2. Most drawdowns recover if fundamentals intact
3. Stop-losses can lock in losses during temporary dips
4. Better approach: Check fundamentals when price drops, not automatic sell
5. Your edge is patience + fundamental analysis, not timing
    """)

if __name__ == '__main__':
    main()
