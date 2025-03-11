# builder/ui/export_tab.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QPlainTextEdit
)
from PyQt6.QtCore import Qt
from builder import security_settings

# Security mode mappings.
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

def generate_security_summary_for_export():
    """
    Generate a plain-English summary of the current security settings
    for display in the Export tab. This summary excludes any gift card data.
    """
    settings = security_settings.load_security_settings()
    # Remove gift card info if present.
    settings.pop("selected_gift_card", None)
    lines = []
    for key, value in settings.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)

class ExportTab(QWidget):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Executable name input.
        layout.addWidget(QLabel("Enter Custom EXE Name:"))
        self.custom_exe_name = QLineEdit()
        self.custom_exe_name.setPlaceholderText("e.g., ScammerPaybackGame")
        layout.addWidget(self.custom_exe_name)
        
        # Reminder label.
        reminder_label = QLabel("Please verify your security settings in the 'Security Mode' tab before exporting.")
        reminder_label.setWordWrap(True)
        reminder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(reminder_label)
        
        # Active Security Settings Summary.
        layout.addWidget(QLabel("Current Security Settings:"))
        self.security_summary = QPlainTextEdit()
        self.security_summary.setReadOnly(True)
        layout.addWidget(self.security_summary)
        self.update_security_summary()
        
        # Export button.
        export_btn = QPushButton("Export to EXE")
        export_btn.clicked.connect(self.on_export)
        layout.addWidget(export_btn)
    
    def update_security_summary(self):
        """
        Read the current security settings from configuration and update
        the read-only summary text.
        """
        summary = generate_security_summary_for_export()
        self.security_summary.setPlainText(summary)
    
    def on_export(self):
        name = self.custom_exe_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a custom EXE name.")
            return
        # Force an update of the security summary before export.
        self.update_security_summary()
        # Retrieve security options from the config (which are set via the dedicated security tab).
        # Here we pass an empty dict; export_exe will read from the config.
        from builder.export import export_exe
        success, summary_report = export_exe(name, self.project_root, security_options={}, disable_lockdown=False)
        # export_exe shows its own final report.
