# ui_style_editor/font_manager.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
from config_manager import ConfigManager
from error_handler import ErrorHandler

class FontManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager(target="both")
        self.error_handler = ErrorHandler()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Font Options"))
        
        # Suggested fonts for a hacker/cyberpunk aesthetic.
        self.font_dropdown = QComboBox()
        suggested_fonts = ["Hack", "Source Code Pro", "Fira Code", "Roboto Mono", "Consolas"]
        self.font_dropdown.addItems(suggested_fonts)
        layout.addWidget(QLabel("Select a Font:"))
        layout.addWidget(self.font_dropdown)
        
        self.custom_font_input = QLineEdit()
        self.custom_font_input.setPlaceholderText("Or enter a custom font name")
        layout.addWidget(self.custom_font_input)
        
        self.save_btn = QPushButton("Save Font Settings")
        self.save_btn.clicked.connect(self.save_font_settings)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
    
    def save_font_settings(self):
        chosen_font = self.custom_font_input.text().strip()
        if not chosen_font:
            chosen_font = self.font_dropdown.currentText()
        font_config = {"font": chosen_font}
        try:
            self.config_manager.save_font_config(font_config)
        except Exception as e:
            self.error_handler.log_error("Error saving font settings", e)
