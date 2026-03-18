# Sports Monitor

Basketball IQ trainer using NBA play-by-play data. Train your pattern recognition the same way you train your trading edge — deliberate reps with feedback.

See [SPEC.md](SPEC.md) for full architecture.

## Quick Start

```bash
pip install nba_api

# Browse annotated plays
python trainer.py library pick-and-roll

# Quiz yourself
python trainer.py quiz --tier 1

# Watch a live game with annotations
python scanner.py --game LAL-BOS

# Review a completed game
python trainer.py film --game 0022500892

# Check your progress
python progress.py
```
