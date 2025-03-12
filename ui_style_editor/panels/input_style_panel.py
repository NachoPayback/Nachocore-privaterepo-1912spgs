# ui_style_editor/input_style_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFormLayout, QSlider, QPushButton, QColorDialog
from PyQt6.QtCore import Qt

class InputStylePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {
            "bg_color": "#3c3f41",
            "text_color": "#dcdcdc",
            "border_color": "#555555",
            "padding": 4
        }
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create preview widget first.
        self.preview_input = QLineEdit("Input Preview")
        self.preview_input.setObjectName("inputPreview")
        layout.addWidget(self.preview_input)
        
        # Create control widgets.
        form_layout = QFormLayout()
        self.bg_btn = QPushButton("Choose Background Color")
        self.bg_btn.clicked.connect(lambda: self.choose_color("bg_color"))
        form_layout.addRow("Background Color:", self.bg_btn)
        
        self.text_btn = QPushButton("Choose Text Color")
        self.text_btn.clicked.connect(lambda: self.choose_color("text_color"))
        form_layout.addRow("Text Color:", self.text_btn)
        
        self.border_btn = QPushButton("Choose Border Color")
        self.border_btn.clicked.connect(lambda: self.choose_color("border_color"))
        form_layout.addRow("Border Color:", self.border_btn)
        
        self.padding_slider = QSlider(Qt.Orientation.Horizontal)
        self.padding_slider.setRange(0, 20)
        self.padding_slider.setValue(self.settings["padding"])
        self.padding_slider.valueChanged.connect(self.update_preview)
        form_layout.addRow("Padding:", self.padding_slider)
        
        layout.addLayout(form_layout)
        
        # Now that all controls are created, update the preview.
        self.update_preview()
        self.setLayout(layout)
    
    def choose_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings[key] = color.name()
            self.update_preview()
    
    def update_preview(self):
        self.settings["padding"] = self.padding_slider.value()
        self.preview_input.setStyleSheet(self.get_style())
    
    def get_style(self):
        return (
            f"background-color: {self.settings['bg_color']}; "
            f"color: {self.settings['text_color']}; "
            f"border: 1px solid {self.settings['border_color']}; "
            f"padding: {self.settings['padding']}px;"
        )
    
    def get_css(self):
        return (
            f"QLineEdit {{ background-color: {self.settings['bg_color']}; "
            f"color: {self.settings['text_color']}; "
            f"border: 1px solid {self.settings['border_color']}; "
            f"padding: {self.settings['padding']}px; }}"
        )
