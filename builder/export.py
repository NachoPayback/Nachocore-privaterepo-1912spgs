#!/usr/bin/env python3
"""
Export Module for Nachocore Builder

This module updates config.json, generates a static manifest,
and exports the game as a standalone executable via PyInstaller.
It cleans up build artifacts (including __pycache__ directories)
and shows a styled QDialog summarizing:
  - Security Settings,
  - Discovered Task Types,
  - Imported Task List.
The final EXE is placed in the 'exported' folder.
"""

import os
import sys
import json
import subprocess
import glob
import importlib.util
import shutil
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Set PROJECT_ROOT (assuming export.py is in the builder folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from shared.utils.data_helpers import get_data_path
except ImportError:
    def get_data_path(relative_path):
        return os.path.join(PROJECT_ROOT, relative_path)

from builder.utils import normalize_task_type

# CHANGED: import from generate_manifest in the parent folder
from generate_manifest import generate_static_manifest

# Helper to center dialogs
def center_dialog(dialog):
    from PyQt6.QtWidgets import QApplication
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    dialog_geometry = dialog.frameGeometry()
    dialog_geometry.moveCenter(screen_geometry.center())
    dialog.move(dialog_geometry.topLeft())

def get_hidden_imports(project_root):
    hidden_imports = [
        "game.game_ui",
        "game.game_logic",
        "shared.config",
        "shared.theme.theme",
        "shared.security.close_button_blocker_security",
        "shared.security.keyboard_blocker_security",
        "shared.security.mouse_locker_security",
        "shared.security.sleep_blocker_security",
        "shared.security.security_monitor_security",
        "shared.utils.logger",
        "shared.utils.ui_keyboard",
        "builder.static_manifest",  # Ensure PyInstaller includes static_manifest
    ]
    tasks_folder = os.path.join(get_data_path("shared/tasks"))
    for filepath in glob.glob(os.path.join(tasks_folder, "*.py")):
        filename = os.path.basename(filepath)
        if filename == "__init__.py":
            continue
        module_name = os.path.splitext(filename)[0]
        hidden_imports.append(f"shared.tasks.{module_name}")
    return hidden_imports

def get_data_files(project_root):
    data_files = []
    folders = [
        ("builder/config.json", "builder"),
        ("builder/data", "builder/data"),
        ("shared/theme", "shared/theme"),
        ("builder/data/gift_cards", "builder/data/gift_cards")
    ]
    for src_rel, dest_rel in folders:
        src_abs = os.path.join(project_root, src_rel)
        if not os.path.exists(src_abs):
            continue
        for root, _, files in os.walk(src_abs):
            for f in files:
                if f.lower().endswith((".json", ".qss")):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, project_root)
                    data_files.append(f"{full_path};{os.path.dirname(rel_path)}")
    return data_files

