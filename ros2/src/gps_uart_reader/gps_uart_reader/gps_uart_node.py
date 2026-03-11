#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import threading
import time

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix, NavSatStatus


def nmea_to_decimal(raw_value: str, direction: str):
    """
    NMEA -> decimal degrees
    lat: ddmm.mmmm
    lon: dddmm.mmmm

    Returns signed decimal coordinates:
    N/E -> +
    S/W -> -
    """
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

        self.declare_parameter('port', '/dev/ttyS5')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('timeout', 1.0)

        self.port = self.get_parameter('port').get_parameter_value().string_value
        self.baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.timeout = self.get_parameter('timeout').get_parameter_value().double_value

        self.serial_port = None
        self.running = True
        self.last_pretty = None

        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            self.get_logger().info(f'UART is open: {self.port} @ {self.baudrate}')
        except Exception as e:
            self.get_logger().error(f'Failed to open UART {self.port}: {e}')
            raise

        self.reader_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.reader_thread.start()

    def format_pretty_text(self, gga_data):
        lat = gga_data["lat"]
        lon = gga_data["lon"]
        lat_dir = gga_data["lat_dir"]
        lon_dir = gga_data["lon_dir"]
        satellites = gga_data["satellites"]
        fix_quality = gga_data["fix_quality"]

        if lat is None or lon is None:
            return "GPS: coordinates are not available yet"

        lat_abs = abs(lat)
        lon_abs = abs(lon)

        if fix_quality == "0":
            return f"{lat_abs:.4f}° {lat_dir}, {lon_abs:.4f}° {lon_dir} | Супутники: {satellites} | FIX: немає"

        return f"{lat_abs:.4f}° {lat_dir}, {lon_abs:.4f}° {lon_dir} | Супутники: {satellites}"

    def handle_nmea_line(self, text):
        if not text.startswith("$"):
            return

        parts = text.split(",")

        if parts[0].endswith("GGA"):
            gga = parse_gga(parts)
            if not gga:
                return

            pretty = self.format_pretty_text(gga)

            if pretty != self.last_pretty:
                self.get_logger().info(pretty)
                self.last_pretty = pretty

    def read_loop(self):
        while self.running and rclpy.ok():
            try:
                line = self.serial_port.readline()
                if not line:
                    continue

                text = line.decode("ascii", errors="replace").strip()
                if not text:
                    continue

                self.handle_nmea_line(text)

            except Exception as e:
                self.get_logger().warn(f'Error reading UART: {e}')
                time.sleep(0.2)

    def destroy_node(self):
        self.running = False

        try:
            if self.reader_thread.is_alive():
                self.reader_thread.join(timeout=1.0)
        except Exception:
            pass

        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.get_logger().info('UART closed')
        except Exception:
            pass

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