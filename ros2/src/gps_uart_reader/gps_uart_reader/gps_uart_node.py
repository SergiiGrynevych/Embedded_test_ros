#!/usr/bin/env python3

import serial
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from gps_position_msgs.msg import GpsPosition


def nmea_to_decimal(raw_value: str, direction: str):
    if not raw_value or not direction:
        return None

    try:
        if direction in ("N", "S"):
            deg = int(raw_value[:2])
            minutes = float(raw_value[2:])
        elif direction in ("E", "W"):
            deg = int(raw_value[:3])
            minutes = float(raw_value[3:])
        else:
            return None

        value = deg + minutes / 60.0

        if direction in ("S", "W"):
            value = -value

        return value
    except Exception:
        return None


def parse_gga(parts):
    """
    example:
    $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
    """
    if len(parts) < 10:
        return None

    lat = nmea_to_decimal(parts[2], parts[3])
    lon = nmea_to_decimal(parts[4], parts[5])

    lat_dir = parts[3]
    lon_dir = parts[5]
    fix_quality = parts[6]
    satellites = parts[7]
    altitude = parts[9]

    try:
        satellites = int(satellites) if satellites else 0
    except Exception:
        satellites = 0

    try:
        altitude = float(altitude) if altitude else float('nan')
    except Exception:
        altitude = float('nan')

    return {
        "lat": lat,
        "lon": lon,
        "lat_dir": lat_dir,
        "lon_dir": lon_dir,
        "fix_quality": fix_quality,
        "satellites": satellites,
        "altitude": altitude,
    }

class GpsUartNode(Node):
    def __init__(self):
        super().__init__('gps_uart_node')

        self.__initialize_params()
        self.__create_publishers()

        threading.Thread(target=self.read_loop, daemon=True).start()

    def __declare_parameters(self):
        self.declare_parameter('port', '/dev/ttyS5')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('timeout', 1.0)
        self.declare_parameter('reconnect_delay', 2.0)
        self.declare_parameter('gps_position_topic', '/gps_position')

    def __log_parameters(self):
        self.get_logger().info('=== GPS node configuration ===')
        self.get_logger().info(f'port: {self.port}')
        self.get_logger().info(f'baudrate: {self.baudrate}')
        self.get_logger().info(f'timeout: {self.timeout}')
        self.get_logger().info(f'reconnect_delay: {self.reconnect_delay}')
        self.get_logger().info(f'gps_position_topic: {self.gps_position_topic}')
        self.get_logger().info(
            f'QoS -> reliability={self.gps_qos.reliability}, ' 
            f'durability={self.gps_qos.durability}, '
            f'history={self.gps_qos.history}, '
            f'depth={self.gps_qos.depth}'
        )
        self.get_logger().info('==============================')

    def __initialize_params(self):
        self.__declare_parameters()

        self.running = True
        self.serial_port = None

        self.port = self.get_parameter('port').get_parameter_value().string_value
        self.baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.timeout = self.get_parameter('timeout').get_parameter_value().double_value
        self.reconnect_delay = self.get_parameter('reconnect_delay').get_parameter_value().double_value
        self.gps_position_topic = self.get_parameter('gps_position_topic').get_parameter_value().string_value

        self.gps_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.__log_parameters()

    def __create_publishers(self):
        self.gps_position_pub = self.create_publisher(
            GpsPosition,
            self.gps_position_topic,
            self.gps_qos
        )

    def __open_serial_port(self):
        try:
            serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            self.get_logger().info(f'UART open: {self.port} @ {self.baudrate}')
            return serial_port
        except (serial.SerialException, OSError) as e:
            self.get_logger().warn(f'Failed to open {self.port}: {e}')
            return None

    def __close_serial_port(self):
        try:
            if self.serial_port is not None and self.serial_port.is_open:
                self.serial_port.close()
                self.get_logger().warn(f'UART closed: {self.port}')
        except Exception as e:
            self.get_logger().warn(f'Error while closing UART: {e}')
        finally:
            self.serial_port = None

    def format_pretty_text(self, gga_data):
        lat = gga_data["lat"]
        lon = gga_data["lon"]
        lat_dir = gga_data["lat_dir"]
        lon_dir = gga_data["lon_dir"]
        satellites = gga_data["satellites"]
        fix_quality = gga_data["fix_quality"]

        if lat is None or lon is None:
            return "GPS: координати ще недоступні"

        lat_abs = abs(lat)
        lon_abs = abs(lon)

        if fix_quality == "0":
            return f"{lat_abs:.4f}° {lat_dir}, {lon_abs:.4f}° {lon_dir} | Супутники: {satellites} | FIX: немає"

        return f"{lat_abs:.4f}° {lat_dir}, {lon_abs:.4f}° {lon_dir} | Супутники: {satellites}"

    def publish_gps_position(self, gga_data):
        lat = gga_data["lat"]
        lon = gga_data["lon"]
        satellites = gga_data["satellites"]

        if lat is None or lon is None:
            return

        msg = GpsPosition()
        msg.latitude = float(lat)
        msg.longitude = float(lon)
        msg.satellites = satellites

        self.gps_position_pub.publish(msg)

    def handle_nmea_line(self, text):
        if not text.startswith("$"):
            return

        parts = text.split(",")

        if parts[0].endswith("GGA"):
            gga = parse_gga(parts)
            if not gga:
                return

            self.publish_gps_position(gga)
            self.get_logger().info(self.format_pretty_text(gga))

    def read_loop(self):
        while self.running and rclpy.ok():
            if self.serial_port is None or not self.serial_port.is_open:
                self.get_logger().info(
                    f'Attempting to connect to UART {self.port}...'
                )
                self.serial_port = self.__open_serial_port()

                if self.serial_port is None:
                    time.sleep(self.reconnect_delay)
                    continue

            try:
                line = self.serial_port.readline()
                if not line:
                    continue

                text = line.decode("ascii", errors="replace").strip()
                if not text:
                    continue

                self.handle_nmea_line(text)

            except (serial.SerialException, OSError) as e:
                self.get_logger().warn(f'UART read error: {e}. Reconnecting...')
                self.__close_serial_port()
                time.sleep(self.reconnect_delay)

            except Exception as e:
                self.get_logger().warn(f'Unexpected read error: {e}')
                time.sleep(0.2)

    def destroy_node(self):
        self.running = False

        try:
            if self.reader_thread.is_alive():
                self.reader_thread.join(timeout=1.0)
        except Exception:
            pass

        self.__close_serial_port()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GpsUartNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()