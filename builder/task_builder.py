import os
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

class TaskListWidget(QListWidget):
    """
    A minimal subclass of QListWidget for displaying tasks.
    You can expand this class if additional functionality is needed.
    """
    pass

class TaskManager:
    def __init__(self, project_root, list_widget: TaskListWidget):
        self.project_root = project_root
        self.list_widget = list_widget
        # Path to tasks.json inside the builder/tasks folder.
        self.tasks_file = os.path.join(self.project_root, "builder", "tasks", "tasks.json")
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from tasks.json and convert 'type' to 'TASK_TYPE' if necessary."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r") as f:
                    self.tasks = json.load(f)
                # Convert any legacy "type" keys to "TASK_TYPE"
                for task in self.tasks:
                    if "type" in task:
                        task["TASK_TYPE"] = task.pop("type")
            except Exception as e:
                print("Error loading tasks:", e)
                self.tasks = []
        else:
            self.tasks = []
        self.update_list_widget()

    def update_list_widget(self):
        """Refresh the list widget to display current tasks."""
        self.list_widget.clear()
        for task in self.tasks:
            # Use the "TASK_TYPE" key for display.
            task_type = task.get("TASK_TYPE", "Unknown Task")
            item = QListWidgetItem(task_type)
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.list_widget.addItem(item)

    def add_task(self, task):
        """
        Add a new task dictionary.
        If the task dictionary contains the key "type", convert it to "TASK_TYPE".
        """
        if "type" in task:
            task["TASK_TYPE"] = task.pop("type")
        self.tasks.append(task)
        self.update_list_widget()

    def delete_task(self, index):
        """Delete the task at the given index."""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.update_list_widget()
        else:
            print("Invalid index for deletion.")

    def clear_tasks(self):
        """Clear all tasks from the manager and update the list widget."""
        self.tasks = []
        self.update_list_widget()

    def save_tasks(self):
        """Write the current tasks to tasks.json, ensuring proper key names."""
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(self.tasks, f, indent=4)
            print("Tasks saved successfully.")
        except Exception as e:
            print("Error saving tasks:", e)
