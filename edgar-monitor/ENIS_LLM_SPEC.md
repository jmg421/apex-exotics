# ENIS + LLM Deep Analysis

**Systematic discovery + AI analysis = institutional-quality reports on overlooked companies**

## The System

**Stage 1: Discovery (ENIS)**
- Monitor SEC RSS feeds
- Filter micro-caps (<$100M)
- Score financials (0-100)
- Calculate network metrics
- Alert on high scores

**Stage 2: Deep Analysis (LLM)**
- Feed company data to Claude/GPT
- Run institutional analysis prompts
- Generate research reports
- Identify trade setups

**Stage 3: Action**
- Long candidates (high score, low risk)
- Short candidates (high concentration, fragile)
- Pass candidates (interesting but not actionable)

## The Prompts

### 1. Goldman Sachs Fundamental Analysis
**When:** Company scores ≥50 on ENIS
**Input:** Ticker, 10-K text, financials
**Output:** Buy/Hold/Avoid with conviction level
**Use:** Long candidate validation

### 2. Bridgewater Risk Assessment
**When:** Customer concentration ≥40%
**Input:** Concentration data, financials, sector
**Output:** Risk score, hedging recommendations
**Use:** Short candidate identification

### 3. Renaissance Quant Screen
**When:** Building watchlist
**Input:** All scored companies
**Output:** Multi-factor ranking
**Use:** Portfolio construction

### 4. JPMorgan Earnings Analyzer
**When:** Earnings date approaching
**Input:** Historical earnings, current estimates
**Output:** Trade setup for earnings
**Use:** Event-driven trades

### 5. Citadel Sector Rotation
**When:** Monthly portfolio review
**Input:** All holdings by sector
**Output:** Overweight/underweight recommendations
**Use:** Portfolio rebalancing

## Implementation

```python
# enis_llm_analyzer.py

def analyze_company(cik, ticker, enis_score, concentration):
    """Run LLM analysis on ENIS-discovered company."""
    
    # Load company data
    financials = load_financials(cik)
    filing_text = load_10k_text(cik)
    
    # Determine analysis type
    if enis_score >= 60:
        # High score = potential long
        report = goldman_sachs_analysis(ticker, financials, filing_text)
        
    elif concentration >= 40:
        # High concentration = potential short
        report = bridgewater_risk_assessment(ticker, concentration, financials)
        
    else:
        # Medium score = watchlist
        report = quick_summary(ticker, enis_score, financials)
    
    # Save report
    save_report(cik, report)
    
    # Alert if actionable
    if report['recommendation'] in ['BUY', 'SHORT']:
        send_alert(ticker, report)
    
    return report

def goldman_sachs_analysis(ticker, financials, filing_text):
    """Generate Goldman-style fundamental analysis."""
    
    prompt = f"""You are a senior equity research analyst at Goldman Sachs.
    
Analyze this micro-cap company as if writing a research report for institutional investors.

Company: {ticker}
Market Cap: ${financials['market_cap']:,.0f}
Revenue: ${financials['revenue']:,.0f}
Net Margin: {financials['net_margin']:.1f}%
Debt/Assets: {financials['debt_to_assets']:.1f}%

Key sections from 10-K:
{filing_text[:5000]}

Provide:
1. Business model breakdown
2. Revenue stream analysis
3. Profitability trends
4. Balance sheet health
5. Competitive advantages (rate 1-10)
6. Bull case and bear case with 12-month price targets
7. One-paragraph verdict: BUY, HOLD, or AVOID with conviction level

Format as Goldman Sachs equity research note."""
    
    response = call_llm(prompt)
    return parse_recommendation(response)

def bridgewater_risk_assessment(ticker, concentration, financials):
    """Generate Bridgewater-style risk analysis."""
    
    prompt = f"""You are a senior portfolio risk analyst at Bridgewater Associates.
    
Assess the risk profile of this micro-cap company with HIGH customer concentration.

Company: {ticker}
Customer Concentration: {concentration}% of revenue from top customers
Market Cap: ${financials['market_cap']:,.0f}
Debt/Equity: {financials['debt_to_assets']:.1f}%

This is a FRAGILITY ANALYSIS. Focus on:
1. What happens if they lose their largest customer?
2. Revenue concentration risk score (1-10)
3. Probability of cascade failure
4. Estimated price decline in customer loss scenario
5. Hedging recommendation (put options, short position)
6. Risk-adjusted verdict: AVOID, HEDGE, or SHORT

Format as Bridgewater risk memo with specific trade recommendations."""
    
    response = call_llm(prompt)
    return parse_recommendation(response)
```

