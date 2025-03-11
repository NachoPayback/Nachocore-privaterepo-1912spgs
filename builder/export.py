#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import glob
import importlib.util
import shutil
import pprint

# Define PROJECT_ROOT (assuming export.py is in the builder folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Try to import get_data_path from shared/utils/data_helpers; otherwise, define fallback.
try:
    from shared.utils.data_helpers import get_data_path
except ImportError:
    def get_data_path(relative_path):
        return os.path.join(PROJECT_ROOT, relative_path)

from builder.utils import normalize_task_type

# Import the static manifest generator.
from generate_manifest import generate_static_manifest

# Import required PyQt6 widgets
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QPlainTextEdit,
    QPushButton, QHBoxLayout, QLabel
)

def get_hidden_imports(project_root):
    """
    Collect hidden imports for PyInstaller by scanning the shared/tasks folder.
    If running in a frozen state, we load from static_manifest.py instead.
    """
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
                print("DEBUG: Found module '{}' with TASK_TYPE '{}' normalized to '{}'".format(
                    module_name, module.TASK_TYPE, normalized))
                hidden_imports.append(hidden_import)
        except Exception as e:
            print("DEBUG: Error importing {}: {}".format(filename, e))
    # Also include any additional shared modules
    additional = [
        "shared.config",
        "shared.theme.theme",
        "shared.utils.close_button_blocker",
        "shared.utils.keyboard_blocker",
        "shared.utils.mouse_locker",
        "shared.utils.sleep_blocker",
        "shared.utils.security_monitor",
        "shared.utils.logger",
        "shared.utils.ui_keyboard",
    ]
    hidden_imports.extend(additional)
    return hidden_imports

def get_data_files(project_root):
    """
    Returns a list of data files to bundle with the EXE.
    Format: "absolute_path;relative_destination"
    """
    data_files = []
    folders = [
        ("builder/config.json", "builder"),
        ("builder/tasks", "builder/tasks"),
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
                    data_files.append("{};{}".format(full_path, os.path.dirname(rel_path)))
    return data_files

def read_tasks_summary(project_root):
    """
    Reads tasks.json (if it exists) and returns a summary of tasks:
    For each task, it shows the TASK_TYPE and, if available, the question text.
    """
    tasks_file = os.path.join(project_root, "builder", "tasks", "tasks.json")
    summary_lines = []
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, "r") as f:
                tasks = json.load(f)
            if isinstance(tasks, list):
                for idx, task in enumerate(tasks, start=1):
                    task_type = task.get("TASK_TYPE", "Unknown")
                    question = task.get("question", "<no question>")
                    summary_lines.append(f"Task {idx}: Type: {task_type} | Question: {question}")
            else:
                summary_lines.append("Tasks file is not a list.")
        except Exception as e:
            summary_lines.append(f"Error reading tasks.json: {e}")
    else:
        summary_lines.append("tasks.json not found.")
    return "\n".join(summary_lines)

def export_exe(custom_name, project_root, security_options, disable_lockdown=False):
    """
    Main export function that:
    1) Updates config.json with current security settings and gift card.
    2) Generates a static manifest (builder/static_manifest.py).
    3) Builds the EXE with PyInstaller (UPX compression, strip).
    4) Cleans up build artifacts and dist folder.
    5) Shows a single "Export Report" dialog with tasks, gift card, and settings info.
    """
    # 1) Update config.json
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
        return False, f"Error writing config: {e}"
    
    # 2) Generate static manifest
    generate_static_manifest()
    
    # 3) Build the EXE
    game_script = os.path.join(project_root, "game", "game.py")
    hidden_imports = get_hidden_imports(project_root)
    data_files = get_data_files(project_root)
    
    export_dir = os.path.join(project_root, "exported")
    os.makedirs(export_dir, exist_ok=True)
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--strip",
        "--upx-dir", "C:/upx",  # Adjust if UPX is in your PATH or remove if not needed
        "--name", custom_name,
        "--paths", project_root,
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    for df in data_files:
        cmd.extend(["--add-data", df])
    cmd.append(game_script)
    
    print("DEBUG: Running PyInstaller with command:")
    print(" ".join(cmd))
    
    try:
        # On Windows, we can avoid extra console windows by using CREATE_NO_WINDOW
        creationflags = 0
        if sys.platform.startswith("win"):
            import subprocess
            creationflags = subprocess.CREATE_NO_WINDOW
        
        result = subprocess.run(
            cmd, check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags
        )
        
        # Build the final report
        report = "Export Report:\n\n"
        try:
            from builder.static_manifest import TASK_MANIFEST
            report += "Imported Task Types (TASK_MANIFEST):\n" + pprint.pformat(TASK_MANIFEST) + "\n\n"
        except Exception as e:
            report += f"Error loading TASK_MANIFEST: {e}\n\n"
        try:
            from builder.static_manifest import GIFT_CARD_STATIC
            report += "Burned-In Gift Card (GIFT_CARD_STATIC):\n" + pprint.pformat(GIFT_CARD_STATIC) + "\n\n"
        except Exception as e:
            report += f"Error loading GIFT_CARD_STATIC: {e}\n\n"
        try:
            from builder.static_manifest import SECURITY_SETTINGS_STATIC
            report += "Security Settings (SECURITY_SETTINGS_STATIC):\n" + pprint.pformat(SECURITY_SETTINGS_STATIC) + "\n\n"
        except Exception as e:
            report += f"Error loading SECURITY_SETTINGS_STATIC: {e}\n\n"
        
        tasks_summary = read_tasks_summary(project_root)
        report += "Exported Tasks Summary:\n" + tasks_summary + "\n\n"
        
        # 4) Cleanup build artifacts
        final_exe = custom_name + ".exe"
        dist_dir = os.path.join(project_root, "dist")
        build_dir = os.path.join(project_root, "build")
        spec_file = os.path.join(project_root, custom_name + ".spec")
        source_exe = os.path.join(dist_dir, final_exe)
        destination_exe = os.path.join(export_dir, final_exe)
        
        if os.path.exists(source_exe):
            shutil.move(source_exe, destination_exe)
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(spec_file):
            os.remove(spec_file)
        
        # 5) Show a single "Export Report" dialog
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Optional: load your style sheet
        stylesheet_path = os.path.join(PROJECT_ROOT, "shared", "theme", "styles.qss")
        stylesheet = ""
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, "r") as f:
                stylesheet = f.read()
        
        dialog = QDialog()
        dialog.setWindowTitle("Export Report")
        if stylesheet:
            dialog.setStyleSheet(stylesheet)
        
        layout = QVBoxLayout(dialog)
        header_label = QLabel("Export Successful!")
        layout.addWidget(header_label)
        
        text_box = QPlainTextEdit()
        text_box.setPlainText(report)
        text_box.setReadOnly(True)
        layout.addWidget(text_box)
        
        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copy Report")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(report))
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.resize(600, 400)
        dialog.exec()
        
        # Return success
        return True, result.stdout
    
    except subprocess.CalledProcessError as e:
        return False, f"PyInstaller error: {e.stderr}"

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
    success, output = export_exe("ScammerPaybackGame", PROJECT_ROOT, security_opts, disable_lockdown=False)
    if success:
        print("Export successful!")
    else:
        print("Export failed:", output)
