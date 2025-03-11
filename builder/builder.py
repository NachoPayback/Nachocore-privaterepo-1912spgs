# builder/builder.py

import os
import sys
import json
import glob
import importlib.util

# Set project root and update sys.path BEFORE any other imports.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
print("PROJECT_ROOT:", PROJECT_ROOT)
print("sys.path:", sys.path)

# Now load the stylesheet.
from shared.theme.theme import load_stylesheet

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

# Configuration file path.
CONFIG_PATH = os.path.join(PROJECT_ROOT, "builder", "config.json")

# Import UI tabs.
from builder.ui.task_builder_tab import TaskBuilderTab
from builder.ui.gift_card_tab import GiftCardTab
from builder.ui.export_tab import ExportTab
from builder.ui.security_mode_tab import SecurityModeTab
from builder.ui.security_header import SecurityHeader

class BuilderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nachocore v1.1")
        self.setGeometry(100, 100, 900, 600)
        central = QWidget()
        main_layout = QVBoxLayout(central)
        self.setCentralWidget(central)
        
        # Security Header: displays current security mode.
        self.header = SecurityHeader()
        main_layout.addWidget(self.header)
        
        # Tab widget.
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        
        # Discover task modules.
        from builder.task_builder import discover_task_modules
        self.discovered_tasks = discover_task_modules()
        
        # Add tabs.
        self.tabs.addTab(TaskBuilderTab(self.discovered_tasks, PROJECT_ROOT), "Task Builder")
        self.tabs.addTab(GiftCardTab(), "Gift Card Selection")
        self.tabs.addTab(ExportTab(PROJECT_ROOT), "Export Options")
        self.securityModeTab = SecurityModeTab()
        self.tabs.addTab(self.securityModeTab, "Security Mode")
        
        # Connect the Security Mode Tab's settingsChanged signal to update the header.
        self.securityModeTab.settingsChanged.connect(
            lambda s: self.header.setMode(s.get("SECURITY_MODE", "Ethical"))
        )
        
        # Apply global stylesheet.
        stylesheet = load_stylesheet("shared/theme/styles.qss")
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self.show()
    
    def refresh_security_header(self):
        self.header.update_security_mode()

def main():
    app = QApplication(sys.argv)
    window = BuilderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