## Data Flow

```
SEC RSS Feed
    ↓
ENIS Screener (feed_parser.py → scorer.py)
    ↓
High-Score Companies (≥50) → Goldman Analysis → Long Candidates
    ↓
High-Concentration (≥40%) → Bridgewater Risk → Short Candidates
    ↓
Medium-Score (30-49) → Quick Summary → Watchlist
    ↓
Reports Database (reports.json)
    ↓
Daily Digest Email
```

## Output Format

```json
{
  "cik": "0001822523",
  "ticker": "AFCG",
  "company": "Advanced Flower Capital Inc.",
  "enis_score": 50,
  "analysis_date": "2026-03-06",
  "analysis_type": "goldman_sachs",
  "recommendation": "HOLD",
  "conviction": "MEDIUM",
  "price_target_12m": 8.50,
  "current_price": 7.25,
  "upside": "17%",
  "key_risks": [
    "High debt (49.9% of assets)",
    "No revenue growth visibility",
    "Illiquid stock"
  ],
  "key_opportunities": [
    "Strong cash position (25.8% of assets)",
    "Profitable operations",
    "Undervalued vs peers"
  ],
  "trade_setup": {
    "action": "WATCH",
    "entry": 6.50,
    "stop": 5.00,
    "target": 9.00,
    "risk_reward": "2.5:1"
  },
  "full_report": "..."
}
```

## Cost Structure

**LLM API Costs:**
- Claude Sonnet: ~$3 per analysis (5K tokens in, 2K tokens out)
- GPT-4: ~$5 per analysis
- Gemini Pro: ~$1 per analysis

**Volume:**
- ~10 new micro-cap filings per day
- ~5 meet ENIS threshold (≥30)
- ~$15-25/day in API costs
- ~$450-750/month

**ROI:**
- One good trade pays for a year of API costs
- Systematic edge compounds over time

## Success Metrics

**Discovery:**
- Companies screened per week
- High-score alerts generated
- False positive rate

**Analysis:**
- Reports generated per week
- Recommendation distribution (Buy/Hold/Avoid/Short)
- Time from filing to report

**Performance:**
- Long recommendations: average return vs S&P 500
- Short recommendations: average decline
- Sharpe ratio of ENIS portfolio

## Phase 1: MVP (1 week)

1. ✅ ENIS screener working (done)
2. ⬜ LLM integration (enis_llm_analyzer.py)
3. ⬜ Goldman Sachs prompt template
4. ⬜ Bridgewater risk prompt template
5. ⬜ Report storage (reports.json)
6. ⬜ Daily digest email

## Phase 2: Validation (1 month)

7. ⬜ Run on 100 historical filings
8. ⬜ Backtest recommendations
9. ⬜ Calculate hit rate
10. ⬜ Refine prompts based on results

## Phase 3: Production (ongoing)

11. ⬜ Automated daily pipeline
12. ⬜ Paper trading portfolio
13. ⬜ Real money (small positions)
14. ⬜ Scale based on performance

## The Edge

**ENIS finds companies nobody's watching.**
**LLMs analyze them like Goldman Sachs would.**
**You get institutional-quality research on overlooked stocks.**

**Nobody else is doing this because:**
1. They don't have the patents (MGF network analysis)
2. They don't monitor micro-cap 10-Ks systematically
3. They don't combine systematic screening + AI analysis

**This is defensible. This is scalable. This makes money.**

But only if you execute.
