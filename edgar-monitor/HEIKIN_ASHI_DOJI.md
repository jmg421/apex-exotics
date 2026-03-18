# Heikin-Ashi Doji Patterns

## What are Heikin-Ashi Candles?

Heikin-Ashi (HA) is a Japanese candlestick technique that uses modified price data to filter out market noise and better identify trends.

**Formula:**
- HA Close = (Open + High + Low + Close) / 4
- HA Open = (Previous HA Open + Previous HA Close) / 2
- HA High = Max(High, HA Open, HA Close)
- HA Low = Min(Low, HA Open, HA Close)

## Heikin-Ashi Doji

A Heikin-Ashi Doji occurs when the HA Open and HA Close are equal (or very close), creating a candle with little to no body.

### Key Characteristics:
- Small or no body (Open ≈ Close)
- Upper and lower shadows present
- Indicates indecision or potential trend reversal
- More reliable than traditional Doji due to smoothing effect

## Trading Signals

### Bullish HA Doji
- Appears after downtrend
- Small body near the low
- Long upper shadow
- **Signal:** Potential reversal to uptrend
- **Confirmation:** Next candle closes higher with no lower shadow

### Bearish HA Doji
- Appears after uptrend
- Small body near the high
- Long lower shadow
- **Signal:** Potential reversal to downtrend
- **Confirmation:** Next candle closes lower with no upper shadow

### Continuation Doji
- Appears mid-trend
- Equal shadows on both sides
- **Signal:** Brief consolidation, trend likely continues
- **Action:** Hold position, wait for confirmation

## Detection Logic

```python
def is_heikin_ashi_doji(candle, threshold=0.1):
    """
    Detect Heikin-Ashi Doji pattern
    
    Args:
        candle: dict with 'open', 'high', 'low', 'close'
        threshold: max body size as % of total range
    
    Returns:
        bool: True if Doji detected
    """
    ha_close = (candle['open'] + candle['high'] + candle['low'] + candle['close']) / 4
    ha_open = candle['ha_open']  # From previous candle
    
    body = abs(ha_close - ha_open)
    total_range = candle['high'] - candle['low']
    
    if total_range == 0:
        return False
    
    body_ratio = body / total_range
    
    return body_ratio <= threshold

def classify_ha_doji(candle, prev_trend):
    """
    Classify Heikin-Ashi Doji type
    
    Args:
        candle: current HA candle
        prev_trend: 'up', 'down', or 'neutral'
    
    Returns:
        str: 'bullish_reversal', 'bearish_reversal', or 'continuation'
    """
    ha_close = (candle['open'] + candle['high'] + candle['low'] + candle['close']) / 4
    ha_open = candle['ha_open']
    
    upper_shadow = candle['high'] - max(ha_open, ha_close)
    lower_shadow = min(ha_open, ha_close) - candle['low']
    
    if prev_trend == 'down' and lower_shadow < upper_shadow:
        return 'bullish_reversal'
    elif prev_trend == 'up' and upper_shadow < lower_shadow:
        return 'bearish_reversal'
    else:
        return 'continuation'
```

## Integration with edgar-monitor

### Pattern Scanner Enhancement
Add to `pattern_scanner.py`:
- Detect HA Doji in real-time
- Score based on trend context
- Alert on high-probability reversals

### Autonomous Trading
Add to `autonomous.py`:
- Use HA Doji as entry/exit signal
- Combine with volume confirmation
- Set stop-loss based on Doji shadows

### Dashboard Display
Add to `dashboard.py`:
- Visual indicator for HA Doji candles
- Color-code by type (bullish/bearish/continuation)
- Show historical accuracy stats

## Best Practices

1. **Always confirm:** Wait for next candle to confirm direction
2. **Volume matters:** Higher volume = stronger signal
3. **Trend context:** More reliable at trend extremes
4. **Combine indicators:** Use with RSI, MACD for confirmation
5. **Timeframe:** Works best on 15m, 1h, 4h charts

## Common Mistakes

- Trading Doji in isolation without confirmation
- Ignoring overall trend direction
- Not accounting for market volatility
- Confusing HA Doji with traditional Doji (different calculations!)

## Resources

- Original Heikin-Ashi research: Munehisa Homma (18th century)
- Modern application: Dan Valcu (2004)
- Backtesting: Test on historical data before live trading
