"""Risk management module for safe trading."""
import os
from datetime import datetime, date
from typing import Optional
import json

# Risk limits
MAX_POSITION_SIZE = 100  # shares per trade
MAX_PORTFOLIO_RISK = 0.02  # 2% of account per trade
MAX_DAILY_LOSS = 0.05  # 5% daily drawdown limit
MIN_ACCOUNT_VALUE = 500  # minimum account size

# Trading mode
DRY_RUN = True  # Set to False for live trading

class RiskManager:
    def __init__(self, log_file="trades.json"):
        self.log_file = log_file
        self.trades = self._load_trades()
    
    def _load_trades(self):
        """Load trade history."""
        if os.path.exists(self.log_file):
            with open(self.log_file) as f:
                return json.load(f)
        return []
    
    def _save_trades(self):
        """Save trade history."""
        with open(self.log_file, 'w') as f:
            json.dump(self.trades, f, indent=2)
    
    def get_daily_pnl(self) -> float:
        """Calculate today's P&L."""
        today = date.today().isoformat()
        return sum(t['pnl'] for t in self.trades 
                   if t.get('exit_date', '').startswith(today) and 'pnl' in t)
    
    def validate_order(self, account_value: float, symbol: str, 
                      position_size: int, stop_loss: float) -> tuple[bool, Optional[str]]:
        """
        Validate order against risk limits.
        Returns (is_valid, error_message)
        """
        # Check account minimum
        if account_value < MIN_ACCOUNT_VALUE:
            return False, f"Account value ${account_value:.2f} below minimum ${MIN_ACCOUNT_VALUE}"
        
        # Check position size
        if position_size > MAX_POSITION_SIZE:
            return False, f"Position {position_size} exceeds max {MAX_POSITION_SIZE}"
        
        # Check per-trade risk
        risk_amount = position_size * abs(stop_loss)
        risk_pct = risk_amount / account_value
        if risk_pct > MAX_PORTFOLIO_RISK:
            return False, f"Risk {risk_pct:.1%} exceeds {MAX_PORTFOLIO_RISK:.1%} limit"
        
        # Check daily loss limit
        daily_pnl = self.get_daily_pnl()
        daily_loss_pct = abs(daily_pnl) / account_value if daily_pnl < 0 else 0
        if daily_loss_pct >= MAX_DAILY_LOSS:
            return False, f"Daily loss {daily_loss_pct:.1%} hit limit {MAX_DAILY_LOSS:.1%}"
        
        return True, None
    
    def log_entry(self, symbol: str, quantity: int, entry_price: float, 
                  stop_loss: float, targets: list[float], order_id: str):
        """Log trade entry."""
        trade = {
            'symbol': symbol,
            'quantity': quantity,
            'entry_price': entry_price,
            'entry_date': datetime.now().isoformat(),
            'stop_loss': stop_loss,
            'targets': targets,
            'order_id': order_id,
            'status': 'open'
        }
        self.trades.append(trade)
        self._save_trades()
        return trade
    
    def log_exit(self, order_id: str, exit_price: float, quantity: int):
        """Log trade exit and calculate P&L."""
        for trade in self.trades:
            if trade['order_id'] == order_id and trade['status'] == 'open':
                pnl = (exit_price - trade['entry_price']) * quantity
                trade['exit_price'] = exit_price
                trade['exit_date'] = datetime.now().isoformat()
                trade['pnl'] = pnl
                trade['quantity'] -= quantity
                if trade['quantity'] <= 0:
                    trade['status'] = 'closed'
                self._save_trades()
                return pnl
        return None
    
    def get_stats(self) -> dict:
        """Get trading statistics."""
        closed = [t for t in self.trades if t['status'] == 'closed' and 'pnl' in t]
        if not closed:
            return {'total_trades': 0, 'total_pnl': 0, 'win_rate': 0, 'avg_win': 0, 'avg_loss': 0}
        
        wins = [t['pnl'] for t in closed if t['pnl'] > 0]
        losses = [t['pnl'] for t in closed if t['pnl'] < 0]
        
        return {
            'total_trades': len(closed),
            'total_pnl': sum(t['pnl'] for t in closed),
            'win_rate': len(wins) / len(closed) if closed else 0,
            'avg_win': sum(wins) / len(wins) if wins else 0,
            'avg_loss': sum(losses) / len(losses) if losses else 0,
            'largest_win': max(wins) if wins else 0,
            'largest_loss': min(losses) if losses else 0
        }

if __name__ == "__main__":
    # Test risk validation
    rm = RiskManager()
    
    # Valid order
    valid, msg = rm.validate_order(
        account_value=1000,
        symbol="AAPL",
        position_size=10,
        stop_loss=2.0  # $20 risk = 2% of account
    )
    print(f"Valid order: {valid}")
    
    # Too much risk
    valid, msg = rm.validate_order(
        account_value=1000,
        symbol="AAPL", 
        position_size=50,
        stop_loss=2.0  # $100 risk = 10% of account
    )
    print(f"Risky order: {valid} - {msg}")
    
    # Stats
    stats = rm.get_stats()
    print(f"\nStats: {stats}")
