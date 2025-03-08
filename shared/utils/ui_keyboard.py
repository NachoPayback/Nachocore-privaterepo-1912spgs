from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt

class UIKeyboardWidget(QWidget):
    keyPressed = pyqtSignal(str)  # Emits the pressed key.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        keys = [
            "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
            "A", "S", "D", "F", "G", "H", "J", "K", "L",
            "Z", "X", "C", "V", "B", "N", "M"
        ]
        for j, key in enumerate(keys[:10]):
            btn = QPushButton(key)
            btn.clicked.connect(lambda checked, k=key: self.on_key_pressed(k))
            grid.addWidget(btn, 0, j)
        for j, key in enumerate(keys[10:19]):
            btn = QPushButton(key)
            btn.clicked.connect(lambda checked, k=key: self.on_key_pressed(k))
            grid.addWidget(btn, 1, j+1)
        for j, key in enumerate(keys[19:]):
            btn = QPushButton(key)
            btn.clicked.connect(lambda checked, k=key: self.on_key_pressed(k))
            grid.addWidget(btn, 2, j+2)
        space_btn = QPushButton("Space")
        space_btn.clicked.connect(lambda: self.on_key_pressed(" "))
        grid.addWidget(space_btn, 3, 0, 1, 5)
        backspace_btn = QPushButton("Backspace")
        backspace_btn.clicked.connect(lambda: self.on_key_pressed("BACKSPACE"))
        grid.addWidget(backspace_btn, 3, 5, 1, 5)
        layout.addLayout(grid)
        self.setLayout(layout)
    
    def on_key_pressed(self, key):
        self.keyPressed.emit(key)
