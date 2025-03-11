# builder/ui/dev_zone_tab.py
"""
Developer Zone Tab Placeholder

This tab is reserved for future beta features and advanced developer settings.
For now, it displays a placeholder message.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class DevZoneTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        placeholder_label = QLabel("Developer Zone\nBeta Features Coming Soon")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Apply a hacker/Cyberpunk/Synthwave aesthetic style
        placeholder_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffff;")
        layout.addWidget(placeholder_label)
