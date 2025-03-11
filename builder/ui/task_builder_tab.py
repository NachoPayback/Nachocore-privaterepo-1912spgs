# builder/ui/task_builder_tab.py
"""
Task Builder Tab UI Module

This module contains the Task Builder tab which handles:
- Displaying the list of tasks.
- Selecting a task type from a dropdown.
- Loading task templates and task details.
- Adding, deleting, clearing, and saving tasks.
"""

import importlib
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QLineEdit, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import pyqtSlot, Qt

# Import helper functions and classes from the builder package.
from builder.utils import normalize_task_type, display_task_type
from builder.task_builder import TaskManager, TaskListWidget

class TaskBuilderTab(QWidget):
    def __init__(self, discovered_tasks, project_root, parent=None):
        """
        Initialize the Task Builder tab.
        
        Args:
            discovered_tasks (dict): Mapping of normalized TASK_TYPE to module import path.
            project_root (str): The project root path.
        """
        super().__init__(parent)
        self.project_root = project_root
        self.discovered_tasks = discovered_tasks
        self.current_task_builder = None
        self.init_ui()
        self.task_manager = TaskManager(self.project_root, self.task_list)
        self.task_manager.update_list_widget()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left side: Task list.
        self.task_list = TaskListWidget()
        self.task_list.setDragDropMode(TaskListWidget.DragDropMode.InternalMove)
        main_layout.addWidget(self.task_list, 1)
        
        # Right side: Task creation and modification panel.
        right_panel = QWidget()
        self.form_layout = QVBoxLayout(right_panel)
        
        # Dropdown for selecting task type.
        self.task_type_dropdown = QComboBox()
        for norm in self.discovered_tasks:
            friendly = display_task_type(norm)
            self.task_type_dropdown.addItem(friendly, norm)
        self.form_layout.addWidget(QLabel("Task Type:"))
        self.form_layout.addWidget(self.task_type_dropdown)
        
        # Container for the task builder widget (loaded dynamically)
        self.builder_widget_container = QWidget()
        self.builder_widget_layout = QVBoxLayout(self.builder_widget_container)
        self.form_layout.addWidget(self.builder_widget_container)
        
        # Buttons for task operations.
        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        self.add_task_btn = QPushButton("Add Task")
        self.delete_task_btn = QPushButton("Delete Task")
        self.clear_tasks_btn = QPushButton("Clear All")
        btn_layout.addWidget(self.add_task_btn)
        btn_layout.addWidget(self.delete_task_btn)
        btn_layout.addWidget(self.clear_tasks_btn)
        self.form_layout.addWidget(btn_row)
        
        self.save_task_list_btn = QPushButton("Save Task List")
        self.form_layout.addWidget(self.save_task_list_btn)
        main_layout.addWidget(right_panel, 2)
        
        # Connect signals to slots.
        self.task_list.itemClicked.connect(self.load_task_details)
        self.add_task_btn.clicked.connect(self.add_task)
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.clear_tasks_btn.clicked.connect(self.clear_all_tasks)
        self.save_task_list_btn.clicked.connect(self.save_tasks)
        self.task_type_dropdown.currentIndexChanged.connect(self.load_task_template)
        self.load_task_template()

    def load_task_template(self):
        """Dynamically load the task template widget based on the selected task type."""
        # Clear previous widgets.
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
        """Load task details into the current template when an item is clicked."""
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
        """Add a new task using the current task builder widget."""
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
        """Delete the selected task from the list."""
        cur = self.task_list.currentItem()
        if cur:
            idx = self.task_list.row(cur)
            self.task_manager.delete_task(idx)
        else:
            QMessageBox.warning(self, "Warning", "No task selected.")

    def clear_all_tasks(self):
        """Clear all tasks after confirmation."""
        conf = QMessageBox.question(self, "Confirm", "Clear all tasks?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if conf == QMessageBox.StandardButton.Yes:
            self.task_manager.clear_tasks()

    def save_tasks(self):
        """Save the current task list to file."""
        self.task_manager.save_tasks()
        QMessageBox.information(self, "Saved", "Task list saved.")
