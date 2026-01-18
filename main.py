#!/usr/bin/env python3
"""
Main entry point for AI Blind Assistant.
"""

import sys
import logging
import signal
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from assistant import BlindAssistant
from config import LOGS_DIR, LOG_LEVEL

def setup_logging():
    """Setup logging configuration."""
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / "blind_assistant.log"

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logging.info("Shutdown signal received. Stopping assistant...")
    if 'assistant' in globals():
        assistant.stop()
    sys.exit(0)

def main():
    """Main function."""
    setup_logging()
    logging.info("Starting AI Blind Assistant...")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize and start assistant
        global assistant
        assistant = BlindAssistant()
        assistant.start()

        # Keep the main thread alive
        while assistant.is_running:
            signal.pause()

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
    finally:
        if 'assistant' in globals():
            assistant.stop()
        logging.info("AI Blind Assistant stopped.")

if __name__ == "__main__":
    main()
