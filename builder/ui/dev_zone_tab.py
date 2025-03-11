# builder/ui/dev_zone_tab.py
"""
Developer Zone Tab UI Module

This module provides the Developer Zone where beta features and aesthetic
customizations are managed, including dynamic security mode changes.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox,
    QComboBox, QFormLayout, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

# Import security settings functions (which now use modules from shared/security)
from builder import security_settings

# Security mode mapping
SECURITY_MODES = {
    0: "Ethical",
    1: "Unethical",
    2: "Grift",
    3: "Custom"
}

def mode_text_color(mode):
    return {
        "Ethical": "green",
        "Unethical": "orange",
        "Grift": "red",
        "Custom": "cyan"
    }.get(mode, "black")

def generate_security_summary(mode):
    if mode in ["Ethical", "Unethical", "Grift"]:
        # Call set_mode from security_settings to get a summary
        _, _, settings = security_settings.set_mode(mode)
        return (
            f"UI Keyboard: {'On' if settings.get('USE_UI_KEYBOARD', False) else 'Off'} | "
            f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)} | "
            f"Mouse Locker: {'On' if settings.get('ENABLE_MOUSE_LOCKER', False) else 'Off'} | "
            f"Sleep Blocker: {'On' if settings.get('ENABLE_SLEEP_BLOCKER', False) else 'Off'} | "
            f"Security Monitor: {'On' if settings.get('ENABLE_SECURITY_MONITOR', False) else 'Off'}"
        )
    return ""

class DevZoneWidget(QWidget):
    modeChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_state()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Slider control row.
        row = QHBoxLayout()
        row.addWidget(QLabel("Set Security Mode:"))
        self.modeSlider = QSlider(Qt.Orientation.Horizontal)
        self.modeSlider.setRange(0, 3)
        self.modeSlider.setTickInterval(1)
        self.modeSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.modeSlider.setSingleStep(1)
        self.modeSlider.valueChanged.connect(self.on_slider_changed)
        row.addWidget(self.modeSlider)
        self.modeDisplay = QLabel(SECURITY_MODES[0])
        row.addWidget(self.modeDisplay)
        layout.addLayout(row)
        
        # Summary label.
        self.summaryLabel = QLabel("")
        self.summaryLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.summaryLabel)
        
        # Container for custom settings (visible only when in Custom mode).
        self.customContainer = QWidget()
        form = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
        form.addRow(self.custom_uiKeyboard)
        form.addRow("Keyboard Blocker Mode:", self.custom_keyboard_blocker)
        form.addRow(self.custom_mouse_locker)
        form.addRow(self.custom_sleep_blocker)
        form.addRow(self.custom_security_monitor)
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
        if mode == "Custom":
            self.customContainer.setVisible(True)
            self.summaryLabel.setText("")
        else:
            self.customContainer.setVisible(False)
            self.summaryLabel.setText(generate_security_summary(mode))
        self.modeChanged.emit(mode)

    def load_existing_state(self):
        config = security_settings.load_security_settings()
        mode = config.get("SECURITY_MODE", "Ethical")
        slider_val = list(SECURITY_MODES.values()).index(mode) if mode in SECURITY_MODES.values() else 0
        self.modeSlider.setValue(slider_val)
        if mode == "Custom":
            self.custom_uiKeyboard.setChecked(config.get("USE_UI_KEYBOARD", False))
            kb_mode = config.get("KEYBOARD_BLOCKER_MODE", 1)
            self.custom_keyboard_blocker.setCurrentIndex(0 if kb_mode == 1 else 1)
            self.custom_mouse_locker.setChecked(config.get("ENABLE_MOUSE_LOCKER", False))
            self.custom_sleep_blocker.setChecked(config.get("ENABLE_SLEEP_BLOCKER", False))
            self.custom_security_monitor.setChecked(config.get("ENABLE_SECURITY_MONITOR", False))
        else:
            self.summaryLabel.setText(generate_security_summary(mode))

    def save_mode(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode == "Custom":
            custom_settings = {
                "USE_UI_KEYBOARD": self.custom_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.custom_keyboard_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.custom_mouse_locker.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.custom_sleep_blocker.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.custom_security_monitor.isChecked(),
                "SECURITY_MODE": mode
            }
            success, message, _ = security_settings.set_mode(mode, custom_settings=custom_settings)
        else:
            success, message, _ = security_settings.set_mode(mode)
            config = security_settings.load_security_settings()
            config["SECURITY_MODE"] = mode
            security_settings.save_security_settings(config)
        if success:
            QMessageBox.information(self, "Success", f"Security mode set to {mode}.")
            self.modeChanged.emit(mode)
        else:
            QMessageBox.critical(self, "Error", message)
