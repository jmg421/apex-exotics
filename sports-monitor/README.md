# Sports Stats Monitor

**Live NCAA basketball margins - attention arbitrage in real-time**

## The Edge

Everyone watches the score. You watch the margins.

## What It Shows

**Score = Stock Price** (what everyone reacts to)
**Field Goal % = Gross Margin** (efficiency predicts future)
**Turnovers = Operating Expenses** (waste kills performance)
**Rebounds = Competitive Advantage** (control = moat)
**3-Point % = High-Margin Products** (50% more value per shot)

## The Pattern

Same as ENIS:
- Free public data (NCAA stats via free API)
- Systematic attention (automated monitoring)
- Margin analysis (efficiency over headlines)
- Predict outcomes before the market (score) reflects it

## Usage

```bash
cd sports-monitor
../venv/bin/python dashboard.py
```

Open http://localhost:5001

Dashboard auto-refreshes every 30 seconds with live game margins.

## Data Source

Free NCAA API: https://github.com/henrygd/ncaa-api
- Live scores
- Team stats (FG%, 3PT%, turnovers, rebounds)
- No authentication required
- 5 requests/second rate limit

## Next Steps

1. Add betting odds (show arbitrage opportunity)
2. Historical margin analysis (which margins predict best)
3. Alert system (when margins diverge from score)
4. Pattern recognition (comeback indicators)

---

**Attention arbitrage works everywhere:** Stocks, sports, car auctions. Find the stats nobody's watching systematically.
