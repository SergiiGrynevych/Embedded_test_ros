# TASK:1

## run application: 
cd ~
python3 UART_ParsingGPS.py

## dependency for this app (if it is not installed):
pip3 install pyserial

# TASK:3
I use ros2-humble

## dependency 
pip3 install pyserial
sudo apt install python3-colcon-common-extensions
## need to intall ros2 

## build
cd ~/ros2 
colcon build --packages-select gps_uart_reader

source ~/ros2/install/setup.bash

## launch:
cd ~/ros2/src/gps_uart_reader/launch
- run from ros2 run:
ros2 run gps_uart_reader gps_uart_node --ros-args -p port:=/dev/ttyS5 -p baudrate:=9600
- run from ros2 launch:
ros2 launch gps_uart_reader gps_uart.launch.py


First Task: 
node name: gps_uart_reader

