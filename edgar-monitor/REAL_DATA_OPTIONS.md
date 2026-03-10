# Real Market Data Options

## Current Situation

**Tastytrade**: Uses DXFeed websocket streaming (not REST API for quotes). Good for real-time trading, overkill for 5-minute scans.

## Best Options for Your Use Case

### 1. **Polygon.io** (Recommended)
- **Free tier**: 5 API calls/minute
- **Stocks + Futures**: Full CME coverage
- **REST API**: Simple, no websockets needed
- **Cost**: Free for development, $29/mo for real-time

```python
# Example
import requests
url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey=YOUR_KEY"
```

### 2. **Alpha Vantage**
- **Free tier**: 25 calls/day (too limited)
- **Stocks only**: No futures
- **Cost**: $50/mo for 75 calls/minute

### 3. **Yahoo Finance** (Unofficial)
- **Free**: No API key needed
- **Rate limited**: ~2000 calls/hour
- **Stocks + Futures**: Works but unreliable

### 4. **Interactive Brokers TWS API**
- **Free**: With IB account
- **Everything**: Stocks, futures, options, forex
- **Complex**: Requires TWS running

## Recommendation

**For production**: Use **Polygon.io**
- Free tier works for 30 stocks + 10 futures every 5 min
- Upgrade to $29/mo when ready
- Clean REST API, no websockets

**For now**: Keep using synthetic data
- Pattern detection works the same
- Swap in real data when ready
- No API limits during development

## Implementation

I can build a Polygon.io connector in 5 minutes when you're ready. Just need an API key from polygon.io/dashboard/signup.

**Tastytrade is better for**:
- Actual order execution (bracket orders)
- Real-time streaming during active trades
- Not for periodic market scans
