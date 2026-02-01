"""
Obstacle Sensor - Ultrasonic sensor for obstacle detection
"""

import logging
import time
from utils.logger import setup_logger

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class ObstacleSensor:
    """
    Ultrasonic sensor (HC-SR04) for obstacle detection
    """
    
    def __init__(self, config):
        """
        Initialize obstacle sensor
        
        Args:
            config: Configuration object
        """
        self.logger = setup_logger('ObstacleSensor', 'data/logs/blind_assistant.log')
        self.config = config
        
        # Get configuration
        sensors = config.get('obstacle_detection.sensors', [])
        if sensors:
            sensor = sensors[0]
            self.trigger_pin = sensor.get('pin_trigger', 23)
            self.echo_pin = sensor.get('pin_echo', 24)
            self.max_distance = sensor.get('max_distance', 400)
        else:
            self.trigger_pin = 23
            self.echo_pin = 24
            self.max_distance = 400
        
        # Initialize GPIO
        self._initialize()
    
    def _initialize(self):
        """Initialize GPIO pins"""
        if not GPIO_AVAILABLE:
            self.logger.warning("RPi.GPIO not available. Using simulated sensor.")
            return
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            self.logger.info("Obstacle sensor initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize obstacle sensor: {e}")
    
    def get_distance(self) -> float:
        """
        Get distance to nearest obstacle
        
        Returns:
            Distance in centimeters
        """
        if not GPIO_AVAILABLE:
            # Return simulated distance for testing
            return 150.0
        
        try:
            # Send trigger pulse
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trigger_pin, False)
            
            # Wait for echo
            start_time = time.time()
            stop_time = time.time()
            
            while GPIO.input(self.echo_pin) == 0:
                start_time = time.time()
            
            while GPIO.input(self.echo_pin) == 1:
                stop_time = time.time()
            
            # Calculate distance
            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2
            
            return min(distance, self.max_distance)
            
        except Exception as e:
            self.logger.error(f"Error reading obstacle sensor: {e}")
            return self.max_distance
    
    def shutdown(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE:
            GPIO.cleanup()
        self.logger.info("Obstacle sensor shutdown")
