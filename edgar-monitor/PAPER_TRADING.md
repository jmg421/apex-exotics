# Paper Trading System

Track ENIS recommendations with simulated $100k portfolio.

## Usage

```bash
# Initialize portfolio
python paper_trading.py init

# Buy stock
python paper_trading.py buy TICKER SHARES "reason"
python paper_trading.py buy IBCP 500 "HOLD recommendation"

# Sell stock
python paper_trading.py sell TICKER SHARES "reason"

# View portfolio
python paper_trading.py portfolio

# View trade history
python paper_trading.py trades
```

## Current Portfolio

**Starting Capital:** $100,000

**Positions:**
- IBCP: 500 shares @ $34.23 (HOLD - strong fundamentals, 31% margin)

## Strategy

Following ENIS recommendations:
- BUY: Full position (10-20% of portfolio)
- HOLD: Half position (5-10% of portfolio)
- AVOID: No position

Track performance over time to validate the attention arbitrage thesis.
