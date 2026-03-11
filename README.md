use ros2-humble

dependency 
pip3 install pyserial
sudo apt install python3-colcon-common-extensions


build
cd ~/ros2 
colcon build --packages-select gps_uart_reader

source ~/ros2/install/setup.bash

launch:
cd ~/ros2/src/gps_uart_reader/launch
- run from ros2 run:
ros2 run gps_uart_reader gps_uart_node --ros-args -p port:=/dev/ttyS5 -p baudrate:=9600
- run from ros2 launch:
ros2 launch gps_uart_reader gps_uart.launch.py

