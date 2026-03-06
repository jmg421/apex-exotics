# ENIS + LLM Implementation Plan (TDD)

**Test-Driven Development approach for systematic, debuggable implementation**

## Phase 1: LLM Integration (Week 1)

### Day 1: Test Infrastructure

**File:** `test_llm_analyzer.py`

```python
def test_llm_connection():
    """Verify we can call Claude API."""
    response = call_llm("Test prompt")
    assert response is not None
    assert len(response) > 0

def test_prompt_formatting():
    """Verify prompts format correctly with company data."""
    company_data = {
        'ticker': 'AFCG',
        'market_cap': 50000000,
        'revenue': 0,
        'net_margin': 0
    }
    prompt = format_goldman_prompt(company_data)
    assert 'AFCG' in prompt
    assert '$50,000,000' in prompt

def test_response_parsing():
    """Verify we can extract recommendation from LLM response."""
    mock_response = """
    Based on analysis, this is a HOLD with MEDIUM conviction.
    Price target: $8.50
    """
    result = parse_recommendation(mock_response)
    assert result['recommendation'] == 'HOLD'
    assert result['conviction'] == 'MEDIUM'
    assert result['price_target'] == 8.50
```

**Run:** `pytest test_llm_analyzer.py -v`
**Expected:** All fail (not implemented yet)

### Day 2: Basic LLM Integration

**File:** `llm_client.py`

```python
import anthropic
import os

def call_llm(prompt, model="claude-3-5-sonnet-20241022"):
    """Call Claude API with prompt."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def format_goldman_prompt(company_data):
    """Format Goldman Sachs analysis prompt."""
    return f"""You are a senior equity research analyst at Goldman Sachs.

Analyze this micro-cap company:

Ticker: {company_data['ticker']}
Market Cap: ${company_data['market_cap']:,.0f}
Revenue: ${company_data.get('revenue', 0):,.0f}
Net Margin: {company_data.get('net_margin', 0):.1f}%

Provide:
1. Business model assessment
2. Financial health rating (1-10)
3. Risk factors
4. Recommendation: BUY, HOLD, or AVOID
5. Conviction: HIGH, MEDIUM, or LOW
6. 12-month price target

Format as brief research note."""

def parse_recommendation(response):
    """Extract structured data from LLM response."""
    import re
    
    # Extract recommendation
    rec_match = re.search(r'(BUY|HOLD|AVOID)', response, re.IGNORECASE)
    recommendation = rec_match.group(1).upper() if rec_match else None
    
    # Extract conviction
    conv_match = re.search(r'(HIGH|MEDIUM|LOW)', response, re.IGNORECASE)
    conviction = conv_match.group(1).upper() if conv_match else None
    
    # Extract price target
    price_match = re.search(r'\$(\d+\.?\d*)', response)
    price_target = float(price_match.group(1)) if price_match else None
    
    return {
        'recommendation': recommendation,
        'conviction': conviction,
        'price_target': price_target,
        'full_text': response
    }
```

**Run:** `pytest test_llm_analyzer.py -v`
**Expected:** Tests pass

**Debug if fails:**
- Print API response to see format
- Check API key is set
- Verify regex patterns match actual output

### Day 3: Goldman Sachs Analyzer

**File:** `test_goldman_analyzer.py`

```python
def test_goldman_analysis_structure():
    """Verify Goldman analysis returns required fields."""
    company_data = load_test_company('AFCG')
    result = goldman_analysis(company_data)
    
    assert 'recommendation' in result
    assert 'conviction' in result
    assert 'price_target' in result
    assert 'key_risks' in result
    assert 'key_opportunities' in result

def test_goldman_analysis_with_real_data():
    """Test with actual ENIS company data."""
    # Load AFCG from ENIS database
    company = load_company_from_enis('0001822523')
    result = goldman_analysis(company)
    
    # Should have valid recommendation
    assert result['recommendation'] in ['BUY', 'HOLD', 'AVOID']
    assert result['conviction'] in ['HIGH', 'MEDIUM', 'LOW']
    
    # Should identify key risks
    assert len(result['key_risks']) > 0
    
    print(f"\nGoldman Analysis for {company['ticker']}:")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Conviction: {result['conviction']}")
    print(f"  Price Target: ${result['price_target']}")
```

