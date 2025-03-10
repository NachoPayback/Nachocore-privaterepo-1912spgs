import os
import json
from builder.utils import normalize_task_type

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

def generate_static_manifest():
    project_root = get_project_root()
    # Build TASK_MANIFEST dynamically:
    tasks_folder = os.path.join(project_root, "shared", "tasks")
    task_manifest = {}
    for filename in os.listdir(tasks_folder):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = os.path.splitext(filename)[0]
            # For simplicity, assume the TASK_TYPE is the normalized module name.
            # (For a robust solution, you might import the module and extract TASK_TYPE.)
            task_manifest[module_name] = f"shared.tasks.{module_name}"
    
    # Load config.json to get current gift card selection and security settings.
    config_path = os.path.join(project_root, "builder", "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        print("Error loading config.json:", e)
        config = {}
    gift_card = config.get("selected_gift_card", {})
    security_settings = {key: config.get(key) for key in [
        "USE_UI_KEYBOARD", "KEYBOARD_BLOCKER_MODE", "ENABLE_MOUSE_LOCKER",
        "ENABLE_SLEEP_BLOCKER", "ENABLE_SECURITY_MONITOR", "CLOSE_BUTTON_DISABLED",
        "ENABLE_LOGGER", "SECURITY_MODE"
    ]}
    
    manifest = {
        "TASK_MANIFEST": task_manifest,
        "GIFT_CARD_STATIC": gift_card,
        "SECURITY_SETTINGS_STATIC": security_settings
    }
    
    # Write out to builder/static_manifest.py
    manifest_path = os.path.join(project_root, "builder", "static_manifest.py")
    with open(manifest_path, "w") as f:
        f.write("# This file is auto-generated. Do not edit manually.\n")
        f.write("TASK_MANIFEST = " + json.dumps(manifest["TASK_MANIFEST"], indent=4) + "\n")
        f.write("GIFT_CARD_STATIC = " + json.dumps(manifest["GIFT_CARD_STATIC"], indent=4) + "\n")
        f.write("SECURITY_SETTINGS_STATIC = " + json.dumps(manifest["SECURITY_SETTINGS_STATIC"], indent=4) + "\n")
    print("Static manifest generated at:", manifest_path)

if __name__ == "__main__":
    generate_static_manifest()
