# builder/ui/security_header.py
"""
Security Header UI Module

This widget displays the current security mode persistently at the top of the builder UI.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

def mode_text_color(mode):
    return {
        "Ethical": "green",
        "Unethical": "orange",
        "Grift": "red",
        "Custom": "cyan"
    }.get(mode, "black")

from builder import security_settings

class SecurityHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        # Load current security mode from config.
        config = security_settings.load_security_settings()
        mode = config.get("SECURITY_MODE", "Ethical")
        self.modeLabel = QLabel(f"Security Mode: {mode}")
        self.modeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.modeLabel.setStyleSheet(f"color: {mode_text_color(mode)}; font-weight: bold;")
        layout.addWidget(self.modeLabel)

    def update_mode(self, mode):
        """Update the header with the current security mode."""
        color = mode_text_color(mode)
        self.modeLabel.setText(f"Security Mode: {mode}")
        self.modeLabel.setStyleSheet(f"color: {color}; font-weight: bold;")
