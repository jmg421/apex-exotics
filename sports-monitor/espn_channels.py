"""
ESPN channel mapping for VSeeBox
Source: https://www.vseebox.net/pages/channel-list
"""

CHANNEL_MAP = {
    # ESPN Networks
    'ESPN': 809,
    'ESPN Backup': 810,
    'ESPN2': 811,
    'ESPNU': 812,
    'ESPN Deportes': 813,
    'ESPNews': 814,
    
    # Other Sports
    'MLB Network': 815,
    'NBA TV': 838,
    'NHL Network': 877,
    'NFL Network': 845,
    
    # College Networks
    'ACC Network': 801,
    'Big Ten Network': 826,
    'SEC Network': 849,
    'Longhorn Network': 878,
    'Pac-12 Network': 848,
    
    # Major Sports Networks
    'Fox Sports 1': 833,
    'FS1': 833,
    'Fox Sports 2': 834,
    'FS2': 834,
    'CBS Sports Network': 827,
    'Golf Channel': 835,
}

def get_channel(network_name):
    """Get channel number for a network"""
    # Try exact match first
    if network_name in CHANNEL_MAP:
        return CHANNEL_MAP[network_name]
    
    # Try case-insensitive partial match
    network_upper = network_name.upper()
    for key, value in CHANNEL_MAP.items():
        if network_upper in key.upper() or key.upper() in network_upper:
            return value
    
    return None

