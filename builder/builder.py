# builder/builder.py
"""
Main entry point for the Nachocore Builder application.
"""

import os
import sys

# Set project root and update sys.path BEFORE any other imports.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
print("PROJECT_ROOT:", PROJECT_ROOT)
print("sys.path:", sys.path)

from shared.theme.theme import load_stylesheet  # Now resolved correctly.
from builder import security_settings  # Uses the updated security settings module.

# Import UI modules.
from builder.ui.security_header import SecurityHeader
from builder.ui.task_builder_tab import TaskBuilderTab
from builder.ui.gift_card_tab import GiftCardTab
from builder.ui.export_tab import ExportTab
from builder.ui.dev_zone_tab import DevZoneWidget

from builder.task_builder import TaskManager, TaskListWidget, discover_task_modules
from builder.cleanup import clean_pycache
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSlot

class BuilderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nachocore v1.0")
        self.setGeometry(100, 100, 900, 600)
        central = QWidget()
        main_layout = QVBoxLayout(central)
        self.setCentralWidget(central)
        
        # Security header.
        self.header = SecurityHeader()
        main_layout.addWidget(self.header)
        
        # Tab widget with modular UI.
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        self.discovered_tasks = discover_task_modules()
        self.tabs.addTab(TaskBuilderTab(self.discovered_tasks, PROJECT_ROOT), "Task Builder")
        self.tabs.addTab(GiftCardTab(), "Gift Card Selection")
        self.tabs.addTab(ExportTab(PROJECT_ROOT), "Export Options")
        self.tabs.addTab(self.create_dev_zone_tab(), "Developer Zone")
        
        # Apply global stylesheet.
        stylesheet = load_stylesheet("shared/theme/styles.qss")
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self.show()

    def create_dev_zone_tab(self):
        """Create and return the Developer Zone tab."""
        dev = DevZoneWidget()
        dev.modeChanged.connect(self.update_global_mode)
        return dev

    @pyqtSlot(str)
    def update_global_mode(self, mode):
        self.header.update_mode(mode)
        # Additional global updates can be added here.

    def closeEvent(self, event):
        print("Builder is closing. Cleaning up __pycache__...")
        clean_pycache(PROJECT_ROOT)
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = BuilderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
