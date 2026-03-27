#!/usr/bin/env python3
"""Sync latest HLS stream from external drive to local dir for dashboard access.

Workaround: launchd processes lack Full Disk Access to external volumes.
This runs via cron (which inherits user FDA) and copies the active m3u8
+ its referenced .ts segments to a local directory the dashboard can read.

Usage:
    python stream_sync.py          # run once
    python stream_sync.py --loop   # run continuously (every 2s)
"""
import os
import shutil
import glob
import sys
import time

SRC = '/Volumes/Seagate Backup/scratch'
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stream')

def sync():
    os.makedirs(DST, exist_ok=True)

    # Find latest m3u8 with active .ts segments
    m3u8_files = glob.glob(f'{SRC}/*.m3u8')
    if not m3u8_files:
        return
    m3u8_files.sort(key=os.path.getmtime, reverse=True)

    active = None
    for m in m3u8_files:
        bn = os.path.splitext(os.path.basename(m))[0]
        if glob.glob(f'{SRC}/{bn}*.ts'):
            active = m
            break
    if not active:
        return

    # Read m3u8 to find referenced .ts files
    with open(active) as f:
        lines = f.readlines()
    ts_names = [l.strip() for l in lines if l.strip() and not l.startswith('#')]

    # Copy m3u8
    shutil.copy2(active, os.path.join(DST, os.path.basename(active)))

    # Copy referenced .ts segments (skip if already exists and same size)
    for ts in ts_names:
        src_path = os.path.join(SRC, ts)
        dst_path = os.path.join(DST, ts)
        if not os.path.exists(src_path):
            continue
        src_size = os.path.getsize(src_path)
        if os.path.exists(dst_path) and os.path.getsize(dst_path) == src_size:
            continue
        shutil.copy2(src_path, dst_path)

    # Clean up old .ts and .m3u8 files in DST not referenced by current m3u8
    ts_set = set(ts_names)
    active_name = os.path.basename(active)
    for f in os.listdir(DST):
        if f.endswith('.ts') and f not in ts_set:
            os.remove(os.path.join(DST, f))
        elif f.endswith('.m3u8') and f != active_name:
            os.remove(os.path.join(DST, f))

if __name__ == '__main__':
    if '--loop' in sys.argv:
        print(f"Stream sync: {SRC} -> {DST} (every 2s)", flush=True)
        while True:
            try:
                sync()
            except Exception as e:
                print(f"Sync error: {e}", flush=True)
            time.sleep(2)
    else:
        sync()
