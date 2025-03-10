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

# Import helpers from builder/utils.py
from builder.utils import normalize_task_type, display_task_type
# Import TaskManager and TaskListWidget from builder/task_builder.py
from builder.task_builder import TaskManager, TaskListWidget
# Import centralized security_settings module.
from builder import security_settings

# ---------------- Security Mode Mappings ----------------
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

def discover_task_modules():
    """
    Scans the shared/tasks folder for .py files (excluding __init__.py)
    and returns a dictionary mapping normalized TASK_TYPE -> module import path.
    If running frozen, returns a static manifest.
    """
    if getattr(sys, "frozen", False):
        return {
            "location_collection": "shared.tasks.location_collection",
            "multiple_choice": "shared.tasks.multiple_choice",
            "name_collection": "shared.tasks.name_collection",
            "short_answer": "shared.tasks.short_answer"
        }
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
                normalized = normalize_task_type(module.TASK_TYPE)
                task_modules[normalized] = f"shared.tasks.{module_name}"
        except Exception as e:
            print(f"Error importing {filename}: {e}")
    return task_modules

# ---------------- Persistent Security Header ----------------
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
        self.modeLabel.setText(f"Security Mode: {mode}")
        self.modeLabel.setStyleSheet(f"color: {color}; font-weight: bold;")

