#!/bin/bash
# Auto-restarting ffmpeg transcoder for CloudFront streaming (macOS compatible)
REMOTE_DIR="$HOME/Movies/remote"
SOURCE="http://localhost:8081"

while true; do
    # Find latest active m3u8
    M3U8=$(ls -t ~/Movies/*.m3u8 2>/dev/null | head -1)
    if [ -z "$M3U8" ]; then
        echo "$(date): No m3u8 found, retrying in 5s..."
        sleep 5
        continue
    fi
    BASENAME=$(basename "$M3U8")
    ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$BASENAME'))")
    echo "$(date): Starting transcode from $BASENAME"
    cd "$REMOTE_DIR" && rm -f *.ts stream.m3u8
    ffmpeg -i "$SOURCE/$ENCODED" \
        -c:v libx264 -preset veryfast -b:v 800k -maxrate 900k -bufsize 1200k \
        -vf scale=854:480 -r 30 -g 30 -keyint_min 30 \
        -c:a aac -b:a 96k \
        -f hls -hls_time 1 -hls_list_size 5 -hls_flags delete_segments \
        -hls_segment_filename 'stream%d.ts' stream.m3u8 2>&1 | tail -1
    echo "$(date): ffmpeg exited, restarting in 3s..."
    sleep 3
done
