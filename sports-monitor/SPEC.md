# Sports Monitor — Basketball IQ Trainer

## The Insight

Same insight as ENIS: pattern recognition is a trainable skill. Douglas says you can't see what you haven't internalized. A coach sees the pick-and-roll developing three passes before the shot. A casual fan sees the ball go in or not. The difference is reps — thousands of pattern exposures until recognition becomes automatic.

This system accelerates that process. Instead of watching 10,000 games, you watch annotated sequences that teach you what to look for, then test whether you can see it in real-time.

## Architecture

```
Sports Monitor
├── ingest.py           - Pull play-by-play + tracking data from NBA API
├── plays.py            - Classify plays into pattern types
├── trainer.py          - Interactive training: show sequence, quiz user
├── scanner.py          - Real-time game monitor: annotate plays as they happen
└── progress.py         - Track pattern recognition improvement over time
```

## Data Sources

### nba_api (Python package)
- `pip install nba_api`
- Free, unofficial client for stats.nba.com
- Play-by-play: every event in a game (shot, pass, turnover, foul)
- Player tracking: speed, distance, touches, passes
- Shot charts: location, defender distance, shot clock
- No auth required, rate-limited (~1 req/sec)

### NBA Player Tracking (Second Spectrum)
- Camera system: 25 fps positional data for all 10 players + ball
- Raw tracking data is NOT public (NBA sells to teams/media)
- Aggregated tracking stats ARE public via stats.nba.com endpoints
- Available: speed, distance, touches, passes, drives, catch-and-shoot
- NOT available: raw x/y coordinates (would need NBA partnership)

### What We Can Get (Free)
- Play-by-play event logs (every game, every season)
- Player tracking aggregates (touches, passes, drives, rebounds)
- Shot detail (location, distance, closest defender, shot clock)
- Lineup data (who was on court for each play)
- Synergy play type stats (pick-and-roll, isolation, post-up, etc.)

## Play Patterns to Train

### Tier 1 — Fundamentals
1. **Pick-and-Roll (Ball Handler)** — screener sets pick, ball handler drives
2. **Pick-and-Roll (Roll Man)** — screener rolls to basket after pick
3. **Isolation** — one-on-one, clear out
4. **Spot-Up** — catch and shoot off ball movement
5. **Transition** — fast break, numbers advantage

### Tier 2 — Intermediate
6. **Off-Ball Screen** — pin-down, flare, back screen
7. **Post-Up** — back to basket, low block
8. **Cut** — backdoor, face cut, basket cut
9. **Hand-Off** — dribble hand-off (DHO) action
10. **Drive and Kick** — penetrate, collapse defense, kick to open shooter

### Tier 3 — Advanced
11. **Spain Pick-and-Roll** — PnR with back screen on roll man's defender
12. **Horns** — two bigs at elbows, multiple action options
13. **Floppy** — shooter runs off staggered screens, reads defense
14. **Motion Weak** — ball reversal into weak side action
15. **ATO (After Timeout)** — designed plays, often unique per team

## Training Modes

### 1. Pattern Library (passive)
Browse annotated play-by-play sequences for each pattern type.
Shows: what happened, who was involved, what to watch for.

```
$ python trainer.py library pick-and-roll
```

### 2. Pattern Quiz (active)
System shows a play-by-play sequence, stops before the action.
User guesses: what play type is developing? What happens next?

```
$ python trainer.py quiz --tier 1
```

### 3. Live Game Scanner (real-time)
During a live game, pulls play-by-play as it happens.
Annotates each possession with the play type detected.
User can predict before the annotation reveals.

```
$ python scanner.py --game LAL-BOS
```

### 4. Film Session (review)
Load a completed game. Step through possession by possession.
System annotates, user reviews, builds pattern vocabulary.

```
$ python trainer.py film --game 0022500892
```

## Pattern Detection

### Using Synergy Play Type Data
NBA tracks play types via Synergy Sports (now part of stats.nba.com):
- Each possession is classified: PnR ball handler, PnR roll man, isolation, spot-up, post-up, cut, off-screen, hand-off, transition, misc
- Available per-player and per-team
- This is the ground truth for training

### Using Play-by-Play Heuristics
When Synergy data isn't available, detect patterns from event sequences:
- Screen assist + drive + shot within 6 seconds = likely PnR
- Isolation: single player dribbles 3+ seconds, no pass, shot attempt
- Transition: shot attempt within 8 seconds of defensive rebound
- Spot-up: catch + shoot within 2 seconds, no dribble

```python
def classify_possession(events):
    """Classify a possession into play type from play-by-play events."""
    # Time between rebound/inbound and shot
    # Number of passes
    # Dribble time
    # Screen events
    # Player movement patterns
```

## Progress Tracking

Same philosophy as ConsistencyMetrics in trading_psychology.py.
Measure process (pattern recognition accuracy), not outcomes.

```python
class PatternRecognitionScore:
    def __init__(self):
        self.attempts = []  # (pattern_type, predicted, actual, timestamp)

    def accuracy_by_tier(self):
        """How well can you identify patterns at each difficulty level?"""

    def accuracy_by_type(self):
        """Which patterns do you see easily? Which do you miss?"""

    def improvement_over_time(self):
        """Rolling accuracy over last N sessions."""
```

## Implementation Order

1. `ingest.py` — fetch play-by-play for a game using nba_api
2. `plays.py` — classify possessions using Synergy data + heuristics
3. `trainer.py` — pattern library + quiz mode
4. `progress.py` — track recognition accuracy
5. `scanner.py` — live game annotation

## Dependencies

```
nba_api          # NBA stats API client
```

## The Connection to Trading

This isn't a distraction from trading. It's the same skill:
- Trading: see the pattern → check the edge → execute the system
- Basketball: see the play developing → predict the action → verify

Both require internalizing patterns at a functional level (Douglas Ch. 8).
Both improve with deliberate, annotated repetition.
Both degrade when emotions override pattern recognition.

The sports monitor trains the same neural pathways — pattern recognition under uncertainty — in a domain with zero financial risk. Reps without tuition.