**File:** `goldman_analyzer.py`

```python
from llm_client import call_llm, format_goldman_prompt, parse_recommendation
import json

def goldman_analysis(company_data):
    """Run Goldman Sachs-style fundamental analysis."""
    
    # Format prompt
    prompt = format_goldman_prompt(company_data)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Parse response
    result = parse_recommendation(response)
    
    # Extract additional fields
    result['key_risks'] = extract_risks(response)
    result['key_opportunities'] = extract_opportunities(response)
    result['ticker'] = company_data['ticker']
    result['analysis_date'] = datetime.now().isoformat()
    
    return result

def extract_risks(text):
    """Extract risk factors from analysis."""
    # Look for risk section
    import re
    risks = []
    
    # Pattern: "Risk:" or "Risks:" followed by bullet points
    risk_section = re.search(r'Risk[s]?:(.*?)(?=Opportunit|$)', text, re.DOTALL | re.IGNORECASE)
    if risk_section:
        # Extract bullet points
        bullets = re.findall(r'[-•]\s*(.+)', risk_section.group(1))
        risks = [b.strip() for b in bullets]
    
    return risks[:5]  # Top 5 risks

def extract_opportunities(text):
    """Extract opportunities from analysis."""
    import re
    opps = []
    
    opp_section = re.search(r'Opportunit[y|ies]:(.*?)(?=Risk|$)', text, re.DOTALL | re.IGNORECASE)
    if opp_section:
        bullets = re.findall(r'[-•]\s*(.+)', opp_section.group(1))
        opps = [b.strip() for b in bullets]
    
    return opps[:5]
```

**Run:** `pytest test_goldman_analyzer.py -v`
**Expected:** Tests pass, see actual analysis output

**Debug if fails:**
- Print full LLM response to see structure
- Adjust regex patterns to match actual format
- Add more specific prompting if output inconsistent

### Day 4: Bridgewater Risk Analyzer

**File:** `test_bridgewater_analyzer.py`

```python
def test_bridgewater_risk_analysis():
    """Test risk analysis for high-concentration company."""
    company_data = {
        'ticker': 'TASK',
        'concentration': 87,
        'market_cap': 100000000,
        'debt_to_assets': 30
    }
    
    result = bridgewater_risk_analysis(company_data)
    
    assert 'risk_score' in result
    assert result['risk_score'] >= 7  # High concentration = high risk
    assert 'recommendation' in result
    assert result['recommendation'] in ['AVOID', 'HEDGE', 'SHORT']

def test_low_concentration_company():
    """Test that low concentration gets lower risk score."""
    company_data = {
        'ticker': 'AFCG',
        'concentration': 0,
        'market_cap': 50000000,
        'debt_to_assets': 50
    }
    
    result = bridgewater_risk_analysis(company_data)
    
    assert result['risk_score'] < 5  # Lower risk
```

**File:** `bridgewater_analyzer.py`

```python
def bridgewater_risk_analysis(company_data):
    """Run Bridgewater-style risk assessment."""
    
    prompt = f"""You are a senior portfolio risk analyst at Bridgewater Associates.

Assess the risk profile of this company:

Ticker: {company_data['ticker']}
Customer Concentration: {company_data['concentration']}% from top customers
Market Cap: ${company_data['market_cap']:,.0f}
Debt/Assets: {company_data.get('debt_to_assets', 0):.1f}%

Focus on:
1. Revenue fragility (what if largest customer leaves?)
2. Risk score (1-10, where 10 = extreme risk)
3. Estimated price decline in customer loss scenario
4. Recommendation: AVOID, HEDGE, or SHORT
5. Specific hedging strategy (put options, short position)

Format as Bridgewater risk memo."""
    
    response = call_llm(prompt)
    
    # Parse response
    result = parse_risk_assessment(response)
    result['ticker'] = company_data['ticker']
    result['concentration'] = company_data['concentration']
    
    return result

def parse_risk_assessment(response):
    """Extract risk metrics from response."""
    import re
    
    # Extract risk score
    risk_match = re.search(r'Risk Score:?\s*(\d+)', response, re.IGNORECASE)
    risk_score = int(risk_match.group(1)) if risk_match else None
    
    # Extract recommendation
    rec_match = re.search(r'(AVOID|HEDGE|SHORT)', response, re.IGNORECASE)
    recommendation = rec_match.group(1).upper() if rec_match else None
    
    return {
        'risk_score': risk_score,
        'recommendation': recommendation,
        'full_text': response
    }
```

