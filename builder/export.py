#!/usr/bin/env python3
"""
Export Module for Nachocore Builder

This module updates configuration files, generates a static manifest,
and exports the game as a standalone executable via PyInstaller.
It includes optimization flags (--strip and --upx-dir), cleans up build artifacts,
and shows a final export report that summarizes:
  - Discovered task types,
  - Security settings,
  - And the task list.
The report is displayed in plain English, styled to fit our hacker/Cyberpunk/Synthwave aesthetic.
"""

import os
import sys
import json
import subprocess
import glob
import importlib.util
import shutil

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QApplication
)
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
from generate_manifest import generate_static_manifest

def get_hidden_imports(project_root):
    if getattr(sys, "frozen", False):
        try:
            from builder.static_manifest import TASK_MANIFEST
            print("DEBUG: Frozen state. Using TASK_MANIFEST:", TASK_MANIFEST)
            return list(TASK_MANIFEST.values())
        except Exception as e:
            print("DEBUG: Error importing TASK_MANIFEST:", e)
            return []
    hidden_imports = []
    tasks_folder = os.path.join(get_data_path("shared/tasks"))
    for filepath in glob.glob(os.path.join(tasks_folder, "*.py")):
        filename = os.path.basename(filepath)
        if filename == "__init__.py":
            continue
        module_name = os.path.splitext(filename)[0]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "TASK_TYPE"):
                normalized = normalize_task_type(module.TASK_TYPE)
                hidden_import = f"shared.tasks.{module_name}"
                print(f"DEBUG: Found module '{module_name}' with TASK_TYPE '{module.TASK_TYPE}' normalized to '{normalized}'")
                hidden_imports.append(hidden_import)
        except Exception as e:
            print(f"DEBUG: Error importing {filename}: {e}")
    additional = [
        "shared.config",
        "shared.theme.theme",
        "shared.security.close_button_blocker_security",
        "shared.security.keyboard_blocker_security",
        "shared.security.mouse_locker_security",
        "shared.security.sleep_blocker_security",
        "shared.security.security_monitor_security",
        "shared.utils.logger",
        "shared.utils.ui_keyboard",
    ]
    hidden_imports.extend(additional)
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
            print(f"DEBUG: Removed folder {folder_path}")
    for file in os.listdir(project_root):
        if file.endswith(".spec"):
            os.remove(os.path.join(project_root, file))
            print(f"DEBUG: Removed spec file {file}")

def build_export_summary(project_root):
    lines = []
    # --- Discovered Task Types ---
    from builder.task_builder import discover_task_modules, display_task_type
    task_modules = discover_task_modules()
    lines.append("=== Discovered Task Types ===")
    if task_modules:
        for key, module in task_modules.items():
            friendly = display_task_type(key)
            lines.append(f"  • {friendly}: {module}")
    else:
        lines.append("  (No task types found)")
    
    # --- Security Settings (excluding selected gift card) ---
    from builder.security_settings import load_security_settings
    sec_settings = load_security_settings()
    sec_settings.pop("selected_gift_card", None)
    lines.append("\n=== Security Settings ===")
    if sec_settings:
        for key, value in sec_settings.items():
            lines.append(f"  {key}: {value}")
    else:
        lines.append("  (No security settings found)")
    
    # --- Task List Imported ---
    tasks_file = get_data_path(os.path.join("builder", "data", "tasks.json"))
    try:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)
    except Exception as e:
        tasks = []
        lines.append(f"Error reading tasks.json: {e}")
    lines.append("\n=== Task List Imported ===")
    if tasks:
        for i, task in enumerate(tasks, 1):
            task_type = task.get("TASK_TYPE", "unknown")
            from builder.utils import display_task_type
            friendly_type = display_task_type(task_type)
            question = task.get("question", "No question provided – default functionality.")
            lines.append(f"  {i}. Type: {friendly_type}")
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
    report_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    layout.addWidget(report_edit)
    
    button_layout = QHBoxLayout()
    copy_button = QPushButton("Copy Report")
    copy_button.clicked.connect(lambda: QApplication.clipboard().setText(summary))
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    button_layout.addWidget(copy_button)
    button_layout.addWidget(close_button)
    layout.addLayout(button_layout)
    
    dialog.resize(800, 600)
    dialog.exec()

def export_exe(custom_name, project_root, security_options, disable_lockdown=False):
    config_path = os.path.join(project_root, "builder", "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}
    except Exception as e:
        print("DEBUG: Error reading config.json:", e)
        config = {}
    config.update(security_options)
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        return False, "Error writing config: {}".format(e)
    
    generate_static_manifest()
    
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
        output = result.stdout + "\n" + result.stderr
        cleanup_artifacts(project_root)
        summary_report = build_export_summary(project_root)
        show_export_readout(True, summary_report)
        return True, summary_report
    except subprocess.CalledProcessError as e:
        output = e.stdout + "\n" + e.stderr
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
