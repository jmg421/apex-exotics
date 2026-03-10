#!/usr/bin/env python3
"""
VSeeBox Stream Server - Captures Elgato 4K X and serves HLS stream
"""
import subprocess
import os
from flask import Flask, Response, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

STREAM_DIR = "/Users/apple/Movies"
HLS_PLAYLIST = "vseebox_stream.m3u8"

def start_capture():
    """OBS is creating the HLS stream, no need to run ffmpeg"""
    os.makedirs(STREAM_DIR, exist_ok=True)
    return None  # No subprocess needed

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any file from stream directory"""
    import urllib.parse
    decoded_filename = urllib.parse.unquote(filename)
    if decoded_filename.endswith(('.ts', '.m3u8')):
        return send_from_directory(STREAM_DIR, decoded_filename)
    return "Not found", 404

@app.route('/stream/<path:filename>')
def stream_file(filename):
    """Serve HLS segments - handle URL encoded filenames"""
    import urllib.parse
    decoded_filename = urllib.parse.unquote(filename)
    return send_from_directory(STREAM_DIR, decoded_filename)

@app.route('/stream.m3u8')
def playlist():
    """Serve latest HLS playlist"""
    import glob
    # Find latest .m3u8 file in Movies directory
    m3u8_files = glob.glob(f'{STREAM_DIR}/*.m3u8')
    if not m3u8_files:
        return "No stream found", 404
    
    latest = max(m3u8_files, key=os.path.getmtime)
    return send_from_directory(STREAM_DIR, os.path.basename(latest))

@app.route('/')
def index():
    """Simple test page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>VSeeBox Stream</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    </head>
    <body style="margin:0; background:#000;">
        <video id="video" controls autoplay muted style="width:100%; height:100vh;"></video>
        <script>
            var video = document.getElementById('video');
            if (Hls.isSupported()) {
                var hls = new Hls({
                    liveSyncDurationCount: 1,
                    liveMaxLatencyDurationCount: 3
                });
                hls.loadSource('/stream.m3u8');
                hls.attachMedia(video);
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting VSeeBox stream server...")
    print("OBS should be recording to:", f"{STREAM_DIR}/{HLS_PLAYLIST}")
    print("Stream server running at http://localhost:8081")
    print("Embed URL: http://localhost:8081/stream.m3u8")
    
    app.run(host='0.0.0.0', port=8081, debug=False)
