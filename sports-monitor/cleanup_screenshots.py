#!/usr/bin/env python3
"""Cleanup old intel screenshots — keep last 24 hours."""
import time
from pathlib import Path

SCREENSHOT_DIR = Path(__file__).parent / 'data' / 'intel_screenshots'
KEEP_SECONDS = 24 * 3600

def cleanup():
    now = time.time()
    deleted = 0
    for f in SCREENSHOT_DIR.glob('*.jpg'):
        if now - f.stat().st_mtime > KEEP_SECONDS:
            f.unlink()
            deleted += 1
    if deleted:
        print(f'Cleaned up {deleted} screenshots older than 24h')

if __name__ == '__main__':
    cleanup()
