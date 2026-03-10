# VSeeBox EPG Database Extraction - Findings

## Objective
Extract channel data from encrypted `epg.db.zip` file from VSeeBox device.

## What We Accomplished ✓

### 1. Reverse Engineered Password Algorithm
- Decompiled ARM32 native library (`libjson.so`) using radare2
- Extracted `getZipPwd()` function logic
- Reimplemented in Python: `/tmp/extract_password.py`

### 2. Algorithm Details
```
Input: 32-character string from readme.txt
Process:
  1. Validate length == 32 bytes
  2. Compare against hardcoded key: "CC17AFAD24FDEC480C1142CCEF6D1B47"
  3. Extract only digits: "172448011426147"
  4. Append magic suffix: "BA4EFE35"
  5. Combined: "172448011426147BA4EFE35"
  6. Return MD5: d44632557d3502e71596d202b1ec7a36
```

### 3. Technical Details
- ZIP uses AES-256 encryption (PKZip v5.1)
- Password generation function at address: 0x000544cc
- Hardcoded comparison key at: 0xb2916
- Magic suffix constructed at: 0x5458e-0x545aa

## The Problem ❌

**Chicken-and-egg situation:**
- Password depends on `readme.txt` content
- `readme.txt` is encrypted inside the ZIP
- Can't read `readme.txt` without the password
- Can't generate password without `readme.txt`

**Why our password doesn't work:**
- Generated password: `d44632557d3502e71596d202b1ec7a36`
- This assumes `readme.txt` contains the hardcoded key
- Actual `readme.txt` likely contains device/user-specific data
- Could be: device ID, user PID, MAC address, or other unique identifier

## Attempted Solutions

1. ✗ ARM32 Android emulator - Not supported on Apple Silicon
2. ✓ Reverse engineering - Successfully extracted algorithm
3. ✗ Password brute force - Tried common patterns, none worked
4. ✗ ADB access to device - Connection hangs/unavailable

## Network Traffic Analysis

Analyzed 9 pcap files from `/private/tmp/`:
- Found 1806 ZIP file fragments in `vseebox_factory_reset.pcap`
- Extracted ZIP file with encrypted `readme.txt` (32 bytes)
- Tested all 14 unique 32-character strings from network traffic
- **Result**: Password not transmitted over network

**Conclusion**: The `readme.txt` content is generated locally on the device (likely from device ID, MAC address, or other hardware identifier) and never transmitted in plaintext.

## Possible Next Steps

### Option A: Alternative Data Source
- Check if VSeeBox has a web interface or API
- Look for channel listings on their website
- Find if other users have shared channel data

### Option B: Network Capture
- Monitor VSeeBox network traffic when it downloads/decrypts the database
- Might capture the readme.txt or password in transit
- Use Wireshark or tcpdump on your network

### Option C: Manual Channel Mapping
- Use the existing `channel_map.txt` approach
- Manually map channels by watching what plays
- Your `vseebox_sync.py` already does this via ADB logcat

### Option D: Wait for Device Access
- If ADB becomes available, can pull files directly:
  ```bash
  adb shell find /data/data/com.google.heatlive -name "readme.txt"
  adb shell find /sdcard -name "epg.db*"
  ```

## Files Created

- `/tmp/extract_password.py` - Working password generator
- `/Users/apple/apex-exotics/vseebox_emulator_progress.md` - Full technical log
- This file - Summary of findings

## Recommendation

**Use Option C (Manual Mapping)** - Your existing approach in `sports-monitor/` is working:
- `vseebox_sync.py` monitors current channel via ADB
- `channel_map.txt` maps channels to content
- This is more reliable than trying to decrypt a device-specific database

The EPG database would be nice to have, but your current manual mapping approach is functional and doesn't depend on device-specific encryption.
