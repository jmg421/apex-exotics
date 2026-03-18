# Commercial Detection - Usage Guide

## What It Does

Uses kiro-cli vision to:
1. **Detect** if current stream shows a commercial
2. **Identify** what product/company is being advertised

## Performance

- **Capture**: ~0.2 seconds (ffmpeg)
- **Analysis**: ~30-40 seconds (kiro-cli vision)
- **Total**: ~40 seconds per check

## API Endpoint

```bash
curl http://localhost:5001/api/commercial_check
```

**Response:**
```json
{
  "success": true,
  "is_commercial": true,
  "commercial_type": "Progressive Insurance"
}
```

## Manual Testing

```bash
cd /Users/apple/apex-exotics/sports-monitor
../venv/bin/python commercial_integration.py
```

Output:
```
🚫 COMMERCIAL DETECTED: Progressive Insurance
```

or

```
✅ Game Content: Live Action
```

## Accuracy

Tested during live ACC Tournament broadcast:
- ✅ Correctly identified Progressive Insurance commercial (with Flo)
- ✅ Correctly distinguished from game content

## Recommended Usage

**Periodic Checks** (every 2-3 minutes):
- Check during timeouts/breaks
- Don't spam - vision analysis is expensive
- Cache results for 30-60 seconds

**Auto-Channel Switching**:
- When commercial detected → switch to most exciting game
- When game resumes → switch back
- Requires confidence threshold (2-3 consecutive detections)

## Integration Ideas

1. **Dashboard Alert**: Show "🚫 Commercial: [Product]" banner
2. **Auto-Switch**: Change channel during commercials
3. **Commercial Log**: Track what ads air during games
4. **Ad Analytics**: Which products advertise during which games

## Technical Details

- Captures upper 2/3 of frame (game action area)
- Lower 1/3 has scoreboard (not useful for commercial detection)
- Uses single prompt for speed: "Is this a commercial? If YES, name product"
- Parses response for YES/NO and product name
