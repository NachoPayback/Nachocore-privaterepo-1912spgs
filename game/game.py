#!/usr/bin/env python3
import os
import sys

# Ensure the project root (parent directory) is in sys.path.
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(current_dir, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Safeguard for importing shared modules.
try:
    from shared.utils.data_helpers import get_data_path
except ImportError as e:
    # Attempt to re-add PROJECT_ROOT and try again.
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    try:
        from shared.utils.data_helpers import get_data_path
    except ImportError as e:
        print("Failed to import shared.utils.data_helpers:", e)
        sys.exit(1)

import json
import importlib
import glob
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent, QObject

# --- Dynamic Security Settings Loader ---
CONFIG_PATH = os.path.join(PROJECT_ROOT, "builder", "config.json")

def load_security_settings():
    # Defaults: Disable lockdown features for testing.
    defaults = {
        "USE_UI_KEYBOARD": True,
        "KEYBOARD_BLOCKER_MODE": 1,
        "ENABLE_MOUSE_LOCKER": False,       # Disabled by default.
        "ENABLE_SLEEP_BLOCKER": False,        # Disabled by default.
        "ENABLE_SECURITY_MONITOR": False,     # Disabled by default.
        "CLOSE_BUTTON_DISABLED": False,       # Disabled by default.
        "ENABLE_LOGGER": True
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                defaults.update(config)
        except Exception as e:
            print("Error reading config.json:", e)
    return defaults

settings = load_security_settings()
USE_UI_KEYBOARD = settings["USE_UI_KEYBOARD"]
KEYBOARD_BLOCKER_MODE = settings["KEYBOARD_BLOCKER_MODE"]
ENABLE_MOUSE_LOCKER = settings["ENABLE_MOUSE_LOCKER"]
ENABLE_SLEEP_BLOCKER = settings["ENABLE_SLEEP_BLOCKER"]
ENABLE_SECURITY_MONITOR = settings["ENABLE_SECURITY_MONITOR"]
CLOSE_BUTTON_DISABLED = settings["CLOSE_BUTTON_DISABLED"]
ENABLE_LOGGER = settings["ENABLE_LOGGER"]
# --- End Dynamic Loader ---

from shared.utils.close_button_blocker import disable_close_button, enable_close_button
from shared.utils.keyboard_blocker import start_keyboard_blocker, stop_keyboard_blocker
from shared.utils.mouse_locker import start_mouse_locker, stop_mouse_locker
from shared.utils.sleep_blocker import start_sleep_blocker, stop_sleep_blocker
from shared.utils.security_monitor import start_security_monitor, stop_security_monitor
from shared.utils.logger import log_event
from shared.utils.ui_keyboard import UIKeyboardWidget
from shared.theme.theme import load_stylesheet

# Use get_data_path() to locate tasks.json.
TASKS_FILE = get_data_path(os.path.join("builder", "tasks", "tasks.json"))

def load_all_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            data = json.load(f)
            # Convert any legacy "type" key to "TASK_TYPE"
            if isinstance(data, list):
                for task in data:
                    if "type" in task:
                        task["TASK_TYPE"] = task.pop("type")
                return data
            else:
                return []
    except Exception as e:
        if ENABLE_LOGGER:
            log_event(f"Error reading tasks file: {e}")
        return []

def discover_task_modules():
    task_modules = {}
    tasks_folder = get_data_path(os.path.join("shared", "tasks"))
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
                task_modules[module.TASK_TYPE] = f"shared.tasks.{module_name}"
        except Exception as e:
            if ENABLE_LOGGER:
                log_event(f"Error importing {filename}: {e}")
    return task_modules

currentLineEdit = None

class UIKeyboardEventFilter(QObject):
    def __init__(self, line_edit, keyboard_widget):
        super().__init__(line_edit)
        self.line_edit = line_edit
        self.keyboard_widget = keyboard_widget
    def eventFilter(self, obj, event):
        global currentLineEdit
        if event.type() == QEvent.Type.FocusIn:
            currentLineEdit = self.line_edit
        return False

def install_ui_keyboard(widget, keyboard_widget):
    for le in widget.findChildren(QLineEdit):
        le.installEventFilter(UIKeyboardEventFilter(le, keyboard_widget))
        le.setReadOnly(USE_UI_KEYBOARD)
        le.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    le_list = widget.findChildren(QLineEdit)
    if le_list:
        le_list[0].setFocus()

class GameUI(QMainWindow):
    def __init__(self):
        super().__init__()
        if CLOSE_BUTTON_DISABLED:
            disable_close_button(self)
        self.setGeometry(100, 100, 800, 600)
        if ENABLE_LOGGER:
            log_event("Game starting up...")
        self.tasks = load_all_tasks()
        if ENABLE_LOGGER:
            log_event(f"Loaded tasks: {self.tasks}")
        self.current_task_index = 0
        self.discovered_tasks = discover_task_modules()
        self.gift_card = self.load_gift_card_from_config()
        self.keyboard_blocker = None
        if KEYBOARD_BLOCKER_MODE in (1, 2):
            self.keyboard_blocker = start_keyboard_blocker(mode=KEYBOARD_BLOCKER_MODE)
            if ENABLE_LOGGER:
                log_event(f"Keyboard blocker started (mode={KEYBOARD_BLOCKER_MODE}).")
        self.mouse_locker_timer = None
        if ENABLE_MOUSE_LOCKER:
            self.mouse_locker_timer = start_mouse_locker(self)
            if ENABLE_LOGGER:
                log_event("Mouse locker started.")
        if ENABLE_SLEEP_BLOCKER:
            start_sleep_blocker()
            if ENABLE_LOGGER:
                log_event("Sleep blocker started.")
        if ENABLE_SECURITY_MONITOR:
            start_security_monitor()
            if ENABLE_LOGGER:
                log_event("Security monitor started.")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        # Load stylesheet from bundled data.
        stylesheet_path = get_data_path(os.path.join("shared", "theme", "styles.qss"))
        if os.path.exists(stylesheet_path):
            try:
                with open(stylesheet_path, "r") as f:
                    stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
            except Exception as e:
                if ENABLE_LOGGER:
                    log_event(f"Error loading stylesheet: {e}")
        self.progress_label = QLabel("Gift Card Progress: 0%")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.progress_label)
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.layout.addWidget(self.task_container)
        self.ui_keyboard = UIKeyboardWidget(self)
        self.ui_keyboard.hide()
        self.ui_keyboard.keyPressed.connect(self.on_keyboard_key_pressed)
        self.layout.addWidget(self.ui_keyboard)
        self.load_next_task()
        self.center_window()

    def load_gift_card_from_config(self):
        config_file = get_data_path(os.path.join("builder", "config.json"))
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
                gift = config_data.get("selected_gift_card", {})
                return {
                    "code": gift.get("code", "XXXX-XXXX-XXXX"),
                    "pin": gift.get("pin", "----"),
                    "type": gift.get("name", "Gift Card"),
                    "pin_required": gift.get("pin_required", True)
                }
        except Exception as e:
            if ENABLE_LOGGER:
                log_event(f"Error loading gift card config: {e}")
            return {"code": "XXXX-XXXX-XXXX", "pin": "----", "type": "Gift Card", "pin_required": True}

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def load_next_task(self):
        # Clear current task widget.
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if self.current_task_index < len(self.tasks):
            task_data = self.tasks[self.current_task_index]
            # Updated to use "TASK_TYPE" instead of "type"
            task_type = task_data.get("TASK_TYPE", "Short Answer")
            module_import = self.discovered_tasks.get(task_type)
            if module_import:
                try:
                    module = importlib.import_module(module_import)
                    task_instance = module.Task()
                    if hasattr(task_instance, "set_task_data"):
                        try:
                            task_instance.set_task_data(task_data)
                        except Exception as e:
                            if ENABLE_LOGGER:
                                log_event(f"Error applying saved data for {task_type}: {e}")
                    task_widget = task_instance.get_widget(self.task_finished)
                    self.task_layout.addWidget(task_widget)
                    install_ui_keyboard(task_widget, self.ui_keyboard)
                    if task_widget.findChildren(QLineEdit):
                        self.ui_keyboard.show()
                    else:
                        self.ui_keyboard.hide()
                    self.update_gift_card_reveal()
                except Exception as e:
                    if ENABLE_LOGGER:
                        log_event(f"Error loading task: {e}")
                    error_label = QLabel(f"Error loading task: {e}")
                    self.task_layout.addWidget(error_label)
            else:
                if ENABLE_LOGGER:
                    log_event(f"Task type '{task_type}' not discovered.")
                error_label = QLabel(f"Task type '{task_type}' not found.")
                self.task_layout.addWidget(error_label)
        else:
            self.complete_game()

    def on_keyboard_key_pressed(self, key):
        global currentLineEdit
        if currentLineEdit:
            current_text = currentLineEdit.text()
            if key == "BACKSPACE":
                currentLineEdit.setText(current_text[:-1])
            else:
                currentLineEdit.setText(current_text + key)

    def task_finished(self, success):
        if success:
            self.current_task_index += 1
            self.update_progress()
            self.load_next_task()
        else:
            if ENABLE_LOGGER:
                log_event("Task finished with incorrect answer.")

    def update_progress(self):
        if self.tasks:
            progress = int((self.current_task_index / len(self.tasks)) * 100)
        else:
            progress = 0
        self.progress_label.setText(f"Gift Card Progress: {progress}%")
        self.update_gift_card_reveal()

    def update_gift_card_reveal(self):
        full_code = self.gift_card["code"]
        total = len(full_code)
        if self.tasks:
            fraction = self.current_task_index / len(self.tasks)
        else:
            fraction = 1
        revealed = int(total * fraction)
        visible = full_code[:revealed]
        hidden = ''.join(ch if ch == '-' else '█' for ch in full_code[revealed:])
        self.progress_label.setText(f"Gift Card Code: {visible}{hidden}  ({int(fraction*100)}%)")

    def complete_game(self):
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.ui_keyboard.hide()
        self.layout.removeWidget(self.progress_label)
        self.progress_label.deleteLater()
        if CLOSE_BUTTON_DISABLED:
            from shared.utils.close_button_blocker import enable_close_button
            enable_close_button(self)
        final_text = f"Gift Card Type: {self.gift_card['type']}\nCode: {self.gift_card['code']}"
        if self.gift_card.get("pin_required", True):
            final_text += f"\nPIN: {self.gift_card['pin']}"
        final_label = QLabel(f"Congratulations! You've completed the game.\n{final_text}")
        final_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(final_label)
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        self.layout.addWidget(exit_button)
        self.unlock_system()
        if ENABLE_LOGGER:
            log_event("Game completed successfully.")

    def unlock_system(self):
        if self.keyboard_blocker:
            stop_keyboard_blocker(self.keyboard_blocker)
        if self.mouse_locker_timer:
            stop_mouse_locker()
        if ENABLE_SLEEP_BLOCKER:
            stop_sleep_blocker()
        if ENABLE_SECURITY_MONITOR:
            stop_security_monitor()

    def closeEvent(self, event):
        self.unlock_system()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = GameUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