**Run:** `pytest test_bridgewater_analyzer.py -v`

### Day 5: Integration with ENIS

**File:** `test_enis_llm_integration.py`

```python
def test_analyze_high_score_company():
    """Test that high-score companies get Goldman analysis."""
    # AFCG has score of 50
    result = analyze_company_from_enis('0001822523')
    
    assert result['analysis_type'] == 'goldman_sachs'
    assert 'recommendation' in result

def test_analyze_high_concentration_company():
    """Test that high-concentration companies get risk analysis."""
    # Mock company with 87% concentration
    result = analyze_company_from_enis('0001829864')  # TaskUs
    
    assert result['analysis_type'] == 'bridgewater_risk'
    assert result['risk_score'] >= 7

def test_save_and_load_reports():
    """Test report persistence."""
    result = analyze_company_from_enis('0001822523')
    save_report(result)
    
    loaded = load_report('0001822523')
    assert loaded['ticker'] == result['ticker']
    assert loaded['recommendation'] == result['recommendation']
```

**File:** `enis_llm_analyzer.py`

```python
from goldman_analyzer import goldman_analysis
from bridgewater_analyzer import bridgewater_risk_analysis
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
REPORTS_FILE = DATA_DIR / "llm_reports.json"

def analyze_company_from_enis(cik):
    """Analyze company from ENIS database using LLM."""
    
    # Load company data from ENIS
    company = load_company_data(cik)
    
    # Determine analysis type
    if company['enis_score'] >= 50:
        # High score = potential long
        result = goldman_analysis(company)
        result['analysis_type'] = 'goldman_sachs'
        
    elif company.get('concentration', 0) >= 40:
        # High concentration = potential short
        result = bridgewater_risk_analysis(company)
        result['analysis_type'] = 'bridgewater_risk'
        
    else:
        # Medium score = quick summary
        result = quick_summary(company)
        result['analysis_type'] = 'quick_summary'
    
    result['cik'] = cik
    result['enis_score'] = company['enis_score']
    
    return result

def load_company_data(cik):
    """Load company data from ENIS databases."""
    # Load from scores.json
    with open(DATA_DIR / "enis_scores.json") as f:
        scores = json.load(f)
    
    company = next((c for c in scores if c['cik'] == cik), None)
    if not company:
        raise ValueError(f"Company {cik} not found in ENIS database")
    
    # Load concentration data
    with open(DATA_DIR / "relationships.json") as f:
        relationships = json.load(f)
    
    if cik in relationships:
        rels = relationships[cik]['relationships']
        company['concentration'] = rels.get('customer_concentration', [0])[0] if rels.get('customer_concentration') else 0
    
    return company

def save_report(report):
    """Save LLM analysis report."""
    reports = load_all_reports()
    reports[report['cik']] = report
    
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=2)

def load_all_reports():
    """Load all saved reports."""
    if not REPORTS_FILE.exists():
        return {}
    
    with open(REPORTS_FILE) as f:
        return json.load(f)

def load_report(cik):
    """Load specific company report."""
    reports = load_all_reports()
    return reports.get(cik)
```

**Run:** `pytest test_enis_llm_integration.py -v`

## Phase 2: Automation (Week 2)

### Day 6: Batch Processing

**File:** `test_batch_analyzer.py`

```python
def test_analyze_all_companies():
    """Test batch analysis of all ENIS companies."""
    results = analyze_all_companies()
    
    assert len(results) > 0
    assert all('recommendation' in r or 'risk_score' in r for r in results)

def test_filter_actionable_recommendations():
    """Test filtering for BUY and SHORT recommendations."""
    results = analyze_all_companies()
    actionable = filter_actionable(results)
    
    for r in actionable:
        assert r.get('recommendation') in ['BUY', 'SHORT'] or r.get('risk_score', 0) >= 7
```

