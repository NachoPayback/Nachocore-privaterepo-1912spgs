# ui_style_editor/reactive_color_manager.py
import os
import sys
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QComboBox, QMessageBox
from error_handler import ErrorHandler

# Ensure that the project root (which contains the shared folder) is in sys.path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.utils.data_helpers import get_data_path

class ReactiveColorManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_handler = ErrorHandler()
        self.config_path = os.path.join("shared", "themes", "builder", "reactive_color_config.json")
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reactive Color Options"))
        
        self.enable_checkbox = QCheckBox("Enable Reactive Color")
        layout.addWidget(self.enable_checkbox)
        
        # For each security mode, create a combobox for selecting a color.
        self.mode_comboboxes = {}
        modes = ["Ethical", "Unethical", "Grift", "Custom"]
        default_mappings = {
            "Ethical": "#00FF00",   # green
            "Unethical": "#FFA500",  # orange
            "Grift": "#FF0000",      # red
            "Custom": "#00FFFF"      # cyan
        }
        for mode in modes:
            label = QLabel(f"{mode} Color:")
            combo = QComboBox()
            suggestions = {
                "Ethical": ["#00FF00", "#008000", "#32CD32"],
                "Unethical": ["#FFA500", "#FF8C00", "#FF7F50"],
                "Grift": ["#FF0000", "#8B0000", "#B22222"],
                "Custom": ["#00FFFF", "#008B8B", "#20B2AA"]
            }
            combo.addItems(suggestions.get(mode, []))
            combo.setCurrentText(default_mappings[mode])
            self.mode_comboboxes[mode] = combo
            layout.addWidget(label)
            layout.addWidget(combo)
        
        self.save_btn = QPushButton("Save Reactive Color Settings")
        self.save_btn.clicked.connect(self.save_config)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
    
    def load_config(self):
        try:
            full_path = get_data_path(self.config_path)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    config = json.load(f)
                self.enable_checkbox.setChecked(config.get("enabled", False))
                mappings = config.get("mappings", {})
                for mode, color in mappings.items():
                    if mode in self.mode_comboboxes:
                        self.mode_comboboxes[mode].setCurrentText(color)
        except Exception as e:
            self.error_handler.log_error("Error loading reactive color config", e)
    
    def save_config(self):
        config = {
            "enabled": self.enable_checkbox.isChecked(),
            "mappings": { mode: self.mode_comboboxes[mode].currentText() for mode in self.mode_comboboxes }
        }
        try:
            full_path = get_data_path(self.config_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(self, "Saved", "Reactive Color settings saved.")
        except Exception as e:
            self.error_handler.log_error("Error saving reactive color config", e)
