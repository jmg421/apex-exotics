#!/Users/apple/apex-exotics/edgar-monitor/venv/bin/python3
"""
Weekly Trading Rhythm — the happy turtle is methodical and consistent.

Schedule (all times ET):
  Sunday    6:00pm  Futures open — HIGH ALERT scan every 30s for 30min, then every 5min
  Monday    6:00am  Pre-market prep: overnight recap + day plan
            9:25am  Opening scan burst (every 30s for 10min)
            9:35am  Regular rhythm: scan every 5min until 3:30pm
            3:30pm  EOD watch: scan every 2min until close
            4:05pm  EOD summary
  Tue-Thu   Same as Monday
  Friday    Same until 2:00pm
            2:00pm  STOP — no new trades. Monitor only, wider stops.
            4:05pm  Weekly review + digest
  Saturday  Off. Rest. Review journal.

Gary's rules:
  - Best time to trade: Sunday 6pm (futures open, weekend gap)
  - Worst time to trade: Friday afternoon (noise, book-squaring)
"""
import time
import subprocess
import json
import os
from datetime import datetime, timedelta

EDGAR_DIR = '/Users/apple/apex-exotics/edgar-monitor'
VENV_PY = f'{EDGAR_DIR}/venv/bin/python3'
LOG_FILE = f'{EDGAR_DIR}/data/weekly_rhythm_log.txt'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def run_scan(label):
    log(f"📊 {label}")
    try:
        subprocess.run(
            [VENV_PY, 'autonomous.py'],
            cwd=EDGAR_DIR, timeout=120,
            stdout=open(f'{EDGAR_DIR}/data/autonomous_log.txt', 'a'),
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        log(f"⚠️  Scan failed: {e}")

def run_digest():
    log("📋 Generating daily digest...")
    try:
        subprocess.run(
            [VENV_PY, 'daily_digest.py'],
            cwd=EDGAR_DIR, timeout=60,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        log(f"⚠️  Digest failed: {e}")

def run_psychology_report():
    log("🧠 Psychology report...")
    try:
        subprocess.run(
            [VENV_PY, 'psychology_report.py'],
            cwd=EDGAR_DIR, timeout=60,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        log(f"⚠️  Psychology report failed: {e}")

def get_phase():
    """Return current trading phase based on day/time."""
    now = datetime.now()
    day = now.weekday()  # 0=Mon, 6=Sun
    h, m = now.hour, now.minute
    t = h * 60 + m  # minutes since midnight

    if day == 5:  # Saturday
        return 'OFF', 0

    if day == 6:  # Sunday
        if t < 17 * 60 + 55:  # Before 5:55pm
            return 'OFF', 0
        if t < 18 * 60 + 30:  # 5:55pm - 6:30pm
            return 'FUTURES_OPEN', 30  # scan every 30s
        return 'FUTURES_EVENING', 300  # after 6:30pm, every 5min

    # Monday-Friday
    if day == 4 and t >= 14 * 60:  # Friday after 2pm
        if t < 16 * 60:
            return 'FRIDAY_STOP', 300  # monitor only
        if t < 16 * 60 + 10:
            return 'WEEKLY_REVIEW', 0
        return 'OFF', 0

    if t < 6 * 60:  # Before 6am
        return 'FUTURES_OVERNIGHT', 300
    if t < 9 * 60 + 25:  # 6am - 9:25am
        return 'PREMARKET', 300
    if t < 9 * 60 + 35:  # 9:25 - 9:35am
        return 'OPENING_BURST', 30
    if t < 15 * 60 + 30:  # 9:35am - 3:30pm
        return 'REGULAR', 300
    if t < 16 * 60:  # 3:30 - 4:00pm
        return 'EOD_WATCH', 120
    if t < 16 * 60 + 10:  # 4:00 - 4:10pm
        return 'EOD_SUMMARY', 0
    if t < 18 * 60:  # 4:10 - 6pm
        return 'FUTURES_EVENING', 300
    return 'FUTURES_OVERNIGHT', 300  # 6pm+

def run():
    log("🐢 Weekly Rhythm started — methodical and consistent")
    last_phase = None
    did_eod = False
    did_weekly = False

    while True:
        phase, interval = get_phase()

        # Phase transition announcements
        if phase != last_phase:
            log(f"{'='*50}")
            log(f"⏰ Phase: {phase}" + (f" (every {interval}s)" if interval else ""))
            log(f"{'='*50}")

            if phase == 'EOD_SUMMARY' and not did_eod:
                run_digest()
                run_psychology_report()
                did_eod = True
            elif phase == 'WEEKLY_REVIEW' and not did_weekly:
                run_digest()
                run_psychology_report()
                log("📅 WEEKLY REVIEW — check journal, review wins/losses")
                did_weekly = True
            elif phase == 'PREMARKET':
                did_eod = False
            elif phase == 'FUTURES_OPEN':
                log("🔔 FUTURES OPEN — Sunday gap, highest-signal window of the week")
                did_weekly = False

            last_phase = phase

        if phase == 'OFF':
            time.sleep(60)
            continue

        if phase == 'FRIDAY_STOP':
            log("🛑 Friday stop — no new trades, monitor only")
            run_scan("Friday monitor (no entries)")
            time.sleep(interval)
            continue

        if interval > 0:
            label = {
                'FUTURES_OPEN': '🔔 Sunday open scan',
                'FUTURES_OVERNIGHT': '🌙 Overnight futures',
                'FUTURES_EVENING': '🌆 Evening futures',
                'PREMARKET': '☀️ Pre-market',
                'OPENING_BURST': '🚀 Opening burst',
                'REGULAR': '📊 Regular scan',
                'EOD_WATCH': '⚡ EOD watch',
            }.get(phase, phase)
            run_scan(label)
            time.sleep(interval)
        else:
            time.sleep(60)

if __name__ == '__main__':
    run()
