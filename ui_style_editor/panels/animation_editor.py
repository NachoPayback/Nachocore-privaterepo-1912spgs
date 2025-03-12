# ui_style_editor/animation_editor.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QComboBox, QMessageBox, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QPoint
from config_manager import ConfigManager
from error_handler import ErrorHandler

class AnimationEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager(target="both")
        self.error_handler = ErrorHandler()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Animation Editor"))
        
        self.enable_checkbox = QCheckBox("Enable Animations")
        try:
            current_config = self.config_manager.get_animation_config()
        except Exception as e:
            self.error_handler.log_error("Error loading animation config", e)
            current_config = {"enable_animations": True, "button_hover_effect": "none"}
        self.enable_checkbox.setChecked(current_config.get("enable_animations", True))
        layout.addWidget(self.enable_checkbox)
        
        layout.addWidget(QLabel("Button Hover Animation:"))
        self.button_animation_dropdown = QComboBox()
        # Available effects include new glitch effect with position shift.
        self.button_animation_dropdown.addItems(["none", "fade", "slide", "glitch", "glow"])
        current_animation = current_config.get("button_hover_effect", "none")
        index = self.button_animation_dropdown.findText(current_animation)
        if index != -1:
            self.button_animation_dropdown.setCurrentIndex(index)
        layout.addWidget(self.button_animation_dropdown)
        
        layout.addWidget(QLabel("Demo Animation:"))
        self.demo_widget = QLabel("Demo Animation")
        self.demo_widget.setObjectName("animationDemoWidget")
        self.demo_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.demo_widget.setStyleSheet("background-color: #333333; color: #FFFFFF; padding: 10px;")
        layout.addWidget(self.demo_widget)
        self.demo_btn = QPushButton("Demo Selected Animation")
        self.demo_btn.clicked.connect(self.demo_animation)
        layout.addWidget(self.demo_btn)
        
        self.save_btn = QPushButton("Save Animation Settings")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
    
    def demo_animation(self):
        selected_effect = self.button_animation_dropdown.currentText()
        # For fade, slide, and glow, we use opacity effect.
        if selected_effect in ["fade", "slide", "glow"]:
            effect = QGraphicsOpacityEffect(self.demo_widget)
            self.demo_widget.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(500)
            if selected_effect == "fade":
                animation.setStartValue(0.0)
                animation.setEndValue(1.0)
            elif selected_effect == "slide":
                # Simulate slide with opacity (for demo); ideally, you'd animate position.
                animation.setStartValue(0.5)
                animation.setEndValue(1.0)
            elif selected_effect == "glow":
                animation.setStartValue(0.7)
                animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.start()
            self.demo_animation = animation  # Keep reference.
        elif selected_effect == "glitch":
            # For glitch, animate the widget's position to simulate a jitter effect.
            original_pos = self.demo_widget.pos()
            animation = QPropertyAnimation(self.demo_widget, b"pos")
            animation.setDuration(300)
            animation.setKeyValueAt(0.0, original_pos)
            animation.setKeyValueAt(0.25, original_pos + QPoint(5, -5))
            animation.setKeyValueAt(0.5, original_pos + QPoint(-5, 5))
            animation.setKeyValueAt(0.75, original_pos + QPoint(5, 5))
            animation.setKeyValueAt(1.0, original_pos)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.start()
            self.demo_animation = animation
        else:
            QMessageBox.information(self, "Demo", "No animation selected for demo.")
    
    def save_settings(self):
        config = {
            "enable_animations": self.enable_checkbox.isChecked(),
            "button_hover_effect": self.button_animation_dropdown.currentText()
        }
        try:
            self.config_manager.save_animation_config(config)
            QMessageBox.information(self, "Saved", "Animation settings saved.")
        except Exception as e:
            self.error_handler.log_error("Error saving animation settings", e)
