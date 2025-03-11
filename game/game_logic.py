# game/game_logic.py
import os
import sys
import json
import glob
import importlib.util

# We assume your data_helpers is now in shared/security/data_helpers.py.
# If it's in a different location, adjust accordingly.
from shared.utils.data_helpers import get_data_path


def normalize_task_type(task_type: str) -> str:
    return task_type.lower().replace(" ", "_")

def load_security_settings():
    """
    Unified approach to load security settings.
    If frozen, load from static manifest's SECURITY_SETTINGS_STATIC.
    Otherwise, read from builder/config.json.
    """
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import SECURITY_SETTINGS_STATIC
            print("DEBUG: Loaded SECURITY_SETTINGS_STATIC from manifest:", SECURITY_SETTINGS_STATIC)
            return SECURITY_SETTINGS_STATIC
        except Exception as e:
            print("DEBUG: Could not load SECURITY_SETTINGS_STATIC from manifest:", e)
            # Fall back to config if something fails.
    # Not frozen or fallback:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(project_root, "builder", "config.json")
    defaults = {
        "SECURITY_MODE": "Ethical",
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": False,
        "ENABLE_SLEEP_BLOCKER": False,
        "ENABLE_SECURITY_MONITOR": False,
        "CLOSE_BUTTON_DISABLED": False,
        "ENABLE_LOGGER": True
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            defaults.update(config)
        except Exception as e:
            print("Error reading config.json for security:", e)
    return defaults

def load_all_tasks():
    """
    If frozen, load from static manifest's TASK_MANIFEST.
    Otherwise, read tasks from builder/data/tasks.json.
    """
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import TASK_MANIFEST
            print("DEBUG: Using TASK_MANIFEST from static manifest:", TASK_MANIFEST)
            # We'll still need to load the actual tasks data (like question text) from
            # builder/data/tasks.json, or store them in the static manifest as well.
            # If your manifest only stores the module mapping, you still need the actual tasks list.
            # We'll just do the normal file read for the actual tasks list:
        except Exception as e:
            print("DEBUG: Could not load TASK_MANIFEST from manifest:", e)
    
    tasks_file = get_data_path(os.path.join("builder", "data", "tasks.json"))
    if not os.path.exists(tasks_file):
        return []
    try:
        with open(tasks_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            for task in data:
                if "type" in task:
                    task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
                elif "TASK_TYPE" in task:
                    task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
            return data
        return []
    except Exception as e:
        print("Error loading tasks:", e)
        return []

def discover_task_modules():
    """
    If frozen, load from static manifest's TASK_MANIFEST for the import paths.
    Otherwise, discover dynamically from shared/tasks.
    """
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import TASK_MANIFEST
            # Return exactly what the static manifest says
            print("DEBUG: Using TASK_MANIFEST from static manifest:", TASK_MANIFEST)
            return TASK_MANIFEST
        except Exception as e:
            print("DEBUG: Could not load TASK_MANIFEST from manifest:", e)
            # Fall back to dynamic discovery
    # Dynamic (non-frozen) or fallback
    task_modules = {}
    tasks_folder = get_data_path(os.path.join("shared", "tasks"))
    for filepath in glob.glob(os.path.join(tasks_folder, "*.py")):
        filename = os.path.basename(filepath)
        if filename == "__init__.py":
            continue
        module_name = os.path.splitext(filename)[0]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "TASK_TYPE"):
                normalized = normalize_task_type(module.TASK_TYPE)
                task_modules[normalized] = f"shared.tasks.{module_name}"
        except Exception as e:
            print(f"Error importing {filename}: {e}")
    return task_modules

def load_gift_card():
    """
    If frozen, load GIFT_CARD_STATIC from static manifest.
    Otherwise, read from builder/config.json (selected_gift_card).
    """
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import GIFT_CARD_STATIC
            print("DEBUG: Loaded GIFT_CARD_STATIC from manifest:", GIFT_CARD_STATIC)
            return GIFT_CARD_STATIC
        except Exception as e:
            print("DEBUG: Could not load GIFT_CARD_STATIC from manifest:", e)
    # Not frozen or fallback
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(project_root, "builder", "config.json")
    gift_defaults = {"code": "XXXX-XXXX-XXXX", "pin": "----", "name": "Gift Card", "pin_required": True}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            gift = config_data.get("selected_gift_card", {})
            gift_defaults.update(gift)
            print("DEBUG: Loaded gift card from config.json:", gift_defaults)
            return gift_defaults
        except Exception as e:
            print("Error reading gift card from config.json:", e)
    return gift_defaults
