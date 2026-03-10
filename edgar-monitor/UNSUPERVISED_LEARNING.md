# Unsupervised Learning Market Monitor

**Real-time pattern detection for micro-cap stocks + CME futures**

## What It Does

1. **Captures market data** at open and every 5 minutes
2. **Detects patterns** using unsupervised learning (DBSCAN clustering)
3. **Identifies anomalies** - stocks/futures behaving differently
4. **Asks Jarvis** (multi-model AI) for trading recommendations
5. **Generates bracket orders** for futures (entry + 3 targets + stop)

## Quick Start

```bash
# One-time scan (stocks + futures)
python3 market_open_synthetic.py    # Capture stock data
python3 detect_patterns.py          # Find patterns
python3 futures_scanner.py          # Capture futures data
python3 futures_patterns.py         # Analyze futures

# View dashboard
python3 dashboard_view.py

# Automated monitoring (every 5 min during market hours)
python3 monitor.py
```

## Files

### Data Collection
- `market_open_synthetic.py` - Capture micro-cap stock quotes
- `futures_scanner.py` - Capture CME futures quotes

### Pattern Detection
- `detect_patterns.py` - Unsupervised learning for stocks
- `futures_patterns.py` - Pattern detection + Jarvis analysis for futures

### Analysis
- `ask_jarvis.py` - Query Jarvis API for stock analysis
- `dashboard_view.py` - Combined dashboard view

### Automation
- `monitor.py` - Run scans every 5 minutes during market hours

## Output

### Stock Patterns (`data/pattern_detection.json`)
- Anomalies: Stocks that don't fit any pattern
- Clusters: Groups of stocks with similar behavior

### Futures Analysis (`data/futures_analysis.json`)
- Anomalies: Futures contracts with unusual moves
- Clusters: Correlated futures groups
- Jarvis recommendations: Long/short signals with confidence

## Bracket Orders

For futures trading with 3 contracts:
- **Entry**: Current price
- **Stop Loss**: -$10 (risk)
- **Target 1**: +$10 (exit 1/3)
- **Target 2**: +$20 (exit 1/3)
- **Target 3**: +$30 (exit 1/3)

**Risk/Reward**: Risk $10 to make $60 total (6:1)

## Jarvis Integration

Jarvis analyzes patterns and provides:
1. Which anomalies to investigate
2. Trading strategies per cluster
3. Long/short recommendations
4. Correlated moves to watch
5. Risk management guidance

## Next Steps

### Real Data Integration
Replace synthetic data with:
- **Stocks**: Tastytrade API, Alpha Vantage, or Yahoo Finance
- **Futures**: CME DataMine, Interactive Brokers, or Tastytrade

### Automated Trading
- Connect to broker API (Tastytrade, Interactive Brokers)
- Implement bracket order execution
- Add position tracking and P&L

### Enhanced Patterns
- Track pattern evolution over time
- Detect regime changes (cluster switching)
- Backtest which anomalies predict moves

## API Keys Needed

### Jarvis (already configured)
- Base URL: `https://staging.nodes.bio`
- Token in `jarvis.txt`

### Market Data (choose one)
- **Tastytrade**: Already in `.env` (sandbox currently down)
- **Alpha Vantage**: Free tier, get key at alphavantage.co
- **Interactive Brokers**: TWS API for real-time futures

## Architecture

```
Market Open (9:30 AM)
    ↓
Capture Data (stocks + futures)
    ↓
Extract Features (price, volume, momentum)
    ↓
DBSCAN Clustering (unsupervised learning)
    ↓
Identify Anomalies + Clusters
    ↓
Ask Jarvis for Analysis
    ↓
Generate Trading Signals
    ↓
Display Dashboard
    ↓
Repeat every 5 minutes
```

## The Edge

**Attention arbitrage**: Nobody is systematically watching micro-caps + futures patterns with unsupervised learning + multi-model AI analysis.

**Free data**: Market quotes are public. The edge is in the systematic process.

**Boring = moat**: Most people won't do this. That's the point.
