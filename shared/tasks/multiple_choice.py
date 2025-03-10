TASK_TYPE = "multiple_choice"

import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QPushButton, QLineEdit, QFormLayout, QHBoxLayout, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt

class Task:
    def __init__(self):
        # Default values; these will be overridden if saved data is loaded.
        self.question = "Which color is the sky on a clear day?"
        self.options = ["Blue", "Green", "Red", "Yellow"]
        self.correct_indices = [0]
        self.feedback_messages = [
            "Wrong! Try harder next time.",
            "Incorrect. Focus and try again!",
            "Nope, that's not it. Give it another shot!"
        ]
        # These builder UI attributes are set when get_builder_widget() is called.
        self.option_rows = []  # Will be populated in builder mode.

    def get_widget(self, finish_callback):
        """Game mode widget: displays the question and radio buttons for options."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        q_label = QLabel(self.question)
        q_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(q_label)
        self.button_group = QButtonGroup(widget)
        for idx, option in enumerate(self.options):
            rb = QRadioButton(option)
            self.button_group.addButton(rb, idx)
            layout.addWidget(rb)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
        submit_btn = QPushButton("Submit")
        def on_submit():
            selected = self.button_group.checkedId()
            if selected in self.correct_indices:
                finish_callback(True)
            else:
                feedback = random.choice(self.feedback_messages)
                self.feedback_label.setText(feedback)
        submit_btn.clicked.connect(on_submit)
        layout.addWidget(submit_btn)
        return widget

    def get_builder_widget(self):
        """Builder widget: includes a spinbox and dynamic option rows for editing."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        form_layout = QFormLayout()
        self.question_edit = QLineEdit(self.question)
        form_layout.addRow("Question:", self.question_edit)
        # SpinBox to choose number of options.
        self.option_count_spin = QSpinBox()
        self.option_count_spin.setMinimum(2)
        self.option_count_spin.setMaximum(10)
        self.option_count_spin.setValue(len(self.options))
        form_layout.addRow("Number of Options:", self.option_count_spin)
        main_layout.addLayout(form_layout)
        
        main_layout.addWidget(QLabel("Options and Correctness:"))
        # Container for dynamic option rows.
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        main_layout.addWidget(self.options_container)
        self.option_rows = []  # Reset the option rows.
        self.populate_option_rows(len(self.options))
        self.option_count_spin.valueChanged.connect(self.update_option_rows)
        
        return widget

    def populate_option_rows(self, count):
        # Clear current rows.
        for row in self.option_rows:
            row["widget"].setParent(None)
        self.option_rows = []
        # Create a row for each option.
        for i in range(count):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            option_edit = QLineEdit()
            if i < len(self.options):
                option_edit.setText(self.options[i])
            else:
                option_edit.setText("")
            correct_checkbox = QCheckBox("Correct")
            if i in self.correct_indices:
                correct_checkbox.setChecked(True)
            row_layout.addWidget(QLabel(f"Option {i+1}:"))
            row_layout.addWidget(option_edit)
            row_layout.addWidget(correct_checkbox)
            self.options_layout.addWidget(row_widget)
            self.option_rows.append({
                "widget": row_widget,
                "option_edit": option_edit,
                "correct_checkbox": correct_checkbox
            })

    def update_option_rows(self, new_count):
        current_count = len(self.option_rows)
        if new_count > current_count:
            # Add additional rows.
            for i in range(current_count, new_count):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                option_edit = QLineEdit()
                correct_checkbox = QCheckBox("Correct")
                row_layout.addWidget(QLabel(f"Option {i+1}:"))
                row_layout.addWidget(option_edit)
                row_layout.addWidget(correct_checkbox)
                self.options_layout.addWidget(row_widget)
                self.option_rows.append({
                    "widget": row_widget,
                    "option_edit": option_edit,
                    "correct_checkbox": correct_checkbox
                })
        elif new_count < current_count:
            # Remove extra rows.
            for i in range(current_count - 1, new_count - 1, -1):
                row = self.option_rows.pop(i)
                row["widget"].setParent(None)

    def get_task_data(self):
        question = self.question_edit.text().strip()
        options = []
        correct_indices = []
        for i, row in enumerate(self.option_rows):
            text = row["option_edit"].text().strip()
            if text:
                options.append(text)
                if row["correct_checkbox"].isChecked():
                    correct_indices.append(i)
        return {
            "question": question,
            "options": options,
            "correct_indices": correct_indices,
            "type": TASK_TYPE
        }

    def set_task_data(self, data):
        # Update internal attributes.
        self.question = data.get("question", self.question)
        self.options = data.get("options", self.options)
        self.correct_indices = data.get("correct_indices", self.correct_indices)
        # Update builder widget elements only if they exist.
        if hasattr(self, "question_edit"):
            self.question_edit.setText(self.question)
        if hasattr(self, "option_count_spin"):
            self.option_count_spin.setValue(len(self.options))
        # Only update dynamic option rows if they exist (i.e. builder UI is active).
        if hasattr(self, "option_rows") and self.option_rows:
            self.populate_option_rows(len(self.options))
            for i, row in enumerate(self.option_rows):
                if i < len(self.options):
                    row["option_edit"].setText(self.options[i])
                row["correct_checkbox"].setChecked(i in self.correct_indices)

    def clear(self):
        if hasattr(self, "question_edit"):
            self.question_edit.clear()
        for row in self.option_rows:
            row["option_edit"].clear()
            row["correct_checkbox"].setChecked(False)
