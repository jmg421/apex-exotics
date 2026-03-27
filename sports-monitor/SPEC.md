# Sports Monitor — Home TV Automation

## What It Does

Automated sports TV system that captures live TV, serves it as a web stream, and auto-switches channels to the most exciting live game.

## Architecture

```
VSeeBox → Elgato 4K X → OBS (HLS) → hls_server.py (:8081)
                                            ↓
ESPN API → excitement_engine.py → auto_channel.py → Broadlink IR → VSeeBox
                                            ↓
                                    dashboard.py (:5001)
                                            ↓
                              EC2 relay → remote browser
```

## Core Components

| File | Purpose |
|---|---|
| `dashboard.py` | Flask web UI — scores, headlines, stream, channel control |
| `auto_channel.py` | Auto-switches to most exciting live game |
| `excitement_engine.py` | Scores live games (margin, time, period) |
| `channel_switcher.py` | Sends IR codes to VSeeBox via Broadlink |
| `hls_server.py` | Serves OBS HLS stream over HTTP |
| `lower_third_ocr.py` | Extracts headlines from TV lower thirds |
| `dvr_cleanup.py` | Keeps last 30 min of HLS segments |
| `cleanup_screenshots.py` | Keeps last 24h of intel screenshots |

## Data Flow

1. OBS captures Elgato input → writes HLS segments to `/Volumes/Seagate Backup/scratch/`
2. `hls_server.py` serves segments over HTTP on port 8081
3. `dashboard.py` serves the web UI on port 5001 with embedded HLS player
4. `excitement_engine.py` polls ESPN API, scores each live game
5. `auto_channel.py` picks the most exciting game and sends IR to switch
6. During dead air, rotates through Bloomberg/CNBC/ESPN and screenshots lower thirds
7. EC2 relay tunnels ports 5001, 8081, and SSH (2222) for remote access

## Services (launchd)

- `com.apex.sports-monitor` — dashboard.py (KeepAlive)
- `com.apex.hls-server` — hls_server.py (KeepAlive)
- `com.apex.relay-tunnel` — SSH tunnel to EC2
- `com.apex.dashboard-kiosk` — Chrome kiosk mode

## Cron

- `dvr_cleanup.py` — every 10 min, deletes HLS segments older than 30 min
- `cleanup_screenshots.py` — every 10 min, deletes screenshots older than 24h

## Dependencies

See `requirements.txt`.
