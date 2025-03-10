import os
import sys
import json
import glob
import importlib.util
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFormLayout, QGroupBox, QListWidget,
    QListWidgetItem, QMessageBox, QCheckBox, QDialog, QPlainTextEdit, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

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

# Import centralized security_settings module.
from builder import security_settings

# Mapping slider values to mode names.
SECURITY_MODES = {
    0: "Ethical",
    1: "Unethical",
    2: "Grift",
    3: "Custom"
}

def mode_text_color(mode):
    colors = {
        "Ethical": "green",
        "Unethical": "orange",
        "Grift": "red",
        "Custom": "cyan"
    }
    return colors.get(mode, "black")

def generate_security_summary(mode):
    # For Ethical, Unethical, and Grift modes, load the defaults.
    if mode in ["Ethical", "Unethical", "Grift"]:
        _, _, settings = security_settings.set_mode(mode)
    else:
        settings = security_settings.load_security_settings()
    summary = (
        f"UI Keyboard: {'On' if settings.get('USE_UI_KEYBOARD', False) else 'Off'} | "
        f"Keyboard Blocker: {settings.get('KEYBOARD_BLOCKER_MODE', 0)} | "
        f"Mouse Locker: {'On' if settings.get('ENABLE_MOUSE_LOCKER', False) else 'Off'} | "
        f"Sleep Blocker: {'On' if settings.get('ENABLE_SLEEP_BLOCKER', False) else 'Off'} | "
        f"Security Monitor: {'On' if settings.get('ENABLE_SECURITY_MONITOR', False) else 'Off'}"
    )
    return summary

# ---------------- Persistent Security Header ----------------
# This header displays the current security mode and, for Ethical, Unethical,
# and Grift modes, a summary of which settings are active.
class SecurityHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.modeLabel = QLabel("Security Mode: Ethical")
        self.modeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.modeLabel.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.modeLabel)
    
    def update_mode(self, mode):
        color = mode_text_color(mode)
        summary = ""
        if mode in ["Ethical", "Unethical", "Grift"]:
            summary = generate_security_summary(mode)
        self.modeLabel.setText(f"Security Mode: {mode}" + (f" - {summary}" if summary else ""))
        self.modeLabel.setStyleSheet(f"color: {color}; font-weight: bold;")

