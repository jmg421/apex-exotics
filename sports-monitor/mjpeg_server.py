#!/usr/bin/env python3
"""Low-latency MJPEG stream from Elgato via ffmpeg"""
import subprocess
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/stream')
def stream():
    cmd = [
        'ffmpeg', '-f', 'avfoundation',
        '-pixel_format', 'nv12', '-framerate', '30',
        '-video_size', '1920x1080',
        '-thread_queue_size', '1024',
        '-i', '0:none',
        '-vf', 'fps=30',
        '-c:v', 'mjpeg', '-q:v', '3',
        '-f', 'mpjpeg', '-boundary_tag', 'frame',
        'pipe:1'
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return Response(proc.stdout, mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("MJPEG stream at http://localhost:8082/stream")
    app.run(host='0.0.0.0', port=8082, threaded=True)
