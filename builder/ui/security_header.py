import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from builder.security_settings import load_security_settings
from shared.theme.theme import load_stylesheet

def mode_text_color(mode: str) -> str:
    # This function is kept for reference or fallback, but now styling is handled via QSS.
    return {
        "Ethical": "green",
        "Unethical": "orange",
        "Grift": "red",
        "Custom": "cyan"
    }.get(mode, "white")

class SecurityHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.modeLabel = QLabel()
        self.modeLabel.setObjectName("securityHeaderLabel")
        self.modeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.modeLabel)
        self.update_security_mode()
    
    def update_security_mode(self):
        settings = load_security_settings()
        mode = settings.get("SECURITY_MODE", "Ethical")
        self.setMode(mode)
    
    def setMode(self, mode: str):
        self.modeLabel.setText(f"Security Mode: {mode}")
        # Set dynamic property so QSS can target this label based on its security mode.
        self.modeLabel.setProperty("securityMode", mode)
        # Force a style refresh.
        self.modeLabel.style().unpolish(self.modeLabel)
        self.modeLabel.style().polish(self.modeLabel)
