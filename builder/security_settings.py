#!/usr/bin/env python3
import os
import json

# Define the default config file location.
# (Assuming config.json remains in the same folder as security_settings.py)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Default security settings for each mode.
DEFAULTS = {
    "Ethical": {
        "USE_UI_KEYBOARD": False,
        "KEYBOARD_BLOCKER_MODE": 2,
        "ENABLE_MOUSE_LOCKER": False,
        "ENABLE_SLEEP_BLOCKER": False,
        "ENABLE_SECURITY_MONITOR": False,
        "CLOSE_BUTTON_DISABLED": False,
        "ENABLE_LOGGER": True
    },
    "Unethical": {
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "ENABLE_SECURITY_MONITOR": True,
        "CLOSE_BUTTON_DISABLED": True,
        "ENABLE_LOGGER": True
    },
    "Grift": {
        # Placeholder settings for Grift mode; update as needed.
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "ENABLE_SECURITY_MONITOR": True,
        "CLOSE_BUTTON_DISABLED": True,
        "ENABLE_LOGGER": True
    }
}

def load_security_settings():
    """Load existing security settings from the config file."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_security_settings(new_settings):
    """Save the provided security settings to the config file."""
    current_settings = load_security_settings()
    current_settings.update(new_settings)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(current_settings, f, indent=4)
        return True, "Settings saved successfully."
    except Exception as e:
        return False, f"Error saving settings: {e}"

# Update imports to reflect the new security folder structure.
from shared.security.close_button_blocker_security import disable_close_button, enable_close_button
from shared.security.keyboard_blocker_security import start_keyboard_blocker, stop_keyboard_blocker
from shared.security.mouse_locker_security import start_mouse_locker, stop_mouse_locker
from shared.security.sleep_blocker_security import start_sleep_blocker, stop_sleep_blocker
from shared.security.security_monitor_security import start_security_monitor, stop_security_monitor

def set_mode(mode, custom_settings=None):
    """
    Set the security settings based on the selected mode.

    Args:
        mode (str): One of "Ethical", "Unethical", "Grift", or "Custom".
        custom_settings (dict, optional): Custom settings for "Custom" mode.

    Returns:
        tuple: (success_flag, message, settings_dictionary)
    """
    if mode in ["Ethical", "Unethical", "Grift"]:
        settings = DEFAULTS[mode]
    elif mode == "Custom":
        # For custom mode, if no settings are provided, load existing ones.
        if custom_settings is None:
            settings = load_security_settings()
        else:
            settings = custom_settings
    else:
        settings = {}
    
    success, message = save_security_settings(settings)
    return success, message, settings

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Set and save security settings for the game."
    )
    parser.add_argument(
        "--mode",
        choices=["Ethical", "Unethical", "Grift", "Custom"],
        default="Ethical",
        help="Select a security mode (default: Ethical)"
    )
    parser.add_argument("--use-ui-keyboard", type=lambda s: s.lower() in ['true', '1', 'yes'], help="Use UI Keyboard")
    parser.add_argument("--keyboard-blocker-mode", type=int, help="Keyboard Blocker Mode")
    parser.add_argument("--enable-mouse-locker", type=lambda s: s.lower() in ['true', '1', 'yes'], help="Enable Mouse Locker")
    parser.add_argument("--enable-sleep-blocker", type=lambda s: s.lower() in ['true', '1', 'yes'], help="Enable Sleep Blocker")
    parser.add_argument("--enable-security-monitor", type=lambda s: s.lower() in ['true', '1', 'yes'], help="Enable Security Monitor")
    parser.add_argument("--close-button-disabled", type=lambda s: s.lower() in ['true', '1', 'yes'], help="Disable Close Button")
    parser.add_argument("--enable-logger", type=lambda s: s.lower() in ['true', '1', 'yes'], help="Enable Logger")

    args = parser.parse_args()
    
    if args.mode == "Custom":
        custom_settings = {}
        if args.use_ui_keyboard is not None:
            custom_settings["USE_UI_KEYBOARD"] = args.use_ui_keyboard
        if args.keyboard_blocker_mode is not None:
            custom_settings["KEYBOARD_BLOCKER_MODE"] = args.keyboard_blocker_mode
        if args.enable_mouse_locker is not None:
            custom_settings["ENABLE_MOUSE_LOCKER"] = args.enable_mouse_locker
        if args.enable_sleep_blocker is not None:
            custom_settings["ENABLE_SLEEP_BLOCKER"] = args.enable_sleep_blocker
        if args.enable_security_monitor is not None:
            custom_settings["ENABLE_SECURITY_MONITOR"] = args.enable_security_monitor
        if args.close_button_disabled is not None:
            custom_settings["CLOSE_BUTTON_DISABLED"] = args.close_button_disabled
        if args.enable_logger is not None:
            custom_settings["ENABLE_LOGGER"] = args.enable_logger
        mode_settings = custom_settings
    else:
        mode_settings = None

    success, message, settings = set_mode(args.mode, custom_settings=mode_settings)
    if success:
        print(f"Mode '{args.mode}' applied successfully.")
        print(settings)
    else:
        print(message)
