# builder/task_builder.py

import os
import json
import glob
import importlib.util
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QMessageBox
from builder.utils import normalize_task_type, display_task_type

class TaskListTable(QTableWidget):
    # Signal for double-clicking a row (to edit a task)
    rowDoubleClicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Task Type", "Question/Description"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        # Enable drag-and-drop reordering.
        self.setDragDropMode(QTableWidget.DragDropMode.InternalMove)
        # Inform users they can double-click a row to edit.
        self.setToolTip("Double-click a task to edit it")
        self.cellDoubleClicked.connect(self.on_cell_double_clicked)
    
    def on_cell_double_clicked(self, row, column):
        self.rowDoubleClicked.emit(row)
    
    def update_tasks(self, tasks: list):
        self.setRowCount(0)
        for i, task in enumerate(tasks):
            self.insertRow(i)
            # Task Type column:
            task_type = task.get("TASK_TYPE", "unknown")
            friendly_type = display_task_type(task_type)
            type_item = QTableWidgetItem(friendly_type)
            type_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(i, 0, type_item)
            # Question/Description column: use a QLabel to allow word wrapping.
            question = task.get("question", "No question provided – default functionality.")
            q_label = QLabel(question)
            q_label.setWordWrap(True)
            q_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.setCellWidget(i, 1, q_label)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

class TaskManager:
    def __init__(self, project_root, table_widget: TaskListTable):
        self.project_root = project_root
        self.table_widget = table_widget
        # Updated tasks file path: tasks.json is now in builder/data.
        self.tasks_file = os.path.join(self.project_root, "builder", "data", "tasks.json")
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r") as f:
                    self.tasks = json.load(f)
                for task in self.tasks:
                    if "type" in task:
                        task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
                    elif "TASK_TYPE" in task:
                        task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
            except Exception as e:
                print("Error loading tasks:", e)
                self.tasks = []
        else:
            self.tasks = []
        self.update_table()
    
    def update_table(self):
        self.table_widget.update_tasks(self.tasks)
    
    def add_task(self, task):
        if "type" in task:
            task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
        elif "TASK_TYPE" in task:
            task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
        self.tasks.append(task)
        self.update_table()
    
    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.update_table()
    
    def clear_tasks(self):
        self.tasks = []
        self.update_table()
    
    def save_tasks(self):
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(self.tasks, f, indent=4)
            print("Tasks saved successfully.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error saving tasks: {e}")
    
    def get_task(self, index):
        if 0 <= index < len(self.tasks):
            return self.tasks[index]
        return None
    
    def edit_task(self, index, new_data):
        if 0 <= index < len(self.tasks):
            self.tasks[index] = new_data
            self.update_table()

def discover_task_modules():
    """
    Scans the shared/tasks folder for .py files (excluding __init__.py)
    and returns a dictionary mapping normalized TASK_TYPE -> module import path.
    If running frozen, returns a static manifest.
    """
    import sys
    if getattr(sys, "frozen", False):
        return {
            "location_collection": "shared.tasks.location_collection",
            "multiple_choice": "shared.tasks.multiple_choice",
            "name_collection": "shared.tasks.name_collection",
            "short_answer": "shared.tasks.short_answer"
        }
    task_modules = {}
    tasks_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared", "tasks")
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
