import os
import json
import glob
import pprint
from builder.utils import normalize_task_type

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

def generate_static_manifest():
    project_root = get_project_root()
    tasks_folder = os.path.join(project_root, "shared", "tasks")
    task_manifest = {}
    for filepath in glob.glob(os.path.join(tasks_folder, "*.py")):
        filename = os.path.basename(filepath)
        if filename == "__init__.py":
            continue
        module_name = os.path.splitext(filename)[0]
        try:
            spec = __import__("importlib").util.spec_from_file_location(module_name, filepath)
            module = __import__("importlib").util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "TASK_TYPE"):
                normalized = normalize_task_type(module.TASK_TYPE)
                task_manifest[normalized] = f"shared.tasks.{module_name}"
        except Exception as e:
            print("Error processing {}: {}".format(filename, e))
    
    config_path = os.path.join(project_root, "builder", "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        print("Error loading config.json:", e)
        config = {}
    
    gift_card_static = config.get("selected_gift_card", {})
    security_settings_static = { key: config.get(key) for key in [
        "USE_UI_KEYBOARD", "KEYBOARD_BLOCKER_MODE", "ENABLE_MOUSE_LOCKER",
        "ENABLE_SLEEP_BLOCKER", "ENABLE_SECURITY_MONITOR", "CLOSE_BUTTON_DISABLED",
        "ENABLE_LOGGER", "SECURITY_MODE"
    ]}
    
    manifest = {
        "TASK_MANIFEST": task_manifest,
        "GIFT_CARD_STATIC": gift_card_static,
        "SECURITY_SETTINGS_STATIC": security_settings_static
    }
    
    manifest_path = os.path.join(project_root, "builder", "static_manifest.py")
    try:
        with open(manifest_path, "w") as f:
            f.write("# This file is auto-generated. Do not edit manually.\n")
            f.write("TASK_MANIFEST = " + pprint.pformat(manifest["TASK_MANIFEST"]) + "\n\n")
            f.write("GIFT_CARD_STATIC = " + pprint.pformat(manifest["GIFT_CARD_STATIC"]) + "\n\n")
            f.write("SECURITY_SETTINGS_STATIC = " + pprint.pformat(manifest["SECURITY_SETTINGS_STATIC"]) + "\n")
        print("Static manifest generated at:", manifest_path)
    except Exception as e:
        print("Error writing static manifest:", e)

if __name__ == "__main__":
    generate_static_manifest()
