# ui_style_editor/config_manager.py
import os
import json

class ConfigManager:
    def __init__(self, target="builder"):
        self.target = target.lower()
        if self.target in ["builder", "both"]:
            self.base_path_builder = os.path.join("shared", "themes", "builder")
        if self.target in ["game", "both"]:
            self.base_path_game = os.path.join("shared", "themes", "game")
        
        self.animations_config_path = self._get_path("animations_config.json")
        self.boot_config_path = self._get_path("boot_screen_config.json")
        self.palette_config_path = self._get_path("palette_config.json")
        self.font_config_path = self._get_path("font_config.json")
    
    def _get_path(self, filename):
        if self.target in ["builder", "both"]:
            return os.path.join("shared", "themes", "builder", filename)
        else:
            return os.path.join("shared", "themes", "game", filename)
    
    def get_animation_config(self):
        return self._load_json(self.animations_config_path, default={"enable_animations": True, "button_hover_effect": "none"})
    
    def save_animation_config(self, config):
        self._save_json(self.animations_config_path, config)
        if self.target == "both":
            game_path = os.path.join("shared", "themes", "game", "animations_config.json")
            self._save_json(game_path, config)
    
    def get_boot_config(self):
        return self._load_json(self.boot_config_path, default={"enable_boot_screen": True, "boot_text": "Welcome to Nachocore", "background_image": ""})
    
    def save_boot_config(self, config):
        self._save_json(self.boot_config_path, config)
        if self.target == "both":
            game_path = os.path.join("shared", "themes", "game", "boot_screen_config.json")
            self._save_json(game_path, config)
    
    def save_palette_config(self, config):
        self._save_json(self.palette_config_path, config)
        if self.target == "both":
            game_path = os.path.join("shared", "themes", "game", "palette_config.json")
            self._save_json(game_path, config)
    
    def get_palette_config(self):
        return self._load_json(self.palette_config_path, default={})
    
    def save_font_config(self, config):
        self._save_json(self.font_config_path, config)
        if self.target == "both":
            game_path = os.path.join("shared", "themes", "game", "font_config.json")
            self._save_json(game_path, config)
    
    def get_font_config(self):
        return self._load_json(self.font_config_path, default={"font": "Arial"})
    
    def _load_json(self, path, default=None):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {path}: {e}")
        return default if default is not None else {}
    
    def _save_json(self, path, data):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving {path}: {e}")
