# ENIS Production Pipeline

## Full Pipeline (with data collection)

```bash
./run_enis.sh
```

**Steps:**
1. Run tests
2. Fetch latest SEC filings
3. Filter micro-caps (<$100M)
4. Parse financials
5. Extract relationships
6. Build network graph
7. Calculate MGF + ENIS scores
8. **Run LLM analysis** (NEW)
9. **Generate daily digest** (NEW)
10. Check for alerts

**Output:**
- `data/digest_YYYYMMDD.md` - Daily report with longs/shorts
- `data/llm_reports.json` - Full analysis details
- `data/enis_scores.json` - ENIS scores
- `data/alerts.json` - Alert history

## Quick Analysis (existing data only)

```bash
./run_quick.sh
```

**Steps:**
1. Run LLM analysis on existing companies
2. Generate daily digest
3. Run validation

**Use when:** You just want fresh LLM analysis without re-scraping SEC data.

## Manual Steps

```bash
# Just LLM analysis
python batch_analyzer.py

# Just digest
python daily_digest.py

# Just validation
python validation.py

# Fetch prices (requires ALPHA_VANTAGE_KEY)
python price_fetcher.py
```

## Scheduling

**Daily cron job:**
```bash
0 18 * * 1-5 cd /path/to/edgar-monitor && ./run_enis.sh >> logs/enis_$(date +\%Y\%m\%d).log 2>&1
```

Runs at 6pm weekdays after market close.

## Cost Estimate

**Current (2 companies):**
- LLM: $0.016/day ($0.008 × 2)
- Monthly: ~$0.50

**Full scale (50 companies):**
- LLM: $0.40/day ($0.008 × 50)
- Monthly: ~$12

**Full scale (500 companies):**
- LLM: $4/day ($0.008 × 500)
- Monthly: ~$120

## Output Example

```markdown
# ENIS Daily Digest
**Generated:** 2026-03-06 09:18:51
**Model:** Jarvis (Anthropic Claude)

## Summary
- **Total Analyzed:** 50
- **Actionable:** 8
  - Longs: 3
  - Shorts: 5
- **Passes:** 42

## 🟢 Long Opportunities
### TICK (0001234567)
**Recommendation:** BUY
**Conviction:** HIGH
**Price Target:** $25.0
**ENIS Score:** 85.0/100
...

## 🔴 Short Opportunities
### AFCG (0001822523)
**Recommendation:** AVOID
**Conviction:** HIGH
**ENIS Score:** 30.0/100
...
```
