#!/usr/bin/env bash
set -euo pipefail

DEVICE="${DEVICE:-/dev/video1}"
WIDTH="${WIDTH:-640}"
HEIGHT="${HEIGHT:-480}"
FPS="${FPS:-30}"
BITRATE="${BITRATE:-2000k}"
MTX_HOST="${MTX_HOST:-127.0.0.1}"
RTSP_PORT="${RTSP_PORT:-8554}"
MTX_PATH="${MTX_PATH:-cam}"

echo "[rgb_cam] starting FFmpeg publish to rtsp://${MTX_HOST}:${RTSP_PORT}/${MTX_PATH}"

exec ffmpeg \
  -f v4l2 \
  -input_format mjpeg \
  -framerate "${FPS}" \
  -video_size "${WIDTH}x${HEIGHT}" \
  -i "${DEVICE}" \
  -an \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -preset ultrafast \
  -tune zerolatency \
  -b:v "${BITRATE}" \
  -f rtsp \
  "rtsp://${MTX_HOST}:${RTSP_PORT}/${MTX_PATH}"