# OBS Setup for VSeeBox Stream

## Simple File-Based Approach

1. **In OBS:**
   - Settings → Output
   - Output Mode: Advanced
   - Recording:
     - Type: Custom Output (FFmpeg)
     - FFmpeg Output Type: Output to File
     - File path: `/tmp/vseebox_stream/stream.m3u8`
     - Container Format: `hls`
     - Video Encoder: `libx264`
     - Audio Encoder: `aac`
   
2. **Start Recording** (this will create the HLS stream)

3. **Stream server will serve it** at http://192.168.0.180:8081

## Alternative: Use OBS Browser Source

Just add a Browser Source in your dashboard that points to OBS's preview window (if OBS has a web preview feature).
