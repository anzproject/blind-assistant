"""
Navigation Engine - Provides turn-by-turn navigation
"""

import logging
from typing import Optional, Tuple

from utils.logger import setup_logger

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False


class NavigationEngine:
    """
    Navigation engine using Google Maps API
    """
    
    def __init__(self, config, gps_module, audio_manager):
        """
        Initialize navigation engine
        
        Args:
            config: Configuration object
            gps_module: GPS module instance
            audio_manager: Audio manager instance
        """
        self.logger = setup_logger('NavigationEngine', 'data/logs/blind_assistant.log')
        self.config = config
        self.gps = gps_module
        self.audio = audio_manager
        
        # Get configuration
        self.api_key = config.get('api_keys.google_maps_api_key', '')
        self.mode = config.get('navigation.mode', 'walking')
        self.units = config.get('navigation.units', 'metric')
        
        # Google Maps client
        self.gmaps = None
        
        # Navigation state
        self.navigating = False
        self.current_route = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Maps client"""
        if not GOOGLEMAPS_AVAILABLE:
            self.logger.warning("googlemaps library not installed")
            return
        
        if not self.api_key:
            self.logger.warning("Google Maps API key not configured")
            return
        
        try:
            self.gmaps = googlemaps.Client(key=self.api_key)
            self.logger.info("Google Maps client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Maps: {e}")
    
    def navigate_to(self, destination: str) -> bool:
        """
        Start navigation to destination
        
        Args:
            destination: Destination address or place name
            
        Returns:
            True if navigation started successfully
        """
        if not self.gmaps:
            self.logger.error("Google Maps not available")
            return False
        
        if not self.gps:
            self.logger.error("GPS not available")
            return False
        
        try:
            # Get current location
            current_location = self.gps.get_location()
            if not current_location:
                self.logger.error("Unable to get current location")
                return False
            
            # Get directions
            directions = self.gmaps.directions(
                current_location,
                destination,
                mode=self.mode,
                units=self.units
            )
            
            if not directions:
                self.logger.error("No route found")
                return False
            
            self.current_route = directions[0]
            self.navigating = True
            
            # Announce start of navigation
            if self.audio:
                self.audio.speak_high(f"Navigation started to {destination}")
            
            self.logger.info(f"Navigation started to {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting navigation: {e}")
            return False
    
    def get_address(self, lat: float, lon: float) -> Optional[str]:
        """
        Get address from coordinates (reverse geocoding)
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Address string or None
        """
        if not self.gmaps:
            return None
        
        try:
            result = self.gmaps.reverse_geocode((lat, lon))
            if result:
                return result[0]['formatted_address']
            return None
        except Exception as e:
            self.logger.error(f"Error in reverse geocoding: {e}")
            return None
    
    def stop(self):
        """Stop navigation"""
        self.navigating = False
        self.current_route = None
        
        if self.audio:
            self.audio.speak("Navigation stopped")
        
        self.logger.info("Navigation stopped")
    
    def shutdown(self):
        """Shutdown navigation"""
        self.stop()
        self.logger.info("Navigation engine shutdown")
