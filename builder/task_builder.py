import os
import json
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

class TaskManager:
    def __init__(self, project_root, list_widget: QListWidget):
        """
        Initialize the TaskManager.
        
        Args:
            project_root (str): The absolute path to the project root.
            list_widget (QListWidget): The widget in the builder UI that displays tasks.
        """
        self.project_root = project_root
        self.list_widget = list_widget
        self.tasks_file = os.path.join(self.project_root, "builder", "tasks", "tasks.json")
        self.tasks = self.load_tasks()
        # Set up the list widget for drag-and-drop reordering.
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        # Update the widget to reflect the loaded tasks.
        self.update_list_widget()

    def load_tasks(self):
        """Loads tasks from tasks.json; returns a list of task dictionaries."""
        if not os.path.exists(self.tasks_file):
            return []
        try:
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []
        except Exception as e:
            print("Error loading tasks:", e)
            return []

    def save_tasks(self):
        """Saves the current task list to tasks.json."""
        try:
            tasks_dir = os.path.dirname(self.tasks_file)
            if not os.path.exists(tasks_dir):
                os.makedirs(tasks_dir)
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            print("Error saving tasks:", e)

    def update_list_widget(self):
        """Clears and repopulates the QListWidget based on self.tasks."""
        self.list_widget.clear()
        for index, task in enumerate(self.tasks):
            # Use a short representation; you can customize this as needed.
            display_text = f"{index+1}: {task.get('question', 'No question')}"
            item = QListWidgetItem(display_text)
            # Store the entire task dictionary in UserRole (1000)
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.list_widget.addItem(item)

    def add_task(self, task_data):
        """Adds a new task to the list."""
        self.tasks.append(task_data)
        self.update_list_widget()
        self.save_tasks()

    def delete_task(self, index):
        """Deletes the task at the given index."""
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.update_list_widget()
            self.save_tasks()

    def clear_tasks(self):
        """Clears the entire task list."""
        self.tasks = []
        self.update_list_widget()
        self.save_tasks()

    def reorder_tasks(self):
        """
        After drag-and-drop reordering in the list widget,
        update self.tasks to match the new order.
        """
        new_order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            task_data = item.data(Qt.ItemDataRole.UserRole)
            new_order.append(task_data)
        self.tasks = new_order
        self.save_tasks()

# Optional: A subclass of QListWidget that automatically updates task order on drop.
class TaskListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_changed_callback = None

    def dropEvent(self, event):
        super().dropEvent(event)
        if self.order_changed_callback:
            self.order_changed_callback()
