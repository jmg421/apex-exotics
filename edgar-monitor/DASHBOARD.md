# ENIS Dashboard

Real-time web dashboard for portfolio tracking.

## Quick Start

```bash
# Start dashboard
python dashboard.py

# Open browser
open http://localhost:5000
```

## Features

- **Real-time portfolio value** - Updates every 60 seconds
- **Performance chart** - Historical tracking with Chart.js
- **Position breakdown** - All holdings with P&L
- **Visual allocation** - See portfolio weights at a glance

## Screenshots

Dashboard shows:
- Total value, return, return %, cash
- Line chart of portfolio performance over time
- Each position with shares, avg price, current price, P&L
- Allocation bars showing portfolio weights

## Data Sources

- Portfolio: `data/paper_portfolio.json`
- History: `data/portfolio_tracking.json`
- Prices: yfinance (real-time)

## Auto-refresh

Dashboard auto-refreshes every 60 seconds. Click "↻ Refresh" for manual update.
