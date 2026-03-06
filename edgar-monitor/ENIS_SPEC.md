# EDGAR Network Intelligence System (ENIS)

**Apply patented network math to find overlooked companies. Make money. Don't get copied.**

## The Insight

Biological networks = Financial networks. Same math. Different domain.

Patents 10,176,442 & 10,997,540 cover the system and method. 20-year monopoly.

## What We're Building

**Input:** SEC 10-K filings (free, public, nobody reads them)

**Process:** 
1. Extract financials (revenue, margins, cash, debt)
2. Extract relationships (customers, suppliers, partners)
3. Build network graph
4. Apply patented MGF algorithm
5. Calculate: systemic importance, contagion risk, network value

**Output:** Ranked list of undervalued micro-caps with network intelligence

**Edge:** Patented math + systematic attention + free data = can't be replicated

## The Math (from patents)

```python
# MGF Threshold Distribution Algorithm
# Calculates network propagation metrics

def calculate_network_metrics(company, network):
    N = network.max_degree()
    p = network.degree_distribution()
    
    G0 = G1 = G2 = 0
    for k in range(N + 1):
        rhok = 1 if k <= 0 else threshold_func(1/k)
        sk = rhok * p[k]
        G0 += sk              # Connectivity
        G1 += k * sk          # Expected propagation
        G2 += k * (k-1) * sk  # Variance/risk
    
    return {
        'systemic_importance': G1 / G0,
        'contagion_risk': (G2 - G1**2) / (G1 + 1),
        'network_value': estimate_option_value(G0, G1, G2)
    }
```

## What We Build First

**Phase 1 (Now):** Relationship extractor
- Parse 10-Ks for major customers, suppliers, partners
- Build company relationship graph
- Store in network database

**Phase 2 (Next):** Network metrics
- Implement MGF algorithm
- Calculate systemic importance scores
- Add to existing financial scoring

**Phase 3 (Then):** Validation
- Backtest on historical data
- Prove alpha generation
- Show Gary the results

## Why This Wins

**Patents:** System and method protection. Can't be copied.
**Data:** Free SEC filings. No expensive feeds.
**Market:** Micro-caps nobody watches. Inefficient.
**Math:** Advanced network science. High barrier.
**Moat:** Compounds over time. More data = better network.

## Success = 

Find undervalued companies before anyone else. Take positions. Make money. Repeat.

Patent protection means nobody can replicate the method.

That's the entire strategy.
