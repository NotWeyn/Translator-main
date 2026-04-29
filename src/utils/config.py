import os
import copy
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Config file lives next to start.sh (project root)
# We resolve it relative to this file's location: src/utils/config.py -> ../../config.toml
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.toml")

# ─── Default configuration (nested structure matching TOML sections) ───

DEFAULT_CONFIG: Dict[str, Any] = {
    "general": {
        "source_lang": "auto",
        "target_lang": "tr",
        "theme": "dark",
    },
    "ocr": {
        "backend": "EasyOCR",
        "use_gpu": True,
        "correction_enabled": True,
        "merge_distance": 20,
    },
    "translation": {
        "backend": "Argos Translate",
        "openai_api_key": "",
        "deepl_api_key": "",
        "llm_api_base": "http://127.0.0.1:5000/v1",
    },
    "capture": {
        "region": "",
        "interval": 5,
    },
    "overlay": {
        "enabled": False,
        "background_opacity": 0.75,
        "background_color": "#000000",
        "background_padding": 4,
        "font_family": "Arial",
        "font_size": 14,
        "font_color": "#FFFFFF",
        "font_bold": False,
        "target_region": "",
        "always_on_top": True,
        "click_through": True,
        "show_original": False,
        "refresh_interval": 3,
    },
    "hotkeys": {
        "toggle_overlay": "Ctrl+Shift+T",
        "select_region": "Ctrl+Shift+R",
        "stop_translation": "Escape",
    },
    "developer": {
        "perf_logging": False,
        "region_check": False,
        "log_level": "INFO",
    },
}

# ─── TOML template header (written once on first creation) ───

_TOML_HEADER = """\
# ═══════════════════════════════════════════════════
#  Screen Translator — config.toml
#  Bu dosya otomatik oluşturulmuştur.
#  Düzenleyerek ayarlarınızı özelleştirebilirsiniz.
# ═══════════════════════════════════════════════════

"""


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base* (returns a new dict)."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """
    Manages application configuration using a TOML file in the project root.
    The file is auto-created with sensible defaults when missing.
    """

    @staticmethod
    def ensure_config() -> str:
        """Create ``config.toml`` with defaults if it does not exist.

        Returns the absolute path to the config file.
        """
        if not os.path.exists(CONFIG_FILE):
            logger.info(f"config.toml not found – creating default at {CONFIG_FILE}")
            ConfigManager.save_config(DEFAULT_CONFIG)
        return CONFIG_FILE

    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Load config from ``config.toml``, merging with defaults so every
        key is guaranteed to exist even if the user deleted some lines."""
        import toml

        ConfigManager.ensure_config()

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
                user_cfg = toml.load(fh)
            merged = _deep_merge(copy.deepcopy(DEFAULT_CONFIG), user_cfg)
            return merged
        except Exception as exc:
            logger.error(f"Error loading config.toml: {exc} – falling back to defaults")
            return copy.deepcopy(DEFAULT_CONFIG)

    @staticmethod
    def save_config(config: Dict[str, Any]) -> None:
        """Write *config* dict to ``config.toml``."""
        import toml

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
                fh.write(_TOML_HEADER)
                toml.dump(config, fh)
            logger.info("config.toml saved")
        except Exception as exc:
            logger.error(f"Error saving config.toml: {exc}")

    # ── convenience helpers ──────────────────────────────────────────

    @staticmethod
    def get(config: Dict[str, Any], section: str, key: str, fallback=None):
        """Safe nested getter: ``ConfigManager.get(cfg, 'overlay', 'font_size')``."""
        return config.get(section, {}).get(key, fallback)

    @staticmethod
    def set(config: Dict[str, Any], section: str, key: str, value) -> None:
        """Safe nested setter (mutates *config* in-place)."""
        config.setdefault(section, {})[key] = value
