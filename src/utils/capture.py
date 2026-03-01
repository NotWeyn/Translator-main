import subprocess
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ScreenCapture:
    """
    Handles screen capturing on Wayland using grim and slurp.
    """
    
    @staticmethod
    def select_region() -> Optional[str]:
        """
        Interactive region selection using slurp.
        Returns the geometry string (e.g., "x,y wxh") or None if cancelled.
        """
        try:
            result = subprocess.run(['slurp'], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            logger.info("Region selection cancelled.")
            return None
        except FileNotFoundError:
            logger.error("slurp not found. Please install 'slurp'.")
            return None

    @staticmethod
    def capture_screenshot(output_path: str, region: Optional[str] = None) -> bool:
        """
        Captures a screenshot using grim.
        
        Args:
            output_path: Path to save the screenshot.
            region: Optional geometry string (from slurp). If None, captures full screen.
            
        Returns:
            True if successful, False otherwise.
        """
        cmd = ['grim']
        if region:
            cmd.extend(['-g', region])
        cmd.append(output_path)
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Screenshot failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("grim not found. Please install 'grim'.")
            return False
