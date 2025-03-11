# builder/ui/security_header.py
import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from builder.security_settings import load_security_settings

def mode_text_color(mode: str) -> str:
    return {
        "Ethical": "green",
        "Unethical": "orange",
        "Grift": "red",
        "Custom": "cyan"
    }.get(mode, "white")

class SecurityHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.modeLabel = QLabel()
        self.modeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.modeLabel)
        # Immediately update the header with the current security mode at boot-up.
        self.update_security_mode()
    
    def update_security_mode(self):
        settings = load_security_settings()
        # If no mode is found, default to "Ethical"
        mode = settings.get("SECURITY_MODE", "Ethical")
        self.modeLabel.setText(f"Security Mode: {mode}")
        self.modeLabel.setStyleSheet(f"color: {mode_text_color(mode)}; font-weight: bold;")
