# March Madness Dashboard Integration Spec

## Overview
Integrate March Madness bracket intelligence into the sports dashboard sidebar with automatic channel switching for live tournament games.

## Components

### 1. Sidebar Integration
**Location:** Replace right sidebar content when "🏀 Bracket" button clicked

**Content Sections:**
- **Upset Alerts** (top priority)
  - Show vulnerable favorites with upset probability scores
  - Display matchup factors (tempo, defense, 3PT, etc.)
  - Click to auto-switch to that game's channel if live

- **Injury Watch** (critical for bracket decisions)
  - Real-time injury status for top seeds
  - Impact assessment (-5% for starting PG/C, -2% for bench)
  - Auto-refresh every 5 minutes during tournament

- **Live Tournament Games** (during March Madness)
  - Current games on ESPN channels
  - One-click channel switching
  - Score + upset probability indicator

### 2. Automatic Channel Switching
**Trigger Conditions:**
1. High-upset-probability game starts (score ≥ 7)
2. Close game in final 5 minutes (within 5 points)
3. Major upset in progress (underdog leading by 10+)

**Logic:**
```python
def should_auto_switch(game):
    if game.upset_score >= 7 and game.time_remaining > 35:
        return True, "High upset potential"
    
    if game.time_remaining <= 5 and abs(game.score_diff) <= 5:
        return True, "Close finish"
    
    if game.underdog_leading and game.score_diff >= 10:
        return True, "Major upset alert"
    
    return False, None
```

**User Control:**
- Manual mode toggle (disable auto-switching)
- "Return to previous channel" button after auto-switch
- Notification before switching (3 second countdown)

### 3. Data Sources

**Upset Predictions:**
- Source: `march-madness-2026/upset_detector.py`
- Refresh: Once daily (morning of game day)
- Storage: `upset_alerts.csv`

**Injury Data:**
- Source: ESPN API + manual verification
- Refresh: Every 5 minutes during tournament
- Storage: `injury_status.json`

**Live Games:**
- Source: EPG parser (`epg_parser.py`)
- Refresh: Every 30 seconds
- Match with upset predictions for enhanced display

### 4. UI Flow

**Button Click:**
```
User clicks "🏀 Bracket" 
  → Sidebar switches to March Madness view
  → Load upset alerts from API
  → Load injury watch list
  → Load live tournament games from EPG
  → Display in sidebar (not popup)
```

**Sidebar Layout:**
```
┌─────────────────────────────┐
│ 🏀 March Madness            │
├─────────────────────────────┤
│ 🚨 UPSET ALERTS             │
│ ┌─────────────────────────┐ │
│ │ Duke vs New Mexico      │ │
│ │ Score: 7 | TEMPO_TRAP   │ │
│ │ [📺 Watch Live]         │ │
│ └─────────────────────────┘ │
│                             │
│ ⚕️ INJURY WATCH             │
│ ┌─────────────────────────┐ │
│ │ ✅ Duke - All healthy   │ │
│ │ 🚨 Arizona - PG out     │ │
│ └─────────────────────────┘ │
│                             │
│ 📺 LIVE NOW                 │
│ ┌─────────────────────────┐ │
│ │ ESPN: Duke 45-42 NM     │ │
│ │ 🔥 Upset Alert! [CH809] │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

### 5. Implementation Steps

**Phase 1: Sidebar Integration** (30 min)
- [ ] Move March Madness content to sidebar instead of popup
- [ ] Add close button to return to game stats
- [ ] Style to match existing sidebar design

**Phase 2: Data Pipeline** (1 hour)
- [ ] Fix `march_madness_integration.py` import paths
- [ ] Create `injury_status.json` with mock data
- [ ] Add EPG filtering for ESPN tournament games
- [ ] Test API endpoint returns correct data

**Phase 3: Auto-Switching** (1 hour)
- [ ] Add upset detection logic to excitement engine
- [ ] Create notification system (3-sec countdown)
- [ ] Add manual mode toggle to UI
- [ ] Save/restore previous channel

**Phase 4: Polish** (30 min)
- [ ] Add loading states
- [ ] Error handling for missing data
- [ ] Refresh intervals
- [ ] Mobile responsive design

### 6. File Structure
```
sports-monitor/
├── march_madness_integration.py  # API integration
├── auto_switcher.py              # NEW: Auto-switch logic
├── dashboard.py                  # Add /api/march_madness endpoint
├── templates/
│   └── dashboard.html            # Sidebar integration
└── data/
    ├── upset_alerts.csv          # Daily predictions
    └── injury_status.json        # Live injury data
```

### 7. API Endpoints

**GET /api/march_madness**
```json
{
  "upsets": [
    {
      "matchup": "Duke vs New Mexico",
      "upset_score": 7,
      "flags": ["TEMPO_TRAP", "ELITE_DEFENSE"],
      "live": true,
      "channel": 809,
      "current_score": "45-42"
    }
  ],
  "injuries": [
    {"team": "Duke", "status": "healthy"},
    {"team": "Arizona", "player": "Starting PG", "status": "out", "impact": -5}
  ],
  "live_games": [
    {
      "channel": 809,
      "game": "Duke vs New Mexico",
      "score": "45-42",
      "time": "12:34 2H",
      "upset_alert": true
    }
  ]
}
```

**POST /api/auto_switch**
```json
{
  "enabled": true,
  "notify_before_switch": true,
  "countdown_seconds": 3
}
```

### 8. Success Metrics
- ✅ Sidebar loads in <1 second
- ✅ Auto-switch triggers within 5 seconds of upset condition
- ✅ Zero false positives (no switching to blowouts)
- ✅ User can disable and re-enable auto-switching
- ✅ Injury data updates every 5 minutes during tournament

### 9. Future Enhancements
- Bracket builder integration
- Historical upset patterns
- Player prop betting alerts
- Multi-game picture-in-picture
- Slack/Discord notifications for upsets

---

**Priority:** High  
**Complexity:** Medium  
**Timeline:** 3 hours total  
**Dependencies:** march-madness-2026 submodule, EPG parser, channel switcher
