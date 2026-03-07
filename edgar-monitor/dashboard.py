#!/usr/bin/env python3
"""Simple web dashboard for portfolio tracking."""

from flask import Flask, render_template, jsonify
from pathlib import Path
import json
from paper_trading import load_portfolio, get_current_price, STARTING_CAPITAL
from track_portfolio import load_tracking
import yfinance as yf

app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data"

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/portfolio')
def api_portfolio():
    """Get current portfolio data."""
    import random
    from datetime import datetime
    
    portfolio = load_portfolio()
    
    # Demo mode: simulate price movements if market is closed
    demo_mode = datetime.now().weekday() >= 5 or datetime.now().hour < 9 or datetime.now().hour >= 16
    
    # Calculate current values
    total_value = portfolio['cash']
    positions = []
    
    for ticker, pos in portfolio['positions'].items():
        if demo_mode:
            # Simulate small random movements (-0.5% to +0.5%)
            current_price = pos['avg_price'] * (1 + random.uniform(-0.005, 0.005))
        else:
            current_price = get_current_price(ticker)
        
        shares = pos['shares']
        avg_price = pos['avg_price']
        cost_basis = shares * avg_price
        current_value = shares * current_price
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis) * 100 if cost_basis else 0
        
        total_value += current_value
        
        positions.append({
            'ticker': ticker,
            'shares': shares,
            'avg_price': avg_price,
            'current_price': current_price,
            'value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'allocation': (current_value / total_value) * 100
        })
    
    # Sort by value
    positions.sort(key=lambda x: x['value'], reverse=True)
    
    total_return = total_value - STARTING_CAPITAL
    total_return_pct = (total_return / STARTING_CAPITAL) * 100
    
    return jsonify({
        'total_value': total_value,
        'cash': portfolio['cash'],
        'invested': total_value - portfolio['cash'],
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'positions': positions,
        'demo_mode': demo_mode
    })

@app.route('/api/scalping')
def api_scalping():
    """Get scalping account status."""
    scalping_file = DATA_DIR / "scalping_trades.json"
    if scalping_file.exists():
        with open(scalping_file) as f:
            return jsonify(json.load(f))
    
    # Return default account
    return jsonify({
        "starting_capital": 10000,
        "cash": 10000,
        "position": None,
        "trades": [],
        "total_pnl": 0
    })

@app.route('/api/news')
def api_news():
    """Get recent news alerts."""
    news_file = DATA_DIR / "news_alerts.json"
    if news_file.exists():
        with open(news_file) as f:
            data = json.load(f)
            # Return last 10 alerts, newest first
            return jsonify(list(reversed(data['alerts'][-10:])))
    return jsonify([])

@app.route('/api/history')
def api_history():
    """Get historical performance data."""
    tracking = load_tracking()
    
    if not tracking:
        return jsonify([])
    
    # Format for charting
    history = []
    for snapshot in tracking:
        history.append({
            'date': snapshot['date'][:10],
            'value': snapshot['total_value'],
            'return_pct': snapshot['total_return_pct']
        })
    
    return jsonify(history)

@app.route('/api/intraday/<ticker>')
def api_intraday(ticker):
    """Get intraday candlestick data for a ticker."""
    import random
    from datetime import datetime, timedelta
    
    demo_mode = datetime.now().weekday() >= 5 or datetime.now().hour < 9 or datetime.now().hour >= 16
    
    if demo_mode:
        # Generate historical demo candles (last 30 candles, 10 seconds apart)
        portfolio = load_portfolio()
        if ticker not in portfolio['positions']:
            return jsonify({'error': 'Ticker not found'}), 404
        
        base_price = portfolio['positions'][ticker]['avg_price']
        now = datetime.now()
        candles = []
        
        # Generate 30 historical candles
        for i in range(30):
            candle_time = now - timedelta(seconds=(30 - i) * 10)
            
            # Random walk from base price
            price_drift = random.uniform(-0.02, 0.02)  # -2% to +2% from base
            open_price = base_price * (1 + price_drift)
            
            # Intracandle movement
            high_move = random.uniform(0, 0.01)  # 0-1% above
            low_move = random.uniform(0, 0.01)   # 0-1% below
            close_move = random.uniform(-0.005, 0.005)  # -0.5% to +0.5%
            
            candles.append({
                't': int(candle_time.timestamp() * 1000),
                'o': round(open_price, 2),
                'h': round(open_price * (1 + high_move), 2),
                'l': round(open_price * (1 - low_move), 2),
                'c': round(open_price * (1 + close_move), 2)
            })
        
        return jsonify(candles)
    else:
        # Real market data - use yfinance 1-minute bars
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period='1d', interval='1m')
            
            candles = []
            for idx, row in df.iterrows():
                candles.append({
                    't': int(idx.timestamp() * 1000),
                    'o': round(row['Open'], 2),
                    'h': round(row['High'], 2),
                    'l': round(row['Low'], 2),
                    'c': round(row['Close'], 2)
                })
            
            return jsonify(candles)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*80)
    print("ENIS DASHBOARD")
    print("="*80)
    print()
    print("Starting web server...")
    print("Open: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    app.run(debug=True, port=5000)
