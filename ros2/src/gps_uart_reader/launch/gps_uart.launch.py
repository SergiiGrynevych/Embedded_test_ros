from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='gps_uart_reader',
            executable='gps_node',
            name='gps_uart_node',
            output='screen',
            parameters=[
                {
                    'port': '/dev/ttyS5',
                    'baudrate': 9600,
                    'timeout': 1.0,
                    'reconnect_delay': 2.0,
                    'gps_position_topic': '/gps_position',
                }
            ]
        )
    ])
