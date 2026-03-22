#!/bin/bash
# Direct Elgato capture to HLS — video only, audio via Loopback
STREAM_DIR="$HOME/Movies/remote"
mkdir -p "$STREAM_DIR"
cd "$STREAM_DIR" && rm -f *.ts stream.m3u8

echo "🎥 Capturing Elgato 4K X → HLS (video only)"
echo "   Stream: http://localhost:8081/remote/stream.m3u8"
echo "   Audio: via Loopback"

ffmpeg -f avfoundation -pixel_format nv12 -framerate 30 -video_size 1920x1080 \
    -probesize 10M -thread_queue_size 1024 -i "0:none" \
    -vf "fps=30" \
    -c:v h264_videotoolbox -b:v 15000k -realtime 1 -prio_speed 1 \
    -an \
    -f hls -hls_time 2 -hls_list_size 8 -hls_flags delete_segments \
    -hls_segment_filename 'stream%d.ts' stream.m3u8
