# ui_style_editor/style_manager.py
import os
import json

class StyleManager:
    def __init__(self, target="both"):
        """
        target: "builder", "game", or "both"
        """
        self.target = target.lower()
        self.builder_theme_path = os.path.join("shared", "themes", "builder", "exported_stylesheet.qss")
        self.game_theme_path = os.path.join("shared", "themes", "game", "exported_stylesheet.qss")
        self.default_style_path = os.path.join("shared", "themes", "default.qss")
    
    def load_style(self):
        # Load from builder theme by default.
        if os.path.exists(self.builder_theme_path):
            with open(self.builder_theme_path, "r") as f:
                return f.read()
        return ""
    
    def save_style(self, style_text):
        temp_path = os.path.join("ui_style_editor", "temp_style.qss")
        with open(temp_path, "w") as f:
            f.write(style_text)
    
    def load_default_style(self):
        if os.path.exists(self.default_style_path):
            with open(self.default_style_path, "r") as f:
                return f.read()
        return ""
    
    def export_style(self, style_text):
        if self.target in ["builder", "both"]:
            os.makedirs(os.path.dirname(self.builder_theme_path), exist_ok=True)
            with open(self.builder_theme_path, "w") as f:
                f.write(style_text)
        if self.target in ["game", "both"]:
            os.makedirs(os.path.dirname(self.game_theme_path), exist_ok=True)
            with open(self.game_theme_path, "w") as f:
                f.write(style_text)
