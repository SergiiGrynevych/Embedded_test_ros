#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import sys
import time

UART_PORT = "/dev/ttyS5"
BAUDRATE = 9600
TIMEOUT = 1.0
RECONNECT_DELAY = 2.0

def nmea_to_decimal_with_dir(raw_value: str, direction: str):
    """
    NMEA -> decimal degrees
    lat: ddmm.mmmm
    lon: dddmm.mmmm
    """
    if not raw_value or not direction:
        return None, None

    try:
        if direction in ("N", "S"):
            if len(raw_value) < 4:
                return None, None
            deg = int(raw_value[:2])
            minutes = float(raw_value[2:])
        elif direction in ("E", "W"):
            if len(raw_value) < 5:
                return None, None
            deg = int(raw_value[:3])
            minutes = float(raw_value[3:])
        else:
            return None, None

        value = deg + minutes / 60.0
        return value, direction

    except (ValueError, TypeError):
        return None, None

def parse_gga(parts):
    """
    $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
    """
    if len(parts) < 8:
        return None

    lat, lat_dir = nmea_to_decimal_with_dir(parts[2], parts[3])
    lon, lon_dir = nmea_to_decimal_with_dir(parts[4], parts[5])
    fix_quality = parts[6]
    satellites = parts[7]

    return {
        "lat": lat,
        "lat_dir": lat_dir,
        "lon": lon,
        "lon_dir": lon_dir,
        "fix_quality": fix_quality,
        "satellites": satellites,
    }

def format_gps_line(gga_data):
    if not gga_data:
        return None

    lat = gga_data["lat"]
    lon = gga_data["lon"]
    lat_dir = gga_data["lat_dir"]
    lon_dir = gga_data["lon_dir"]
    satellites = gga_data["satellites"]
    fix_quality = gga_data["fix_quality"]

    if lat is None or lon is None:
        return "GPS: coordinates not yet available"

    if fix_quality == "0":
        return f"{lat:.4f}° {lat_dir}, {lon:.4f}° {lon_dir} | Супутники: {satellites} | FIX: немає"

    return f"{lat:.4f}° {lat_dir}, {lon:.4f}° {lon_dir} | Супутники: {satellites}"


def close_serial_safely(ser):
    if ser is not None:
        try:
            if ser.is_open:
                ser.close()
        except Exception:
            pass


def open_serial_port(port: str, baudrate: int, timeout: float):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        print(f"[INFO] UART open: {port} @ {baudrate}")
        return ser
    except (serial.SerialException, OSError) as e:
        print(f"[WARN] Failed to open {port}: {e}")
        return None


def read_line_from_serial(ser):
    line = ser.readline()
    if not line:
        return None

    try:
        return line.decode("ascii", errors="replace").strip()
    except UnicodeDecodeError:
        return None


def read_loop(ser):
    while True:
        text = read_line_from_serial(ser)
        if not text:
            continue

        if not text.startswith("$"):
            continue

        parts = text.split(",")

        if not parts:
            continue

        if parts[0].endswith("GGA"):
            gga = parse_gga(parts)

            if gga is None:
                print(f"[WARN] Invalid GGA line: {text}")
                continue

            pretty = format_gps_line(gga)
            if pretty:
                print(pretty)


def main():
    port = UART_PORT
    if len(sys.argv) > 1:
        port = sys.argv[1]
        prinf(f"[INFO] Using port from argument: {port}")

    ser = None

    try:
        while True:
            if ser is None or not ser.is_open:
                ser = open_serial_port(
                    port=port,
                    baudrate=BAUDRATE,
                    timeout=TIMEOUT,
                )

                if ser is None:
                    time.sleep(RECONNECT_DELAY)
                    continue

            try:
                read_loop(ser)

            except (serial.SerialException, OSError) as e:
                print(f"[WARN] Port {port} disconnected: {e}")
                close_serial_safely(ser)
                ser = None
                print(f"[INFO] Retrying connection in {RECONNECT_DELAY} seconds...")
                time.sleep(RECONNECT_DELAY)

            except Exception as e:
                print(f"[WARN] Unknown error occurred: {e}")
                close_serial_safely(ser)
                ser = None
                print(f"[INFO] Retrying connection in {RECONNECT_DELAY} seconds...")
                time.sleep(RECONNECT_DELAY)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")
    finally:
        close_serial_safely(ser)
        print("[INFO] UART closed")


if __name__ == "__main__":
    main()