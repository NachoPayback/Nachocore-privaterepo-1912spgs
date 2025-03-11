# builder/task_builder.py

import os
import json
import glob
import importlib.util
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QLabel, QHBoxLayout
from builder.utils import normalize_task_type, display_task_type

class TaskListItemWidget(QWidget):
    """
    Custom widget for displaying a task in the task list.
    It shows the friendly task type and the task's question (if provided).
    If there is no question, it shows a default description.
    """
    def __init__(self, task: dict, parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        # Label for the task type.
        task_type = self.task.get("TASK_TYPE", "unknown")
        friendly_type = display_task_type(task_type)
        self.type_label = QLabel(friendly_type)
        self.type_label.setStyleSheet("font-weight: bold;")
        self.type_label.setFixedWidth(150)  # Fixed width for alignment.
        layout.addWidget(self.type_label)
        
        # Label for the question or description.
        question = self.task.get("question")
        if not question:
            question = "No question provided – displays default functionality."
        self.question_label = QLabel(question)
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)

class TaskListWidget(QListWidget):
    """
    Custom QListWidget for displaying tasks.
    """
    pass

class TaskManager:
    def __init__(self, project_root, list_widget: TaskListWidget):
        """
        Initialize TaskManager with the project root and a custom list widget.
        """
        self.project_root = project_root
        self.list_widget = list_widget
        # Updated tasks file path: tasks.json is now in builder/data
        self.tasks_file = os.path.join(self.project_root, "builder", "data", "tasks.json")
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """
        Load tasks from tasks_file, normalize task types, and update the list widget.
        """
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
        self.update_list_widget()
    
    def update_list_widget(self):
        """
        Refresh the list widget to display all tasks using the custom TaskListItemWidget.
        """
        self.list_widget.clear()
        for task in self.tasks:
            # Create a custom widget for this task.
            item_widget = TaskListItemWidget(task)
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            # Store task data in the list item for future reference.
            list_item.setData(Qt.ItemDataRole.UserRole, task)
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
    
    def add_task(self, task):
        """
        Add a new task, normalize its type, and update the list widget.
        """
        if "type" in task:
            task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
        elif "TASK_TYPE" in task:
            task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
        self.tasks.append(task)
        self.update_list_widget()
    
    def delete_task(self, index):
        """
        Delete the task at the specified index and update the list widget.
        """
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.update_list_widget()
    
    def clear_tasks(self):
        """
        Clear all tasks and update the list widget.
        """
        self.tasks = []
        self.update_list_widget()
    
    def save_tasks(self):
        """
        Save the current task list to tasks_file in JSON format.
        """
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(self.tasks, f, indent=4)
            print("Tasks saved successfully.")
        except Exception as e:
            print("Error saving tasks:", e)

def discover_task_modules():
    """
    Scans the shared/tasks folder for .py files (excluding __init__.py)
    and returns a dictionary mapping normalized TASK_TYPE to module import path.
    If running in a frozen state, returns a static manifest.
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
