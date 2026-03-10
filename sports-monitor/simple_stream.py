#!/usr/bin/env python3
"""
Simple approach: Use OBS regular recording, tail the file and stream it
"""
from flask import Flask, Response
import subprocess
import time

app = Flask(__name__)

OBS_RECORDING_PATH = "/tmp/obs_recording.mp4"

@app.route('/stream')
def stream():
    """Stream OBS recording file"""
    def generate():
        # Start OBS recording to /tmp/obs_recording.mp4
        # Then tail and stream it
        proc = subprocess.Popen(
            ['ffmpeg', '-re', '-i', OBS_RECORDING_PATH, '-c', 'copy', '-f', 'mpegts', '-'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        while True:
            data = proc.stdout.read(1024)
            if not data:
                break
            yield data
    
    return Response(generate(), mimetype='video/mp2t')

@app.route('/')
def index():
    return '''
    <video controls autoplay muted style="width:100%">
        <source src="/stream" type="video/mp2t">
    </video>
    '''

if __name__ == '__main__':
    print("Set OBS to record to: /tmp/obs_recording.mp4")
    print("Then start recording and open http://192.168.0.180:8081")
    app.run(host='0.0.0.0', port=8081)
