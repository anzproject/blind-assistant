"""
AI-Based Blind Assistant - Main Entry Point

This is the main application that initializes and coordinates all modules
of the blind assistant system.
"""

import sys
import signal
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.system_manager import SystemManager
from utils.logger import setup_logger


def signal_handler(sig, frame):
    """Handle graceful shutdown on CTRL+C"""
    logger.info("Shutdown signal received. Cleaning up...")
    if 'system_manager' in globals():
        system_manager.shutdown()
    sys.exit(0)


def main():
    """Main application entry point"""
    global logger, system_manager
    
    # Setup logging
    logger = setup_logger('main', 'data/logs/blind_assistant.log')
    logger.info("=" * 60)
    logger.info("AI-Based Blind Assistant Starting...")
    logger.info("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize system manager
        system_manager = SystemManager()
        
        # Start the system
        logger.info("Initializing system components...")
        system_manager.initialize()
        
        logger.info("System initialized successfully!")
        logger.info("Blind Assistant is ready. Listening for commands...")
        
        # Run main loop
        system_manager.run()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        if 'system_manager' in locals():
            system_manager.shutdown()
        logger.info("Blind Assistant stopped")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
