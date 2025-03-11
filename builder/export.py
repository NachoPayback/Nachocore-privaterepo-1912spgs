# builder/export.py
"""
Export Module for Nachocore Builder

This module updates configuration files, generates a static manifest, and
exports the game as a standalone executable via PyInstaller.

Changes in this version:
- tasks.json is now located in builder/data/tasks.json.
- Utility functions (like get_data_path) are imported from shared/utils/data_helpers.
- The manifest includes a stable version of security settings for frozen mode.
"""

import os
import json
import subprocess

# Import get_data_path from the updated location.
from shared.utils.data_helpers import get_data_path

# Import discover_task_modules from task_builder (which now uses the updated tasks.json path).
from builder.task_builder import discover_task_modules

# Import security settings for retrieving current security configuration.
from builder.security_settings import load_security_settings

# Path to the main configuration file (remains in builder/config.json)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def update_config_with_current_settings(security_opts):
    """
    Update the config.json file with the provided security options.
    
    Args:
        security_opts (dict): Security options to update in the configuration.
    
    Returns:
        dict: The updated configuration.
    """
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except Exception as e:
        print("Error reading config.json:", e)
        config = {}
    config.update(security_opts)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print("Error writing config.json:", e)
    return config

def generate_manifest():
    """
    Generate or update the static manifest (builder/static_manifest.py) which contains:
    - TASK_MANIFEST: mapping of normalized task types to module import paths.
    - GIFT_CARD_STATIC: gift card configuration loaded from config.json.
    - SECURITY_SETTINGS_STATIC: current security settings.
    
    This manifest is used to ensure the frozen executable has stable fallback values.
    
    Returns:
        str: The path to the generated manifest file.
    """
    # Discover available task modules.
    task_manifest = discover_task_modules()
    
    # Load current security settings.
    security_settings = load_security_settings()
    
    # Load gift card configuration from config.json.
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        gift_card = config.get("selected_gift_card", {})
    except Exception as e:
        print("Error reading gift card configuration:", e)
        gift_card = {}
    
    # Build the manifest content as a Python file.
    manifest_content = f"""# Auto-generated static manifest. Do not edit.
TASK_MANIFEST = {json.dumps(task_manifest, indent=4)}
GIFT_CARD_STATIC = {json.dumps(gift_card, indent=4)}
SECURITY_SETTINGS_STATIC = {json.dumps(security_settings, indent=4)}
"""
    # Manifest file will be saved in the builder folder.
    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_manifest.py")
    try:
        with open(manifest_path, "w") as f:
            f.write(manifest_content)
    except Exception as e:
        print("Error writing static manifest:", e)
    return manifest_path

def export_exe(exe_name, project_root, security_opts, disable_lockdown=False):
    """
    Export the game to a standalone executable using PyInstaller.
    
    Args:
        exe_name (str): Custom name for the executable.
        project_root (str): The project root directory.
        security_opts (dict): Security options to update the configuration.
        disable_lockdown (bool): Whether to disable lockdown features.
        
    Returns:
        tuple: (success_flag, output_message)
    """
    try:
        # Update configuration file with the provided security options.
        update_config_with_current_settings(security_opts)
        
        # Generate the static manifest with current settings and task mappings.
        manifest = generate_manifest()
        print("Static manifest generated at:", manifest)
        
        # Locate the main game script (assumed to be in game/game.py).
        main_script = os.path.join(project_root, "game", "game.py")
        if not os.path.exists(main_script):
            return False, f"Main game script not found at: {main_script}"
        
        # Build the executable with PyInstaller.
        cmd = [
            "pyinstaller",
            "--onefile",
            "--noconsole",
            "--name", exe_name,
            main_script
        ]
        print("Running PyInstaller command:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("PyInstaller error:", result.stderr)
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # For testing purposes:
    test_security_opts = {
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "ENABLE_SECURITY_MONITOR": True,
        "CLOSE_BUTTON_DISABLED": True,
        "ENABLE_LOGGER": True
    }
    # Assume the project root is one level up from the builder folder.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    updated_config = update_config_with_current_settings(test_security_opts)
    print("Updated config:", updated_config)
    manifest_path = generate_manifest()
    print("Manifest generated at:", manifest_path)
    success, output = export_exe("ScammerPaybackGame", PROJECT_ROOT, test_security_opts)
    if success:
        print("Export successful!")
    else:
        print("Export failed:", output)
