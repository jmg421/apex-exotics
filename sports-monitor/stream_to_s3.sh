#!/bin/bash
# Sync HLS segments to S3 with cleanup of stale files
REMOTE_DIR="$HOME/Movies/remote"
BUCKET="s3://apex-sports-stream/live"
REGION="us-east-2"

echo "🎥 Streaming to S3 → CloudFront"

while true; do
    [ ! -f "$REMOTE_DIR/stream.m3u8" ] && sleep 1 && continue

    # Sync everything, delete files on S3 that no longer exist locally
    aws s3 sync "$REMOTE_DIR/" "$BUCKET/" \
        --delete \
        --exclude "index.html" \
        --size-only \
        --region $REGION \
        --no-progress 2>/dev/null

    # Re-upload m3u8 with no-cache header
    aws s3 cp "$REMOTE_DIR/stream.m3u8" "$BUCKET/stream.m3u8" \
        --content-type "application/vnd.apple.mpegurl" \
        --cache-control "no-cache, no-store, must-revalidate" \
        --region $REGION --no-progress 2>/dev/null

    sleep 1
done
