"""
Developer Zone Tab Placeholder

This tab is reserved for future beta features and advanced developer settings.
For now, it displays a placeholder message.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from shared.theme.theme import load_stylesheet

class DevZoneTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        placeholder_label = QLabel("Developer Zone\nBeta Features Coming Soon")
        placeholder_label.setObjectName("devZoneLabel")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Instead of inline style, load external stylesheet (if it defines styles for #devZoneLabel)
        style = load_stylesheet("shared/theme/styles.qss")
        if style:
            placeholder_label.setStyleSheet(style)
        layout.addWidget(placeholder_label)
