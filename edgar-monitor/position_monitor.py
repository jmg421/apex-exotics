"""Position monitor: tracks open trades and manages exits."""
import asyncio
import json
from datetime import datetime
from tastytrade_client import get_session, get_quote
from risk_manager import RiskManager, DRY_RUN

class PositionMonitor:
    def __init__(self):
        self.risk_manager = RiskManager()
        self.session = None
    
    async def initialize(self):
        """Initialize session."""
        self.session = await get_session()
    
    def get_open_positions(self):
        """Get all open positions from trade log."""
        return [t for t in self.risk_manager.trades if t['status'] == 'open']
    
    async def check_exits(self):
        """Check if any positions hit profit targets or stops."""
        open_positions = self.get_open_positions()
        
        if not open_positions:
            print("No open positions to monitor.")
            return
        
        print(f"\n📊 Monitoring {len(open_positions)} open positions...")
        
        for position in open_positions:
            symbol = position['symbol']
            entry_price = position['entry_price']
            stop_loss = position['stop_loss']
            targets = position['targets']
            quantity = position['quantity']
            
            # Get current quote
            quote = await get_quote(self.session, symbol)
            current_price = float(quote.bid_price)
            
            pnl = (current_price - entry_price) * quantity
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            print(f"\n{symbol}:")
            print(f"  Entry: ${entry_price:.2f}")
            print(f"  Current: ${current_price:.2f}")
            print(f"  P&L: ${pnl:.2f} ({pnl_pct:+.1f}%)")
            print(f"  Stop: ${entry_price - stop_loss:.2f}")
            print(f"  Targets: {[f'${entry_price + t:.2f}' for t in targets]}")
            
            # Check stop loss
            if current_price <= (entry_price - stop_loss):
                print(f"  🛑 STOP HIT - Exit all {quantity} shares")
                if not DRY_RUN:
                    # TODO: Place market sell order
                    pass
                self.risk_manager.log_exit(position['order_id'], current_price, quantity)
                continue
            
            # Check profit targets (scale out)
            for i, target in enumerate(targets):
                if current_price >= (entry_price + target):
                    shares_to_exit = 1  # Exit 1 share per target
                    print(f"  ✅ TARGET {i+1} HIT - Exit {shares_to_exit} share(s)")
                    if not DRY_RUN:
                        # TODO: Place limit sell order
                        pass
                    self.risk_manager.log_exit(position['order_id'], current_price, shares_to_exit)
                    break

async def main():
    """Monitor positions."""
    monitor = PositionMonitor()
    await monitor.initialize()
    await monitor.check_exits()

if __name__ == "__main__":
    asyncio.run(main())
