#!/usr/bin/env python3
"""
Script to setup and test PiCamera2 on Raspberry Pi 5.
"""

import sys
import subprocess

def install_picamera2():
    """Install PiCamera2 if not already installed."""
    try:
        import picamera2
        print("PiCamera2 is already installed.")
    except ImportError:
        print("Installing PiCamera2...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "picamera2"])
        print("PiCamera2 installed successfully.")

def test_camera():
    """Test camera functionality."""
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        print("Camera initialized successfully.")
        # Basic test: capture a frame
        config = picam2.create_still_configuration()
        picam2.configure(config)
        picam2.start()
        frame = picam2.capture_array()
        picam2.stop()
        print(f"Camera test successful. Frame shape: {frame.shape}")
    except Exception as e:
        print(f"Camera test failed: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Setting up PiCamera2...")
    install_picamera2()
    if test_camera():
        print("Camera setup complete.")
    else:
        print("Camera setup failed. Please check hardware connections.")
