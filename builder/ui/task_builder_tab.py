# builder/ui/task_builder_tab.py

import os
import json
import importlib
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QPushButton,
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from builder.task_builder import TaskManager, TaskListTable, discover_task_modules
from builder.utils import display_task_type
from builder.presets import list_presets, load_preset, save_preset

class TaskBuilderTab(QWidget):
    def __init__(self, discovered_tasks, project_root, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.discovered_tasks = discovered_tasks
        self.current_task_builder = None  # For dynamic task editor widget
        self.init_ui()
        self.task_manager = TaskManager(self.project_root, self.taskTable)
    
    def init_ui(self):
        # Main horizontal layout divides the UI into two columns.
        main_layout = QHBoxLayout(self)
        
        # LEFT: Task List Table with object name.
        self.taskTable = TaskListTable()
        self.taskTable.setObjectName("taskListTable")
        self.taskTable.rowDoubleClicked.connect(self.on_task_double_clicked)
        main_layout.addWidget(self.taskTable, 2)
        
        # RIGHT: Controls Panel with object name.
        right_panel = QWidget()
        right_panel.setObjectName("taskBuilderControls")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top Section: Task Type Selection & Dynamic Task Builder.
        top_section = QWidget()
        top_section.setObjectName("taskBuilderTopSection")
        top_layout = QVBoxLayout(top_section)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Task Type dropdown row.
        type_layout = QHBoxLayout()
        type_label = QLabel("Task Type:")
        type_label.setObjectName("taskTypeLabel")
        type_layout.addWidget(type_label)
        self.taskTypeDropdown = QComboBox()
        self.taskTypeDropdown.setObjectName("taskTypeDropdown")
        for norm in self.discovered_tasks:
            friendly = display_task_type(norm)
            self.taskTypeDropdown.addItem(friendly, norm)
        type_layout.addWidget(self.taskTypeDropdown)
        top_layout.addLayout(type_layout)
        
        # Dynamic Task Builder widget container.
        self.builderWidgetContainer = QWidget()
        self.builderWidgetContainer.setObjectName("taskBuilderWidgetContainer")
        self.builderWidgetLayout = QVBoxLayout(self.builderWidgetContainer)
        self.builderWidgetLayout.setSpacing(5)
        self.builderWidgetLayout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.builderWidgetContainer, 1)
        
        right_layout.addWidget(top_section, 1)
        
        # Bottom Section: Action Buttons and Preset Controls.
        bottom_section = QWidget()
        bottom_section.setObjectName("taskBuilderBottomSection")
        bottom_layout = QVBoxLayout(bottom_section)
        bottom_layout.setSpacing(5)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Group 1: Task Actions.
        self.taskActionsContainer = QWidget()
        self.taskActionsContainer.setObjectName("taskActionsContainer")
        actions_layout = QHBoxLayout(self.taskActionsContainer)
        actions_layout.setSpacing(5)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        self.addTaskButton = QPushButton("Add Task")
        self.addTaskButton.setObjectName("addTaskButton")
        self.addTaskButton.clicked.connect(self.add_task)
        actions_layout.addWidget(self.addTaskButton)
        
        self.deleteTaskButton = QPushButton("Delete Task")
        self.deleteTaskButton.setObjectName("deleteTaskButton")
        self.deleteTaskButton.clicked.connect(self.delete_task)
        actions_layout.addWidget(self.deleteTaskButton)
        
        self.clearTasksButton = QPushButton("Clear All")
        self.clearTasksButton.setObjectName("clearTasksButton")
        self.clearTasksButton.clicked.connect(self.clear_tasks)
        actions_layout.addWidget(self.clearTasksButton)
        
        self.saveTaskListButton = QPushButton("Save Task List")
        self.saveTaskListButton.setObjectName("saveTaskListButton")
        self.saveTaskListButton.clicked.connect(self.save_tasks)
        actions_layout.addWidget(self.saveTaskListButton)
        
        bottom_layout.addWidget(self.taskActionsContainer)
        
        # Group 2: Task Presets.
        self.taskPresetsContainer = QWidget()
        self.taskPresetsContainer.setObjectName("taskPresetsContainer")
        presets_layout = QHBoxLayout(self.taskPresetsContainer)
        presets_layout.setSpacing(5)
        presets_layout.setContentsMargins(0, 0, 0, 0)
        
        presets_layout.addWidget(QLabel("Preset:"))
        self.taskPresetDropdown = QComboBox()
        self.taskPresetDropdown.setObjectName("taskPresetDropdown")
        self.refresh_task_presets()
        presets_layout.addWidget(self.taskPresetDropdown)
        
        self.loadTaskPresetButton = QPushButton("Load Preset")
        self.loadTaskPresetButton.setObjectName("loadTaskPresetButton")
        self.loadTaskPresetButton.clicked.connect(self.load_task_preset)
        presets_layout.addWidget(self.loadTaskPresetButton)
        
        self.saveTaskPresetButton = QPushButton("Save Preset")
        self.saveTaskPresetButton.setObjectName("saveTaskPresetButton")
        self.saveTaskPresetButton.clicked.connect(self.save_task_preset)
        presets_layout.addWidget(self.saveTaskPresetButton)
        
        bottom_layout.addWidget(self.taskPresetsContainer)
        
        right_layout.addWidget(bottom_section)
        
        main_layout.addWidget(right_panel, 1)
        
        self.taskTypeDropdown.currentIndexChanged.connect(self.load_task_template)
        self.load_task_template()
    
    def add_task(self):
        if self.current_task_builder and hasattr(self.current_task_builder, "get_task_data"):
            try:
                new_data = self.current_task_builder.get_task_data()
                new_data["TASK_TYPE"] = self.taskTypeDropdown.currentData()
                self.task_manager.add_task(new_data)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error adding task: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No task template available to add.")
    
    def delete_task(self):
        selected_rows = self.taskTable.selectionModel().selectedRows()
        if selected_rows:
            index = selected_rows[0].row()
            self.task_manager.delete_task(index)
        else:
            QMessageBox.warning(self, "Warning", "No task selected.")
    
    def clear_tasks(self):
        reply = QMessageBox.question(self, "Confirm", "Clear all tasks?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.task_manager.clear_tasks()
    
    def save_tasks(self):
        self.task_manager.save_tasks()
        QMessageBox.information(self, "Tasks Saved", "Task list saved successfully.")
    
    def refresh_task_presets(self):
        self.taskPresetDropdown.clear()
        presets = list_presets("task")
        self.taskPresetDropdown.addItems(presets)
    
    def load_task_preset(self):
        preset_name = self.taskPresetDropdown.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Warning", "No task preset selected.")
            return
        preset_tasks = load_preset("task", preset_name)
        if preset_tasks:
            self.task_manager.tasks = preset_tasks
            self.task_manager.update_table()
            QMessageBox.information(self, "Preset Loaded", f"Task preset '{preset_name}' loaded successfully.")
        else:
            QMessageBox.warning(self, "Error", f"Failed to load task preset '{preset_name}'.")
    
    def save_task_preset(self):
        preset_name, ok = QInputDialog.getText(self, "Save Task Preset", "Enter a name for this task preset:")
        if not ok or not preset_name:
            QMessageBox.information(self, "Cancelled", "Task preset save cancelled.")
            return
        if save_preset("task", self.task_manager.tasks, parent_widget=self):
            QMessageBox.information(self, "Preset Saved", f"Task preset '{preset_name}' saved successfully.")
            self.refresh_task_presets()
    
    def load_task_template(self):
        for i in reversed(range(self.builderWidgetLayout.count())):
            widget = self.builderWidgetLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        norm = self.taskTypeDropdown.currentData()
        if norm:
            module_import = self.discovered_tasks.get(norm)
            if module_import:
                try:
                    mod = importlib.import_module(module_import)
                    task_instance = mod.Task()
                    if hasattr(task_instance, "get_builder_widget"):
                        widget = task_instance.get_builder_widget()
                        self.current_task_builder = task_instance
                    else:
                        widget = QWidget()
                        self.current_task_builder = None
                    self.builderWidgetLayout.addWidget(widget)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error loading template for {norm}: {e}")
    
    def on_task_double_clicked(self, row):
        task_data = self.task_manager.get_task(row)
        if task_data and self.current_task_builder and hasattr(self.current_task_builder, "set_task_data"):
            try:
                self.current_task_builder.set_task_data(task_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading task data for editing: {e}")
        else:
            QMessageBox.information(self, "Info", "No editable task data available for this selection.")
