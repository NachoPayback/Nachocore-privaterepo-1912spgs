# ui_style_editor/preset_manager.py
import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QInputDialog, QMessageBox
from config_manager import ConfigManager
from error_handler import ErrorHandler

class PresetManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager(target="both")
        self.error_handler = ErrorHandler()
        self.presets_file = os.path.join("ui_style_editor", "presets.json")
        self.init_ui()
        self.load_presets()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Preset Manager"))
        self.preset_dropdown = QComboBox()
        layout.addWidget(self.preset_dropdown)
        
        btn_layout = QVBoxLayout()
        self.load_btn = QPushButton("Load Preset")
        self.load_btn.clicked.connect(self.load_preset)
        btn_layout.addWidget(self.load_btn)
        self.save_btn = QPushButton("Save Current Settings as Preset")
        self.save_btn.clicked.connect(self.save_preset)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_presets(self):
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, "r") as f:
                    self.presets = json.load(f)
            except Exception as e:
                self.error_handler.log_error("Error loading presets", e)
                self.presets = {}
        else:
            # Preload default presets if no file exists.
            self.presets = {
                "Dark Hacker": {
                    "animation": {"enable_animations": True, "button_hover_effect": "glow"},
                    "boot": {"enable_boot_screen": True, "boot_text": "Welcome to the Dark Side", "background_image": ""},
                    "palette": {"primary": "#1E1E1E", "complementary": "#00FF00", "analogous1": "#007700", "analogous2": "#005500", "text": "#D4D4D4"},
                    "font": {"font": "Courier New"}
                },
                "Retro Glitch": {
                    "animation": {"enable_animations": True, "button_hover_effect": "slide"},
                    "boot": {"enable_boot_screen": True, "boot_text": "Retro Glitch Mode", "background_image": ""},
                    "palette": {"primary": "#2D2D2D", "complementary": "#FF00FF", "analogous1": "#AA00AA", "analogous2": "#880088", "text": "#FFFFFF"},
                    "font": {"font": "Consolas"}
                },
                "Corporate": {
                    "animation": {"enable_animations": False, "button_hover_effect": "none"},
                    "boot": {"enable_boot_screen": False, "boot_text": "", "background_image": ""},
                    "palette": {"primary": "#FFFFFF", "complementary": "#000080", "analogous1": "#CCCCCC", "analogous2": "#999999", "text": "#000000"},
                    "font": {"font": "Arial"}
                }
            }
            self._save_presets()
        self.refresh_dropdown()
    
    def _save_presets(self):
        try:
            with open(self.presets_file, "w") as f:
                json.dump(self.presets, f, indent=4)
        except Exception as e:
            self.error_handler.log_error("Error saving presets file", e)
    
    def refresh_dropdown(self):
        self.preset_dropdown.clear()
        for name in self.presets.keys():
            self.preset_dropdown.addItem(name)
    
    def save_preset(self):
        preset_name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        if not ok or not preset_name:
            QMessageBox.information(self, "Cancelled", "Preset save cancelled.")
            return
        # Save current configurations from all managers
        preset_data = {
            "animation": self.config_manager.get_animation_config(),
            "boot": self.config_manager.get_boot_config(),
            "palette": self.config_manager.get_palette_config(),
            "font": self.config_manager.get_font_config()
        }
        self.presets[preset_name] = preset_data
        try:
            self._save_presets()
            QMessageBox.information(self, "Preset Saved", f"Preset '{preset_name}' saved successfully.")
            self.refresh_dropdown()
        except Exception as e:
            self.error_handler.log_error("Error saving preset", e)
    
    def load_preset(self):
        preset_name = self.preset_dropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Warning", "No preset selected.")
            return
        preset_data = self.presets.get(preset_name)
        if not preset_data:
            QMessageBox.warning(self, "Warning", f"Preset '{preset_name}' not found.")
            return
        try:
            self.config_manager.save_animation_config(preset_data.get("animation", {}))
            self.config_manager.save_boot_config(preset_data.get("boot", {}))
            self.config_manager.save_palette_config(preset_data.get("palette", {}))
            self.config_manager.save_font_config(preset_data.get("font", {}))
            QMessageBox.information(self, "Preset Loaded", f"Preset '{preset_name}' loaded successfully.")
        except Exception as e:
            self.error_handler.log_error("Error loading preset", e)
