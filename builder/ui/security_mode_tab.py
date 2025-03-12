# builder/ui/security_mode_tab.py
import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QCheckBox, QPushButton, QFormLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from builder.security_settings import set_mode, load_security_settings
from builder.presets import list_presets, load_preset, save_preset

SECURITY_MODES = {
    0: "Ethical",
    1: "Unethical",
    2: "Grift",
    3: "Custom"
}

def generate_live_summary(settings: dict) -> str:
    lines = [
        f"Mode: {settings.get('SECURITY_MODE', 'Ethical')}",
        f"UI Keyboard: {settings.get('USE_UI_KEYBOARD', False)}",
        f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)}",
        f"Mouse Locker: {settings.get('ENABLE_MOUSE_LOCKER', False)}",
        f"Sleep Blocker: {settings.get('ENABLE_SLEEP_BLOCKER', False)}",
        f"Security Monitor: {settings.get('ENABLE_SECURITY_MONITOR', False)}",
        f"Close Button Disabled: {settings.get('CLOSE_BUTTON_DISABLED', False)}",
        f"Logger: {settings.get('ENABLE_LOGGER', False)}"
    ]
    return "\n".join(lines)

class SecurityModeTab(QWidget):
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_state()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Set Security Mode:")
        slider_label.setObjectName("securityModeLabel")
        slider_layout.addWidget(slider_label)
        self.modeSlider = QSlider(Qt.Orientation.Horizontal)
        self.modeSlider.setObjectName("securityModeSlider")
        self.modeSlider.setRange(0, 3)
        self.modeSlider.setSingleStep(1)
        self.modeSlider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.modeSlider)
        self.modeDisplay = QLabel("Ethical")
        self.modeDisplay.setObjectName("securityModeDisplay")
        self.modeDisplay.setStyleSheet("font-weight: bold;")
        slider_layout.addWidget(self.modeDisplay)
        layout.addLayout(slider_layout)
        
        self.customContainer = QWidget()
        self.customContainer.setObjectName("securityCustomContainer")
        form = QFormLayout(self.customContainer)
        self.chk_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.cbo_blocker = QComboBox()
        self.cbo_blocker.addItem("Block All (Mode 1)", 1)
        self.cbo_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.chk_mouse = QCheckBox("Enable Mouse Locker")
        self.chk_sleep = QCheckBox("Enable Sleep Blocker")
        self.chk_monitor = QCheckBox("Enable Security Monitor")
        form.addRow(self.chk_uiKeyboard)
        form.addRow("Keyboard Blocker:", self.cbo_blocker)
        form.addRow(self.chk_mouse)
        form.addRow(self.chk_sleep)
        form.addRow(self.chk_monitor)
        self.customContainer.setVisible(False)
        layout.addWidget(self.customContainer)
        
        self.summaryLabel = QLabel("Security Summary will appear here")
        self.summaryLabel.setObjectName("securitySummaryLabel")
        layout.addWidget(self.summaryLabel)
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.presetDropdown = QComboBox()
        self.presetDropdown.setObjectName("securityPresetDropdown")
        self.refresh_presets_dropdown()
        preset_layout.addWidget(self.presetDropdown)
        self.loadPresetButton = QPushButton("Load Preset")
        self.loadPresetButton.setObjectName("loadSecurityPresetButton")
        self.loadPresetButton.clicked.connect(self.load_preset)
        preset_layout.addWidget(self.loadPresetButton)
        self.savePresetButton = QPushButton("Save Preset")
        self.savePresetButton.setObjectName("saveSecurityPresetButton")
        self.savePresetButton.clicked.connect(self.save_preset)
        preset_layout.addWidget(self.savePresetButton)
        layout.addLayout(preset_layout)
        
        self.setLayout(layout)
    
    def load_existing_state(self):
        cfg = load_security_settings()
        mode = cfg.get("SECURITY_MODE", "Ethical")
        try:
            idx = list(SECURITY_MODES.values()).index(mode)
        except ValueError:
            idx = 0
        self.modeSlider.setValue(idx)
        
        if mode == "Custom":
            self.customContainer.setVisible(True)
            self.chk_uiKeyboard.setChecked(cfg.get("USE_UI_KEYBOARD", False))
            kb_mode = cfg.get("KEYBOARD_BLOCKER_MODE", 1)
            index = 0 if kb_mode == 1 else 1
            self.cbo_blocker.setCurrentIndex(index)
            self.chk_mouse.setChecked(cfg.get("ENABLE_MOUSE_LOCKER", False))
            self.chk_sleep.setChecked(cfg.get("ENABLE_SLEEP_BLOCKER", False))
            self.chk_monitor.setChecked(cfg.get("ENABLE_SECURITY_MONITOR", False))
        else:
            self.customContainer.setVisible(False)
        
        self.update_live_summary()
    
    def on_slider_changed(self, value):
        mode = SECURITY_MODES.get(value, "Ethical")
        self.modeDisplay.setText(mode)
        self.customContainer.setVisible(mode == "Custom")
        self.apply_mode(mode)
    
    def on_custom_control_changed(self):
        if SECURITY_MODES.get(self.modeSlider.value(), "Ethical") == "Custom":
            self.apply_mode("Custom")
    
    def apply_mode(self, mode):
        if mode in ["Ethical", "Unethical", "Grift"]:
            success, msg, updated = set_mode(mode)
        else:
            custom_settings = {
                "USE_UI_KEYBOARD": self.chk_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.cbo_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.chk_mouse.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.chk_sleep.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.chk_monitor.isChecked()
            }
            success, msg, updated = set_mode("Custom", custom_settings=custom_settings)
        
        if success:
            self.update_live_summary()
            self.settingsChanged.emit(updated)
        else:
            QMessageBox.critical(self, "Error", f"Failed to set mode: {msg}")
    
    def update_live_summary(self):
        cfg = load_security_settings()
        self.summaryLabel.setText(generate_live_summary(cfg))
    
    def refresh_presets_dropdown(self):
        self.presetDropdown.clear()
        presets = list_presets("security")
        self.presetDropdown.addItems(presets)
    
    def load_preset(self):
        preset_name = self.presetDropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Warning", "No preset selected.")
            return
        preset_settings = load_preset("security", preset_name)
        if preset_settings:
            self.modeSlider.setValue(3)  # Force slider to Custom
            self.customContainer.setVisible(True)
            self.chk_uiKeyboard.setChecked(preset_settings.get("USE_UI_KEYBOARD", False))
            kb_mode = preset_settings.get("KEYBOARD_BLOCKER_MODE", 1)
            self.cbo_blocker.setCurrentIndex(0 if kb_mode == 1 else 1)
            self.chk_mouse.setChecked(preset_settings.get("ENABLE_MOUSE_LOCKER", False))
            self.chk_sleep.setChecked(preset_settings.get("ENABLE_SLEEP_BLOCKER", False))
            self.chk_monitor.setChecked(preset_settings.get("ENABLE_SECURITY_MONITOR", False))
            QMessageBox.information(self, "Preset Loaded", f"Preset '{preset_name}' loaded successfully.")
            self.apply_mode("Custom")
        else:
            QMessageBox.warning(self, "Error", f"Failed to load preset '{preset_name}'.")
    
    def save_preset(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode != "Custom":
            QMessageBox.warning(self, "Warning", "Presets can only be saved in Custom mode.")
            return
        custom_dict = {
            "SECURITY_MODE": "Custom",
            "USE_UI_KEYBOARD": self.chk_uiKeyboard.isChecked(),
            "KEYBOARD_BLOCKER_MODE": self.cbo_blocker.currentData(),
            "ENABLE_MOUSE_LOCKER": self.chk_mouse.isChecked(),
            "ENABLE_SLEEP_BLOCKER": self.chk_sleep.isChecked(),
            "ENABLE_SECURITY_MONITOR": self.chk_monitor.isChecked()
        }
        if save_preset("security", custom_dict, parent_widget=self):
            QMessageBox.information(self, "Preset Saved", "Security preset saved successfully.")
            self.refresh_presets_dropdown()