# ---------------- Developer Zone Tab ----------------
# This widget uses a slider to select the global security mode. When in Custom mode,
# additional custom controls appear.
class DevZoneWidget(QWidget):
    modeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Set Security Mode:")
        slider_layout.addWidget(slider_label)
        self.modeSlider = QSlider(Qt.Orientation.Horizontal)
        self.modeSlider.setMinimum(0)
        self.modeSlider.setMaximum(3)
        self.modeSlider.setTickInterval(1)
        self.modeSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.modeSlider.setSingleStep(1)
        self.modeSlider.valueChanged.connect(self.on_slider_changed)
        slider_layout.addWidget(self.modeSlider)
        self.modeDisplay = QLabel(SECURITY_MODES[0])
        slider_layout.addWidget(self.modeDisplay)
        layout.addLayout(slider_layout)
        
        # Container for custom security controls (visible only in Custom mode).
        self.customContainer = QWidget()
        customLayout = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_uiKeyboard.setChecked(False)
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_mouse_locker.setChecked(False)
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_sleep_blocker.setChecked(False)
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
        self.custom_security_monitor.setChecked(False)
        customLayout.addRow(self.custom_uiKeyboard)
        customLayout.addRow("Keyboard Blocker Mode:", self.custom_keyboard_blocker)
        customLayout.addRow(self.custom_mouse_locker)
        customLayout.addRow(self.custom_sleep_blocker)
        customLayout.addRow(self.custom_security_monitor)
        self.customContainer.setVisible(False)
        layout.addWidget(self.customContainer)
        
        # Save button.
        self.saveButton = QPushButton("Apply Security Mode")
        self.saveButton.clicked.connect(self.save_mode)
        layout.addWidget(self.saveButton)
    
    @pyqtSlot(int)
    def on_slider_changed(self, value):
        mode = SECURITY_MODES.get(value, "Ethical")
        self.modeDisplay.setText(mode)
        self.customContainer.setVisible(mode == "Custom")
        self.modeChanged.emit(mode)
    
    def load_existing_settings(self):
        self.modeSlider.setValue(0)
    
    def save_mode(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode == "Custom":
            custom_settings = {
                "USE_UI_KEYBOARD": self.custom_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.custom_keyboard_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.custom_mouse_locker.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.custom_sleep_blocker.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.custom_security_monitor.isChecked()
            }
            success, message, _ = security_settings.set_mode(mode, custom_settings=custom_settings)
        else:
            success, message, _ = security_settings.set_mode(mode)
        if success:
            QMessageBox.information(self, "Success", f"Security mode set to {mode}.")
            self.modeChanged.emit(mode)
        else:
            QMessageBox.critical(self, "Error", message)

# ---------------- Main Builder UI ----------------
class BuilderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nachocore v1.0")
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        # Persistent header.
        self.securityHeader = SecurityHeader()
        main_layout.addWidget(self.securityHeader)
        # Tab widget.
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central_widget)
        self.discovered_tasks = discover_task_modules()
        self.tabs.addTab(self.create_task_tab(), "Task Builder")
        self.tabs.addTab(self.create_gift_card_tab(), "Gift Card Selection")
        self.tabs.addTab(self.create_export_tab(), "Export Options")
        self.tabs.addTab(self.create_dev_zone_tab(), "Developer Zone")
        stylesheet = load_stylesheet("shared/theme/styles.qss")
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self.show()
    
    def mode_to_index(self, mode):
        for idx, m in SECURITY_MODES.items():
            if m == mode:
                return idx
        return 0
    
    @pyqtSlot(str)
    def update_global_mode(self, mode):
        self.securityHeader.update_mode(mode)
        if hasattr(self, 'export_security_slider'):
            idx = self.mode_to_index(mode)
            self.export_security_slider.blockSignals(True)
            self.export_security_slider.setValue(idx)
            self.export_security_slider.blockSignals(False)
            self.update_export_mode_label()
    
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
        self.task_list = TaskListWidget()
        self.task_list.setDragDropMode(TaskListWidget.DragDropMode.InternalMove)
        main_layout.addWidget(self.task_list, 1)
        self.task_manager = TaskManager(PROJECT_ROOT, self.task_list)
        self.task_manager.update_list_widget()
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
        # Security Mode Slider in Export Options.
        layout.addWidget(QLabel("Select Security Mode:"))
        self.export_security_slider = QSlider(Qt.Orientation.Horizontal)
        self.export_security_slider.setMinimum(0)
        self.export_security_slider.setMaximum(3)
        self.export_security_slider.setTickInterval(1)
        self.export_security_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.export_security_slider.setSingleStep(1)
        self.export_security_slider.valueChanged.connect(self.update_export_mode_label)
        layout.addWidget(self.export_security_slider)
        self.export_mode_label = QLabel("")
        self.export_mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.export_mode_label)
        self.update_export_mode_label()
        # Export button.
        export_button = QPushButton("Export to EXE")
        def on_export():
            name = self.custom_exe_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a custom EXE name.")
                return
            mode_index = self.export_security_slider.value()
            mode = SECURITY_MODES.get(mode_index, "Ethical")
            if mode == "Custom":
                security_options = {
                    "USE_UI_KEYBOARD": True,
                    "KEYBOARD_BLOCKER_MODE": self.export_keyboard_mode_combo.currentData() if hasattr(self, 'export_keyboard_mode_combo') else 1,
                    "ENABLE_MOUSE_LOCKER": True,
                    "ENABLE_SLEEP_BLOCKER": True,
                    "ENABLE_SECURITY_MONITOR": True
                }
            else:
                from builder import security_settings
                _, _, security_options = security_settings.set_mode(mode)
            success, output = export_exe(name, PROJECT_ROOT, security_options, disable_lockdown=False)
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
    
    def update_export_mode_label(self):
        mode = SECURITY_MODES.get(self.export_security_slider.value(), "Ethical")
        self.export_mode_label.setText(f"Export Security Mode: {mode}")
        self.export_mode_label.setStyleSheet(f"color: {mode_text_color(mode)}; font-weight: bold;")
    
    # ----------------- Developer Zone Tab -----------------
    def create_dev_zone_tab(self):
        from builder.dev_zone import DevZoneWidget
        dev_zone = DevZoneWidget()
        dev_zone.modeChanged.connect(self.update_global_mode)
        return dev_zone

def main():
    app = QApplication(sys.argv)
    window = BuilderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
