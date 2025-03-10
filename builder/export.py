#!/usr/bin/env python3
"""
Export Module

This module implements the export functionality for the game.
The export_exe function exports the game to an executable using PyInstaller.
It constructs the command with hidden imports and additional data files.
This version is updated to use get_data_path() for locating resources so that
the bundled executable finds all task modules, data files (like tasks.json, stylesheets,
gift card data), and shared modules.
"""

import os
import sys
import json
import subprocess
import glob
import importlib.util

# Ensure the project root (parent directory) is in sys.path.
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(current_dir, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import get_data_path from your data helpers so that resource paths work correctly in the bundle.
try:
    from shared.utils.data_helpers import get_data_path
except ImportError as e:
    # Fallback: use PROJECT_ROOT directly if get_data_path is not found.
    def get_data_path(relative_path):
        return os.path.join(PROJECT_ROOT, relative_path)

# Safeguard: re-check if project root is available.
try:
    import shared.config
except ImportError as e:
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    try:
        import shared.config
    except ImportError as e:
        print("Failed to import shared.config:", e)
        sys.exit(1)

def get_hidden_imports(project_root):
    hidden_imports = []
    # Use get_data_path() to locate the shared/tasks folder.
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
                # We use the module’s TASK_TYPE (assumed to be consistent with tasks.json)
                hidden_imports.append(f"shared.tasks.{module_name}")
        except Exception as e:
            print(f"Error importing {filename}: {e}")
    # Always include these shared modules.
    other_modules = [
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
    hidden_imports.extend(other_modules)
    # Include gift card handling module.
    hidden_imports.append("builder.gift_card")
    return hidden_imports

def get_data_files(project_root):
    data_files = []
    folders = [
        ("builder/tasks", "builder/tasks"),
        ("shared/theme", "shared/theme"),
        ("builder/data/gift_cards", "builder/data/gift_cards")
    ]
    for src_rel, tgt_rel in folders:
        # Use get_data_path() to locate these folders.
        src_abs = get_data_path(src_rel)
        if not os.path.exists(src_abs):
            continue
        for root, _, files in os.walk(src_abs):
            for f in files:
                if f.lower().endswith((".json", ".qss")):
                    file_abs = os.path.join(root, f)
                    rel_path = os.path.relpath(file_abs, project_root)
                    data_files.append(f"{file_abs};{os.path.dirname(rel_path)}")
    return data_files

def export_exe(custom_name, project_root, security_options, disable_lockdown=False):
    # If disable_lockdown is True, override relevant security options.
    if disable_lockdown:
        security_options["ENABLE_MOUSE_LOCKER"] = False
        security_options["ENABLE_SLEEP_BLOCKER"] = False
        security_options["ENABLE_SECURITY_MONITOR"] = False

    # Update configuration.
    config_path = os.path.join(project_root, "builder", "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}
    except Exception:
        config = {}
    config.update(security_options)
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        return False, f"Error writing config: {e}"

    # Set the main script for the EXE.
    game_script = os.path.join(project_root, "game", "game.py")
    hidden_imports = get_hidden_imports(project_root)
    data_files = get_data_files(project_root)

    # Define output directories.
    export_dir = os.path.join(project_root, "exported")
    os.makedirs(export_dir, exist_ok=True)

    # Build the PyInstaller command.
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", custom_name,
        "--paths", project_root,
    ]
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    for data in data_files:
        cmd.extend(["--add-data", data])
    cmd.append(game_script)

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"PyInstaller error: {e.stderr}"

if __name__ == "__main__":
    # Example usage.
    security_options = {
        "ENABLE_SECURITY_MONITOR": True,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "CLOSE_BUTTON_DISABLED": True,
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1
    }
    success, message = export_exe("ScammerPaybackGame", PROJECT_ROOT, security_options, disable_lockdown=False)
    if success:
        print("Export successful!")
    else:
        print("Export failed:", message)
