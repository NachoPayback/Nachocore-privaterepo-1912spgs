TASK_TYPE = "location_collection"

import requests
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
from PyQt6.QtCore import Qt

class Task:
    def __init__(self):
        self.question = "Where are you located?"
        self.answer = ""  # Default empty; auto-detection occurs at runtime.
        self.feedback_messages = [
            "Please provide your location.",
            "Don't leave this blank—where are you located?",
            "You must answer this!",
            "Come on, at least type something!"
        ]
    
    def auto_detect_location(self):
        try:
            response = requests.get("https://ipapi.co/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country_name", "")
                detected = ", ".join(filter(None, [city, region, country]))
                if detected:
                    return detected
        except Exception:
            pass
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country", "")
                detected = ", ".join(filter(None, [city, region, country]))
                if detected:
                    return detected
        except Exception:
            pass
        return ""
    
    def get_widget(self, finish_callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        q_label = QLabel(self.question)
        q_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(q_label)
        # Chain: use builder answer if set; else auto-detect.
        current_answer = self.answer if self.answer else self.auto_detect_location()
        self.location_input = QLineEdit()
        self.location_input.setText(current_answer)
        self.location_input.setReadOnly(True)
        layout.addWidget(self.location_input)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
        submit_btn = QPushButton("Submit")
        def on_submit():
            if self.location_input.text().strip():
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
