# game/game_ui.py
import os, sys, json, importlib, glob, shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QPlainTextEdit, QMessageBox, QHBoxLayout, QDialog
)
from PyQt6.QtCore import Qt, QEvent, QObject, QTimer
from shared.theme.theme import load_stylesheet
from shared.utils.data_helpers import get_data_path
from game_logic import GameLogic

# Import security and utility modules.
from shared.security.close_button_blocker_security import disable_close_button, enable_close_button
from shared.security.keyboard_blocker_security import start_keyboard_blocker, stop_keyboard_blocker
from shared.security.mouse_locker_security import start_mouse_locker, stop_mouse_locker
from shared.security.sleep_blocker_security import start_sleep_blocker, stop_sleep_blocker
from shared.security.security_monitor_security import start_security_monitor, stop_security_monitor
from shared.utils.logger import log_event
from shared.utils.ui_keyboard import UIKeyboardWidget

# Global variable for UIKeyboard event filtering.
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
        le.setReadOnly(True)
        le.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    le_list = widget.findChildren(QLineEdit)
    if le_list:
        le_list[0].setFocus()

class GameUI(QMainWindow):
    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root
        from builder.security_settings import load_security_settings
        self.security_settings = load_security_settings()
        if self.security_settings.get("CLOSE_BUTTON_DISABLED", False):
            disable_close_button(self)
        self.setGeometry(100, 100, 800, 600)
        log_event("Game starting up...")
        self.logic = GameLogic(project_root)
        self.logic.load_all_tasks()
        self.current_task_index = 0
        self.logic.discover_task_modules()
        self.gift_card = self.logic.load_gift_card_from_config()
        self.keyboard_blocker = None
        if self.security_settings.get("KEYBOARD_BLOCKER_MODE", 1) in (1,2):
            self.keyboard_blocker = start_keyboard_blocker(mode=self.security_settings.get("KEYBOARD_BLOCKER_MODE", 1))
            log_event(f"Keyboard blocker started (mode={self.security_settings.get('KEYBOARD_BLOCKER_MODE', 1)}).")
        self.mouse_locker_timer = None
        if self.security_settings.get("ENABLE_MOUSE_LOCKER", False):
            self.mouse_locker_timer = start_mouse_locker(self)
            log_event("Mouse locker started.")
        if self.security_settings.get("ENABLE_SLEEP_BLOCKER", False):
            start_sleep_blocker()
            log_event("Sleep blocker started.")
        if self.security_settings.get("ENABLE_SECURITY_MONITOR", False):
            start_security_monitor()
            log_event("Security monitor started.")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        stylesheet_path = get_data_path(os.path.join("shared", "theme", "styles.qss"))
        if os.path.exists(stylesheet_path):
            try:
                with open(stylesheet_path, "r") as f:
                    stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
            except Exception as e:
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
    
    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        center = screen_geometry.center()
        window_geometry.moveCenter(center)
        self.move(window_geometry.topLeft())
    
    def load_next_task(self):
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if self.current_task_index < len(self.logic.tasks):
            task_data = self.logic.tasks[self.current_task_index]
            task_type = task_data.get("TASK_TYPE", "short_answer")
            module_import = self.logic.discovered_tasks.get(task_type)
            if module_import:
                try:
                    module = importlib.import_module(module_import)
                    task_instance = module.Task()
                    if hasattr(task_instance, "set_task_data"):
                        try:
                            task_instance.set_task_data(task_data)
                        except Exception as ex:
                            log_event(f"Error applying saved data for {task_type}: {ex}")
                    task_widget = task_instance.get_widget(self.task_finished)
                    self.task_layout.addWidget(task_widget)
                    install_ui_keyboard(task_widget, self.ui_keyboard)
                    if task_widget.findChildren(QLineEdit):
                        self.ui_keyboard.show()
                    else:
                        self.ui_keyboard.hide()
                    self.update_gift_card_reveal()
                except Exception as e:
                    log_event(f"Error loading task: {e}")
                    error_label = QLabel(f"Error loading task: {e}")
                    self.task_layout.addWidget(error_label)
            else:
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
            log_event("Task finished with incorrect answer.")
    
    def update_progress(self):
        if self.logic.tasks:
            progress = int((self.current_task_index / len(self.logic.tasks)) * 100)
        else:
            progress = 0
        self.progress_label.setText(f"Gift Card Progress: {progress}%")
        self.update_gift_card_reveal()
    
    def update_gift_card_reveal(self):
        full_code = self.gift_card.get("code", "XXXX-XXXX-XXXX")
        total = len(full_code)
        fraction = self.current_task_index / len(self.logic.tasks) if self.logic.tasks else 1
        revealed = int(total * fraction)
        visible = full_code[:revealed]
        hidden = "".join(ch if ch == '-' else '█' for ch in full_code[revealed:])
        self.progress_label.setText(f"Gift Card Code: {visible}{hidden}  ({int(fraction*100)}%)")
    
    def complete_game(self):
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.ui_keyboard.hide()
        self.layout.removeWidget(self.progress_label)
        self.progress_label.deleteLater()
        from shared.security.close_button_blocker_security import enable_close_button
        if self.security_settings.get("CLOSE_BUTTON_DISABLED", False):
            enable_close_button(self)
        try:
            gift_type = self.gift_card.get("name", "Gift Card")
            code = self.gift_card.get("code", "XXXX-XXXX-XXXX")
            pin_required = self.gift_card.get("pin_required", True)
            pin = self.gift_card.get("pin", "----")
            final_text = f"Gift Card Type: {gift_type}\nCode: {code}"
            if pin_required:
                final_text += f"\nPIN: {pin}"
        except Exception as e:
            print("DEBUG: Error constructing final gift card text:", e)
            final_text = "Error reading gift card data."
        final_label = QLabel(f"Congratulations! You've completed the game.\n{final_text}")
        final_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(final_label)
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        self.layout.addWidget(exit_btn)
        self.unlock_system()
        log_event("Game completed successfully.")
    
    def unlock_system(self):
        from shared.security.keyboard_blocker_security import stop_keyboard_blocker
        from shared.security.mouse_locker_security import stop_mouse_locker
        from shared.security.sleep_blocker_security import stop_sleep_blocker
        from shared.security.security_monitor_security import stop_security_monitor
        if self.keyboard_blocker:
            stop_keyboard_blocker(self.keyboard_blocker)
        if self.mouse_locker_timer:
            stop_mouse_locker()
        if self.security_settings.get("ENABLE_SLEEP_BLOCKER", False):
            stop_sleep_blocker()
        if self.security_settings.get("ENABLE_SECURITY_MONITOR", False):
            stop_security_monitor()
    
    def closeEvent(self, event):
        self.unlock_system()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = GameUI(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
