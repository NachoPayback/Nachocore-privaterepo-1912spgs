# builder/ui/security_mode_tab.py
import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QCheckBox, QPushButton, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from builder import security_settings

# Define the security modes.
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

def generate_security_summary_for_confirmation(settings: dict) -> str:
    """
    Generate a plain-English summary of the security settings for confirmation.
    This excludes the 'selected_gift_card' information.
    """
    lines = []
    lines.append(f"Security Mode: {settings.get('SECURITY_MODE', 'Ethical')}")
    lines.append(f"Use UI Keyboard: {settings.get('USE_UI_KEYBOARD', False)}")
    lines.append(f"Keyboard Blocker Mode: {settings.get('KEYBOARD_BLOCKER_MODE', 0)}")
    lines.append(f"Enable Mouse Locker: {settings.get('ENABLE_MOUSE_LOCKER', False)}")
    lines.append(f"Enable Sleep Blocker: {settings.get('ENABLE_SLEEP_BLOCKER', False)}")
    lines.append(f"Enable Security Monitor: {settings.get('ENABLE_SECURITY_MONITOR', False)}")
    lines.append(f"Close Button Disabled: {settings.get('CLOSE_BUTTON_DISABLED', False)}")
    lines.append(f"Enable Logger: {settings.get('ENABLE_LOGGER', False)}")
    return "\n".join(lines)

class SecurityModeTab(QWidget):
    """
    A dedicated tab for managing security settings.
    This centralizes all security-related controls, allows for preset integration,
    and provides a confirmation dialog before export.
    """
    # Signal to notify when settings change.
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_state()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Security Mode Slider ---
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
        
        # --- Custom Security Options (visible only in Custom mode) ---
        self.customContainer = QWidget()
        custom_form = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
        custom_form.addRow(self.custom_uiKeyboard)
        custom_form.addRow("Keyboard Blocker Mode:", self.custom_keyboard_blocker)
        custom_form.addRow(self.custom_mouse_locker)
        custom_form.addRow(self.custom_sleep_blocker)
        custom_form.addRow(self.custom_security_monitor)
        self.customContainer.setVisible(False)
        layout.addWidget(self.customContainer)
        
        # --- Buttons ---
        # Apply Button: Save and apply the current settings.
        self.applyButton = QPushButton("Apply Security Settings")
        self.applyButton.clicked.connect(self.apply_settings)
        layout.addWidget(self.applyButton)
        
        # Confirm Button: Show a confirmation dialog before export.
        self.confirmButton = QPushButton("Confirm Security Settings for Export")
        self.confirmButton.clicked.connect(self.confirm_settings)
        layout.addWidget(self.confirmButton)
    
    @pyqtSlot(int)
    def on_slider_changed(self, value):
        mode = SECURITY_MODES.get(value, "Ethical")
        self.modeDisplay.setText(mode)
        if mode == "Custom":
            self.customContainer.setVisible(True)
        else:
            self.customContainer.setVisible(False)
    
    def load_existing_state(self):
        """Load existing security settings and update UI controls."""
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
    
    def apply_settings(self):
        """Apply and save the current security settings."""
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        settings = {"SECURITY_MODE": mode}
        if mode == "Custom":
            settings["USE_UI_KEYBOARD"] = self.custom_uiKeyboard.isChecked()
            settings["KEYBOARD_BLOCKER_MODE"] = self.custom_keyboard_blocker.currentData()
            settings["ENABLE_MOUSE_LOCKER"] = self.custom_mouse_locker.isChecked()
            settings["ENABLE_SLEEP_BLOCKER"] = self.custom_sleep_blocker.isChecked()
            settings["ENABLE_SECURITY_MONITOR"] = self.custom_security_monitor.isChecked()
        else:
            # For preset modes, load defaults from security_settings.
            _, _, defaults = security_settings.set_mode(mode)
            settings.update(defaults)
        security_settings.save_security_settings(settings)
        self.settingsChanged.emit(settings)
        QMessageBox.information(self, "Settings Applied", "Security settings have been updated.")
    
    def confirm_settings(self):
        """
        Show a confirmation dialog with a plain-English summary of the current security settings.
        The builder must confirm these settings before proceeding with an export.
        """
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        settings = {"SECURITY_MODE": mode}
        if mode == "Custom":
            settings["USE_UI_KEYBOARD"] = self.custom_uiKeyboard.isChecked()
            settings["KEYBOARD_BLOCKER_MODE"] = self.custom_keyboard_blocker.currentData()
            settings["ENABLE_MOUSE_LOCKER"] = self.custom_mouse_locker.isChecked()
            settings["ENABLE_SLEEP_BLOCKER"] = self.custom_sleep_blocker.isChecked()
            settings["ENABLE_SECURITY_MONITOR"] = self.custom_security_monitor.isChecked()
        else:
            _, _, defaults = security_settings.set_mode(mode)
            settings.update(defaults)
        summary = generate_security_summary_for_confirmation(settings)
        reply = QMessageBox.question(
            self,
            "Confirm Security Settings",
            f"Please confirm the following security settings before export:\n\n{summary}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Confirmed", "Security settings confirmed for export.")
        else:
            QMessageBox.information(self, "Cancelled", "Export cancelled. Please adjust security settings if needed.")