def cleanup_artifacts(project_root):
    for folder in ["build", "dist"]:
        folder_path = os.path.join(project_root, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    for file in os.listdir(project_root):
        if file.endswith(".spec"):
            os.remove(os.path.join(project_root, file))
    from builder.cleanup import clean_pycache
    clean_pycache(project_root)

def build_export_summary(project_root):
    lines = []
    from builder.security_settings import load_security_settings
    sec_settings = load_security_settings()
    mode = sec_settings.get("SECURITY_MODE", "Ethical")
    lines.append(f"Security Mode: {mode}")
    lines.append(f"UI Keyboard: {sec_settings.get('USE_UI_KEYBOARD', False)}")
    lines.append(f"Keyboard Blocker: {sec_settings.get('KEYBOARD_BLOCKER_MODE', 0)}")
    lines.append(f"Mouse Locker: {sec_settings.get('ENABLE_MOUSE_LOCKER', False)}")
    lines.append(f"Sleep Blocker: {sec_settings.get('ENABLE_SLEEP_BLOCKER', False)}")
    lines.append(f"Security Monitor: {sec_settings.get('ENABLE_SECURITY_MONITOR', False)}")
    lines.append(f"Close Button Disabled: {sec_settings.get('CLOSE_BUTTON_DISABLED', False)}")
    lines.append(f"Logger: {sec_settings.get('ENABLE_LOGGER', False)}")
    
    from builder.task_builder import discover_task_modules, display_task_type
    task_modules = discover_task_modules()
    lines.append("\n=== Discovered Task Types ===")
    if task_modules:
        for key, module in task_modules.items():
            friendly = display_task_type(key)
            lines.append(f"  • {friendly}: {module}")
    else:
        lines.append("  (No task types found)")
    
    tasks_file = get_data_files(project_root)
    tasks_file = get_data_path(os.path.join("builder", "data", "tasks.json"))
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except Exception as e:
        tasks = []
        lines.append(f"Error reading tasks.json: {e}")
    lines.append("\n=== Task List Imported ===")
    if tasks:
        for i, task in enumerate(tasks, 1):
            from builder.utils import display_task_type
            friendly = display_task_type(task.get("TASK_TYPE", "unknown"))
            question = task.get("question", "No question provided – default.")
            lines.append(f"  {i}. Type: {friendly}")
            lines.append(f"       Question: {question}")
    else:
        lines.append("  (No tasks found)")
    
    return "\n".join(lines)

def show_export_readout(success, summary):
    dialog = QDialog()
    dialog.setWindowTitle("Export Report")
    layout = QVBoxLayout(dialog)
    
    status_text = "Build Successful!" if success else "Build Failed!"
    status_label = QLabel(status_text)
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
    layout.addWidget(status_label)
    
    report_edit = QTextEdit()
    report_edit.setReadOnly(True)
    report_edit.setPlainText(summary)
    report_edit.setMinimumHeight(300)
    layout.addWidget(report_edit)
    
    button_layout = QHBoxLayout()
    copy_button = QPushButton("Copy Report")
    copy_button.clicked.connect(lambda: QApplication.clipboard().setText(summary))
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    button_layout.addWidget(copy_button)
    button_layout.addWidget(close_button)
    layout.addLayout(button_layout)
    
    from shared.theme.theme import load_stylesheet
    global_stylesheet = load_stylesheet("shared/theme/styles.qss")
    if global_stylesheet:
        dialog.setStyleSheet(global_stylesheet)
    
    dialog.resize(800, 600)
    center_dialog(dialog)  # center the dialog on the screen
    dialog.exec()

def export_exe(custom_name, project_root, security_options, disable_lockdown=False):
    config_path = os.path.join(project_root, "builder", "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}
    except Exception as e:
        config = {}
        print("DEBUG: Error reading config.json:", e)
    config.update(security_options)
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        return False, f"Error writing config: {e}"
    
    generate_static_manifest()
    
    from builder.security_settings import load_security_settings, set_mode
    current_settings = load_security_settings()
    if current_settings.get("SECURITY_MODE") == "Grift":
        success_mode, msg, updated = set_mode("Grift")
        current_settings = updated
    
    from shared.theme.theme import load_stylesheet
    styled_sheet = load_stylesheet("shared/theme/styles.qss")
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Confirm Security Settings")
    msg_box.setText(
        f"Please confirm the following security settings before export:\n\n"
        f"Security Mode: {current_settings.get('SECURITY_MODE', 'Ethical')}\n"
        f"UI Keyboard: {current_settings.get('USE_UI_KEYBOARD', False)}\n"
        f"Keyboard Blocker: {current_settings.get('KEYBOARD_BLOCKER_MODE', 0)}\n"
        f"Mouse Locker: {current_settings.get('ENABLE_MOUSE_LOCKER', False)}\n"
        f"Sleep Blocker: {current_settings.get('ENABLE_SLEEP_BLOCKER', False)}\n"
        f"Security Monitor: {current_settings.get('ENABLE_SECURITY_MONITOR', False)}\n"
        f"Close Button Disabled: {current_settings.get('CLOSE_BUTTON_DISABLED', False)}\n"
        f"Logger: {current_settings.get('ENABLE_LOGGER', False)}\n\n"
        "Do you wish to proceed?"
    )
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if styled_sheet:
        msg_box.setStyleSheet(styled_sheet)
    center_dialog(msg_box)
    confirmation = msg_box.exec()
    if confirmation != QMessageBox.StandardButton.Yes:
        return False, "Export cancelled by user."
    
    game_script = os.path.join(project_root, "game", "game.py")
    if not os.path.exists(game_script):
        error_msg = f"Main game script not found at: {game_script}"
        print("DEBUG:", error_msg)
        return False, error_msg
    
    hidden_imports = get_hidden_imports(project_root)
    data_files = get_data_files(project_root)
    
    export_dir = os.path.join(project_root, "exported")
    os.makedirs(export_dir, exist_ok=True)
    
    upx_dir = os.path.join(project_root, "upx")
    upx_flag = []
    if os.path.isdir(upx_dir):
        upx_flag = ["--upx-dir", upx_dir]
    else:
        print("DEBUG: UPX directory not found, skipping UPX optimization.")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--strip",
        "--distpath", export_dir,
        "--name", custom_name,
        "--paths", project_root,
    ] + upx_flag
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    for df in data_files:
        cmd.extend(["--add-data", df])
    cmd.append(game_script)
    
    print("DEBUG: Running PyInstaller with command:")
    print(" ".join(cmd))
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cleanup_artifacts(project_root)
        summary_report = build_export_summary(project_root)
        show_export_readout(True, summary_report)
        return True, summary_report
    except subprocess.CalledProcessError as e:
        summary_report = build_export_summary(project_root)
        show_export_readout(False, summary_report)
        return False, summary_report
    except Exception as e:
        summary_report = build_export_summary(project_root)
        show_export_readout(False, summary_report)
        return False, str(e)

if __name__ == "__main__":
    security_opts = {
        "ENABLE_SECURITY_MONITOR": True,
        "ENABLE_MOUSE_LOCKER": True,
        "ENABLE_SLEEP_BLOCKER": True,
        "CLOSE_BUTTON_DISABLED": True,
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "SECURITY_MODE": "Ethical",
        "selected_gift_card": {
            "name": "Google Play",
            "code": "8NDU-HRZ6-SUCZ-RQRF",
            "pin": "4261",
            "pin_required": True
        }
    }
    success, summary = export_exe("ScammerPaybackGame", PROJECT_ROOT, security_opts, disable_lockdown=False)
    if success:
        print("Export successful!")
    else:
        print("Export failed:", summary)
