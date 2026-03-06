# Price Data Integration

## Alpha Vantage Setup

1. Get free API key: https://www.alphavantage.co/support/#api-key
2. Set environment variable:
   ```bash
   export ALPHA_VANTAGE_KEY="your_key_here"
   ```

3. Fetch prices:
   ```bash
   python price_fetcher.py
   ```

## Rate Limits

- Free tier: 5 calls/min, 500 calls/day
- Script auto-sleeps 12 seconds between calls
- Caches results for 1 hour

## Usage

```python
from price_fetcher import fetch_and_cache_prices, get_price_on_date

# Fetch and cache
cache = fetch_and_cache_prices(['AFCG', 'CLRB'])

# Get price on specific date
price = get_price_on_date('AFCG', '2026-03-06', cache)
```

## Validation Integration

Validation automatically uses cached prices if available, falls back to mock data.

To enable live validation:
1. Set ALPHA_VANTAGE_KEY
2. Run `python price_fetcher.py` to populate cache
3. Run `python validation.py` to see real hit rates
