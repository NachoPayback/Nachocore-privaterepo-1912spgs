import os
import sys
import json
import glob
import importlib.util
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFormLayout, QGroupBox, QListWidget,
    QListWidgetItem, QMessageBox, QCheckBox, QDialog, QPlainTextEdit
)
from PyQt6.QtCore import Qt

# Determine project root (assuming builder.py is in the builder folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.theme.theme import load_stylesheet

# File path for configuration.
CONFIG_PATH = os.path.join(PROJECT_ROOT, "builder", "config.json")

def discover_task_modules():
    """
    Scans the shared/tasks folder for .py files (excluding __init__.py)
    and returns a dictionary mapping TASK_TYPE to the module's import path.
    """
    task_modules = {}
    tasks_folder = os.path.join(PROJECT_ROOT, "shared", "tasks")
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
            print(f"Error importing {filename}: {e}")
    return task_modules

# Import TaskManager and our custom TaskListWidget.
from builder.task_builder import TaskManager, TaskListWidget

class BuilderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nachocore v1.0")
        self.setGeometry(100, 100, 800, 600)
        
        # Discover task modules.
        self.discovered_tasks = discover_task_modules()
        
        # Set up the main tab widget.
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(self.create_task_tab(), "Task Builder")
        self.tabs.addTab(self.create_gift_card_tab(), "Gift Card Selection")
        self.tabs.addTab(self.create_export_tab(), "Export Options")
        
        stylesheet = load_stylesheet("shared/theme/styles.qss")
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self.show()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                print("Error loading config:", e)
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print("Error saving config:", e)

    # ----------------- Task Builder Tab -----------------
    def create_task_tab(self):
        task_tab = QWidget()
        main_layout = QHBoxLayout(task_tab)
        
        # Left side: Use our custom TaskListWidget.
        self.task_list = TaskListWidget()
        self.task_list.setDragDropMode(TaskListWidget.DragDropMode.InternalMove)
        main_layout.addWidget(self.task_list, 1)
        
        # Instantiate TaskManager with our TaskListWidget.
        self.task_manager = TaskManager(PROJECT_ROOT, self.task_list)
        self.task_manager.update_list_widget()
        
        # Right side: Builder form.
        right_widget = QWidget()
        self.builder_form_layout = QVBoxLayout(right_widget)
        
        self.task_type_dropdown = QComboBox()
        for task_type in self.discovered_tasks.keys():
            self.task_type_dropdown.addItem(task_type)
        self.task_type_dropdown.currentIndexChanged.connect(self.load_task_template)
        self.builder_form_layout.addWidget(QLabel("Task Type:"))
        self.builder_form_layout.addWidget(self.task_type_dropdown)
        
        self.builder_widget_container = QWidget()
        self.builder_widget_layout = QVBoxLayout(self.builder_widget_container)
        self.builder_form_layout.addWidget(self.builder_widget_container)
        
        button_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("Add Task")
        self.delete_task_btn = QPushButton("Delete Task")
        self.clear_tasks_btn = QPushButton("Clear All")
        button_layout.addWidget(self.add_task_btn)
        button_layout.addWidget(self.delete_task_btn)
        button_layout.addWidget(self.clear_tasks_btn)
        self.builder_form_layout.addLayout(button_layout)
        
        self.save_task_list_btn = QPushButton("Save Task List")
        self.builder_form_layout.addWidget(self.save_task_list_btn)
        
        main_layout.addWidget(right_widget, 2)
        
        self.task_list.itemClicked.connect(self.load_task_details)
        self.add_task_btn.clicked.connect(self.add_task)
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.clear_tasks_btn.clicked.connect(self.clear_all_tasks)
        self.save_task_list_btn.clicked.connect(self.save_tasks)
        
        self.load_task_template()
        return task_tab

    def load_task_template(self):
        # Clear current builder widget.
        for i in reversed(range(self.builder_widget_layout.count())):
            widget = self.builder_widget_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        task_type = self.task_type_dropdown.currentText()
        module_import = self.discovered_tasks.get(task_type)
        if module_import:
            try:
                module = importlib.import_module(module_import)
                task_instance = module.Task()
                if hasattr(task_instance, "get_builder_widget"):
                    builder_widget = task_instance.get_builder_widget()
                    self.current_task_builder = task_instance
                else:
                    builder_widget = QWidget()
                    self.current_task_builder = None
                self.builder_widget_layout.addWidget(builder_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading template for {task_type}: {e}")

    def load_task_details(self, item):
        task_data = item.data(Qt.ItemDataRole.UserRole)
        if task_data:
            self.task_type_dropdown.setCurrentText(task_data.get("type", "Short Answer"))
            self.load_task_template()
            if self.current_task_builder and hasattr(self.current_task_builder, "set_task_data"):
                self.current_task_builder.set_task_data(task_data)

    def add_task(self):
        if self.current_task_builder and hasattr(self.current_task_builder, "get_task_data"):
            try:
                new_task = self.current_task_builder.get_task_data()
                new_task["type"] = self.task_type_dropdown.currentText()
                self.task_manager.add_task(new_task)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error adding task: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No task template available to add.")

    def delete_task(self):
        current_item = self.task_list.currentItem()
        if current_item:
            index = self.task_list.row(current_item)
            self.task_manager.delete_task(index)
        else:
            QMessageBox.warning(self, "Warning", "No task selected.")

    def clear_all_tasks(self):
        reply = QMessageBox.question(self, "Confirm", "Clear all tasks?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.task_manager.clear_tasks()

    def save_tasks(self):
        self.task_manager.save_tasks()
        QMessageBox.information(self, "Info", "Task list saved.")

    # ----------------- Gift Card Selection Tab -----------------
    def create_gift_card_tab(self):
        from builder.gift_card import load_gift_cards
        gift_tab = QWidget()
        layout = QVBoxLayout(gift_tab)
        
        self.gift_card_dropdown = QComboBox()
        self.gift_cards = load_gift_cards()
        options = ["Select Gift Card"] + list(self.gift_cards.keys()) + ["Custom Gift Card"]
        self.gift_card_dropdown.addItems(options)
        self.gift_card_dropdown.currentTextChanged.connect(self.update_gift_card_fields)
        layout.addWidget(QLabel("Select Gift Card:"))
        layout.addWidget(self.gift_card_dropdown)
        
        self.gift_card_group = QGroupBox("Gift Card Details")
        form_layout = QFormLayout()
        self.custom_name_input = QLineEdit()
        self.code_input = QLineEdit()
        self.pin_input = QLineEdit()
        form_layout.addRow("Gift Card Name:", self.custom_name_input)
        form_layout.addRow("Gift Card Code:", self.code_input)
        form_layout.addRow("PIN (if applicable):", self.pin_input)
        self.gift_card_group.setLayout(form_layout)
        layout.addWidget(self.gift_card_group)
        
        self.randomize_button = QPushButton("Randomize Code")
        self.randomize_button.clicked.connect(self.randomize_code)
        layout.addWidget(self.randomize_button)
        save_button = QPushButton("Save Gift Card Selection")
        save_button.clicked.connect(self.save_gift_card)
        layout.addWidget(save_button)
        
        return gift_tab

    def update_gift_card_fields(self):
        selected = self.gift_card_dropdown.currentText()
        if selected == "Custom Gift Card":
            self.custom_name_input.setEnabled(True)
            self.custom_name_input.clear()
            self.code_input.clear()
            self.pin_input.clear()
            self.pin_input.setVisible(True)
        elif selected in self.gift_cards:
            card_data = self.gift_cards[selected]
            self.custom_name_input.setEnabled(False)
            self.custom_name_input.setText(card_data.get("name", selected))
            from builder.gift_card import update_final_gift_card
            final_card = update_final_gift_card(selected)
            self.code_input.setText(final_card.get("code", ""))
            self.pin_input.setVisible(card_data.get("pin_required", True))
        else:
            self.custom_name_input.setEnabled(False)
            self.custom_name_input.clear()
            self.code_input.clear()
            self.pin_input.clear()
            self.pin_input.setVisible(True)

    def randomize_code(self):
        selected = self.gift_card_dropdown.currentText()
        if selected in self.gift_cards:
            from builder.gift_card import generate_random_code, generate_random_pin
            card_data = self.gift_cards[selected]
            self.code_input.setText(generate_random_code(card_data))
            self.pin_input.setText(generate_random_pin(card_data))
    
    def save_gift_card(self):
        selected = self.gift_card_dropdown.currentText()
        from builder.gift_card import update_final_gift_card
        if selected == "Custom Gift Card":
            custom_data = {
                "name": self.custom_name_input.text(),
                "code": self.code_input.text(),
                "pin": self.pin_input.text()
            }
            final_card = update_final_gift_card(selected, custom_data)
        else:
            final_card = update_final_gift_card(selected)
        QMessageBox.information(self, "Info", f"Gift Card Selection Saved!\nFinal Card: {final_card}")

    # ----------------- Export Options Tab -----------------
    def create_export_tab(self):
        from builder.export import export_exe  # Import our export function.
        export_tab = QWidget()
        layout = QVBoxLayout(export_tab)
        
        # Custom EXE Name field.
        layout.addWidget(QLabel("Enter Custom EXE Name:"))
        self.custom_exe_name = QLineEdit()
        self.custom_exe_name.setPlaceholderText("e.g., ScammerPaybackGame")
        layout.addWidget(self.custom_exe_name)
        
        # New: Disable Lockdown Features toggle.
        self.disable_lockdown_checkbox = QCheckBox("Disable Lockdown Features")
        self.disable_lockdown_checkbox.setToolTip(
            "If checked, all lockdown security features will be disabled in the exported executable."
        )
        layout.addWidget(self.disable_lockdown_checkbox)
        
        # Security Options section.
        layout.addWidget(QLabel("Security Options:"))
        self.ui_keyboard_checkbox = QCheckBox("Use UI Keyboard")
        self.ui_keyboard_checkbox.setChecked(True)
        layout.addWidget(self.ui_keyboard_checkbox)
        
        self.keyboard_mode_dropdown = QComboBox()
        self.keyboard_mode_dropdown.addItem("Block All (Mode 1)", 1)
        self.keyboard_mode_dropdown.addItem("Allow Typeable (Mode 2)", 2)
        layout.addWidget(QLabel("Keyboard Blocker Mode:"))
        layout.addWidget(self.keyboard_mode_dropdown)
        
        self.mouse_locker_checkbox = QCheckBox("Enable Mouse Locker")
        self.mouse_locker_checkbox.setChecked(True)
        layout.addWidget(self.mouse_locker_checkbox)
        
        self.sleep_blocker_checkbox = QCheckBox("Enable Sleep Blocker")
        self.sleep_blocker_checkbox.setChecked(True)
        layout.addWidget(self.sleep_blocker_checkbox)
        
        self.security_monitor_checkbox = QCheckBox("Enable Security Monitor")
        self.security_monitor_checkbox.setChecked(True)
        layout.addWidget(self.security_monitor_checkbox)
        
        export_button = QPushButton("Export to EXE")
        
        def on_export():
            name = self.custom_exe_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a custom EXE name.")
                return
            # Collect security options from checkboxes.
            security_options = {
                "USE_UI_KEYBOARD": self.ui_keyboard_checkbox.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.keyboard_mode_dropdown.currentData(),
                "ENABLE_MOUSE_LOCKER": self.mouse_locker_checkbox.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.sleep_blocker_checkbox.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.security_monitor_checkbox.isChecked()
            }
            # If the disable lockdown toggle is checked, override all security options to disable lockdown.
            if self.disable_lockdown_checkbox.isChecked():
                security_options["ENABLE_MOUSE_LOCKER"] = False
                security_options["ENABLE_SLEEP_BLOCKER"] = False
                security_options["ENABLE_SECURITY_MONITOR"] = False
            
            success, output = export_exe(name, PROJECT_ROOT, security_options, disable_lockdown=self.disable_lockdown_checkbox.isChecked())
            
            # Show a dialog with the output.
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Result")
            dialog_layout = QVBoxLayout(dialog)
            header_label = QLabel("Export Successful!" if success else "Export Failed!")
            dialog_layout.addWidget(header_label)
            text_box = QPlainTextEdit()
            text_box.setPlainText(output)
            text_box.setReadOnly(True)
            dialog_layout.addWidget(text_box)
            button_layout = QHBoxLayout()
            copy_button = QPushButton("Copy Output")
            copy_button.clicked.connect(lambda: QApplication.clipboard().setText(output))
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)
            button_layout.addWidget(copy_button)
            button_layout.addWidget(close_button)
            dialog_layout.addLayout(button_layout)
            dialog.resize(600, 400)
            dialog.exec()
        
        export_button.clicked.connect(on_export)
        layout.addWidget(export_button)
        
        return export_tab

def main():
    app = QApplication(sys.argv)
    window = BuilderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
