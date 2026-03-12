git clone this repo.
branch: master  

# TASK:1

## run application (script): 
cd ~
python3 UART_ParsingGPS.py

## TROUBLESHOOT. dependency for this app (if it is not installed):
pip3 install pyserial

# TASK:2
# launch app video cap: ffmpeg:
cd ~/VideoStreaming/
./mediamtx mediamtx_ffmpeg.yml

# launch app video cap: gstreamer:
cd ~/VideoStreaming/
./mediamtx mediamtx_gstreamer.yml

# check:
- you can go to ip address of board from another computer:
http://<IP_ADDR_BOARD>:8080/stream/

- you can get stream also from another computer by FFPLAY:
ffplay rtsp://<IP_ADDR_BOARD>:8554/stream

- you can get stream also from another computer by VLC:
rtsp://<IP_ADDR_BOARD>:8554/stream


## TROUBLESHOOT. dependency for this app (if it is not installed). only for GStreamer:
sudo apt install -y \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-rtsp \
  libgstrtspserver-1.0-0 \
  libgstrtspserver-1.0-dev


# TASK:3
in your system must be installed ros2 (humble, foxy, etc...)

## build (it will build ros2 interface: gps_position_msgs; package: gps_uart_reader)
cd ~/ros2
colcon build --packages-up-to gps_uart_reader 

source ~/ros2/install/setup.bash

## launch from ros2 launch:
source ~/ros2/install/setup.bash
cd ~/ros2
ros2 launch gps_uart_reader gps_uart.launch.py

## launch from ros2 run:
source ~/ros2/install/setup.bash
ros2 run gps_uart_reader gps_node --ros-args -p port:=/dev/ttyS5 -p baudrate:=9600

## dependency 
pip3 install pyserial
sudo apt install python3-colcon-common-extensions


## Show interface for task 3
ros2 interface show gps_position_msgs/msg/GpsPosition