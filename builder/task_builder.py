# builder/task_builder.py
import os
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

# Import from utils, not from builder.py
from builder.utils import normalize_task_type, display_task_type

class TaskListWidget(QListWidget):
    pass

class TaskManager:
    def __init__(self, project_root, list_widget: TaskListWidget):
        self.project_root = project_root
        self.list_widget = list_widget
        self.tasks_file = os.path.join(self.project_root, "builder", "tasks", "tasks.json")
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
        self.update_list_widget()

    def update_list_widget(self):
        self.list_widget.clear()
        for task in self.tasks:
            norm_type = task.get("TASK_TYPE", "unknown_task")
            display_text = display_task_type(norm_type)
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.list_widget.addItem(item)

    def add_task(self, task):
        if "type" in task:
            task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
        elif "TASK_TYPE" in task:
            task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
        self.tasks.append(task)
        self.update_list_widget()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.update_list_widget()

    def clear_tasks(self):
        self.tasks = []
        self.update_list_widget()

    def save_tasks(self):
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(self.tasks, f, indent=4)
            print("Tasks saved successfully.")
        except Exception as e:
            print("Error saving tasks:", e)
