# builder/ui/export_tab.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSlider,
    QFormLayout, QCheckBox, QComboBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from builder import security_settings

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
        _, _, settings = security_settings.set_mode(mode)
        return (
            f"UI Keyboard: {'On' if settings.get('USE_UI_KEYBOARD', False) else 'Off'} | "
            f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)} | "
            f"Mouse Locker: {'On' if settings.get('ENABLE_MOUSE_LOCKER', False) else 'Off'} | "
            f"Sleep Blocker: {'On' if settings.get('ENABLE_SLEEP_BLOCKER', False) else 'Off'} | "
            f"Security Monitor: {'On' if settings.get('ENABLE_SECURITY_MONITOR', False) else 'Off'}"
        )
    return ""

class ExportTab(QWidget):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter Custom EXE Name:"))
        self.custom_exe_name = QLineEdit()
        self.custom_exe_name.setPlaceholderText("e.g., ScammerPaybackGame")
        layout.addWidget(self.custom_exe_name)
        
        layout.addWidget(QLabel("Select Security Mode:"))
        self.export_security_slider = QSlider(Qt.Orientation.Horizontal)
        self.export_security_slider.setRange(0, 3)
        self.export_security_slider.valueChanged.connect(self.on_export_slider_changed)
        layout.addWidget(self.export_security_slider)
        
        self.export_mode_label = QLabel("")
        self.export_mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.export_mode_label)
        self.update_export_mode_label()
        
        self.export_customContainer = QWidget()
        form = QFormLayout(self.export_customContainer)
        self.export_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.export_keyboard_blocker = QComboBox()
        self.export_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.export_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.export_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.export_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.export_security_monitor = QCheckBox("Enable Security Monitor")
        form.addRow(self.export_uiKeyboard)
        form.addRow("Keyboard Blocker Mode:", self.export_keyboard_blocker)
        form.addRow(self.export_mouse_locker)
        form.addRow(self.export_sleep_blocker)
        form.addRow(self.export_security_monitor)
        self.export_customContainer.setVisible(False)
        layout.addWidget(self.export_customContainer)
        
        self.export_security_slider.valueChanged.connect(self.on_export_slider_changed)
        
        export_btn = QPushButton("Export to EXE")
        export_btn.clicked.connect(self.on_export)
        layout.addWidget(export_btn)
        
        self.load_export_state()
    
    def on_export_slider_changed(self, val):
        mode = SECURITY_MODES.get(val, "Ethical")
        if mode == "Custom":
            self.export_customContainer.setVisible(True)
            self.export_mode_label.setText("")
        else:
            self.export_customContainer.setVisible(False)
            self.update_export_mode_label()
        self.save_export_state()
    
    def update_export_mode_label(self):
        idx = self.export_security_slider.value()
        mode = SECURITY_MODES.get(idx, "Ethical")
        summ = ""
        if mode in ["Ethical", "Unethical", "Grift"]:
            summ = generate_security_summary(mode)
        self.export_mode_label.setText(f"Export Security Mode: {mode}" + (f" - {summ}" if summ else ""))
        self.export_mode_label.setStyleSheet(f"color: {mode_text_color(mode)}; font-weight: bold;")
    
    def load_export_state(self):
        cfg = security_settings.load_security_settings()
        mode = cfg.get("SECURITY_MODE", "Ethical")
        idx = list(SECURITY_MODES.values()).index(mode) if mode in SECURITY_MODES.values() else 0
        self.export_security_slider.setValue(idx)
        if mode == "Custom":
            self.export_customContainer.setVisible(True)
            self.export_uiKeyboard.setChecked(cfg.get("USE_UI_KEYBOARD", False))
            kb_mode = cfg.get("KEYBOARD_BLOCKER_MODE", 1)
            i = 0 if kb_mode == 1 else 1
            self.export_keyboard_blocker.setCurrentIndex(i)
            self.export_mouse_locker.setChecked(cfg.get("ENABLE_MOUSE_LOCKER", False))
            self.export_sleep_blocker.setChecked(cfg.get("ENABLE_SLEEP_BLOCKER", False))
            self.export_security_monitor.setChecked(cfg.get("ENABLE_SECURITY_MONITOR", False))
        else:
            self.export_customContainer.setVisible(False)
        self.update_export_mode_label()
    
    def save_export_state(self):
        idx = self.export_security_slider.value()
        mode = SECURITY_MODES.get(idx, "Ethical")
        cfg = security_settings.load_security_settings()
        cfg["SECURITY_MODE"] = mode
        if mode == "Custom":
            cfg["USE_UI_KEYBOARD"] = self.export_uiKeyboard.isChecked()
            cfg["KEYBOARD_BLOCKER_MODE"] = self.export_keyboard_blocker.currentData()
            cfg["ENABLE_MOUSE_LOCKER"] = self.export_mouse_locker.isChecked()
            cfg["ENABLE_SLEEP_BLOCKER"] = self.export_sleep_blocker.isChecked()
            cfg["ENABLE_SECURITY_MONITOR"] = self.export_security_monitor.isChecked()
        security_settings.save_security_settings(cfg)
    
    def on_export(self):
        name = self.custom_exe_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a custom EXE name.")
            return
        idx = self.export_security_slider.value()
        mode = SECURITY_MODES.get(idx, "Ethical")
        if mode == "Custom":
            opts = {
                "USE_UI_KEYBOARD": self.export_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.export_keyboard_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.export_mouse_locker.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.export_sleep_blocker.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.export_security_monitor.isChecked()
            }
        else:
            _, _, opts = security_settings.set_mode(mode)
        from builder.export import export_exe
        success, summary = export_exe(name, self.project_root, opts, disable_lockdown=False)
        # export_exe shows its own final report.
