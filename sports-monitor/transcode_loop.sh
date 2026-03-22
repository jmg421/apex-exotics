#!/bin/bash
REMOTE_DIR="$HOME/Movies/remote"
SOURCE="http://localhost:8081"

while true; do
    M3U8=$(ls -t ~/Movies/*.m3u8 2>/dev/null | head -1)
    if [ -z "$M3U8" ]; then
        echo "$(date): No m3u8 found, retrying in 5s..."
        sleep 5
        continue
    fi

    # Skip finalized playlists
    if grep -q "EXT-X-ENDLIST" "$M3U8"; then
        echo "$(date): Playlist is finalized (not live), waiting..."
        sleep 5
        continue
    fi

    BASENAME=$(basename "$M3U8")
    ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$BASENAME'))")
    echo "$(date): Starting passthrough (re-encoding audio) from $BASENAME"
    cd "$REMOTE_DIR" && rm -f *.ts stream.m3u8
    ffmpeg -live_start_index -3 -i "$SOURCE/$ENCODED" \
        -c:v copy \
        -c:a aac -b:a 192k \
        -f hls -hls_time 2 -hls_list_size 8 -hls_flags delete_segments \
        -hls_segment_filename 'stream%d.ts' stream.m3u8 2>&1 | tail -1
    echo "$(date): ffmpeg exited, restarting in 3s..."
    sleep 3
done
