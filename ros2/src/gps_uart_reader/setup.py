from setuptools import setup
from glob import glob
import os

package_name = 'gps_uart_reader'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='ROS2 node for reading GPS data from UART and publishing NavSatFix',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'gps_node = gps_uart_reader.gps_uart_node:main',
        ],
    },
)