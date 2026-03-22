#!/usr/bin/env python3
"""Build diversified portfolio from quality small-caps."""

from paper_trading import buy, show_portfolio

# Quality small-caps from screening
# Allocate ~10% to each (diversification)
POSITIONS = [
    ('IBCP', 500, 'HOLD - 31% margin, 10.5x P/E, regional bank'),
    ('TASK', 80, 'BPO services, $1.2B revenue, 0.86x P/S'),
    ('GRNT', 150, 'Oil/gas royalties, zero debt, 5.7% margin'),
    ('PLPC', 15, 'Infrastructure hardware, 70yr history, 0% debt'),
    ('FMNB', 300, 'Community bank, 30% margin, 2.56x P/S'),
    ('SPFI', 200, 'Texas bank, 28% margin, strong ROE'),
    ('SD', 300, 'E&P company, 45% margin, 9x P/E'),
]

def build_portfolio():
    """Build diversified portfolio."""
    print("="*80)
    print("BUILDING DIVERSIFIED PORTFOLIO")
    print("="*80)
    print()
    print("Strategy: Equal-weight quality small-caps")
    print("Target: ~10% allocation each")
    print()
    
    total_cost = 0
    
    for ticker, shares, reason in POSITIONS:
        print(f"Buying {ticker}...")
        success = buy(ticker, shares, reason)
        if success:
            # Rough estimate of cost
            import yfinance as yf
            try:
                price = yf.Ticker(ticker).info.get('currentPrice', 0)
                cost = price * shares
                total_cost += cost
                print(f"  Allocated: ${cost:,.0f}")
            except Exception:
                pass
        print()
    
    print("="*80)
    print(f"Total deployed: ~${total_cost:,.0f}")
    print()
    
    show_portfolio()

if __name__ == '__main__':
    build_portfolio()
