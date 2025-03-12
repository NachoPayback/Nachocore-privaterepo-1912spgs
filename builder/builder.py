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

# Load stylesheet helper and path resolution
from shared.theme.theme import load_stylesheet
from shared.utils.data_helpers import get_data_path

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import your UI tabs (all original functionality remains intact)
from builder.ui.task_builder_tab import TaskBuilderTab
from builder.ui.gift_card_tab import GiftCardTab
from builder.ui.export_tab import ExportTab
from builder.ui.security_mode_tab import SecurityModeTab
from builder.ui.security_header import SecurityHeader

def center_dialog(dialog):
    from PyQt6.QtWidgets import QApplication
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    dialog_geometry = dialog.frameGeometry()
    dialog_geometry.moveCenter(screen_geometry.center())
    dialog.move(dialog_geometry.topLeft())

class BuilderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nachocore v1.1")
        self.setGeometry(100, 100, 900, 600)
        
        # Set main container and assign an object name for group styling.
        central = QWidget()
        central.setObjectName("mainContainer")
        main_layout = QVBoxLayout(central)
        self.setCentralWidget(central)
        
        # Security Header (assign object name for targeted styling)
        self.header = SecurityHeader()
        self.header.setObjectName("headerLabel")
        main_layout.addWidget(self.header)
        
        # Tab widget.
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        
        # Discover task modules.
        from builder.task_builder import discover_task_modules
        self.discovered_tasks = discover_task_modules()
        
        # Add tabs (all original functionality preserved)
        self.tabs.addTab(TaskBuilderTab(self.discovered_tasks, PROJECT_ROOT), "Task Builder")
        self.tabs.addTab(GiftCardTab(), "Gift Card Selection")
        self.exportTab = ExportTab(PROJECT_ROOT)
        self.tabs.addTab(self.exportTab, "Export Options")
        self.securityModeTab = SecurityModeTab()
        self.tabs.addTab(self.securityModeTab, "Security Mode")
        self.securityModeTab.settingsChanged.connect(self.on_security_mode_changed)
        
        # --- STYLE INTEGRATION ---
        # Load global stylesheet from builder exported file.
        stylesheet_path = get_data_path("shared/themes/builder/exported_stylesheet.qss")
        if os.path.exists(stylesheet_path):
            try:
                with open(stylesheet_path, "r") as f:
                    stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
            except Exception as e:
                print("Error loading builder stylesheet:", e)
        # Load builder font configuration and apply it.
        font_config_path = get_data_path("shared/themes/builder/font_config.json")
        if os.path.exists(font_config_path):
            try:
                with open(font_config_path, "r") as f:
                    font_config = json.load(f)
                chosen_font = font_config.get("font", "Arial")
                self.setFont(QFont(chosen_font))
            except Exception as e:
                print("Error loading builder font config:", e)
        # --- END STYLE INTEGRATION ---
        
        self.show()
    
    def on_security_mode_changed(self, updated_config: dict):
        mode = updated_config.get("SECURITY_MODE", "Ethical")
        self.header.setMode(mode)
        self.exportTab.update_security_summary()
    
    def refresh_security_header(self):
        self.header.update_security_mode()
    
    def closeEvent(self, event):
        from builder.cleanup import clean_pycache
        clean_pycache(PROJECT_ROOT)
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = BuilderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
