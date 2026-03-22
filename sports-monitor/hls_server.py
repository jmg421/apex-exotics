#!/usr/bin/env python3
"""Threaded HTTP server for HLS streaming"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

class HLSHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path.home() / "Movies"), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        if self.path.endswith('.m3u8'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        elif self.path.endswith('.ts'):
            self.send_header('Cache-Control', 'public, max-age=60')
        super().end_headers()

    def log_message(self, format, *args):
        pass  # silence logs

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8081), HLSHandler)
    print("HLS server (threaded) on http://localhost:8081")
    server.serve_forever()