**File:** `batch_analyzer.py`

```python
def analyze_all_companies():
    """Analyze all companies in ENIS database."""
    from enis_llm_analyzer import analyze_company_from_enis, save_report
    import json
    
    # Load all companies
    with open(DATA_DIR / "enis_scores.json") as f:
        companies = json.load(f)
    
    results = []
    for company in companies:
        cik = company['cik']
        print(f"Analyzing {company['ticker']} ({cik})...")
        
        try:
            result = analyze_company_from_enis(cik)
            save_report(result)
            results.append(result)
            
            # Rate limit
            import time
            time.sleep(2)  # 2 seconds between API calls
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return results

def filter_actionable(results):
    """Filter for actionable recommendations."""
    actionable = []
    
    for r in results:
        # BUY recommendations
        if r.get('recommendation') == 'BUY' and r.get('conviction') in ['HIGH', 'MEDIUM']:
            actionable.append(r)
        
        # SHORT candidates (high risk)
        elif r.get('risk_score', 0) >= 7:
            actionable.append(r)
    
    return actionable
```

### Day 7: Daily Digest

**File:** `daily_digest.py`

```python
def generate_daily_digest():
    """Generate daily digest of new analyses."""
    from batch_analyzer import analyze_all_companies, filter_actionable
    
    # Analyze all companies
    results = analyze_all_companies()
    
    # Filter actionable
    actionable = filter_actionable(results)
    
    # Generate report
    digest = format_digest(actionable)
    
    # Save
    with open(DATA_DIR / "daily_digest.md", 'w') as f:
        f.write(digest)
    
    print(f"✓ Generated digest with {len(actionable)} actionable recommendations")
    
    return digest

def format_digest(recommendations):
    """Format recommendations as markdown."""
    lines = ["# ENIS Daily Digest\n"]
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
    lines.append(f"**Actionable Recommendations:** {len(recommendations)}\n")
    
    # Long candidates
    longs = [r for r in recommendations if r.get('recommendation') == 'BUY']
    if longs:
        lines.append("\n## 🟢 Long Candidates\n")
        for r in longs:
            lines.append(f"### {r['ticker']}")
            lines.append(f"- **Recommendation:** {r['recommendation']} ({r['conviction']} conviction)")
            lines.append(f"- **Price Target:** ${r.get('price_target', 'N/A')}")
            lines.append(f"- **ENIS Score:** {r['enis_score']}/100")
            lines.append("")
    
    # Short candidates
    shorts = [r for r in recommendations if r.get('risk_score', 0) >= 7]
    if shorts:
        lines.append("\n## 🔴 Short Candidates\n")
        for r in shorts:
            lines.append(f"### {r['ticker']}")
            lines.append(f"- **Risk Score:** {r['risk_score']}/10")
            lines.append(f"- **Concentration:** {r.get('concentration', 0)}%")
            lines.append(f"- **Recommendation:** {r.get('recommendation', 'N/A')}")
            lines.append("")
    
    return '\n'.join(lines)
```

**Run:** `python daily_digest.py`

## Debugging Checklist

**If LLM calls fail:**
1. Print full API response
2. Check API key is set
3. Verify rate limits not exceeded
4. Test with simpler prompt

**If parsing fails:**
1. Print raw LLM output
2. Check regex patterns match format
3. Add fallback parsing logic
4. Make prompts more specific

**If integration fails:**
1. Verify ENIS data files exist
2. Check CIK mappings are correct
3. Test each component independently
4. Add detailed logging

**Remember:**
- Test one thing at a time
- Print intermediate values
- Use debugger for complex issues
- Keep tests simple and focused

## Success Metrics

**Week 1:**
- ✅ All tests passing
- ✅ Can analyze 1 company end-to-end
- ✅ Reports save/load correctly

**Week 2:**
- ✅ Batch analysis works
- ✅ Daily digest generates
- ✅ Actionable recommendations identified

**Week 3:**
- ✅ Run on 100 historical companies
- ✅ Validate recommendations make sense
- ✅ Refine prompts based on results
