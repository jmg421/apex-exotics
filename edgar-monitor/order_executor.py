"""Order execution module with dry-run support."""
import asyncio
from datetime import datetime
from risk_manager import RiskManager, DRY_RUN
from tastytrade_client import get_session, get_quote
from tastytrade import Account

class OrderExecutor:
    def __init__(self, account_number: str = None):
        self.risk_manager = RiskManager()
        self.account_number = account_number
        self.session = None
    
    async def initialize(self):
        """Initialize session and account."""
        self.session = await get_session()
        if not self.account_number:
            accounts = await Account.get(self.session)
            if accounts:
                self.account_number = accounts[0].account_number
    
    async def get_account_value(self) -> float:
        """Get current account value."""
        if DRY_RUN:
            return 1000.0  # Simulated account value
        
        account = await Account.get_account(self.session, self.account_number)
        balances = await account.get_balances(self.session)
        return float(balances.net_liquidating_value)
    
    async def place_scaled_exit_order(self, symbol: str, quantity: int = 3, 
                                     stop_loss: float = 10.0, 
                                     targets: list[float] = [10, 20, 30]):
        """
        Place order with scaled exits (Gary's strategy).
        
        Args:
            symbol: Stock symbol
            quantity: Number of contracts/shares (default 3)
            stop_loss: Stop loss in dollars per share (default $10)
            targets: Profit targets in dollars per share (default [10, 20, 30])
        """
        # Get current quote
        quote = await get_quote(self.session, symbol)
        entry_price = float(quote.ask_price)
        
        # Get account value
        account_value = await self.get_account_value()
        
        # Validate risk
        valid, error = self.risk_manager.validate_order(
            account_value, symbol, quantity, stop_loss
        )
        if not valid:
            print(f"❌ Order rejected: {error}")
            return None
        
        # Calculate risk/reward
        total_risk = quantity * stop_loss
        total_reward = sum(targets)
        risk_reward = total_reward / total_risk
        
        print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Order Preview:")
        print(f"Symbol: {symbol}")
        print(f"Entry: ${entry_price:.2f}")
        print(f"Quantity: {quantity}")
        print(f"Stop Loss: ${entry_price - stop_loss:.2f} (-${stop_loss}/share)")
        print(f"Targets: {[f'${entry_price + t:.2f} (+${t})' for t in targets]}")
        print(f"Risk: ${total_risk:.2f} ({total_risk/account_value:.1%} of account)")
        print(f"Reward: ${total_reward:.2f}")
        print(f"R:R = 1:{risk_reward:.1f}")
        
        if DRY_RUN:
            order_id = f"DRY_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"\n✅ DRY RUN: Order logged (not executed)")
        else:
            # TODO: Implement actual order placement via Tastytrade API
            order_id = "LIVE_ORDER_ID"
            print(f"\n✅ LIVE: Order placed")
        
        # Log trade
        self.risk_manager.log_entry(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            targets=targets,
            order_id=order_id
        )
        
        return order_id

async def main():
    """Test order execution."""
    executor = OrderExecutor()
    await executor.initialize()
    
    # Test Gary's strategy on AAPL (smaller size for $1000 account)
    await executor.place_scaled_exit_order(
        symbol="AAPL",
        quantity=2,  # 2 shares instead of 3
        stop_loss=5.0,  # $5 stop = $10 risk = 1% of $1000 account
        targets=[10, 20]  # $30 reward = 3:1 R:R
    )
    
    # Show stats
    stats = executor.risk_manager.get_stats()
    print(f"\n📊 Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
