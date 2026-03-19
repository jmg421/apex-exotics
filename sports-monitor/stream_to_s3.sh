#!/bin/bash
# Continuously sync low-bitrate HLS segments to S3 for CloudFront delivery
REMOTE_DIR="$HOME/Movies/remote"
BUCKET="s3://apex-sports-stream/live"

echo "🎥 Streaming to S3 → CloudFront"
echo "   Source: $REMOTE_DIR"
echo "   Dest:   $BUCKET"
echo "   CDN:    https://d2tb8x2d50uaay.cloudfront.net/live/stream.m3u8"

while true; do
    # Sync .ts segments first, then m3u8 (so playlist never references missing segments)
    aws s3 sync "$REMOTE_DIR/" "$BUCKET/" \
        --exclude "*.m3u8" \
        --size-only \
        --region us-east-2 \
        --no-progress 2>/dev/null

    aws s3 cp "$REMOTE_DIR/stream.m3u8" "$BUCKET/stream.m3u8" \
        --content-type "application/vnd.apple.mpegurl" \
        --cache-control "no-cache, no-store, must-revalidate" \
        --region us-east-2 \
        --no-progress 2>/dev/null

    sleep 1
done
