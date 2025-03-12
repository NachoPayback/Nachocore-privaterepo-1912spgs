# ui_style_editor/element_inspector.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPlainTextEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from error_handler import ErrorHandler

# Map friendly group names to selectors based on object names.
UI_GROUPS = {
    "Header": "QLabel#headerLabel, QLabel.header",
    "Security Header": "QLabel#securityHeaderLabel",
    "Task Input Fields": "QLineEdit#taskInput",
    "Submit Buttons": "QPushButton#submitButton, QPushButton.submit",
    "Preset Buttons": "QPushButton#presetButton, QPushButton.preset",
    "Main Container": "QWidget#mainContainer",
    "Task List": "QTableWidget#taskListTable",
    "On-Screen Keyboard": "QWidget#onScreenKeyboard"
}

class ElementInspectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_handler = ErrorHandler()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Element Inspector")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setObjectName("inspectorHeader")
        layout.addWidget(header)
        
        # Dropdown for selecting UI element group.
        self.group_dropdown = QComboBox()
        self.group_dropdown.setObjectName("elementGroupDropdown")
        self.group_dropdown.addItems(UI_GROUPS.keys())
        layout.addWidget(QLabel("Select UI Element Group:"))
        layout.addWidget(self.group_dropdown)
        
        # Text editor for custom CSS.
        layout.addWidget(QLabel("Custom CSS for Selected Group:"))
        self.css_editor = QPlainTextEdit()
        self.css_editor.setObjectName("elementCssEditor")
        self.css_editor.setPlaceholderText("Enter custom CSS (e.g., color: #FF00FF; padding: 5px;)")
        layout.addWidget(self.css_editor)
        
        # Live preview area.
        layout.addWidget(QLabel("Live Preview:"))
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("elementPreviewFrame")
        self.preview_frame.setFrameShape(QFrame.Shape.Box)
        self.preview_frame.setFixedHeight(150)
        layout.addWidget(self.preview_frame)
        
        # Buttons.
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply to Preview")
        self.apply_btn.setObjectName("applyPreviewButton")
        self.apply_btn.clicked.connect(self.apply_to_demo)
        btn_layout.addWidget(self.apply_btn)
        self.reset_btn = QPushButton("Reset Preview")
        self.reset_btn.setObjectName("resetPreviewButton")
        self.reset_btn.clicked.connect(self.reset_demo)
        btn_layout.addWidget(self.reset_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def apply_to_demo(self):
        group = self.group_dropdown.currentText()
        selector = UI_GROUPS.get(group, "")
        custom_css = self.css_editor.toPlainText().strip()
        if not custom_css:
            return
        css_rule = f"{selector} {{ {custom_css} }}"
        self.preview_frame.setStyleSheet(css_rule)
    
    def reset_demo(self):
        self.preview_frame.setStyleSheet("")
        self.css_editor.clear()
