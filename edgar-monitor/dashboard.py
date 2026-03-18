#!/usr/bin/env python3
"""Simple web dashboard for portfolio tracking."""

from flask import Flask, render_template, jsonify, request
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

@app.route('/trainer')
def trainer():
    """Chart trainer page."""
    return render_template('chart_trainer.html')

@app.route('/api/trainer/chart')
def api_trainer_chart():
    """Get candle data for chart trainer. Returns visible + hidden candles for quiz."""
    from chart_trainer import get_candles, find_pivots, detect_trend, find_support_resistance, find_patterns
    import random

    mode = request.args.get('mode', 'quiz')
    candles = get_candles(period='5d')

    if mode == 'learn':
        pivots = find_pivots(candles)
        support, resistance = find_support_resistance(pivots)
        return jsonify({
            'candles': candles,
            'trend': detect_trend(pivots),
            'support': support,
            'resistance': resistance,
            'patterns': find_patterns(candles),
            'pivots': pivots,
        })

    # Quiz mode: pick random window
    start = random.randint(0, len(candles) - 30)
    visible = candles[start:start + 20]
    hidden = candles[start + 20:start + 24]

    pivots = find_pivots(visible)
    trend = detect_trend(pivots)
    support, resistance = find_support_resistance(pivots)
    patterns = find_patterns(visible)

    last_price = visible[-1]['close']
    future_close = hidden[-1]['close'] if hidden else last_price
    actual = 'UP' if future_close > last_price else 'DOWN'

    return jsonify({
        'candles': visible,
        'trend': trend,
        'support': support,
        'resistance': resistance,
        'patterns': patterns,
        'last_price': last_price,
        'answer': actual,
        'future_price': future_close,
        'move': round(future_close - last_price, 2),
    })

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

@app.route('/api/futures')
def api_futures():
    """Get futures price data."""
    futures_file = DATA_DIR / "futures_data.json"
    if futures_file.exists():
        with open(futures_file) as f:
            return jsonify(json.load(f))
    
    # Return empty data
    return jsonify({"ES": [], "NQ": []})

@app.route('/api/futures/update', methods=['POST'])
def api_futures_update():
    """Update futures price data."""
    data = request.json
    futures_file = DATA_DIR / "futures_data.json"
    
    with open(futures_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({"status": "ok"})

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

@app.route('/api/psychology')
def api_psychology():
    """Get current psychology state — emotional state, consistency, violations."""
    from trading_psychology import TradeJournal, ConsistencyMetrics, EmotionalStateMonitor
    
    journal = TradeJournal()
    recent = journal.get_recent_trades()
    
    # Today's trades only
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    todays_trades = [t for t in recent if t.get('timestamp', '').startswith(today)]
    
    # Emotional state
    state, warnings = EmotionalStateMonitor().check_state(recent)
    
    # Consistency
    consistency = ConsistencyMetrics().calculate_consistency_score(todays_trades)
    
    # Recent violations
    violations = []
    for t in reversed(todays_trades):
        for v in t.get('violations', []):
            violations.append(v)
    
    # Daily trade count vs limit
    psych_cfg = json.loads((DATA_DIR.parent / 'config' / 'psychology.json').read_text())
    
    return jsonify({
        'emotional_state': state,
        'warnings': warnings,
        'consistency_score': consistency['consistency_score'],
        'consistency_grade': consistency['grade'],
        'consistency_breakdown': consistency['breakdown'],
        'trade_count': len(todays_trades),
        'max_daily_trades': psych_cfg.get('max_daily_trades', 5),
        'recent_violations': violations[:10],
    })

@app.route('/api/intraday/<ticker>')
def api_intraday(ticker):
    """Get intraday candlestick data for a ticker."""
    import random
    from datetime import datetime, timedelta
    
    demo_mode = datetime.now().weekday() >= 5 or datetime.now().hour < 9 or datetime.now().hour >= 16
    
    if demo_mode:
        portfolio = load_portfolio()
        if ticker not in portfolio['positions']:
            return jsonify({'error': 'Ticker not found'}), 404
        
        base_price = portfolio['positions'][ticker]['avg_price']
        now = datetime.now()
        candles = []
        price = base_price
        
        # Random walk with momentum — each candle continues from the last
        momentum = 0
        for i in range(50):
            candle_time = now - timedelta(seconds=(50 - i) * 10)
            open_price = price
            
            # Momentum with mean reversion toward base
            momentum = momentum * 0.7 + random.gauss(0, 0.004)
            reversion = (base_price - price) / base_price * 0.1
            move = momentum + reversion
            
            close_price = open_price * (1 + move)
            
            # Wicks extend beyond body
            wick_up = abs(random.gauss(0, 0.003))
            wick_down = abs(random.gauss(0, 0.003))
            high = max(open_price, close_price) * (1 + wick_up)
            low = min(open_price, close_price) * (1 - wick_down)
            
            candles.append({
                't': int(candle_time.timestamp() * 1000),
                'o': round(open_price, 2),
                'h': round(high, 2),
                'l': round(low, 2),
                'c': round(close_price, 2)
            })
            price = close_price
        
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
    
    app.run(host='0.0.0.0', debug=False, port=5002)
