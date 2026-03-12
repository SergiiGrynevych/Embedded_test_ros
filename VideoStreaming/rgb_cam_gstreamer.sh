#!/usr/bin/env bash
set -euo pipefail

DEVICE="${DEVICE:-/dev/video1}"
WIDTH="${WIDTH:-640}"
HEIGHT="${HEIGHT:-480}"
FPS="${FPS:-30}"
BITRATE="${BITRATE:-2000}"
MTX_HOST="${MTX_HOST:-127.0.0.1}"
RTSP_PORT="${RTSP_PORT:-8554}"
MTX_PATH="${MTX_PATH:-cam}"

echo "[rgb_am] starting GStreamer publish to rtsp://${MTX_HOST}:${RTSP_PORT}/${MTX_PATH}"

exec gst-launch-1.0 -e \
  v4l2src device="${DEVICE}" \
  ! image/jpeg,width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1 \
  ! jpegdec \
  ! videoconvert \
  ! x264enc tune=zerolatency speed-preset=ultrafast bitrate=${BITRATE} key-int-max=${FPS} \
  ! h264parse \
  ! rtspclientsink location="rtsp://${MTX_HOST}:${RTSP_PORT}/${MTX_PATH}" protocols=tcp