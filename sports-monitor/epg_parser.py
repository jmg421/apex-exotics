#!/usr/bin/env python3
"""
EPG parser for ESPN channels using XMLTV data
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import pytz

EPG_URL = "https://iptv-epg.org/files/epg-us.xml"

# Map VSeeBox channel numbers to EPG IDs (actual VSeeBox lineup)
# Note: ESPN2 and ESPNU are swapped compared to EPG data
CHANNEL_MAP = {
    # ESPN Family
    809: "ESPN.us",
    810: "ESPN.us",  # ESPN backup
    811: "ESPN2.us",
    812: "ESPNU.us",
    813: "ESPNDeportes.us",
    814: "ESPNEWS.us",
    
    # March Madness broadcast channels
    28:  "CBSEast_WCBS.us",  # CBS East
    156: "TBS.us",          # TBS East
    162: "TNT.us",          # TNT East
    166: "truTV.us",        # truTV East
    
    # Major Sports Networks
    807: "BigTenNetwork.us",
    808: "CBSSportsNetwork.us",
    815: "MLBNetwork.us",
    816: "NBATV.us",
    817: "NFLNetwork.us",
    820: "SECNetwork.us",
    
    # Fox Sports
    860: "FS1.us",
    862: "FS2.us",
    
    # Other
    912: "GolfChannel.us",
}

# March Madness channels for quick lookup
MARCH_MADNESS_CHANNELS = [28, 156, 162, 166]

def fetch_epg():
    """Download and parse EPG XML"""
    print("📡 Downloading EPG data...")
    response = requests.get(EPG_URL, timeout=30)
    return ET.fromstring(response.content)

def get_current_program(epg_root, channel_id):
    """Get currently airing program for a channel"""
    now = datetime.now(timezone.utc)
    
    for programme in epg_root.findall('programme'):
        if programme.get('channel') == channel_id:
            # Parse times (format: 20260311190000 +0000)
            start_str = programme.get('start')
            stop_str = programme.get('stop')
            
            start = datetime.strptime(start_str[:14], '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
            stop = datetime.strptime(stop_str[:14], '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
            
            if start <= now < stop:
                title = programme.find('title').text if programme.find('title') is not None else "N/A"
                desc = programme.find('desc').text if programme.find('desc') is not None else ""
                
                # Convert to Eastern Time
                eastern = pytz.timezone('America/New_York')
                start_et = start.astimezone(eastern)
                stop_et = stop.astimezone(eastern)
                
                return {
                    'title': title,
                    'description': desc,
                    'start': start_et.strftime('%I:%M %p'),
                    'end': stop_et.strftime('%I:%M %p'),
                }
    
    return None

def scan_espn_channels():
    """Scan all ESPN channels for current programs"""
    epg = fetch_epg()
    
    print("\n📺 Current ESPN Programming")
    print("=" * 60)
    
    for channel_num, epg_id in CHANNEL_MAP.items():
        program = get_current_program(epg, epg_id)
        
        channel_name = epg_id.replace('.us', '').replace('ESPN', 'ESPN ')
        
        if program:
            print(f"\n{channel_name} (Ch {channel_num}):")
            print(f"  {program['start']} - {program['end']}")
            print(f"  {program['title']}")
            if program['description']:
                print(f"  {program['description'][:100]}...")
        else:
            print(f"\n{channel_name} (Ch {channel_num}): No program data")

def get_march_madness_now(epg=None):
    """Get current March Madness games with their VSeeBox channel numbers."""
    if epg is None:
        epg = fetch_epg()
    
    games = []
    for ch_num in MARCH_MADNESS_CHANNELS:
        epg_id = CHANNEL_MAP.get(ch_num)
        if not epg_id:
            continue
        program = get_current_program(epg, epg_id)
        if program:
            title = program.get('title', '')
            # Match NCAA tournament, March Madness, or college basketball
            if any(kw in title.lower() for kw in ['ncaa', 'march madness', 'first four', 'tournament']):
                games.append({
                    'channel': ch_num,
                    'title': title,
                    'description': program.get('description', ''),
                    'start': program['start'],
                    'end': program['end'],
                })
    return games


if __name__ == '__main__':
    scan_espn_channels()
