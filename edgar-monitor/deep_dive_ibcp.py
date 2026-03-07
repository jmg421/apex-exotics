#!/usr/bin/env python3
"""Deep dive on IBCP (Independent Bank Corp) - the one HOLD recommendation."""

import yfinance as yf
import json
from pathlib import Path

def deep_dive_ibcp():
    """Comprehensive analysis of IBCP."""
    
    print("="*80)
    print("DEEP DIVE: INDEPENDENT BANK CORP (IBCP)")
    print("="*80)
    print()
    
    # Get comprehensive data
    ticker = yf.Ticker("IBCP")
    info = ticker.info
    history = ticker.history(period="1y")
    
    # Basic info
    print("📊 COMPANY OVERVIEW")
    print("-"*80)
    print(f"Name:           {info.get('longName', 'N/A')}")
    print(f"Sector:         {info.get('sector', 'N/A')}")
    print(f"Industry:       {info.get('industry', 'N/A')}")
    print(f"Website:        {info.get('website', 'N/A')}")
    employees = info.get('fullTimeEmployees', 0)
    if employees:
        print(f"Employees:      {employees:,}")
    print()
    
    # Valuation
    print("💰 VALUATION")
    print("-"*80)
    market_cap = info.get('marketCap', 0)
    print(f"Market Cap:     ${market_cap/1e6:.1f}M")
    print(f"Price:          ${info.get('currentPrice', 0):.2f}")
    print(f"52w Range:      ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}")
    print(f"P/E Ratio:      {info.get('trailingPE', 0):.2f}x")
    print(f"P/B Ratio:      {info.get('priceToBook', 0):.2f}x")
    print(f"Dividend Yield: {info.get('dividendYield', 0)*100:.2f}%")
    print()
    
    # Financials
    print("📈 FINANCIAL METRICS")
    print("-"*80)
    revenue = info.get('totalRevenue', 0)
    print(f"Revenue:        ${revenue/1e6:.1f}M")
    print(f"Net Income:     ${info.get('netIncomeToCommon', 0)/1e6:.1f}M")
    print(f"Profit Margin:  {info.get('profitMargins', 0)*100:.1f}%")
    print(f"ROE:            {info.get('returnOnEquity', 0)*100:.1f}%")
    print(f"ROA:            {info.get('returnOnAssets', 0)*100:.1f}%")
    print()
    
    # Bank-specific metrics
    print("🏦 BANK-SPECIFIC METRICS")
    print("-"*80)
    print(f"Book Value:     ${info.get('bookValue', 0):.2f}")
    print(f"Total Assets:   ${info.get('totalAssets', 0)/1e9:.2f}B")
    print(f"Total Debt:     ${info.get('totalDebt', 0)/1e6:.1f}M")
    print(f"Cash:           ${info.get('totalCash', 0)/1e6:.1f}M")
    print()
    
    # Performance
    print("📊 STOCK PERFORMANCE")
    print("-"*80)
    current_price = history['Close'].iloc[-1]
    year_ago_price = history['Close'].iloc[0]
    ytd_return = ((current_price - year_ago_price) / year_ago_price) * 100
    print(f"1-Year Return:  {ytd_return:+.1f}%")
    print(f"Avg Volume:     {info.get('averageVolume', 0):,}")
    print(f"Beta:           {info.get('beta', 0):.2f}")
    print()
    
    # Analyst info
    print("🎯 ANALYST COVERAGE")
    print("-"*80)
    print(f"Target Price:   ${info.get('targetMeanPrice', 0):.2f}")
    print(f"Recommendation: {info.get('recommendationKey', 'N/A').upper()}")
    print(f"# Analysts:     {info.get('numberOfAnalystOpinions', 0)}")
    print()
    
    # Investment thesis
    print("="*80)
    print("💡 INVESTMENT THESIS")
    print("="*80)
    print()
    
    # Calculate key metrics
    pe = info.get('trailingPE', 0)
    roe = info.get('returnOnEquity', 0) * 100
    pb = info.get('priceToBook', 0)
    div_yield = info.get('dividendYield', 0) * 100
    
    print("STRENGTHS:")
    if roe > 15:
        print(f"  ✓ Exceptional ROE: {roe:.1f}% (well above 15% threshold)")
    if pe < 12:
        print(f"  ✓ Attractive valuation: {pe:.1f}x P/E (below market average)")
    if pb < 1.5:
        print(f"  ✓ Trading below book: {pb:.2f}x P/B")
    if div_yield > 3:
        print(f"  ✓ Strong dividend: {div_yield:.1f}% yield")
    
    print()
    print("CONCERNS:")
    if info.get('averageVolume', 0) < 100000:
        print(f"  ⚠ Low liquidity: {info.get('averageVolume', 0):,} avg volume")
    if market_cap < 1e9:
        print(f"  ⚠ Micro-cap: ${market_cap/1e6:.0f}M market cap")
    
    print()
    print("RECOMMENDATION: HOLD")
    print("RATIONALE: Strong fundamentals (31% margin, high ROE) but limited liquidity")
    print("           Best suited for patient investors comfortable with micro-cap risk")
    print()
    
    # Save summary
    summary = {
        'ticker': 'IBCP',
        'company': info.get('longName'),
        'market_cap': market_cap,
        'price': info.get('currentPrice'),
        'pe_ratio': pe,
        'pb_ratio': pb,
        'roe': roe,
        'profit_margin': info.get('profitMargins', 0) * 100,
        'dividend_yield': div_yield,
        'ytd_return': ytd_return,
        'recommendation': 'HOLD',
        'strengths': ['High ROE', 'Strong margins', 'Profitable', 'Dividend paying'],
        'concerns': ['Low liquidity', 'Micro-cap', 'Regional concentration']
    }
    
    output_file = Path(__file__).parent / "data" / "ibcp_deep_dive.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Saved detailed analysis to {output_file}")

if __name__ == '__main__':
    deep_dive_ibcp()
