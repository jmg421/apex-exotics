#!/bin/bash
# Apex Exotics — Unified Dashboard Launcher
# Starts all backends + gateway, opens browser

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS=()

cleanup() {
  echo "Shutting down..."
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null; done
  wait 2>/dev/null
  echo "Done."
}
trap cleanup EXIT INT TERM

echo "🚀 Apex Exotics — Starting unified dashboard"
echo ""

# 1. Sports monitor (port 5001)
echo "  Starting sports-monitor on :5001..."
cd "$ROOT/sports-monitor"
python3 dashboard.py &
PIDS+=($!)

# 2. Edgar monitor (port 5002)
echo "  Starting edgar-monitor on :5002..."
cd "$ROOT/edgar-monitor"
source venv/bin/activate 2>/dev/null
python3 dashboard.py &
PIDS+=($!)

# 3. Gateway (port 5000)
sleep 1
echo "  Starting gateway on :5000..."
cd "$ROOT/dashboard"
python3 dashboard.py &
PIDS+=($!)

sleep 2
echo ""
echo "✅ All systems running"
echo "   Gateway:  http://localhost:5001"
echo "   Sports:   http://localhost:5001"
echo "   Markets:  http://localhost:5002"
echo ""

# Open browser
open "http://localhost:5001" 2>/dev/null || true

echo "Press Ctrl+C to stop all"
wait
