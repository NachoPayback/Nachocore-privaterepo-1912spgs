# game/game_ui.py
import os
import sys
import importlib
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.theme.theme import load_stylesheet
from shared.utils.data_helpers import get_data_path
from shared.animations import apply_glow_effect  # Example animation function
from shared.utils.logger import log_event
from shared.utils.ui_keyboard import UIKeyboardWidget

# Original local logic imports remain intact.
from game.game_logic import (
    load_security_settings,
    load_all_tasks,
    discover_task_modules,
    load_gift_card
)

currentLineEdit = None  # Global reference for on-screen keyboard events

class GameUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load security settings from game_logic.
        sec_settings = load_security_settings()
        if sec_settings.get("CLOSE_BUTTON_DISABLED", False):
            from shared.security.close_button_blocker_security import disable_close_button
            disable_close_button(self)
        self.setGeometry(100, 100, 800, 600)
        if sec_settings.get("ENABLE_LOGGER", True):
            log_event("Game starting up...")
        
        # Load tasks, discovered modules, and gift card (unchanged).
        self.tasks = load_all_tasks()
        if sec_settings.get("ENABLE_LOGGER", True):
            log_event(f"Loaded tasks: {self.tasks}")
        self.current_task_index = 0
        self.discovered_tasks = discover_task_modules()
        self.gift_card = load_gift_card()
        
        # Security feature checks (unchanged).
        kb_mode = sec_settings.get("KEYBOARD_BLOCKER_MODE", 1)
        if kb_mode in (1, 2):
            from shared.security.keyboard_blocker_security import start_keyboard_blocker
            self.keyboard_blocker = start_keyboard_blocker(mode=kb_mode)
            log_event(f"Keyboard blocker started (mode={kb_mode}).")
        else:
            self.keyboard_blocker = None
        
        if sec_settings.get("ENABLE_MOUSE_LOCKER", False):
            from shared.security.mouse_locker_security import start_mouse_locker
            self.mouse_locker_timer = start_mouse_locker(self)
            log_event("Mouse locker started.")
        else:
            self.mouse_locker_timer = None
        
        if sec_settings.get("ENABLE_SLEEP_BLOCKER", False):
            from shared.security.sleep_blocker_security import start_sleep_blocker
            start_sleep_blocker()
            log_event("Sleep blocker started.")
        
        if sec_settings.get("ENABLE_SECURITY_MONITOR", False):
            from shared.security.security_monitor_security import start_security_monitor
            start_security_monitor()
            log_event("Security monitor started.")
        
        # --- STYLE INTEGRATION FOR GAME ---
        # Load Game stylesheet from shared/themes/game/exported_stylesheet.qss.
        stylesheet_path = get_data_path(os.path.join("shared", "themes", "game", "exported_stylesheet.qss"))
        if os.path.exists(stylesheet_path):
            try:
                with open(stylesheet_path, "r") as f:
                    stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
            except Exception as e:
                log_event(f"Error loading game stylesheet: {e}")
        # Load additional configuration files for animations, boot screen, palette, and font.
        self.animation_config = self._load_config(os.path.join("shared", "themes", "game", "animations_config.json"), {"enable_animations": True})
        self.boot_config = self._load_config(os.path.join("shared", "themes", "game", "boot_screen_config.json"),
                                             {"enable_boot_screen": False, "boot_text": "Booting up...", "background_image": ""})
        self.palette_config = self._load_config(os.path.join("shared", "themes", "game", "palette_config.json"), {})
        self.font_config = self._load_config(os.path.join("shared", "themes", "game", "font_config.json"), {"font": "Arial"})
        # Apply palette configuration.
        if self.palette_config:
            primary_color = self.palette_config.get("primary", "#FFFFFF")
            self.central_widget_bg = f"background-color: {primary_color};"
        else:
            self.central_widget_bg = ""
        # Apply font configuration.
        if self.font_config:
            chosen_font = self.font_config.get("font", "Arial")
            self.setFont(QFont(chosen_font))
        # --- END STYLE INTEGRATION FOR GAME ---
        
        # Set up main container with object name.
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainContainer")
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Progress label with object name.
        self.progress_label = QLabel("Gift Card Progress: 0%")
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.progress_label)
        
        # Task container with object name.
        self.task_container = QWidget()
        self.task_container.setObjectName("taskContainer")
        self.task_layout = QVBoxLayout(self.task_container)
        self.layout.addWidget(self.task_container)
        
        self.ui_keyboard = UIKeyboardWidget(self)
        self.ui_keyboard.setObjectName("onScreenKeyboard")
        self.ui_keyboard.hide()
        self.ui_keyboard.keyPressed.connect(self.on_keyboard_key_pressed)
        self.layout.addWidget(self.ui_keyboard)
        
        self.load_next_task()
        self.center_window()
    
    def _load_config(self, relative_path, default=None):
        path = get_data_path(relative_path)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception as e:
                log_event(f"Error loading config {relative_path}: {e}")
        return default if default is not None else {}
    
    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
    
    def load_next_task(self):
        # Clear old task widgets.
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if self.current_task_index < len(self.tasks):
            task_data = self.tasks[self.current_task_index]
            task_type = task_data.get("TASK_TYPE", "short_answer")
            module_import = self.discovered_tasks.get(task_type)
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
                    # If the widget has QLineEdits, show our UI keyboard.
                    line_edits = task_widget.findChildren(QLineEdit)
                    if line_edits:
                        for le in line_edits:
                            le.setObjectName("taskInput")
                            le.setReadOnly(True)
                            le.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
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
        from shared.utils.logger import log_event
        if success:
            self.current_task_index += 1
            self.update_progress()
            self.load_next_task()
        else:
            log_event("Task finished with incorrect answer.")
    
    def update_progress(self):
        if self.tasks:
            progress = int((self.current_task_index / len(self.tasks)) * 100)
        else:
            progress = 0
        self.progress_label.setText(f"Gift Card Progress: {progress}%")
        self.update_gift_card_reveal()
    
    def update_gift_card_reveal(self):
        full_code = self.gift_card.get("code", "XXXX-XXXX-XXXX")
        total = len(full_code)
        fraction = self.current_task_index / len(self.tasks) if self.tasks else 1
        revealed = int(total * fraction)
        visible = full_code[:revealed]
        hidden = "".join(ch if ch == '-' else '█' for ch in full_code[revealed:])
        self.progress_label.setText(f"Gift Card Code: {visible}{hidden}  ({int(fraction*100)}%)")
    
    def complete_game(self):
        from shared.utils.logger import log_event
        for i in reversed(range(self.task_layout.count())):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.ui_keyboard.hide()
        self.layout.removeWidget(self.progress_label)
        self.progress_label.deleteLater()
        from shared.security.close_button_blocker_security import enable_close_button
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
        sec_settings = load_security_settings()
        if sec_settings.get("ENABLE_SLEEP_BLOCKER", False):
            stop_sleep_blocker()
        if sec_settings.get("ENABLE_SECURITY_MONITOR", False):
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
