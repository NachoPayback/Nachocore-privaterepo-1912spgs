#!/usr/bin/env python3
import os
import json
import glob
import importlib.util
from shared.utils.data_helpers import get_data_path
from builder.utils import normalize_task_type

def generate_static_manifest():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # --- Build TASK_MANIFEST ---
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
    
    # --- Load static gift card data and security settings from config.json ---
    config_path = os.path.join(project_root, "builder", "config.json")
    gift_card_static = {}
    security_settings_static = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            gift_card_static = config.get("selected_gift_card", {})
            # Build security settings from top-level keys:
            security_settings_static = {
                "SECURITY_MODE": config.get("SECURITY_MODE", "Ethical"),
                "USE_UI_KEYBOARD": config.get("USE_UI_KEYBOARD", True),
                "KEYBOARD_BLOCKER_MODE": config.get("KEYBOARD_BLOCKER_MODE", 1),
                "ENABLE_MOUSE_LOCKER": config.get("ENABLE_MOUSE_LOCKER", False),
                "ENABLE_SLEEP_BLOCKER": config.get("ENABLE_SLEEP_BLOCKER", False),
                "ENABLE_SECURITY_MONITOR": config.get("ENABLE_SECURITY_MONITOR", False),
                "CLOSE_BUTTON_DISABLED": config.get("CLOSE_BUTTON_DISABLED", False),
                "ENABLE_LOGGER": config.get("ENABLE_LOGGER", True)
            }
            print("DEBUG: Security settings to be burned in:", security_settings_static)
        except Exception as e:
            print("Error loading config for manifest:", e)
    
    manifest = {
        "TASK_MANIFEST": task_manifest,
        "GIFT_CARD_STATIC": gift_card_static,
        "SECURITY_SETTINGS_STATIC": security_settings_static
    }
    
    manifest_path = os.path.join(project_root, "builder", "static_manifest.py")
    try:
        with open(manifest_path, "w") as f:
            f.write("# Auto-generated static manifest\n")
            f.write("TASK_MANIFEST = ")
            json.dump(task_manifest, f, indent=4)
            f.write("\n\n")
            f.write("GIFT_CARD_STATIC = ")
            json.dump(gift_card_static, f, indent=4)
            f.write("\n\n")
            f.write("SECURITY_SETTINGS_STATIC = ")
            json.dump(security_settings_static, f, indent=4)
            f.write("\n")
        print("Static manifest generated successfully.")
    except Exception as e:
        print("Error generating static manifest:", e)

if __name__ == "__main__":
    generate_static_manifest()
