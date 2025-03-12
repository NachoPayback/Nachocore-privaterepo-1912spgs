# ui_style_editor/interactive_style_editor.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QSplitter, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from panels.header_style_panel import HeaderStylePanel
from panels.button_style_panel import ButtonStylePanel
from panels.input_style_panel import InputStylePanel
from simulated_preview import SimulatedPreviewWidget
from sidebar_navigation import SidebarNavigation
from style_manager import StyleManager
from config_manager import ConfigManager
from error_handler import ErrorHandler

class InteractiveStyleEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive UI Style Editor")
        self.setGeometry(50, 50, 1400, 900)
        self.error_handler = ErrorHandler()
        self.style_manager = StyleManager(target="both")
        self.config_manager = ConfigManager(target="both")
        self.init_ui()
    
    def init_ui(self):
        # Main container widget.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Sidebar for navigation.
        self.sidebar = SidebarNavigation()
        main_layout.addWidget(self.sidebar, 1)
        
        # Right side: Splitter with interactive panels (tabs) and persistent preview.
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(right_splitter, 4)
        
        # Tab widget for interactive panels.
        self.tabs = QTabWidget()
        # Add panels for each UI element group.
        self.tabs.addTab(HeaderStylePanel(), "Header Styles")
        self.tabs.addTab(ButtonStylePanel(), "Button Styles")
        self.tabs.addTab(InputStylePanel(), "Input Styles")
        # ... (Add additional panels for animations, boot screen, etc.)
        right_splitter.addWidget(self.tabs)
        
        # Persistent live preview panel.
        self.preview_widget = SimulatedPreviewWidget()
        right_splitter.addWidget(self.preview_widget)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 2)
        
        # Bottom export bar.
        export_btn = QPushButton("Export & Apply Styles")
        export_btn.clicked.connect(self.export_and_apply)
        main_layout.addWidget(export_btn)
        
        self.update_preview()
    
    def export_and_apply(self):
        try:
            # Aggregate CSS from each interactive panel that implements get_css().
            css = ""
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if hasattr(widget, "get_css"):
                    css += widget.get_css() + "\n"
            self.style_manager.export_style(css)
            QMessageBox.information(self, "Exported", "Styles exported successfully!")
            self.update_preview()
        except Exception as e:
            self.error_handler.log_error("Error exporting styles", e)
    
    def update_preview(self):
        try:
            new_style = self.style_manager.load_style()
            self.preview_widget.setStyleSheet(new_style)
        except Exception as e:
            self.error_handler.log_error("Error updating preview", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InteractiveStyleEditor()
    window.show()
    sys.exit(app.exec())
