# ui_style_editor/color_manager.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QColorDialog, QHBoxLayout, QComboBox, QFrame
from config_manager import ConfigManager
import colorsys
from error_handler import ErrorHandler

class ColorManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager(target="both")
        self.error_handler = ErrorHandler()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Color Palette Manager"))
        
        # Palette generation style selector.
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Palette Generation Type:"))
        self.palette_type_dropdown = QComboBox()
        self.palette_type_dropdown.addItems(["Analogous", "Complementary", "Triadic"])
        style_layout.addWidget(self.palette_type_dropdown)
        layout.addLayout(style_layout)
        
        # Base color selection.
        base_layout = QHBoxLayout()
        self.choose_color_btn = QPushButton("Choose Base Color")
        self.choose_color_btn.clicked.connect(self.choose_color)
        base_layout.addWidget(self.choose_color_btn)
        self.selected_color_display = QFrame()
        self.selected_color_display.setFixedSize(50, 50)
        self.selected_color_display.setStyleSheet("background-color: #FFFFFF; border: 1px solid #000;")
        base_layout.addWidget(self.selected_color_display)
        layout.addLayout(base_layout)
        
        # Generate palette button.
        self.generate_palette_btn = QPushButton("Generate Palette")
        self.generate_palette_btn.clicked.connect(self.generate_palette)
        layout.addWidget(self.generate_palette_btn)
        
        # Display generated palette with swatches.
        self.palette_display = QVBoxLayout()
        layout.addLayout(self.palette_display)
        
        # Save palette button.
        self.save_palette_btn = QPushButton("Save Palette")
        self.save_palette_btn.clicked.connect(self.save_palette)
        layout.addWidget(self.save_palette_btn)
        
        self.setLayout(layout)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.base_color = color.name()
            self.selected_color_display.setStyleSheet(f"background-color: {self.base_color}; border: 1px solid #000;")
    
    def generate_palette(self):
        if not hasattr(self, "base_color"):
            self.show_message("Please choose a base color first.")
            return
        base_hex = self.base_color
        palette_type = self.palette_type_dropdown.currentText()
        palette = self.generate_palette_by_type(base_hex, palette_type)
        # Clear previous swatches.
        while self.palette_display.count():
            item = self.palette_display.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # Create swatches.
        for key, color in palette.items():
            swatch = QFrame()
            swatch.setFixedSize(100, 50)
            swatch.setStyleSheet(f"background-color: {color}; border: 1px solid #000;")
            label = QLabel(f"{key}: {color}")
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.addWidget(swatch)
            container_layout.addWidget(label)
            self.palette_display.addWidget(container)
        self.generated_palette = palette
    
    def generate_palette_by_type(self, base_hex, palette_type):
        r, g, b = [int(base_hex[i:i+2], 16) for i in (1, 3, 5)]
        if palette_type == "Analogous":
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            ana1 = colorsys.hsv_to_rgb((h+0.1)%1, s, v)
            ana2 = colorsys.hsv_to_rgb((h-0.1)%1, s, v)
            ana1_hex = "#{:02X}{:02X}{:02X}".format(int(ana1[0]*255), int(ana1[1]*255), int(ana1[2]*255))
            ana2_hex = "#{:02X}{:02X}{:02X}".format(int(ana2[0]*255), int(ana2[1]*255), int(ana2[2]*255))
            return {"primary": base_hex, "analogous1": ana1_hex, "analogous2": ana2_hex}
        elif palette_type == "Complementary":
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            comp_rgb = colorsys.hsv_to_rgb((h+0.5)%1, s, v)
            comp_hex = "#{:02X}{:02X}{:02X}".format(int(comp_rgb[0]*255), int(comp_rgb[1]*255), int(comp_rgb[2]*255))
            return {"primary": base_hex, "complementary": comp_hex}
        elif palette_type == "Triadic":
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            triad1 = colorsys.hsv_to_rgb((h+1/3)%1, s, v)
            triad2 = colorsys.hsv_to_rgb((h+2/3)%1, s, v)
            triad1_hex = "#{:02X}{:02X}{:02X}".format(int(triad1[0]*255), int(triad1[1]*255), int(triad1[2]*255))
            triad2_hex = "#{:02X}{:02X}{:02X}".format(int(triad2[0]*255), int(triad2[1]*255), int(triad2[2]*255))
            return {"primary": base_hex, "triadic1": triad1_hex, "triadic2": triad2_hex}
        else:
            return {"primary": base_hex}
    
    def save_palette(self):
        if hasattr(self, "generated_palette"):
            try:
                self.config_manager.save_palette_config(self.generated_palette)
            except Exception as e:
                self.error_handler.log_error("Error saving palette config", e)
    
    def show_message(self, message):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Info", message)
