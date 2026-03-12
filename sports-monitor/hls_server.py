#!/usr/bin/env python3
"""
Simple HTTP server optimized for HLS streaming
Serves files from ~/Movies with proper caching headers
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path

class HLSHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path.home() / "Movies"), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Cache control based on file type
        if self.path.endswith('.m3u8'):
            # Don't cache playlists
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        elif self.path.endswith('.ts'):
            # Cache segments for 60 seconds
            self.send_header('Cache-Control', 'public, max-age=60')
        
        super().end_headers()

if __name__ == '__main__':
    PORT = 8081
    server = HTTPServer(('0.0.0.0', PORT), HLSHandler)
    print(f"HLS server running on http://localhost:{PORT}")
    print(f"Serving from: {Path.home() / 'Movies'}")
    server.serve_forever()
