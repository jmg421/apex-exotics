#!/usr/bin/env python3
"""Generate simulated historical data for demo purposes."""

import json
from pathlib import Path
from datetime import datetime, timedelta
import random

DATA_DIR = Path(__file__).parent / "data"
TRACKING_FILE = DATA_DIR / "portfolio_tracking.json"
STARTING_CAPITAL = 100_000

def generate_demo_history(days=30):
    """Generate simulated historical performance data."""
    
    history = []
    current_value = STARTING_CAPITAL
    
    # Generate daily snapshots going back
    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        
        # Random daily return between -2% and +2%
        daily_return = random.uniform(-0.02, 0.02)
        current_value *= (1 + daily_return)
        
        snapshot = {
            'date': date.isoformat(),
            'total_value': current_value,
            'cash': 43424.60,
            'invested': current_value - 43424.60,
            'total_return': current_value - STARTING_CAPITAL,
            'total_return_pct': ((current_value - STARTING_CAPITAL) / STARTING_CAPITAL) * 100,
            'positions': [],
            'sp500_price': 450 + random.uniform(-10, 10)
        }
        
        history.append(snapshot)
    
    # Save
    with open(TRACKING_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"✓ Generated {days} days of demo history")
    print(f"  Starting value: ${STARTING_CAPITAL:,.2f}")
    print(f"  Ending value: ${current_value:,.2f}")
    print(f"  Total return: ${current_value - STARTING_CAPITAL:+,.2f} ({((current_value - STARTING_CAPITAL) / STARTING_CAPITAL) * 100:+.2f}%)")

if __name__ == '__main__':
    generate_demo_history(30)
