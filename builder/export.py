import os
import sys
import json
import subprocess
import glob
import importlib.util

def get_hidden_imports(project_root):
    hidden_imports = []
    tasks_folder = os.path.join(project_root, "shared", "tasks")
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
    
    # Define output directories (if needed).
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
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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
