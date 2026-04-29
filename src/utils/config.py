import json
import os
from typing import Dict, Any

CONFIG_FILE = os.path.expanduser("~/.config/screen_translator/config.json")

DEFAULT_CONFIG = {
    "ocr_backend": "EasyOCR",
    "translator_backend": "Argos Translate",
    "source_lang": "auto",
    "target_lang": "tr",
    "openai_api_key": "",
    "deepl_api_key": "",
    "use_gpu": True,
    "correction_enabled": True,
    "region": "",  # Selected screen region (saved from slurp)
    "interval": 5  # Translation check interval in ticks
}

class ConfigManager:
    """
    Manages application configuration.
    """
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Loads config from file or returns default."""
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG.copy()
            
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with default to ensure all keys exist
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(config: Dict[str, Any]):
        """Saves config to file."""
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
