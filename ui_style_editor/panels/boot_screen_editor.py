# ui_style_editor/boot_screen_editor.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QHBoxLayout, QMessageBox
from config_manager import ConfigManager
from error_handler import ErrorHandler
from resource_converter import convert_image_to_base64

class BootScreenEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager(target="both")
        self.error_handler = ErrorHandler()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Boot Screen Editor"))
        
        self.enable_boot_checkbox = QCheckBox("Enable Boot Screen")
        try:
            current_boot = self.config_manager.get_boot_config()
        except Exception as e:
            self.error_handler.log_error("Error loading boot config", e)
            current_boot = {"enable_boot_screen": True, "boot_text": "Welcome to Nachocore", "background_image": ""}
        self.enable_boot_checkbox.setChecked(current_boot.get("enable_boot_screen", True))
        layout.addWidget(self.enable_boot_checkbox)
        
        layout.addWidget(QLabel("Boot Screen Text:"))
        self.boot_text_input = QLineEdit()
        self.boot_text_input.setObjectName("bootTextInput")
        self.boot_text_input.setText(current_boot.get("boot_text", "Welcome to Nachocore"))
        layout.addWidget(self.boot_text_input)
        
        layout.addWidget(QLabel("Background Image (optional):"))
        self.bg_image_input = QLineEdit()
        self.bg_image_input.setObjectName("bootImageInput")
        self.bg_image_input.setText(current_boot.get("background_image", ""))
        layout.addWidget(self.bg_image_input)
        
        btn_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_image)
        btn_layout.addWidget(self.browse_btn)
        self.embed_btn = QPushButton("Embed Image")
        self.embed_btn.clicked.connect(self.embed_image)
        btn_layout.addWidget(self.embed_btn)
        layout.addLayout(btn_layout)
        
        self.save_btn = QPushButton("Save Boot Screen Settings")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
    
    def browse_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.bg_image_input.setText(selected_files[0])
    
    def embed_image(self):
        image_path = self.bg_image_input.text().strip()
        if not image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return
        try:
            base64_str = convert_image_to_base64(image_path)
            data_url = f"data:image/png;base64,{base64_str}"
            self.bg_image_input.setText(data_url)
            QMessageBox.information(self, "Embedded", "Image successfully embedded.")
        except Exception as e:
            self.error_handler.log_error("Error embedding image", e)
    
    def save_settings(self):
        config = {
            "enable_boot_screen": self.enable_boot_checkbox.isChecked(),
            "boot_text": self.boot_text_input.text(),
            "background_image": self.bg_image_input.text()
        }
        try:
            self.config_manager.save_boot_config(config)
            QMessageBox.information(self, "Saved", "Boot screen settings saved.")
        except Exception as e:
            self.error_handler.log_error("Error saving boot screen settings", e)
