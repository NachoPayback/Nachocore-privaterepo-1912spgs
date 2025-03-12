# ui_style_editor/button_style_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFormLayout, QSlider, QComboBox, QColorDialog
from PyQt6.QtCore import Qt

class ButtonStylePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {"bg_color": "#007ACC", "text_color": "#FFFFFF", "border_color": "#005B9E", "padding": 5}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.preview_button = QPushButton("Button Preview")
        self.preview_button.setObjectName("buttonPreview")
        layout.addWidget(self.preview_button)
        
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
        self.setLayout(layout)
        # Now that all widgets are created, update the preview.
        self.update_preview()
    
    def choose_color(self, key):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings[key] = color.name()
            self.update_preview()
    
    def update_preview(self):
        self.settings["padding"] = self.padding_slider.value()
        self.preview_button.setStyleSheet(self.get_style())
    
    def get_style(self):
        return f"background-color: {self.settings['bg_color']}; color: {self.settings['text_color']}; border: 2px solid {self.settings['border_color']}; padding: {self.settings['padding']}px;"
    
    def get_css(self):
        return f"QPushButton.submit {{ background-color: {self.settings['bg_color']}; color: {self.settings['text_color']}; border: 2px solid {self.settings['border_color']}; padding: {self.settings['padding']}px; }}"
