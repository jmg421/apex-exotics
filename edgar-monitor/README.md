# EDGAR Network Intelligence System (ENIS)

**Patented network analysis for financial markets**

Micro-cap screening system using MGF threshold distributions (US Patents 10,176,442 & 10,997,540).

## The Insight

Biological networks = Financial networks. The same patented math that analyzes protein interactions can analyze company relationships, supply chain risk, and financial contagion.

## Strategy

Go where nobody is paying attention. Read what nobody is reading. Analyze what nobody can replicate.

Micro-cap companies (<$100M market cap) have:
- Zero analyst coverage
- Zero institutional ownership  
- Audited financials nobody reads
- Network relationships nobody maps

**That's not a problem. That's the opportunity.**

**See [ENIS_SPEC.md](ENIS_SPEC.md) for full system architecture and patent strategy.**

## Quick Start

```bash
# Full pipeline (scrape + analyze + LLM)
./run_enis.sh

# Quick analysis (existing data only)
./run_quick.sh

# View today's digest
cat data/digest_$(date +%Y%m%d).md
```

See [PIPELINE.md](PIPELINE.md) for production setup and [ENIS_LLM_SPEC.md](ENIS_LLM_SPEC.md) for LLM integration details.

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key (get free key from https://www.alphavantage.co/support/#api-key)
cp .env.example .env
# Edit .env and add your Alpha Vantage API key

# Run full pipeline
./run.sh

# Or run steps individually:
python feed_parser.py    # Parse latest EDGAR filings
python market_cap.py     # Filter for micro-caps (<$100M market cap)
python financials.py     # Parse financial metrics from XBRL
python scorer.py         # Score and rank companies
python alerts.py         # Alert on high-score opportunities (score >= 50)
```

## Test Results

Successfully tested on live SEC data (March 4, 2026):
- Fetched 5 recent 10-K filings from EDGAR RSS
- Identified 2 micro-caps: AFCG ($49.9M cap), CLRB ($11.4M cap)
- Parsed XBRL financials via SEC CompanyFacts API
- Scored companies: AFCG (50/100), CLRB (35/100)
- Generated alert for AFCG (profitable, strong cash position, moderate debt)

## Architecture

```
EDGAR Monitor
├── feed_parser.py      - Parse SEC RSS for new 10-K/10-Q filings
├── market_cap.py       - Filter for micro-caps (<$100M)
├── financials.py       - Extract metrics from XBRL
├── scorer.py           - Score companies on key criteria
└── alerts.py           - Notify on high-score opportunities
```

## The Edge

The 10-K is free. The edge is free.

Most people won't do this because it's boring.

That's the point.
