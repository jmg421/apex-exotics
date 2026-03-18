# Heart Rate Integration Spec

## Concept

Use Apple Watch heart rate as a physiological signal in `validate_trade`. Elevated HR during trade entry = you haven't truly accepted the risk (Douglas Ch. 8). The body doesn't lie.

## Architecture

```
Apple Watch → HealthKit → Shortcuts → HTTP POST → heartbridge (Python) → hr_data.json → validate_trade
```

## Components

### 1. Data Pipeline: Apple Watch → Python

**Option A: heartbridge (recommended)**
- PyPI package: `pip install heartbridge`
- Runs a local HTTP server that receives health data from iOS Shortcuts
- Exports to JSON/CSV automatically
- GitHub: https://github.com/mm/heartbridge

**Option B: Shortcuts → iCloud file**
- iOS Shortcut: "Find Health Samples where Type is Heart Rate, sorted by Date, limit 1"
- Save to iCloud Drive as JSON
- Python reads from `~/Library/Mobile Documents/` path
- Simpler but higher latency (iCloud sync delay)

**Sampling rate:**
- Passive: Apple Watch samples every ~10 minutes (not enough)
- Workout mode: Every ~5 seconds (ideal but drains battery)
- Compromise: Start an "Other" workout session during trading hours (9:30-4:00) for continuous sampling, triggered by a Shortcuts automation

### 2. Shortcuts Automation

```
Trigger: Time of Day = 9:25 AM (weekdays)
Actions:
  1. Start Workout (type: Other)  ← enables continuous HR
  2. Repeat every 30 seconds:
     - Find Health Samples (Heart Rate, last 1, sorted by date)
     - Get Contents of URL: POST http://localhost:8080/heartrate
       Body: {"bpm": [sample], "timestamp": [current date]}
```

Second automation at 4:05 PM to stop the workout.

### 3. Python: PhysiologicalMonitor

```python
class PhysiologicalMonitor:
    def __init__(self, hr_file='data/hr_data.json', baseline_bpm=None,
                 spike_threshold=20, stale_seconds=120):
        self.hr_file = Path(hr_file)
        self.spike_threshold = spike_threshold
        self.stale_seconds = stale_seconds
        self.baseline = baseline_bpm  # None = auto-calculate

    def get_current_hr(self):
        """Read latest HR sample. Returns (bpm, timestamp) or (None, None)."""

    def calculate_baseline(self, window_minutes=30):
        """Rolling average of last 30 min as baseline."""

    def check_state(self):
        """
        Returns (state, message):
          NORMAL  - HR within baseline range → trade allowed
          ELEVATED - HR > baseline + threshold → flag (soft or hard gate)
          UNKNOWN  - No recent data → degrade gracefully, don't block
        """
```

### 4. Integration into validate_trade

```python
def validate_trade(trade_plan, account_balance, recent_trades):
    # 1. RiskAcceptance (existing)
    # 2. RuleAdherence (existing)
    # 3. EmotionalStateMonitor (existing)
    # 4. PhysiologicalMonitor (NEW)

    hr_monitor = PhysiologicalMonitor()
    hr_state, hr_msg = hr_monitor.check_state()

    if hr_state == 'ELEVATED':
        # Soft gate: add as emotional flag, don't hard-block
        # Contributes toward TILT threshold
        ...
```

## Design Decisions

**Soft gate, not hard gate.** Elevated HR is one more flag feeding into EmotionalStateMonitor's CAUTION/TILT calculation. Reason: HR can spike from coffee, standing up, excitement about a good setup. Hard-blocking on HR alone would produce false positives. But HR + revenge pattern + overtrading = TILT is a strong signal.

**Graceful degradation.** If no HR data (watch not worn, Shortcuts not running, stale data), the system works exactly as it does today. HR is additive, not required.

**Auto-baseline, not fixed.** Everyone's resting HR is different, and it varies day to day. Rolling 30-min average adapts to your current state. Spike = deviation from YOUR normal, not an absolute number.

**Stale data cutoff: 2 minutes.** If the last HR sample is older than 2 min, treat as UNKNOWN. Don't make decisions on stale physiology.

## Data Format (hr_data.json)

```json
{
  "samples": [
    {"bpm": 72, "timestamp": "2026-03-14T10:30:00"},
    {"bpm": 68, "timestamp": "2026-03-14T10:30:30"},
    {"bpm": 91, "timestamp": "2026-03-14T10:31:00"}
  ]
}
```

## Implementation Order

1. Create `config/psychology.json` with HR thresholds
2. Write `PhysiologicalMonitor` class
3. Wire into `validate_trade` as soft flag
4. Set up heartbridge + Shortcuts automation
5. Paper trade with HR logging for 1 week before using as gate