# ---------------- Developer Zone Tab ----------------
class DevZoneWidget(QWidget):
    modeChanged = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_existing_state()
    def init_ui(self):
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("Set Security Mode:"))
        self.modeSlider = QSlider(Qt.Orientation.Horizontal)
        self.modeSlider.setRange(0, 3)
        self.modeSlider.setTickInterval(1)
        self.modeSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.modeSlider.setSingleStep(1)
        self.modeSlider.valueChanged.connect(self.on_slider_changed)
        row.addWidget(self.modeSlider)
        self.modeDisplay = QLabel(SECURITY_MODES[0])
        row.addWidget(self.modeDisplay)
        layout.addLayout(row)
        self.summaryLabel = QLabel("")
        self.summaryLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.summaryLabel)
        self.customContainer = QWidget()
        form = QFormLayout(self.customContainer)
        self.custom_uiKeyboard = QCheckBox("Use UI Keyboard")
        self.custom_keyboard_blocker = QComboBox()
        self.custom_keyboard_blocker.addItem("Block All (Mode 1)", 1)
        self.custom_keyboard_blocker.addItem("Allow Typeable (Mode 2)", 2)
        self.custom_mouse_locker = QCheckBox("Enable Mouse Locker")
        self.custom_sleep_blocker = QCheckBox("Enable Sleep Blocker")
        self.custom_security_monitor = QCheckBox("Enable Security Monitor")
        form.addRow(self.custom_uiKeyboard)
        form.addRow("Keyboard Blocker Mode:", self.custom_keyboard_blocker)
        form.addRow(self.custom_mouse_locker)
        form.addRow(self.custom_sleep_blocker)
        form.addRow(self.custom_security_monitor)
        self.customContainer.setVisible(False)
        layout.addWidget(self.customContainer)
        self.saveButton = QPushButton("Apply Security Mode")
        self.saveButton.clicked.connect(self.save_mode)
        layout.addWidget(self.saveButton)
    @pyqtSlot(int)
    def on_slider_changed(self, value):
        mode = SECURITY_MODES.get(value, "Ethical")
        self.modeDisplay.setText(mode)
        if mode == "Custom":
            self.customContainer.setVisible(True)
            self.summaryLabel.setText("")
        else:
            self.customContainer.setVisible(False)
            self.summaryLabel.setText(generate_security_summary(mode))
        self.modeChanged.emit(mode)
    def load_existing_state(self):
        config = security_settings.load_security_settings()
        mode = config.get("SECURITY_MODE", "Ethical")
        slider_val = list(SECURITY_MODES.values()).index(mode) if mode in SECURITY_MODES.values() else 0
        self.modeSlider.setValue(slider_val)
        if mode == "Custom":
            self.custom_uiKeyboard.setChecked(config.get("USE_UI_KEYBOARD", False))
            kb_mode = config.get("KEYBOARD_BLOCKER_MODE", 1)
            self.custom_keyboard_blocker.setCurrentIndex(0 if kb_mode == 1 else 1)
            self.custom_mouse_locker.setChecked(config.get("ENABLE_MOUSE_LOCKER", False))
            self.custom_sleep_blocker.setChecked(config.get("ENABLE_SLEEP_BLOCKER", False))
            self.custom_security_monitor.setChecked(config.get("ENABLE_SECURITY_MONITOR", False))
        else:
            self.summaryLabel.setText(generate_security_summary(mode))
    def save_mode(self):
        mode = SECURITY_MODES.get(self.modeSlider.value(), "Ethical")
        if mode == "Custom":
            custom_settings = {
                "USE_UI_KEYBOARD": self.custom_uiKeyboard.isChecked(),
                "KEYBOARD_BLOCKER_MODE": self.custom_keyboard_blocker.currentData(),
                "ENABLE_MOUSE_LOCKER": self.custom_mouse_locker.isChecked(),
                "ENABLE_SLEEP_BLOCKER": self.custom_sleep_blocker.isChecked(),
                "ENABLE_SECURITY_MONITOR": self.custom_security_monitor.isChecked(),
                "SECURITY_MODE": mode
            }
            success, message, _ = security_settings.set_mode(mode, custom_settings=custom_settings)
        else:
            success, message, _ = security_settings.set_mode(mode)
            config = security_settings.load_security_settings()
            config["SECURITY_MODE"] = mode
            security_settings.save_security_settings(config)
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
        self.setGeometry(100, 100, 900, 600)
        central = QWidget()
        main_layout = QVBoxLayout(central)
        self.setCentralWidget(central)
        self.header = SecurityHeader()
        main_layout.addWidget(self.header)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        self.discovered_tasks = discover_task_modules()
        self.tabs.addTab(self.create_task_tab(), "Task Builder")
        self.tabs.addTab(self.create_gift_card_tab(), "Gift Card Selection")
        self.tabs.addTab(self.create_export_tab(), "Export Options")
        self.tabs.addTab(self.create_dev_zone_tab(), "Developer Zone")
        stylesheet = load_stylesheet("shared/theme/styles.qss")
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self.show()
    @pyqtSlot(str)
    def update_global_mode(self, mode):
        self.header.update_mode(mode)
        if hasattr(self, "export_security_slider"):
            idx = list(SECURITY_MODES.values()).index(mode) if mode in SECURITY_MODES.values() else 0
            self.export_security_slider.blockSignals(True)
            self.export_security_slider.setValue(idx)
            self.export_security_slider.blockSignals(False)
            self.update_export_mode_label()
            self.load_export_state()
    # -------------- Task Builder Tab --------------
    def create_task_tab(self):
        task_tab = QWidget()
        main_layout = QHBoxLayout(task_tab)
        self.task_list = TaskListWidget()
        self.task_list.setDragDropMode(TaskListWidget.DragDropMode.InternalMove)
        main_layout.addWidget(self.task_list, 1)
        self.task_manager = TaskManager(PROJECT_ROOT, self.task_list)
        self.task_manager.update_list_widget()
        right = QWidget()
        self.builder_form_layout = QVBoxLayout(right)
        self.task_type_dropdown = QComboBox()
        for norm in self.discovered_tasks:
            friendly = display_task_type(norm)
            self.task_type_dropdown.addItem(friendly, norm)
        self.builder_form_layout.addWidget(QLabel("Task Type:"))
        self.builder_form_layout.addWidget(self.task_type_dropdown)
        self.builder_widget_container = QWidget()
        self.builder_widget_layout = QVBoxLayout(self.builder_widget_container)
        self.builder_form_layout.addWidget(self.builder_widget_container)
        btn_row = QHBoxLayout()
        self.add_task_btn = QPushButton("Add Task")
        self.delete_task_btn = QPushButton("Delete Task")
        self.clear_tasks_btn = QPushButton("Clear All")
        btn_row.addWidget(self.add_task_btn)
        btn_row.addWidget(self.delete_task_btn)
        btn_row.addWidget(self.clear_tasks_btn)
        self.builder_form_layout.addLayout(btn_row)
        self.save_task_list_btn = QPushButton("Save Task List")
        self.builder_form_layout.addWidget(self.save_task_list_btn)
        main_layout.addWidget(right, 2)
        self.task_list.itemClicked.connect(self.load_task_details)
        self.add_task_btn.clicked.connect(self.add_task)
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.clear_tasks_btn.clicked.connect(self.clear_all_tasks)
        self.save_task_list_btn.clicked.connect(self.save_tasks)
        # IMPORTANT: update builder widget when dropdown selection changes.
        self.task_type_dropdown.currentIndexChanged.connect(self.load_task_template)
        self.load_task_template()
        return task_tab
    def load_task_template(self):
        for i in reversed(range(self.builder_widget_layout.count())):
            widget = self.builder_widget_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        norm = self.task_type_dropdown.currentData()
        if norm:
            module_import = self.discovered_tasks.get(norm)
            if module_import:
                try:
                    mod = importlib.import_module(module_import)
                    task_inst = mod.Task()
                    if hasattr(task_inst, "get_builder_widget"):
                        widget = task_inst.get_builder_widget()
                        self.current_task_builder = task_inst
                    else:
                        widget = QWidget()
                        self.current_task_builder = None
                    self.builder_widget_layout.addWidget(widget)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error loading template for {norm}: {e}")
    def load_task_details(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            norm = data.get("TASK_TYPE", "short_answer")
            idx = self.task_type_dropdown.findData(norm)
            if idx >= 0:
                self.task_type_dropdown.setCurrentIndex(idx)
            self.load_task_template()
            if self.current_task_builder and hasattr(self.current_task_builder, "set_task_data"):
                self.current_task_builder.set_task_data(data)
    def add_task(self):
        if self.current_task_builder and hasattr(self.current_task_builder, "get_task_data"):
            try:
                new_data = self.current_task_builder.get_task_data()
                new_data["TASK_TYPE"] = self.task_type_dropdown.currentData()
                self.task_manager.add_task(new_data)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error adding task: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No task template available to add.")
    def delete_task(self):
        cur = self.task_list.currentItem()
        if cur:
            idx = self.task_list.row(cur)
            self.task_manager.delete_task(idx)
        else:
            QMessageBox.warning(self, "Warning", "No task selected.")
    def clear_all_tasks(self):
        conf = QMessageBox.question(self, "Confirm", "Clear all tasks?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if conf == QMessageBox.StandardButton.Yes:
            self.task_manager.clear_tasks()
    def save_tasks(self):
        self.task_manager.save_tasks()
        QMessageBox.information(self, "Saved", "Task list saved.")
    # -------------- Gift Card Selection Tab --------------
    def create_gift_card_tab(self):
        from builder.gift_card import load_gift_cards
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.gift_card_dropdown = QComboBox()
        self.gift_cards = load_gift_cards()
        items = ["Select Gift Card"] + list(self.gift_cards.keys()) + ["Custom Gift Card"]
        self.gift_card_dropdown.addItems(items)
        self.gift_card_dropdown.currentTextChanged.connect(self.update_gift_card_fields)
        layout.addWidget(QLabel("Select Gift Card:"))
        layout.addWidget(self.gift_card_dropdown)
        self.gift_card_group = QGroupBox("Gift Card Details")
        form = QFormLayout(self.gift_card_group)
        self.custom_name_input = QLineEdit()
        self.code_input = QLineEdit()
        self.pin_input = QLineEdit()
        form.addRow("Gift Card Name:", self.custom_name_input)
        form.addRow("Gift Card Code:", self.code_input)
        form.addRow("PIN (if applicable):", self.pin_input)
        layout.addWidget(self.gift_card_group)
        self.randomize_button = QPushButton("Randomize Code")
        self.randomize_button.clicked.connect(self.randomize_code)
        layout.addWidget(self.randomize_button)
        save_btn = QPushButton("Save Gift Card Selection")
        save_btn.clicked.connect(self.save_gift_card)
        layout.addWidget(save_btn)
        return tab
    def update_gift_card_fields(self):
        from builder.gift_card import update_final_gift_card
        sel = self.gift_card_dropdown.currentText()
        if sel == "Custom Gift Card":
            self.custom_name_input.setEnabled(True)
            self.custom_name_input.clear()
            self.code_input.clear()
            self.pin_input.clear()
            self.pin_input.setVisible(True)
        elif sel in self.gift_cards:
            card_data = self.gift_cards[sel]
            self.custom_name_input.setEnabled(False)
            self.custom_name_input.setText(card_data.get("name", sel))
            final = update_final_gift_card(sel)
            self.code_input.setText(final.get("code", ""))
            self.pin_input.setVisible(card_data.get("pin_required", True))
        else:
            self.custom_name_input.setEnabled(False)
            self.custom_name_input.clear()
            self.code_input.clear()
            self.pin_input.clear()
            self.pin_input.setVisible(True)
    def randomize_code(self):
        from builder.gift_card import generate_random_code, generate_random_pin
        sel = self.gift_card_dropdown.currentText()
        if sel in self.gift_cards:
            card_data = self.gift_cards[sel]
            self.code_input.setText(generate_random_code(card_data))
            self.pin_input.setText(generate_random_pin(card_data))
    def save_gift_card(self):
        from builder.gift_card import update_final_gift_card
        sel = self.gift_card_dropdown.currentText()
        if sel == "Custom Gift Card":
            cdata = {
                "name": self.custom_name_input.text(),
                "code": self.code_input.text(),
                "pin": self.pin_input.text()
            }
            final = update_final_gift_card(sel, cdata)
        else:
            final = update_final_gift_card(sel)
        QMessageBox.information(self, "Info", f"Gift Card Saved!\n{final}")
    # -------------- Export Options Tab --------------
    def create_export_tab(self):
        from builder.export import export_exe
        tab = QWidget()
        layout = QVBoxLayout(tab)
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
        self.load_export_state()
        self.export_security_slider.valueChanged.connect(self.on_export_slider_changed)
        export_btn = QPushButton("Export to EXE")
        def on_export():
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
                from builder import security_settings
                _, _, opts = security_settings.set_mode(mode)
            success, output = export_exe(name, PROJECT_ROOT, opts, disable_lockdown=False)
            d = QDialog(self)
            d.setWindowTitle("Export Result")
            dlayout = QVBoxLayout(d)
            lbl = QLabel("Export Successful!" if success else "Export Failed!")
            dlayout.addWidget(lbl)
            txt = QPlainTextEdit()
            txt.setPlainText(output)
            txt.setReadOnly(True)
            dlayout.addWidget(txt)
            row = QHBoxLayout()
            cpy = QPushButton("Copy Output")
            cpy.clicked.connect(lambda: QApplication.clipboard().setText(output))
            close = QPushButton("Close")
            close.clicked.connect(d.close)
            row.addWidget(cpy)
            row.addWidget(close)
            dlayout.addLayout(row)
            d.resize(600, 400)
            d.exec()
        export_btn.clicked.connect(on_export)
        layout.addWidget(export_btn)
        return tab

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

    # -------------- Developer Zone Tab --------------
    def create_dev_zone_tab(self):
        from builder.dev_zone import DevZoneWidget
        dev = DevZoneWidget()
        dev.modeChanged.connect(self.update_global_mode)
        return dev

def main():
    app = QApplication(sys.argv)
    window = BuilderUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
