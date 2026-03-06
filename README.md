# Apex Exotics

**Systematic attention arbitrage across overlooked markets**

## Philosophy

Markets aren't efficient. They're just crowded in some places and empty in others.

Edge comes from systematic attention where nobody else is looking.

## Systems

### BaT Monitor (`bat-monitor/`)
Exotic car arbitrage system. Monitors Bring a Trailer auctions, matches listings to buyer network, alerts on high-margin opportunities.

**The edge:** Systematic screening of niche auctions nobody's watching systematically.

### EDGAR Monitor (`edgar-monitor/`)
Micro-cap intelligence system. Parses SEC 10-Ks, extracts financials and relationships, applies patented network analysis (US Patents 10,176,442 & 10,997,540).

**The edge:** Patented MGF threshold distribution analysis + systematic attention on companies with zero coverage.

## The Pattern

Both systems:
1. Monitor free public data feeds (BaT listings, SEC filings)
2. Extract structured information (vehicle specs, financial metrics)
3. Score opportunities (margin calculations, network analysis)
4. Alert when criteria met (high-margin deals, undervalued companies)
5. Prevent duplicates (alert history tracking)

## Why This Works

**Attention arbitrage:** Everyone watches Bloomberg, S&P 500, major auctions. Nobody systematically watches micro-cap 10-Ks or niche vehicle auctions.

**Free data:** BaT listings and SEC filings are public. No expensive feeds.

**Systematic process:** Automated screening beats human attention every time.

**Boring = moat:** Most people won't do this because it's tedious. That's the point.

## Architecture

Both systems share the same architecture:
- Data ingestion (RSS/API monitoring)
- Parsing & extraction (structured data from unstructured sources)
- Scoring & ranking (opportunity identification)
- Alert system (notification with deduplication)
- Storage (JSON databases for simplicity)

## Getting Started

See individual system READMEs:
- [BaT Monitor](bat-monitor/README.md) - Vehicle arbitrage
- [EDGAR Monitor](edgar-monitor/README.md) - Micro-cap intelligence

---

**Apex Exotics:** Finding rare opportunities at the apex of overlooked markets.
