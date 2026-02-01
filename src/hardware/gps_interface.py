"""
GPS Interface - Interfaces with GPS hardware module
"""

import logging
import serial
from typing import Optional, Tuple

from utils.logger import setup_logger


class GPSInterface:
    """
    Interface for GPS module (NEO-6M or similar)
    """
    
    def __init__(self, config):
        """
        Initialize GPS interface
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('GPSInterface', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        self.port = config.get('gps.port', '/dev/ttyAMA0')
        self.baudrate = config.get('gps.baudrate', 9600)
        self.timeout = config.get('gps.timeout', 1)
        
        # Serial connection
        self.serial = None
        
        # Current location
        self.latitude = None
        self.longitude = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize GPS connection"""
        try:
            self.logger.info(f"Initializing GPS on port {self.port}")
            self.serial = serial.Serial(
                self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.logger.info("GPS initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize GPS: {e}")
            self.logger.info("GPS will use simulated data for testing")
    
    def get_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current GPS location
        
        Returns:
            Tuple of (latitude, longitude) or None
        """
        if self.serial is None:
            # Return simulated location for testing
            return (37.7749, -122.4194)  # San Francisco coordinates
        
        try:
            # Read NMEA sentence
            line = self.serial.readline().decode('ascii', errors='ignore')
            
            # Parse GPGGA sentence
            if line.startswith('$GPGGA'):
                parts = line.split(',')
                
                if len(parts) > 6 and parts[2] and parts[4]:
                    # Parse latitude
                    lat = float(parts[2][:2]) + float(parts[2][2:]) / 60
                    if parts[3] == 'S':
                        lat = -lat
                    
                    # Parse longitude
                    lon = float(parts[4][:3]) + float(parts[4][3:]) / 60
                    if parts[5] == 'W':
                        lon = -lon
                    
                    self.latitude = lat
                    self.longitude = lon
                    
                    return (lat, lon)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error reading GPS: {e}")
            return None
    
    def shutdown(self):
        """Shutdown GPS"""
        if self.serial:
            self.serial.close()
        self.logger.info("GPS shutdown")
