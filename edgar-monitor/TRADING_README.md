# ENIS Trading System

**Systematic micro-cap trading using patented network analysis + LLM fundamental screening + automated execution**

## What It Does

1. **Analyzes** micro-cap 10-Ks using ENIS network analysis (US Patents 10,176,442 & 10,997,540)
2. **Screens** companies with LLM fundamental analysis (revenue quality, financial health, risks)
3. **Identifies** actionable BUY/SHORT signals with conviction levels
4. **Executes** trades automatically via Tastytrade API with scaled exits
5. **Manages** risk with hard limits (2% per trade, 5% daily loss)
6. **Tracks** all trades and generates daily P&L reports

## Safety Features

### Risk Controls
- **Max position size:** 100 shares per trade
- **Max risk per trade:** 2% of account
- **Max daily loss:** 5% of account value
- **Minimum account:** $500

### Dry-Run Mode
- Paper trade indefinitely before going live
- All features work exactly the same
- Zero risk, full audit trail
- Set `DRY_RUN = False` in `risk_manager.py` when ready

### Trade Logging
- Every signal logged with reasoning
- Every order logged with entry/exit/P&L
- Daily reports with win rate, avg win/loss
- Full audit trail in `trades.json`

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/jmg421/apex-exotics.git
cd apex-exotics/edgar-monitor
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
# Anthropic API (for LLM analysis)
ANTHROPIC_API_KEY=your_key_here

# Tastytrade API (for trading)
TASTYTRADE_CLIENT_SECRET=your_secret_here
TASTYTRADE_REFRESH_TOKEN=your_token_here
```

**Get Tastytrade credentials:**
1. Create account at https://developer.tastytrade.com/sandbox/
2. Create OAuth2 app
3. Generate refresh token (never expires)

### 5. Test Connection
```bash
python tastytrade_client.py
# Should show: "Accounts: X" and "AAPL: $XXX.XX / $XXX.XX"
```

## Usage

### Run Full Analysis + Auto-Trade
```bash
python auto_trader.py
```

This will:
1. Analyze all companies in ENIS database
2. Filter for actionable BUY/SHORT signals
3. Execute orders with scaled exits (dry-run by default)
4. Log all trades to `trades.json`

### Monitor Open Positions
```bash
python position_monitor.py
```

Checks all open positions against profit targets and stops.

### Generate Daily Report
```bash
python daily_report.py
```

Creates markdown report with:
- Signals found today
- Orders placed
- Positions closed
- Daily P&L
- Overall statistics

### Manual Order Execution
```python
from order_executor import OrderExecutor
import asyncio

async def main():
    executor = OrderExecutor()
    await executor.initialize()
    
    # Gary's scaled exit strategy
    await executor.place_scaled_exit_order(
        symbol="AAPL",
        quantity=3,
        stop_loss=10.0,      # $10 stop per share
        targets=[10, 20, 30]  # Exit 1 share at each target
    )

asyncio.run(main())
```

## Strategy

### Entry Signals
- **BUY:** ENIS score + LLM recommends BUY with MEDIUM/HIGH conviction
- **SHORT:** High risk score (≥7) or explicit SHORT recommendation

### Position Sizing
- **HIGH conviction:** 3 shares, targets [10, 20, 30]
- **MEDIUM conviction:** 2 shares, targets [10, 20]
- Risk validated before every order

### Exit Strategy (Gary's Method)
- **Scaled exits:** Exit 1 share at each profit target
- **Fixed stop:** All shares stopped at -$10/share
- **Risk/Reward:** Typically 1:2 or 1:3

### Example Trade
```
Entry: 3 shares @ $100
Stop: $90 (risk $30 total)
Targets:
  - Exit 1 @ $110 (+$10)
  - Exit 1 @ $120 (+$20)
  - Exit 1 @ $130 (+$30)
Total reward: $60
R:R = 1:2
```

## Files

### Core Trading
- `auto_trader.py` - Main entry point, connects analyzer to executor
- `order_executor.py` - Places orders with scaled exits
- `position_monitor.py` - Tracks open positions, manages exits
- `risk_manager.py` - Enforces risk limits, logs trades
- `tastytrade_client.py` - Tastytrade API wrapper

### Analysis
- `batch_analyzer.py` - Runs LLM analysis on all companies
- `enis_scorer.py` - Calculates ENIS network scores
- `network.py` - Builds relationship graphs from 10-Ks

### Reporting
- `daily_report.py` - Generates daily trading reports
- `trades.json` - Trade log (auto-created)
- `data/trading_report_*.md` - Daily reports

## Going Live

### Paper Trade First (Recommended)
1. Run `auto_trader.py` daily for 30 days
2. Review `trades.json` and daily reports
3. Verify win rate, avg win/loss, max drawdown
4. Ensure risk limits are working

### Switch to Live Trading
1. Open real Tastytrade account (not sandbox)
2. Update `.env` with production credentials
3. Set `DRY_RUN = False` in `risk_manager.py`
4. Start with small account ($500-1000)
5. Monitor closely for first week

### Production Deployment (Mac Mini)
```bash
# Hardwired ethernet for lower latency
git clone https://github.com/jmg421/apex-exotics.git
cd apex-exotics/edgar-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Copy .env with production credentials
python auto_trader.py
```

## Risk Warnings

⚠️ **This system trades real money. Understand the risks:**

- Past performance doesn't guarantee future results
- Micro-caps are illiquid and volatile
- Wide spreads can kill profitability
- System can have losing streaks
- Start small, scale slowly
- Never risk more than you can afford to lose

## Support

Questions? Issues? Open a GitHub issue or contact the maintainer.

## License

Proprietary. ENIS analysis uses patented technology (US Patents 10,176,442 & 10,997,540).
