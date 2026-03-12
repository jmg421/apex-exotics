#!/usr/bin/env python3
"""
DVR Manager - Keep last 4 hours of video
"""
import os
import time
from pathlib import Path

MOVIES_DIR = Path.home() / "Movies"
KEEP_HOURS = 4
KEEP_SECONDS = KEEP_HOURS * 3600

def cleanup_old_segments():
    """Delete segments older than KEEP_HOURS"""
    now = time.time()
    deleted = 0
    kept = 0
    
    for ts_file in MOVIES_DIR.glob("*.ts"):
        age = now - ts_file.stat().st_mtime
        
        if age > KEEP_SECONDS:
            ts_file.unlink()
            deleted += 1
        else:
            kept += 1
    
    print(f"DVR: Kept {kept} segments ({kept*5/60:.1f} min), deleted {deleted}")

if __name__ == '__main__':
    cleanup_old_segments()
