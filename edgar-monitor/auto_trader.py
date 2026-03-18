"""Auto-trader: connects batch analyzer to order executor."""
import asyncio
from batch_analyzer import analyze_all_companies, filter_actionable
from order_executor import OrderExecutor
from risk_manager import DRY_RUN

async def auto_trade():
    """
    Run batch analyzer and automatically execute actionable signals.
    """
    # ZONE GUARD: Automated trading disabled.
    # The zone trader enforces single-instrument, fixed-size, psychology-gated trades.
    print("❌ Auto-trading disabled.")
    print("   Use zone_trader.py — the single gateway for all trades.")
    print("   python3 zone_trader.py long/short PRICE SIGNAL")
    return
    
    print(f"📊 Analyzed {len(results)} companies")
    
    # Filter for actionable signals
    actionable = filter_actionable(results)
    print(f"✅ Found {len(actionable)} actionable signals")
    
    if not actionable:
        print("No actionable signals found.")
        return
    
    # Initialize executor
    executor = OrderExecutor()
    await executor.initialize()
    
    # Execute orders for each signal
    for signal in actionable:
        symbol = signal['ticker']
        recommendation = signal['recommendation']
        conviction = signal.get('conviction', 'MEDIUM')
        
        print(f"\n{'='*60}")
        print(f"Signal: {recommendation} {symbol} ({conviction} conviction)")
        print(f"Reason: {signal.get('reasoning', 'N/A')[:100]}...")
        
        # Position sizing based on conviction
        if conviction == 'HIGH':
            quantity = 3
            stop_loss = 5.0
            targets = [10, 20, 30]
        else:  # MEDIUM
            quantity = 2
            stop_loss = 5.0
            targets = [10, 20]
        
        # Execute order
        try:
            order_id = await executor.place_scaled_exit_order(
                symbol=symbol,
                quantity=quantity,
                stop_loss=stop_loss,
                targets=targets
            )
            
            if order_id:
                print(f"✅ Order placed: {order_id}")
            else:
                print(f"❌ Order rejected (risk limits)")
                
        except Exception as e:
            print(f"❌ Error placing order: {e}")
    
    # Show summary stats
    print(f"\n{'='*60}")
    print("📊 Trading Summary:")
    stats = executor.risk_manager.get_stats()
    print(f"Total trades: {stats['total_trades']}")
    print(f"Total P&L: ${stats['total_pnl']:.2f}")
    print(f"Win rate: {stats['win_rate']:.1%}")
    
    if DRY_RUN:
        print("\n⚠️  DRY RUN MODE - No real orders executed")
        print("Set DRY_RUN=False in risk_manager.py to go live")

if __name__ == "__main__":
    asyncio.run(auto_trade())
