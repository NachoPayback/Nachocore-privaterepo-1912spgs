import os
import json
from PyQt6.QtWidgets import QInputDialog, QMessageBox

# Base presets directory relative to builder folder.
BASE_PRESETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets")
# Subdirectories for different preset types.
SECURITY_PRESETS_DIR = os.path.join(BASE_PRESETS_DIR, "security_presets")
TASK_PRESETS_DIR = os.path.join(BASE_PRESETS_DIR, "task_presets")

# Ensure the preset subdirectories exist.
os.makedirs(SECURITY_PRESETS_DIR, exist_ok=True)
os.makedirs(TASK_PRESETS_DIR, exist_ok=True)

def preset_file_path(preset_name: str, preset_type: str) -> str:
    """
    Return the file path for a given preset name and type.
    preset_type should be "security" or "task".
    """
    if preset_type == "security":
        filename = f"security_preset_{preset_name}.json"
        folder = SECURITY_PRESETS_DIR
    elif preset_type == "task":
        filename = f"task_preset_{preset_name}.json"
        folder = TASK_PRESETS_DIR
    else:
        raise ValueError("Invalid preset type. Must be 'security' or 'task'.")
    return os.path.join(folder, filename)

def list_presets(preset_type: str) -> list:
    """
    Return a list of available preset names for the given type.
    """
    if preset_type == "security":
        folder = SECURITY_PRESETS_DIR
        prefix = "security_preset_"
    elif preset_type == "task":
        folder = TASK_PRESETS_DIR
        prefix = "task_preset_"
    else:
        raise ValueError("Invalid preset type. Must be 'security' or 'task'.")
    
    presets = []
    for fname in os.listdir(folder):
        if fname.startswith(prefix) and fname.endswith(".json"):
            preset_name = fname[len(prefix):-len(".json")]
            presets.append(preset_name)
    return presets

def save_preset(preset_type: str, settings: dict, parent_widget=None) -> bool:
    """
    Prompt the user for a preset name and save the settings to the corresponding preset file.
    
    Args:
        preset_type (str): "security" or "task"
        settings (dict): The settings to save.
        parent_widget: Optional widget for dialog parenting.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    preset_name, ok = QInputDialog.getText(parent_widget, "Save Preset", "Enter a name for this preset:")
    if not ok or not preset_name:
        QMessageBox.information(parent_widget, "Cancelled", "Preset save cancelled.")
        return False
    
    try:
        with open(preset_file_path(preset_name, preset_type), "w") as f:
            json.dump(settings, f, indent=4)
        QMessageBox.information(parent_widget, "Preset Saved", f"Preset '{preset_name}' saved successfully.")
        return True
    except Exception as e:
        QMessageBox.critical(parent_widget, "Error", f"Failed to save preset: {e}")
        return False

def load_preset(preset_type: str, preset_name: str) -> dict:
    """
    Load and return the preset settings for the given type and preset name.
    
    Args:
        preset_type (str): "security" or "task"
        preset_name (str): The name of the preset.
        
    Returns:
        dict: The loaded settings, or an empty dict on failure.
    """
    try:
        with open(preset_file_path(preset_name, preset_type), "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {preset_type} preset '{preset_name}': {e}")
        return {}
