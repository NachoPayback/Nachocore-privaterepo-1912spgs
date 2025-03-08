TASK_TYPE = "Name Collection"

import getpass
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
from PyQt6.QtCore import Qt

class Task:
    def __init__(self):
        self.question = "What is your real name?"
        self.answer = ""  # Default is empty; will be determined at runtime.
        self.feedback_messages = [
            "You must enter something!",
            "At least type your name!",
            "Don't leave this blank!",
            "Answer the question, please!"
        ]
    
    def auto_detect_name(self):
        try:
            detected = getpass.getuser()
            return detected if detected else ""
        except Exception:
            return ""
    
    def get_widget(self, finish_callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        q_label = QLabel(self.question)
        q_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(q_label)
        # Chain: use builder answer if set; otherwise, auto-detect.
        current_answer = self.answer if self.answer else self.auto_detect_name()
        self.name_input = QLineEdit()
        self.name_input.setText(current_answer)
        self.name_input.setReadOnly(True)
        layout.addWidget(self.name_input)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
        submit_btn = QPushButton("Submit")
        def on_submit():
            if self.name_input.text().strip():
                finish_callback(True)
            else:
                feedback = random.choice(self.feedback_messages)
                self.feedback_label.setText(feedback)
        submit_btn.clicked.connect(on_submit)
        layout.addWidget(submit_btn)
        return widget

    def get_builder_widget(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.question_edit = QLineEdit(self.question)
        layout.addRow("Question:", self.question_edit)
        # Do not pre-populate the default answer.
        self.answer_edit = QLineEdit("")
        layout.addRow("Default Answer (optional):", self.answer_edit)
        return widget

    def get_task_data(self):
        question = self.question_edit.text().strip() if hasattr(self, "question_edit") else self.question
        answer = self.answer_edit.text().strip() if hasattr(self, "answer_edit") else self.answer
        return {
            "question": question,
            "answer": answer,
            "type": TASK_TYPE
        }

    def set_task_data(self, data):
        self.question = data.get("question", self.question)
        self.answer = data.get("answer", self.answer)
        if hasattr(self, "question_edit"):
            self.question_edit.setText(self.question)
        if hasattr(self, "answer_edit"):
            self.answer_edit.setText(self.answer)

    def clear(self):
        if hasattr(self, "question_edit"):
            self.question_edit.clear()
        if hasattr(self, "answer_edit"):
            self.answer_edit.clear()
