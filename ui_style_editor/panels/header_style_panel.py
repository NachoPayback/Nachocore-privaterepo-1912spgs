# ui_style_editor/header_style_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFormLayout, QSlider, QPushButton, QComboBox, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class HeaderStylePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {"font_size": 24, "font_weight": "bold", "text_color": "#00FF00"}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create preview label first (it will be updated later)
        self.preview_label = QLabel("Header Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setObjectName("headerPreview")
        layout.addWidget(self.preview_label)
        
        # Now create controls
        form_layout = QFormLayout()
        
        # Font Size slider.
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(16, 48)
        self.size_slider.setValue(self.settings["font_size"])
        self.size_slider.valueChanged.connect(self.update_preview)
        form_layout.addRow("Font Size:", self.size_slider)
        
        # Font Weight dropdown.
        self.weight_dropdown = QComboBox()
        self.weight_dropdown.addItems(["normal", "bold"])
        self.weight_dropdown.setCurrentText(self.settings["font_weight"])
        self.weight_dropdown.currentIndexChanged.connect(self.update_preview)
        form_layout.addRow("Font Weight:", self.weight_dropdown)
        
        # Color picker for text.
        self.color_btn = QPushButton("Choose Text Color")
        self.color_btn.clicked.connect(self.choose_color)
        form_layout.addRow("Text Color:", self.color_btn)
        
        layout.addLayout(form_layout)
        
        # Now that controls are created, update the preview.
        self.update_preview()
        
        self.setLayout(layout)
    
    def choose_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings["text_color"] = color.name()
            self.update_preview()
    
    def update_preview(self):
        self.settings["font_size"] = self.size_slider.value()
        self.settings["font_weight"] = self.weight_dropdown.currentText()
        style = f"font-size: {self.settings['font_size']}px; font-weight: {self.settings['font_weight']}; color: {self.settings['text_color']};"
        self.preview_label.setStyleSheet(style)
    
    def get_css(self):
        return f"QLabel.header {{ font-size: {self.settings['font_size']}px; font-weight: {self.settings['font_weight']}; color: {self.settings['text_color']}; }}"
