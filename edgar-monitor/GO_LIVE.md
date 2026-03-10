# GO LIVE CHECKLIST

## Step 1: Get Real Market Data (TODAY)

### Option A: Yahoo Finance (Free, Start Now)
```bash
# Already works, just swap synthetic for real
python3 market_open_yahoo.py  # Try this first
```
- ✅ Free, no signup
- ⚠️ Rate limited, may fail
- ✅ Good enough to start

### Option B: Polygon.io (Best, $29/mo)
1. Sign up: https://polygon.io/dashboard/signup
2. Get API key (free tier: 5 calls/min)
3. I'll build connector in 5 minutes

### Option C: CME WebSocket (Futures only, ~$50/mo)
1. Sign up: https://dataservices.cmegroup.com/pages/CME-Data-Via-API
2. Get credentials
3. I'll build connector

**DO THIS NOW**: Try Option A (Yahoo), sign up for Option B (Polygon)

---

## Step 2: Connect Broker for Execution (TODAY)

You already have **Tastytrade** credentials. Let's use them.

### Test Your Tastytrade Account
```bash
python3 test_tastytrade.py
```

If sandbox is down, we'll use production API (paper trading mode).

**DO THIS NOW**: Verify Tastytrade login works

---

## Step 3: Place Your First Trade (TODAY)

I'll build a simple order executor:
- Connect to Tastytrade
- Take Jarvis signals
- Place bracket orders (3 contracts, stop + 3 targets)
- Track P&L

**DO THIS NOW**: Tell me your account number and I'll build the executor

---

## Step 4: Run Live System (TOMORROW 9:30 AM)

```bash
# Full live system
./run_live.sh
```

This will:
1. Scan markets at 9:30 AM
2. Detect patterns
3. Ask Jarvis for recommendations
4. **Show you the trades** (you approve manually first)
5. Execute bracket orders
6. Monitor positions

---

## Capital Requirements

**Minimum to start**:
- Futures: $500 margin per contract × 3 = $1,500
- Or stocks: $2,000 for micro-cap positions
- **Start with $2,000-3,000**

**Recommended**:
- $5,000-10,000 for comfortable trading
- Allows multiple positions + drawdowns

---

## Risk Management (CRITICAL)

**Hard rules I'll code in**:
- Max 3 positions at once
- Max $10 risk per trade (futures stop loss)
- Max 2% account risk per day
- Auto-stop if down $100 in a day

**DO THIS NOW**: Tell me your max daily loss limit

---

## What I Need From You

1. **Polygon.io API key** (sign up now, free tier works)
2. **Tastytrade account number** (from your .env or dashboard)
3. **Max daily loss** (e.g., $100, $200, $500)
4. **Starting capital** (how much in account?)

Give me those 4 things and I'll have you live by tomorrow morning.

---

## Timeline

**Today (next 30 min)**:
- You: Sign up for Polygon.io
- Me: Build real data connector
- Me: Build Tastytrade order executor

**Today (next 1 hour)**:
- Test full system with paper trades
- Verify orders execute correctly
- Set risk limits

**Tomorrow 9:30 AM**:
- Run live scan
- Get Jarvis signals
- Place first real trade

**LET'S GO. What's your Polygon API key and Tastytrade account number?**
