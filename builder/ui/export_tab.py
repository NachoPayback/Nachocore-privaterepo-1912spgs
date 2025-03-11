# builder/ui/export_tab.py
import os
import sys
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QPlainTextEdit
)
from PyQt6.QtCore import Qt
from shared.theme.theme import load_stylesheet
from builder.security_settings import load_security_settings
from builder.export import export_exe

class ExportTab(QWidget):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.init_ui()
        self.update_security_summary()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title Label
        title = QLabel("Export Options")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc;")
        layout.addWidget(title)
        
        # Custom EXE Name Input
        name_layout = QHBoxLayout()
        name_label = QLabel("Custom EXE Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., ScammerPaybackGame")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Current Security Settings Summary
        self.security_summary = QPlainTextEdit()
        self.security_summary.setReadOnly(True)
        self.security_summary.setStyleSheet("font-size: 14px;")
        layout.addWidget(QLabel("Current Security Settings:"))
        layout.addWidget(self.security_summary)
        
        # Export Button
        self.export_button = QPushButton("Export to EXE")
        self.export_button.clicked.connect(self.on_export)
        layout.addWidget(self.export_button)
        
        stylesheet = load_stylesheet("shared/theme/styles.qss")
        if stylesheet:
            self.setStyleSheet(stylesheet)
        
        self.setLayout(layout)
    
    def update_security_summary(self):
        settings = load_security_settings()
        summary_lines = []
        summary_lines.append(f"Security Mode: {settings.get('SECURITY_MODE', 'Ethical')}")
        summary_lines.append(f"UI Keyboard: {settings.get('USE_UI_KEYBOARD', False)}")
        summary_lines.append(f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)}")
        summary_lines.append(f"Mouse Locker: {settings.get('ENABLE_MOUSE_LOCKER', False)}")
        summary_lines.append(f"Sleep Blocker: {settings.get('ENABLE_SLEEP_BLOCKER', False)}")
        summary_lines.append(f"Security Monitor: {settings.get('ENABLE_SECURITY_MONITOR', False)}")
        summary_lines.append(f"Close Button Disabled: {settings.get('CLOSE_BUTTON_DISABLED', False)}")
        summary_lines.append(f"Logger: {settings.get('ENABLE_LOGGER', False)}")
        self.security_summary.setPlainText("\n".join(summary_lines))
    
    def on_export(self):
        exe_name = self.name_input.text().strip()
        if not exe_name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please enter a custom EXE name.")
            return
        
        self.update_security_summary()
        export_exe(exe_name, self.project_root, load_security_settings())

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    app = QApplication(sys.argv)
    win = ExportTab(PROJECT_ROOT)
    win.show()
    sys.exit(app.exec())
