TASK_TYPE = "short_answer"

import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QFormLayout
from PyQt6.QtCore import Qt

class Task:
    def __init__(self):
        # Default values; these will be overridden if saved data is loaded.
        self.question = "Type a synonym for 'quick'."
        self.acceptable_answers = ["fast", "rapid", "swift"]
        self.feedback_messages = [
            "That's not right, try again!",
            "Incorrect. Please try once more!",
            "No, that's not it. Think harder!"
        ]
        self.has_correct = True  # By default, a correct answer is required.

    def get_widget(self, finish_callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        # Use the instance's question (which may have been set via set_task_data).
        q_label = QLabel(self.question)
        q_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(q_label)
        self.answer_input = QLineEdit()
        # In game mode, the QLineEdit is read-only (so that on-screen keyboard is used).
        self.answer_input.setReadOnly(True)
        layout.addWidget(self.answer_input)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
        submit_btn = QPushButton("Submit")
        def on_submit():
            entered = self.answer_input.text().strip()
            if self.has_correct:
                if entered.lower() in [ans.lower() for ans in self.acceptable_answers]:
                    finish_callback(True)
                else:
                    feedback = random.choice(self.feedback_messages)
                    self.feedback_label.setText(feedback)
            else:
                if entered:
                    finish_callback(True)
                else:
                    self.feedback_label.setText("You must enter something!")
        submit_btn.clicked.connect(on_submit)
        layout.addWidget(submit_btn)
        return widget

    def get_builder_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.question_edit = QLineEdit(self.question)
        layout.addRow("Question:", self.question_edit)
        self.has_correct_checkbox = QCheckBox("Has Correct Answer")
        self.has_correct_checkbox.setChecked(self.has_correct)
        layout.addRow("Correct Answer Exists:", self.has_correct_checkbox)
        self.answers_edit = QLineEdit(", ".join(self.acceptable_answers))
        layout.addRow("Acceptable Answers (comma-separated):", self.answers_edit)
        def toggle_answers():
            if self.has_correct_checkbox.isChecked():
                self.answers_edit.setEnabled(True)
            else:
                self.answers_edit.clear()
                self.answers_edit.setEnabled(False)
        self.has_correct_checkbox.stateChanged.connect(lambda _: toggle_answers())
        toggle_answers()
        return widget

    def get_task_data(self):
        has_correct = self.has_correct_checkbox.isChecked() if hasattr(self, "has_correct_checkbox") else self.has_correct
        if has_correct:
            answers = [ans.strip() for ans in self.answers_edit.text().split(",") if ans.strip()] if hasattr(self, "answers_edit") else self.acceptable_answers
        else:
            answers = []
        return {
            "question": self.question_edit.text().strip() if hasattr(self, "question_edit") else self.question,
            "acceptable_answers": answers,
            "has_correct": has_correct,
            "type": TASK_TYPE
        }

    def set_task_data(self, data):
        # Update the task instance with saved data.
        if "question" in data:
            self.question = data["question"]
        if "acceptable_answers" in data:
            self.acceptable_answers = data["acceptable_answers"]
        if "has_correct" in data:
            self.has_correct = data["has_correct"]
        # If the builder widget exists (when editing), update its fields.
        if hasattr(self, "question_edit"):
            self.question_edit.setText(self.question)
        if hasattr(self, "has_correct_checkbox"):
            self.has_correct_checkbox.setChecked(self.has_correct)
        if self.has_correct and "acceptable_answers" in data:
            if hasattr(self, "answers_edit"):
                self.answers_edit.setText(", ".join(self.acceptable_answers))
        else:
            if hasattr(self, "answers_edit"):
                self.answers_edit.clear()
                self.answers_edit.setEnabled(False)

    def clear(self):
        if hasattr(self, "question_edit"):
            self.question_edit.clear()
        if hasattr(self, "answers_edit"):
            self.answers_edit.clear()
