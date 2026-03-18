# Bug Tracker - Sports Monitor

**Generated:** 2026-03-12T20:35:00

## Critical Bugs

### Bug #1: Inconsistent Channel State File Paths
**Severity:** Critical  
**Impact:** Dashboard displays wrong channel (shows 809 when actual is 807)

**Root Cause:**
- `channel_switcher.py:77` writes to `current_channel.json` (root directory)
- `dashboard.py:49` reads from `data/current_channel.json` (subdirectory)
- `dashboard.py:1240,1324` reads from `current_channel.json` (root directory)

**Evidence:**
```python
# channel_switcher.py:77 - WRITES HERE
with open('current_channel.json', 'w') as f:
    json.dump({'channel': channel, 'sport': sport, 'timestamp': time.time()}, f)

# dashboard.py:49 - READS HERE (wrong location!)
with open('data/current_channel.json', 'r') as f:
    return jsonify(json.load(f))
```

**Result:** 
- `data/current_channel.json` contains stale data from March 8
- Dashboard API returns incorrect channel information
- Auto-switching logic may use wrong channel state

**Fix:**
Standardize on single path: `data/current_channel.json`

---

### Bug #2: Bare Except Clauses Hiding Errors
**Severity:** High  
**Impact:** Silent failures make debugging impossible

**Violations of debugging_best_practices.md:**
> "Don't Hide the Problem" - bare except clauses bury errors

**Locations:**
- `dashboard.py:51` - channel read failure hidden
- `channel_switcher.py:83` - channel write failure hidden  
- `smart_commercial_handler.py:29` - channel read failure hidden
- `smart_commercial_handler.py:45` - original channel read failure hidden
- `headline_source.py:41` - API failure hidden
- `headline_storage.py:49` - storage failure hidden

**Example:**
```python
# dashboard.py:51 - BAD
try:
    with open('data/current_channel.json', 'r') as f:
        return jsonify(json.load(f))
except:  # ❌ Hides ALL errors
    return jsonify({'channel': 'UNKNOWN', 'timestamp': None, 'peer_count': 0})
```

**Fix:**
```python
# GOOD
try:
    with open('data/current_channel.json', 'r') as f:
        return jsonify(json.load(f))
except FileNotFoundError:
    logger.warning("Channel state file not found")
    return jsonify({'channel': 'UNKNOWN', 'timestamp': None, 'peer_count': 0})
except json.JSONDecodeError as e:
    logger.error(f"Invalid channel state JSON: {e}")
    return jsonify({'channel': 'ERROR', 'timestamp': None, 'peer_count': 0})
```

**Total bare except clauses:** 85+ across codebase

---

### Bug #3: Hardcoded Absolute Paths
**Severity:** Medium  
**Impact:** Code breaks on other machines/deployments

**Locations:**
- `channel_monitor.py:18` - `/Users/apple/apex-exotics/sports-monitor/data/current_channel.json`
- `channel_monitor.py:24` - `/Users/apple/apex-exotics/sports-monitor/data/vseebox_channels.json`
- `channel_classifier.py:137` - `/Users/apple/apex-exotics/sports-monitor/data/channel_model.json`
- `identify_channel.py:33` - `/Users/apple/apex-exotics/sports-monitor/data/channel_model.json`

**Example:**
```python
# channel_monitor.py:18 - BAD
self.log_file = "/Users/apple/apex-exotics/sports-monitor/data/current_channel.json"
```

**Fix:**
```python
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
self.log_file = os.path.join(BASE_DIR, "data", "current_channel.json")
```

---

### Bug #4: Multiple Channel Detection Implementations
**Severity:** Medium  
**Impact:** Code duplication, unclear which to use, maintenance burden

**Duplicate Implementations:**
1. `ChannelClassifier` (channel_classifier.py) - ML-based identification
2. `ChannelIdentifier` (channel_identifier.py) - Peer-based identification  
3. `ChannelDetector` (channel_detector.py) - Change detection

**Methods:**
- `ChannelClassifier.identify_current_channel()`
- `ChannelIdentifier.identify_channel()`
- `identify_channel()` function in identify_channel.py

**From debugging_best_practices.md:**
> "Don't Re-Implement Existing Solutions" - check git history before implementing

**Fix:**
- Audit which implementation is actually used
- Consolidate into single authoritative implementation
- Remove dead code
- Document the chosen approach

---

### Bug #5: Inconsistent Channel Data Schemas
**Severity:** Medium  
**Impact:** Code expects different fields, potential crashes

**Schema 1 (root `current_channel.json`):**
```json
{
  "channel": 809,
  "sport": "nba",
  "timestamp": 1773351975.384215
}
```

**Schema 2 (`data/current_channel.json`):**
```json
{
  "channel": "1600 - Cincinnati Reds (Live)",
  "channel_number": "1600",
  "timestamp": "2026-03-08T16:45:12.184611",
  "peer_count": 9
}
```

**Differences:**
- `channel` type: integer vs string
- `timestamp` format: Unix epoch vs ISO 8601
- Schema 2 has `channel_number` and `peer_count` fields
- Schema 1 has `sport` field

**Impact:**
Code reading these files must handle both schemas or will crash

**Fix:**
Define single canonical schema and migration path

---

## Investigation Notes

**Method:** Software archaeology per debugging_best_practices.md
1. ✅ Inventory - explored codebase structure
2. ✅ Static analysis - grep for patterns, file paths, exceptions
3. ✅ Traced execution paths - followed channel state read/write
4. ✅ Identified root causes - not just symptoms

**Discovery trigger:** User reported channel 807 (BTN) but system showed 809

---

## Next Steps

1. Fix Bug #1 immediately (blocking correct operation)
2. Add logging to all exception handlers (Bug #2)
3. Create constants file for paths (Bug #3)
4. Audit and consolidate channel detection (Bug #4)
5. Define canonical channel state schema (Bug #5)
