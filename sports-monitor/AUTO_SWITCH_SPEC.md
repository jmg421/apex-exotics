# Auto-Switch Pipeline Spec — March Madness 2026

## Goal
Automatically switch the TV to the most exciting live tournament game, with priority boosts for model-flagged toss-ups.

## Confirmed Hardware
- VSeeBox IPTV → Broadlink RM4 Mini → IR channel switching
- All 4 March Madness channels tested and working:
  - CBS East: **28**
  - TBS East: **156**
  - TNT East: **162**
  - truTV East: **166**

## Pipeline

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ ESPN Scoreboard  │────▶│  Excitement   │────▶│  EPG Channel  │────▶│ Channel Switcher  │
│ API (live scores)│     │  Engine       │     │  Resolver     │     │ (Broadlink IR)    │
└─────────────────┘     └──────────────┘     └──────────────┘     └──────────────────┘
                              ▲
                              │
                        ┌─────┴──────┐
                        │ r1_schedule │
                        │ toss-up     │
                        │ boosts      │
                        └────────────┘
```

### Step 1: ESPN Live Scores (existing: `excitement_engine.py`)
- Polls `site.api.espn.com` NCAA scoreboard every 30 seconds
- Returns: teams, scores, time remaining, period, game state
- Already working, no changes needed

### Step 2: Excitement Scoring (modify: `excitement_engine.py`)
Current scoring (0-100):
- Score margin: ≤3 pts → +50, ≤7 → +35, ≤10 → +20, ≤15 → +10
- Second half: +20
- Final 5 min: +30
- Postseason: +20

**Add toss-up boost:**
- Load `data/r1_schedule.json`
- Match ESPN game to schedule entry (fuzzy team name match)
- If `tossup: true` → +15 bonus
- If `priority: "highest"` → +25 bonus
- Boost applies from tip-off so we catch upsets early

### Step 3: EPG Channel Resolver (new function in `epg_parser.py`)
- Map ESPN game → VSeeBox channel number
- Two strategies:
  1. **EPG lookup**: Query XMLTV feed, match game title to truTV/TBS/TNT/CBS program listings
  2. **Static fallback**: CBS/TBS/TNT/truTV each carry one game per window — if EPG is down, use the schedule to infer which network has which game

**Add to `epg_parser.py` CHANNEL_MAP:**
```python
# March Madness broadcast channels
28:  "WCBSDT.us",    # CBS East (or appropriate EPG ID)
156: "TBS.us",       # TBS East
162: "TNT.us",       # TNT East
166: "truTV.us",     # truTV East
```

### Step 4: Channel Switcher (existing: `channel_switcher.py`)
- Already working, tested on all 4 channels
- `change_channel(28)`, `change_channel(156)`, etc.
- No changes needed

## Main Loop: `march_madness_switcher.py` (new file)

```python
"""
Main auto-switch loop for March Madness.
Runs during game windows, checks every 30s, switches to most exciting game.
"""

MARCH_MADNESS_CHANNELS = {
    'CBS': 28,
    'TBS': 156,
    'TNT': 162,
    'truTV': 166,
}

loop:
  1. Fetch ESPN NCAA scoreboard
  2. Score each live game with excitement_engine (includes toss-up boost)
  3. For top-scoring game, resolve which channel it's on via EPG
  4. If different from current channel:
     a. Log: "Switching to {away} vs {home} ({score}) on {network} — excitement {n}"
     b. Send IR via channel_switcher
     c. Update current_channel.json
  5. Sleep 30 seconds
```

## Switching Rules
- **Minimum excitement to switch**: 40 (don't switch to blowouts)
- **Hysteresis**: Current game gets +10 "stickiness" bonus (avoid ping-ponging)
- **Cooldown**: Don't switch more than once per 2 minutes
- **Halftime**: If current game is at halftime, switch immediately to best alternative
- **Manual override**: If user changes channel via remote, pause auto-switching for 5 minutes

## Edge Cases
- **Game ends**: Excitement drops to 0, auto-switch to next best game
- **All blowouts**: Stay on current channel (nothing exciting to switch to)
- **Commercial break**: Could integrate with `commercial_detector.py` later — switch during commercials, switch back when game returns
- **OT**: Overtime games get automatic +30 excitement bonus

## Files to Create/Modify
| File | Action | What |
|------|--------|------|
| `march_madness_switcher.py` | **CREATE** | Main loop |
| `excitement_engine.py` | **MODIFY** | Add toss-up boost from r1_schedule.json |
| `epg_parser.py` | **MODIFY** | Add CBS/TBS/TNT/truTV to CHANNEL_MAP |
| `espn_channels.py` | **MODIFY** | Add March Madness network→channel mapping |

## Testing Plan
1. **Wednesday night**: Run `excitement_engine.py` standalone, verify it picks up any live NCAA games
2. **Thursday morning before tip**: Run full pipeline in dry-run mode (log switches but don't send IR)
3. **Thursday 12:15 PM**: Go live for Window 1 (4 games)

## Success Criteria
- Switches to close games in final 5 minutes
- Prioritizes toss-up games (Santa Clara/Kentucky, BYU/TBD, etc.)
- Doesn't switch during exciting moments on current game (hysteresis)
- Doesn't rapid-fire switch (cooldown)
- Logs every decision for post-tournament review
