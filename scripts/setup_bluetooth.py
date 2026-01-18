#!/usr/bin/env python3
"""
Script to setup and test Bluetooth headset on Raspberry Pi 5.
"""

import sys
import subprocess
import time

def enable_bluetooth():
    """Enable Bluetooth service."""
    try:
        subprocess.run(["sudo", "systemctl", "enable", "bluetooth"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "bluetooth"], check=True)
        print("Bluetooth service enabled and started.")
    except subprocess.CalledProcessError:
        print("Failed to enable/start Bluetooth service.")

def scan_devices():
    """Scan for Bluetooth devices."""
    try:
        result = subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True, timeout=10)
        print("Bluetooth scan initiated. Available devices:")
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("Scan timeout. Stopping scan.")
        subprocess.run(["bluetoothctl", "scan", "off"])
    except subprocess.CalledProcessError:
        print("Failed to scan Bluetooth devices.")

def pair_device(device_address):
    """Pair with a Bluetooth device."""
    try:
        subprocess.run(["bluetoothctl", "pair", device_address], check=True)
        subprocess.run(["bluetoothctl", "connect", device_address], check=True)
        print(f"Paired and connected to device: {device_address}")
    except subprocess.CalledProcessError:
        print(f"Failed to pair/connect to device: {device_address}")

if __name__ == "__main__":
    print("Setting up Bluetooth...")
    enable_bluetooth()
    scan_devices()
    # Note: Pairing requires user input for device address
    print("To pair a device, run: python setup_bluetooth.py <device_address>")
    if len(sys.argv) > 1:
        pair_device(sys.argv[1])
    else:
        print("Bluetooth setup initiated. Run with device address to pair.")
