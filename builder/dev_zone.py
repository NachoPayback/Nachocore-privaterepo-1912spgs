#!/usr/bin/env python3
"""
Developer Zone Module

This module implements the Developer Zone tab for the builder.
It displays a slider labeled “Set Security Mode:” which lets the builder select
one of four modes: Ethical, Unethical, Grift, or Custom.
- For Ethical, Unethical, and Grift modes, a summary of which settings are active is displayed
  below the slider.
- When Custom mode is selected, individual controls appear so the builder can choose
  specific security measures.
The widget now loads the last set state from the configuration so that the slider and,
if in Custom mode, the checkboxes reflect the saved state.
"""

import os
import sys
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, 
    QCheckBox, QComboBox, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from builder import security_settings

# Mapping slider values to mode names.
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

def generate_security_summary(mode):
    """Generate a summary string of active security settings for non-Custom modes."""
    if mode in ["Ethical", "Unethical", "Grift"]:
        _, _, settings = security_settings.set_mode(mode)
        summary = (
            f"UI Keyboard: {'On' if settings.get('USE_UI_KEYBOARD', False) else 'Off'} | "
            f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)} | "
            f"Mouse Locker: {'On' if settings.get('ENABLE_MOUSE_LOCKER', False) else 'Off'} | "
            f"Sleep Blocker: {'On' if settings.get('ENABLE_SLEEP_BLOCKER', False) else 'Off'} | "
            f"Security Monitor: {'On' if settings.get('ENABLE_SECURITY_MONITOR', False) else 'Off'}"
        )
        return summary
    return ""

class DevZoneWidget(QWidget):
    # Signal to notify when the global security mode changes.
    modeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_state()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Slider area with label.
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
        
        # Summary label for non-Custom modes.
        self.summaryLabel = QLabel("")
        self.summaryLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.summaryLabel)
        
        # Container for custom security controls (visible only in Custom mode).
        self.customContainer = QWidget()
        customLayout = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
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
        if mode == "Custom":
            self.customContainer.setVisible(True)
            self.summaryLabel.setText("")
        else:
            self.customContainer.setVisible(False)
            self.summaryLabel.setText(generate_security_summary(mode))
        self.modeChanged.emit(mode)
    
    def load_existing_state(self):
        # Load the current security settings from the configuration.
        config = security_settings.load_security_settings()
        # Determine the mode from config (assuming a key "SECURITY_MODE" exists).
        # If not set, default to Ethical.
        mode = config.get("SECURITY_MODE", "Ethical")
        # Update slider based on mode.
        index = list(SECURITY_MODES.values()).index(mode) if mode in SECURITY_MODES.values() else 0
        self.modeSlider.setValue(index)
        # If in Custom mode, load individual control states.
        if mode == "Custom":
            self.custom_uiKeyboard.setChecked(config.get("USE_UI_KEYBOARD", False))
            kb_mode = config.get("KEYBOARD_BLOCKER_MODE", 1)
            # Set combo box to the appropriate index.
            idx = 0 if kb_mode == 1 else 1
            self.custom_keyboard_blocker.setCurrentIndex(idx)
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
            # Also update config to save the mode.
            config = security_settings.load_security_settings()
            config["SECURITY_MODE"] = mode
            security_settings.save_security_settings(config)
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
