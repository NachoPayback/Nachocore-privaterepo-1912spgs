import os
import sys
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
    QCheckBox, QComboBox, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from builder import security_settings

SECURITY_MODES = {
    0: "Ethical",
    1: "Unethical",
    2: "Grift",
    3: "Custom"
}

def mode_text_color(mode):
    colors = {
        "Ethical": "green",
        "Unethical": "orange",
        "Grift": "red",
        "Custom": "cyan"
    }
    return colors.get(mode, "black")

class DevZoneWidget(QWidget):
    modeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Labeled slider for selecting security mode.
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Set Security Mode:")
        slider_layout.addWidget(slider_label)
        self.modeSlider = QSlider(Qt.Orientation.Horizontal)
        self.modeSlider.setMinimum(0)
        self.modeSlider.setMaximum(3)
        self.modeSlider.setTickInterval(1)
        self.modeSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.modeSlider.setSingleStep(1)
        self.modeSlider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.modeSlider)
        self.modeDisplay = QLabel(SECURITY_MODES[0])
        slider_layout.addWidget(self.modeDisplay)
        layout.addLayout(slider_layout)
        
        # Container for custom security controls (visible only in Custom mode).
        self.customContainer = QWidget()
        customLayout = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_uiKeyboard.setChecked(False)
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_mouse_locker.setChecked(False)
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_sleep_blocker.setChecked(False)
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
        self.custom_security_monitor.setChecked(False)
        customLayout.addRow(self.custom_uiKeyboard)
        customLayout.addRow("Keyboard Blocker Mode:", self.custom_keyboard_blocker)
        customLayout.addRow(self.custom_mouse_locker)
        customLayout.addRow(self.custom_sleep_blocker)
        customLayout.addRow(self.custom_security_monitor)
        self.customContainer.setVisible(False)
        layout.addWidget(self.customContainer)
        
        # Save button.
        self.saveButton = QPushButton("Apply Security Mode")
        self.saveButton.clicked.connect(self.save_mode)
        layout.addWidget(self.saveButton)
    
    @pyqtSlot(int)
    def on_slider_changed(self, value):
        mode = SECURITY_MODES.get(value, "Ethical")
        self.modeDisplay.setText(mode)
        # Show custom controls only when mode is Custom.
        self.customContainer.setVisible(mode == "Custom")
        self.modeChanged.emit(mode)
    
    def load_existing_settings(self):
        # Default to Ethical mode.
        self.modeSlider.setValue(0)
    
    def save_mode(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode == "Custom":
            custom_settings = {
                "USE_UI_KEYBOARD": self.custom_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.custom_keyboard_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.custom_mouse_locker.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.custom_sleep_blocker.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.custom_security_monitor.isChecked()
            }
            success, message, _ = security_settings.set_mode(mode, custom_settings=custom_settings)
        else:
            success, message, _ = security_settings.set_mode(mode)
        if success:
            QMessageBox.information(self, "Success", f"Security mode set to {mode}.")
            self.modeChanged.emit(mode)
        else:
            QMessageBox.critical(self, "Error", message)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = DevZoneWidget()
    widget.show()
    sys.exit(app.exec())
