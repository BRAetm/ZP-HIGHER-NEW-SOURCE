"""
Settings — Load/save ZP HIGHER settings
Reconstructed from exe diagnostic output: load_settings, save_settings functions
"""

import json
import os

SETTINGS_PATH = os.path.expanduser("~/.zp_higher/settings.json")

DEFAULT_SETTINGS = {
    "trigger_percentage": 95,
    "trigger_percentage_l2": 75,
    "defense_enabled": False,
    "infinite_stamina": False,
    "stick_tempo_enabled": False,
    "quickstop_enabled": False,
    "contest_assist": True,
    "lateral_boost": True,
    "sensitivity_boost": True,
    "anti_blowby": True,
    "tempo_ms": 39,
    "calibration_history": [],
}


def load_settings() -> dict:
    """Load settings from disk. Returns defaults if file missing/invalid."""
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, 'r') as f:
            data = json.load(f)
        # Merge with defaults to handle missing keys
        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings
    except (json.JSONDecodeError, IOError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> bool:
    """Save settings to disk. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except IOError:
        return False
