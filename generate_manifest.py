#!/usr/bin/env python3
import os
import json
import glob
import importlib.util

# ADAPT IF NEEDED:
# If "shared.utils.data_helpers" or "builder.utils" are in a different folder,
# ensure your Python path includes them or fix these import statements.
from shared.utils.data_helpers import get_data_path
from builder.utils import normalize_task_type

def generate_static_manifest():
    """
    Generate builder/static_manifest.py, containing:
      - TASK_MANIFEST: mapping of normalized task types to their modules
      - GIFT_CARD_STATIC: selected gift card data
      - SECURITY_SETTINGS_STATIC: top-level security settings
    Writes valid Python code (with True/False) rather than JSON booleans.
    """
    # -----------------------------------------------------------------------
    # 1) Identify your current folder and the 'builder' subfolder:
    # -----------------------------------------------------------------------
    script_dir = os.path.abspath(os.path.dirname(__file__))
    builder_dir = os.path.join(script_dir, "builder")
    os.makedirs(builder_dir, exist_ok=True)  
    # This ensures "builder" exists, so we never get a "No such file or directory" error.

    # -----------------------------------------------------------------------
    # 2) Scan shared/tasks to build TASK_MANIFEST
    # -----------------------------------------------------------------------
    tasks_folder = get_data_path(os.path.join("shared", "tasks"))
    task_manifest = {}

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
                task_manifest[normalized] = f"shared.tasks.{module_name}"
        except Exception as e:
            print(f"Error importing {filename} for manifest: {e}")

    # -----------------------------------------------------------------------
    # 3) Load config.json from builder/ to get gift card & security settings
    # -----------------------------------------------------------------------
    config_path = os.path.join(builder_dir, "config.json")
    gift_card_static = {}
    security_settings_static = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            gift_card_static = config.get("selected_gift_card", {})

            # Build the dictionary with Python booleans instead of JSON booleans
            security_settings_static = {
                "SECURITY_MODE": config.get("SECURITY_MODE", "Ethical"),
                "USE_UI_KEYBOARD": config.get("USE_UI_KEYBOARD", True),
                "KEYBOARD_BLOCKER_MODE": config.get("KEYBOARD_BLOCKER_MODE", 1),
                "ENABLE_MOUSE_LOCKER": config.get("ENABLE_MOUSE_LOCKER", False),
                "ENABLE_SLEEP_BLOCKER": config.get("ENABLE_SLEEP_BLOCKER", False),
                "ENABLE_SECURITY_MONITOR": config.get("ENABLE_SECURITY_MONITOR", False),
                "CLOSE_BUTTON_DISABLED": config.get("CLOSE_BUTTON_DISABLED", False),
                "ENABLE_LOGGER": config.get("ENABLE_LOGGER", True),
            }
            print("DEBUG: Security settings to be written:", security_settings_static)
        except Exception as e:
            print("Error loading config for manifest:", e)

    # We'll combine everything into a single "manifest" dict, but writing them
    # separately below so that static_manifest.py has individual top-level keys.
    manifest_path = os.path.join(builder_dir, "static_manifest.py")

    # -----------------------------------------------------------------------
    # 4) Write builder/static_manifest.py as valid Python (NOT JSON)
    # -----------------------------------------------------------------------
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("# Auto-generated static manifest\n")
            # Repr approach => booleans become True/False
            f.write(f"TASK_MANIFEST = {repr(task_manifest)}\n\n")
            f.write(f"GIFT_CARD_STATIC = {repr(gift_card_static)}\n\n")
            f.write(f"SECURITY_SETTINGS_STATIC = {repr(security_settings_static)}\n")

        print(f"Static manifest generated successfully at: {manifest_path}")
    except Exception as e:
        print("Error generating static manifest:", e)

if __name__ == "__main__":
    generate_static_manifest()
