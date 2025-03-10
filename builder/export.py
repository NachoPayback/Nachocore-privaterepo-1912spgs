#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import glob
import importlib.util

# Define PROJECT_ROOT (assuming export.py is in the builder folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Try to import get_data_path from shared/utils/data_helpers; if not available, define fallback.
try:
    from shared.utils.data_helpers import get_data_path
except ImportError:
    def get_data_path(relative_path):
        return os.path.join(PROJECT_ROOT, relative_path)

# Import the normalization helper from builder/utils.py
from builder.utils import normalize_task_type

def get_hidden_imports(project_root):
    hidden_imports = []
    tasks_folder = get_data_path(os.path.join("shared", "tasks"))
    print("DEBUG: Scanning tasks folder:", tasks_folder)
    
    # In a frozen EXE, return a static manifest.
    if getattr(sys, "frozen", False):
        static_manifest = {
            "location_collection": "shared.tasks.location_collection",
            "multiple_choice": "shared.tasks.multiple_choice",
            "name_collection": "shared.tasks.name_collection",
            "short_answer": "shared.tasks.short_answer"
        }
        print("DEBUG: Running in frozen state. Using static manifest:", static_manifest)
        return list(static_manifest.values())
    
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
                print(f"DEBUG: Found module '{module_name}' with TASK_TYPE '{module.TASK_TYPE}' normalized to '{normalized}'. Adding hidden import: {hidden_import}")
                hidden_imports.append(hidden_import)
            else:
                print(f"DEBUG: Module '{module_name}' does not define TASK_TYPE. Skipping.")
        except Exception as e:
            print(f"DEBUG: Error importing {filename}: {e}")
    print("DEBUG: Final hidden imports list:", hidden_imports)
    # Include additional shared modules if needed.
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
    """
    Returns a list of additional data files to bundle with the EXE.
    Format: "absolute_path;relative_destination_path"
    """
    data_files = []
    folders = [
        ("builder/tasks", "builder/tasks"),
        ("shared/theme", "shared/theme"),
        ("builder/data/gift_cards", "builder/data/gift_cards"),
        ("builder/config.json", "builder"),
    ]
    for src_rel, dest_rel in folders:
        src_abs = os.path.join(project_root, src_rel)
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
    # Update configuration in builder/config.json
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
        return False, f"Error writing config: {e}"

    # Set main script (game.py) as entry point
    game_script = os.path.join(project_root, "game", "game.py")

    hidden_imports = get_hidden_imports(project_root)
    data_files = get_data_files(project_root)

    # Create export directory
    export_dir = os.path.join(project_root, "exported")
    os.makedirs(export_dir, exist_ok=True)

    # Build PyInstaller command
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
        return False, f"PyInstaller error: {e.stderr}"

if __name__ == "__main__":
    security_opts = {
        "ENABLE_SECURITY_MONITOR": True,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "CLOSE_BUTTON_DISABLED": True,
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "SECURITY_MODE": "Ethical"
    }
    success, output = export_exe("ScammerPaybackGame", PROJECT_ROOT, security_opts, disable_lockdown=False)
    if success:
        print("Export successful!")
    else:
        print("Export failed:", output)
