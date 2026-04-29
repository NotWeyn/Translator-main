import sys
import logging
import signal
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.ui.settings import SettingsWindow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Global reference for graceful shutdown
app_instance = None
window_instance = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("Ctrl+C detected, shutting down...")
    if window_instance:
        window_instance.stop_translation()
        window_instance.close()
    if app_instance:
        app_instance.quit()
    sys.exit(0)

def main():
    """Launch the Screen Translator."""
    global app_instance, window_instance
    
    parser = argparse.ArgumentParser(description="Screen Translator")
    parser.add_argument("--overlay", action="store_true",
                        help="Start in overlay mode (no GUI, reads config.toml)")
    args = parser.parse_args()
    
    if args.overlay:
        # Overlay mode — headless, fullscreen click-through overlay
        from src.ui.overlay_app import run_overlay
        run_overlay()
    else:
        # Normal GUI mode
        signal.signal(signal.SIGINT, signal_handler)
        
        app_instance = QApplication(sys.argv)
        window_instance = SettingsWindow()
        window_instance.show()
        
        # Setup timer to allow Python signal handlers to run
        timer = QTimer()
        timer.start(500)
        timer.timeout.connect(lambda: None)
        
        sys.exit(app_instance.exec())

if __name__ == "__main__":
    main()
