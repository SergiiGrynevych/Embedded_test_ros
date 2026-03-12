# GPS UART + Video Streaming + ROS2 Guide

This repository contains instructions for:

1. Running the GPS UART parsing script
2. Launching video streaming through MediaMTX
3. Building and running the ROS2 package `gps_uart_reader`

---

## Repository setup

Clone the repository and switch to the required branch:

```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
git checkout master
```

> Replace `<REPO_URL>` and `<REPO_FOLDER>` with your actual repository values.

---

## Requirements

Make sure the system has the following installed:

- `python3`
- `pip3`
- `MediaMTX`
- `ROS2` (`Humble`, `Foxy`, or another compatible version)
- `colcon`

Optional, depending on how you validate video streaming:

- `ffmpeg`
- `ffplay`
- `VLC`
- GStreamer packages

---

# TASK 1 — Run GPS UART parser

## Run the application

```bash
cd ~
python3 UART_ParsingGPS.py
```

## Troubleshooting

If `pyserial` is missing, install it with:

```bash
pip3 install pyserial
```

---

# TASK 2 — Run video capture / streaming

Go to the MediaMTX folder:

```bash
cd ~/VideoStreaming/
```

## Launch app using FFmpeg config

```bash
./mediamtx mediamtx_ffmpeg.yml
```

## Launch app using GStreamer config

```bash
./mediamtx mediamtx_gstreamer.yml
```

---

## Stream validation

From another computer on the same network, you can verify the stream in the following ways.

### Open in browser

```text
http://<IP_ADDR_BOARD>:8080/stream/
```

### Open with FFplay

```bash
ffplay rtsp://<IP_ADDR_BOARD>:8554/stream
```

### Open with VLC

```text
rtsp://<IP_ADDR_BOARD>:8554/stream
```

---

## Troubleshooting for GStreamer

If GStreamer dependencies are missing, install them with:

```bash
sudo apt install -y \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-rtsp \
  libgstrtspserver-1.0-0 \
  libgstrtspserver-1.0-dev
```

---

# TASK 3 — Build and run ROS2 package

A ROS2 distribution must be installed in your system, such as:

- ROS2 Humble
- ROS2 Foxy
- or another compatible version

---

## Build package

This will build the ROS2 interface package `gps_position_msgs` and the package `gps_uart_reader`.

```bash
cd ~/ros2
colcon build --packages-up-to gps_uart_reader
```

After building, source the workspace:

```bash
source ~/ros2/install/setup.bash
```

---

## Launch with `ros2 launch`

```bash
source ~/ros2/install/setup.bash
cd ~/ros2
ros2 launch gps_uart_reader gps_uart.launch.py
```

---

## Run with `ros2 run`

```bash
source ~/ros2/install/setup.bash
ros2 run gps_uart_reader gps_node --ros-args -p port:=/dev/ttyS5 -p baudrate:=9600
```

---

## Dependencies

Install required Python and ROS2 build dependencies:

```bash
pip3 install pyserial
sudo apt install python3-colcon-common-extensions
```

---

## Show ROS2 interface

```bash
ros2 interface show gps_position_msgs/msg/GpsPosition
```

---

## Notes

- Replace `<IP_ADDR_BOARD>` with the actual IP address of the board.
- Make sure the board and the client computer are in the same network.
- If `ffplay` is not installed on the client machine, use VLC or browser playback instead.
- If ROS2 commands are not found, first source the appropriate ROS2 environment.

---

## Quick Start

### 1. Run GPS parser

```bash
cd ~
python3 UART_ParsingGPS.py
```

### 2. Run MediaMTX

FFmpeg:

```bash
cd ~/VideoStreaming/
./mediamtx mediamtx_ffmpeg.yml
```

GStreamer:

```bash
cd ~/VideoStreaming/
./mediamtx mediamtx_gstreamer.yml
```

### 3. Build and run ROS2 package

```bash
cd ~/ros2
colcon build --packages-up-to gps_uart_reader
source ~/ros2/install/setup.bash
ros2 launch gps_uart_reader gps_uart.launch.py
```

---

## Example validation commands

### Check stream in browser

```text
http://<IP_ADDR_BOARD>:8080/stream/
```

### Check stream with FFplay

```bash
ffplay rtsp://<IP_ADDR_BOARD>:8554/stream
```

### Show ROS2 interface

```bash
ros2 interface show gps_position_msgs/msg/GpsPosition
```
