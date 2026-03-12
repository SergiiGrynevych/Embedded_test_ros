git clone this repo.
branch: master  

# TASK:1

## run application (script): 
cd ~
python3 UART_ParsingGPS.py

## TROUBLESHOOT. dependency for this app (if it is not installed):
pip3 install pyserial

# TASK:2


# TASK:3
I use ros2-humble

## dependency 
pip3 install pyserial
sudo apt install python3-colcon-common-extensions
## need to intall ros2 

## build
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


## Show interface for task 3
ros2 interface show gps_position_msgs/msg/GpsPosition