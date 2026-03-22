"""
Cross-System Signal Bridge — Connects live sports events to market implications.

The thesis: live sports and financial markets are the same attention/money system
viewed from different angles. This module translates signals between them.

sports-monitor sees: close game, upset, overtime, star player injury
edgar-monitor sees: stock moves, SEC filings, volume anomalies
This module connects them.
"""
from datetime import datetime


# ── Publicly traded companies directly tied to live sports outcomes ───

SPORTS_BETTING_TICKERS = {
    'DKNG': 'DraftKings',
    'FLUT': 'Flutter (FanDuel parent)',
    'MGM': 'MGM Resorts (BetMGM)',
    'CZR': 'Caesars Entertainment',
    'PENN': 'Penn Entertainment (ESPN Bet)',
    'RSI': 'Rush Street Interactive',
    'GENI': 'Genius Sports (data/integrity)',
    'SRAD': 'Sportradar (odds/data feeds)',
}

MEDIA_TICKERS = {
    'DIS': 'Disney (ESPN)',
    'WBD': 'Warner Bros Discovery (TNT/TBS)',
    'PARA': 'Paramount (CBS)',
    'FOX': 'Fox Corp',
    'CMCSA': 'Comcast (NBC/Peacock)',
}

# NCAA integrity events affect these differently:
# - Betting companies: revenue risk from voided bets, regulatory scrutiny
# - Data companies (GENI, SRAD): increased demand for integrity monitoring
# - Media: viewership impact if scandal taints tournament


def sports_event_to_market_signal(event):
    """
    Translate a live sports event into potential market implications.
    
    Input: event dict from excitement_engine or similar
    Output: list of market signals to watch
    """
    signals = []
    sport = event.get('sport', '')
    excitement = event.get('excitement', 0)

    # High-excitement tournament game = betting volume spike
    if 'NCAA' in sport and excitement >= 70:
        signals.append({
            'type': 'VOLUME_SPIKE',
            'tickers': list(SPORTS_BETTING_TICKERS.keys()),
            'reason': f"High-excitement NCAA game: {event.get('away')} @ {event.get('home')} (excitement: {excitement})",
            'direction': 'NEUTRAL',  # volume up, direction depends on outcomes
            'urgency': 'MONITOR',
        })

    # Upset in progress (high seed leading low seed late)
    margin = abs(int(event.get('away_score', 0)) - int(event.get('home_score', 0)))
    if 'NCAA' in sport and excitement >= 80 and margin <= 5:
        signals.append({
            'type': 'UPSET_RISK',
            'tickers': ['DKNG', 'FLUT', 'PENN'],
            'reason': f"Potential upset: {event.get('away')} vs {event.get('home')} margin={margin}",
            'direction': 'VOLATILE',
            'urgency': 'WATCH',
        })

    # Overtime = extended broadcast = more ad revenue + more betting handle
    status = event.get('status', '')
    if 'OT' in status:
        signals.append({
            'type': 'OVERTIME_PREMIUM',
            'tickers': list(MEDIA_TICKERS.keys()) + ['DKNG', 'FLUT'],
            'reason': f"Overtime: {event.get('away')} @ {event.get('home')} — extended broadcast + betting",
            'direction': 'POSITIVE',
            'urgency': 'NOTE',
        })

    return signals


def integrity_event_to_market_signal(team, detail):
    """
    Translate an integrity/scandal event into market signals.
    The KSU case: DOJ indictment → betting company regulatory risk.
    """
    signals = []

    # Integrity scandal = regulatory risk for betting companies
    signals.append({
        'type': 'INTEGRITY_SCANDAL',
        'tickers': list(SPORTS_BETTING_TICKERS.keys()),
        'reason': f"Federal investigation: {team} — {detail}",
        'direction': 'NEGATIVE',
        'urgency': 'ALERT',
    })

    # But integrity/data companies benefit from increased demand
    signals.append({
        'type': 'INTEGRITY_DEMAND',
        'tickers': ['GENI', 'SRAD'],
        'reason': f"Integrity monitoring demand increases post-scandal: {team}",
        'direction': 'POSITIVE',
        'urgency': 'WATCH',
    })

    return signals


def ncaa_sanctions_to_market_signal(conference, num_programs):
    """
    NCAA sanctions affect conference media deals.
    17+ programs under investigation = potential conference revenue impact.
    """
    return [{
        'type': 'MEDIA_DEAL_RISK',
        'tickers': list(MEDIA_TICKERS.keys()),
        'reason': f"{num_programs} programs under investigation — conference media deal risk",
        'direction': 'MONITOR',
        'urgency': 'LONG_TERM',
    }]


# ── The unified attention model ──────────────────────────────────────
#
# Your three systems are watching the same thing from different angles:
#
#   sports-monitor:  GAME STATE  → excitement, upsets, overtime
#   march-madness:   TEAM STATS  → probabilities, matchup edges
#   edgar-monitor:   MONEY FLOW  → stock prices, SEC filings, volume
#
# The connection:
#
#   Game state changes → betting handle changes → betting company
#   revenue changes → stock price changes → SEC filing changes
#
# It's one pipeline. Your systems just tap in at different points.
#
# The KSU case shows what happens when someone corrupts the pipeline
# at the source (game state). The corruption propagates downstream
# through every system: tainted stats, mispriced odds, fraudulent
# betting revenue, misleading financial statements.
#
# Your edge: you're the only person watching all three taps
# simultaneously. Everyone else is specialized — the sports bettor
# doesn't watch SEC filings, the stock trader doesn't watch game
# state, the bracket picker doesn't watch either.
#
# That's the real attention arbitrage.
# ─────────────────────────────────────────────────────────────────────
