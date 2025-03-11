# builder/task_builder.py

import os
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

# Import helper functions from utils
from builder.utils import normalize_task_type, display_task_type

class TaskListWidget(QListWidget):
    """Custom QListWidget for displaying tasks."""
    pass

class TaskManager:
    def __init__(self, project_root, list_widget: TaskListWidget):
        """
        Initialize the TaskManager.

        Args:
            project_root (str): The root directory of the project.
            list_widget (TaskListWidget): The widget to display tasks.
        """
        self.project_root = project_root
        self.list_widget = list_widget
        # Update tasks_file to use the new location in builder/data
        self.tasks_file = os.path.join(self.project_root, "builder", "data", "tasks.json")
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from tasks_file and update the list widget."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r") as f:
                    self.tasks = json.load(f)
                for task in self.tasks:
                    # Normalize task type using the helper function
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
        """Refresh the list widget with current tasks."""
        self.list_widget.clear()
        for task in self.tasks:
            norm_type = task.get("TASK_TYPE", "unknown_task")
            display_text = display_task_type(norm_type)
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.list_widget.addItem(item)

    def add_task(self, task):
        """Add a new task and update the list widget."""
        if "type" in task:
            task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
        elif "TASK_TYPE" in task:
            task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
        self.tasks.append(task)
        self.update_list_widget()

    def delete_task(self, index):
        """Delete the task at the specified index."""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.update_list_widget()

    def clear_tasks(self):
        """Clear all tasks and update the list widget."""
        self.tasks = []
        self.update_list_widget()

    def save_tasks(self):
        """Save the current tasks to the tasks file."""
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
    
    If running in a frozen environment, returns a static manifest.
    
    Returns:
        dict: Mapping of normalized task types to their module import paths.
    """
    import glob
    import sys
    import importlib.util

    if getattr(sys, "frozen", False):
        return {
            "location_collection": "shared.tasks.location_collection",
            "multiple_choice": "shared.tasks.multiple_choice",
            "name_collection": "shared.tasks.name_collection",
            "short_answer": "shared.tasks.short_answer"
        }
    
    task_modules = {}
    # Compute the path to the shared/tasks folder relative to this file.
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
                norm = normalize_task_type(module.TASK_TYPE)
                task_modules[norm] = f"shared.tasks.{module_name}"
        except Exception as e:
            print(f"Error importing {filename}: {e}")
    return task_modules
