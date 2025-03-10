#!/usr/bin/env python3
import os
import sys
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFormLayout,
    QCheckBox, QSpinBox, QPushButton, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt

# Define the path to your config file.
# Adjust this path as needed to match your project structure.
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class DevZoneWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DevZoneWidget")
        self.init_ui()
        self.load_existing_settings()
    
    def init_ui(self):
        mainLayout = QVBoxLayout()

        # Watermark label to display the current mode.
        self.watermarkLabel = QLabel("Mode: None")
        self.watermarkLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.watermarkLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        mainLayout.addWidget(self.watermarkLabel)

        # Mode selection control.
        self.modeCombo = QComboBox()
        self.modeCombo.addItems(["Ethical Mode", "Unethical Mode", "Grift Mode", "Custom Mode"])
        self.modeCombo.currentIndexChanged.connect(self.on_mode_changed)
        mainLayout.addWidget(self.modeCombo)

        # Container for custom security settings.
        self.customSettingsWidget = QWidget()
        customLayout = QFormLayout()
        self.uiKeyboardCheck = QCheckBox("Use UI Keyboard")
        self.keyboardBlockerSpin = QSpinBox()
        self.keyboardBlockerSpin.setMinimum(0)
        self.keyboardBlockerSpin.setMaximum(5)
        self.keyboardBlockerSpin.setValue(1)
        self.mouseLockerCheck = QCheckBox("Enable Mouse Locker")
        self.sleepBlockerCheck = QCheckBox("Enable Sleep Blocker")
        self.securityMonitorCheck = QCheckBox("Enable Security Monitor")
        self.closeButtonDisabledCheck = QCheckBox("Disable Close Button")
        self.loggerCheck = QCheckBox("Enable Logger")
        
        customLayout.addRow(self.uiKeyboardCheck)
        customLayout.addRow("Keyboard Blocker Mode:", self.keyboardBlockerSpin)
        customLayout.addRow(self.mouseLockerCheck)
        customLayout.addRow(self.sleepBlockerCheck)
        customLayout.addRow(self.securityMonitorCheck)
        customLayout.addRow(self.closeButtonDisabledCheck)
        customLayout.addRow(self.loggerCheck)
        
        self.customSettingsWidget.setLayout(customLayout)
        mainLayout.addWidget(self.customSettingsWidget)
        
        # Save button for Custom mode.
        self.saveButton = QPushButton("Save Security Settings")
        self.saveButton.clicked.connect(self.save_settings)
        mainLayout.addWidget(self.saveButton)
        
        self.setLayout(mainLayout)
        
        # Initially hide custom controls unless Custom Mode is selected.
        self.customSettingsWidget.setVisible(False)
    
    def on_mode_changed(self, index):
        mode = self.modeCombo.currentText()
        if mode == "Ethical Mode":
            self.apply_ethics_settings()
            self.watermarkLabel.setText("Mode: Ethical")
            self.watermarkLabel.setStyleSheet(
                "background-color: green; font-size: 18px; font-weight: bold; color: white;"
            )
            self.customSettingsWidget.setVisible(False)
        elif mode == "Unethical Mode":
            self.apply_unethical_settings()
            self.watermarkLabel.setText("Mode: Unethical")
            self.watermarkLabel.setStyleSheet(
                "background-color: yellow; font-size: 18px; font-weight: bold; color: black;"
            )
            self.customSettingsWidget.setVisible(False)
        elif mode == "Grift Mode":
            # Placeholder for future stronger security protocols.
            self.watermarkLabel.setText("Mode: Grift")
            self.watermarkLabel.setStyleSheet(
                "background-color: red; font-size: 18px; font-weight: bold; color: white;"
            )
            self.customSettingsWidget.setVisible(False)
        elif mode == "Custom Mode":
            self.watermarkLabel.setText("Mode: Custom")
            self.watermarkLabel.setStyleSheet(
                "background-color: cyan; font-size: 18px; font-weight: bold; color: black;"
            )
            self.customSettingsWidget.setVisible(True)
    
    def apply_ethics_settings(self):
        # Ethical Mode: turn off dangerous security settings.
        settings = {
            "USE_UI_KEYBOARD": False,
            "KEYBOARD_BLOCKER_MODE": 0,
            "ENABLE_MOUSE_LOCKER": False,
            "ENABLE_SLEEP_BLOCKER": False,
            "ENABLE_SECURITY_MONITOR": False,
            "CLOSE_BUTTON_DISABLED": False,
            "ENABLE_LOGGER": True
        }
        self.update_custom_controls(settings)
        self.save_settings_to_file(settings)
    
    def apply_unethical_settings(self):
        # Unethical Mode: turn on all dangerous security settings.
        settings = {
            "USE_UI_KEYBOARD": True,
            "KEYBOARD_BLOCKER_MODE": 5,
            "ENABLE_MOUSE_LOCKER": True,
            "ENABLE_SLEEP_BLOCKER": True,
            "ENABLE_SECURITY_MONITOR": True,
            "CLOSE_BUTTON_DISABLED": True,
            "ENABLE_LOGGER": True
        }
        self.update_custom_controls(settings)
        self.save_settings_to_file(settings)
    
    def update_custom_controls(self, settings):
        self.uiKeyboardCheck.setChecked(settings.get("USE_UI_KEYBOARD", False))
        self.keyboardBlockerSpin.setValue(settings.get("KEYBOARD_BLOCKER_MODE", 0))
        self.mouseLockerCheck.setChecked(settings.get("ENABLE_MOUSE_LOCKER", False))
        self.sleepBlockerCheck.setChecked(settings.get("ENABLE_SLEEP_BLOCKER", False))
        self.securityMonitorCheck.setChecked(settings.get("ENABLE_SECURITY_MONITOR", False))
        self.closeButtonDisabledCheck.setChecked(settings.get("CLOSE_BUTTON_DISABLED", False))
        self.loggerCheck.setChecked(settings.get("ENABLE_LOGGER", True))
    
    def load_existing_settings(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    config = json.load(f)
                    self.uiKeyboardCheck.setChecked(config.get("USE_UI_KEYBOARD", False))
                    self.keyboardBlockerSpin.setValue(config.get("KEYBOARD_BLOCKER_MODE", 0))
                    self.mouseLockerCheck.setChecked(config.get("ENABLE_MOUSE_LOCKER", False))
                    self.sleepBlockerCheck.setChecked(config.get("ENABLE_SLEEP_BLOCKER", False))
                    self.securityMonitorCheck.setChecked(config.get("ENABLE_SECURITY_MONITOR", False))
                    self.closeButtonDisabledCheck.setChecked(config.get("CLOSE_BUTTON_DISABLED", False))
                    self.loggerCheck.setChecked(config.get("ENABLE_LOGGER", True))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load existing settings: {e}")
    
    def save_settings_to_file(self, settings):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    current_config = json.load(f)
            else:
                current_config = {}
        except Exception:
            current_config = {}
        current_config.update(settings)
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(current_config, f, indent=4)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def save_settings(self):
        mode = self.modeCombo.currentText()
        if mode == "Custom Mode":
            # Save settings from the custom controls.
            settings = {
                "USE_UI_KEYBOARD": self.uiKeyboardCheck.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.keyboardBlockerSpin.value(),
                "ENABLE_MOUSE_LOCKER": self.mouseLockerCheck.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.sleepBlockerCheck.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.securityMonitorCheck.isChecked(),
                "CLOSE_BUTTON_DISABLED": self.closeButtonDisabledCheck.isChecked(),
                "ENABLE_LOGGER": self.loggerCheck.isChecked()
            }
            self.save_settings_to_file(settings)
        else:
            # For the other modes, the settings are applied automatically.
            QMessageBox.information(self, "Info", f"Settings for {mode} mode are already applied.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DevZoneWidget()
    widget.show()
    sys.exit(app.exec())
