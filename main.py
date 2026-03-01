import sys
import logging
import signal
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
    """Launch the Screen Translator GUI."""
    global app_instance, window_instance
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    app_instance = QApplication(sys.argv)
    window_instance = SettingsWindow()
    window_instance.show()
    
    # Setup timer to allow Python signal handlers to run
    # This makes Ctrl+C work in console
    timer = QTimer()
    timer.start(500)  # Check every 500ms
    timer.timeout.connect(lambda: None)  # Allow Python to process signals
    
    sys.exit(app_instance.exec())

if __name__ == "__main__":
    main()
