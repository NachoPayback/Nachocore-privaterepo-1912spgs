"""
Gift Card Selection Tab UI Module

This module manages the gift card selection process:
- Displaying available gift cards.
- Showing/editing gift card details.
- Randomizing codes and saving selections.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QGroupBox, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class GiftCardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_gift_cards()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.gift_card_dropdown = QComboBox()
        self.gift_card_dropdown.setObjectName("giftCardDropdown")
        layout.addWidget(QLabel("Select Gift Card:"))
        layout.addWidget(self.gift_card_dropdown)
        self.gift_card_group = QGroupBox("Gift Card Details")
        self.gift_card_group.setObjectName("giftCardGroup")
        form = QFormLayout(self.gift_card_group)
        self.custom_name_input = QLineEdit()
        self.custom_name_input.setObjectName("giftCardNameInput")
        self.code_input = QLineEdit()
        self.code_input.setObjectName("giftCardCodeInput")
        self.pin_input = QLineEdit()
        self.pin_input.setObjectName("giftCardPinInput")
        form.addRow("Gift Card Name:", self.custom_name_input)
        form.addRow("Gift Card Code:", self.code_input)
        form.addRow("PIN (if applicable):", self.pin_input)
        layout.addWidget(self.gift_card_group)
        self.randomize_button = QPushButton("Randomize Code")
        self.randomize_button.setObjectName("randomizeButton")
        layout.addWidget(self.randomize_button)
        self.save_button = QPushButton("Save Gift Card Selection")
        self.save_button.setObjectName("saveGiftCardButton")
        layout.addWidget(self.save_button)

        self.gift_card_dropdown.currentTextChanged.connect(self.update_gift_card_fields)
        self.randomize_button.clicked.connect(self.randomize_code)
        self.save_button.clicked.connect(self.save_gift_card)

    def load_gift_cards(self):
        from builder.gift_card import load_gift_cards
        self.gift_cards = load_gift_cards()
        items = ["Select Gift Card"] + list(self.gift_cards.keys()) + ["Custom Gift Card"]
        self.gift_card_dropdown.clear()
        self.gift_card_dropdown.addItems(items)

    def update_gift_card_fields(self):
        from builder.gift_card import update_final_gift_card
        sel = self.gift_card_dropdown.currentText()
        if sel == "Custom Gift Card":
            self.custom_name_input.setEnabled(True)
            self.custom_name_input.clear()
            self.code_input.clear()
            self.pin_input.clear()
            self.pin_input.setVisible(True)
        elif sel in self.gift_cards:
            card_data = self.gift_cards[sel]
            self.custom_name_input.setEnabled(False)
            self.custom_name_input.setText(card_data.get("name", sel))
            final = update_final_gift_card(sel)
            self.code_input.setText(final.get("code", ""))
            self.pin_input.setVisible(card_data.get("pin_required", True))
        else:
            self.custom_name_input.setEnabled(False)
            self.custom_name_input.clear()
            self.code_input.clear()
            self.pin_input.clear()
            self.pin_input.setVisible(True)

    def randomize_code(self):
        from builder.gift_card import generate_random_code, generate_random_pin
        sel = self.gift_card_dropdown.currentText()
        if sel in self.gift_cards:
            card_data = self.gift_cards[sel]
            self.code_input.setText(generate_random_code(card_data))
            self.pin_input.setText(generate_random_pin(card_data))

    def save_gift_card(self):
        from builder.gift_card import update_final_gift_card
        sel = self.gift_card_dropdown.currentText()
        if sel == "Custom Gift Card":
            cdata = {
                "name": self.custom_name_input.text(),
                "code": self.code_input.text(),
                "pin": self.pin_input.text()
            }
            final = update_final_gift_card(sel, cdata)
        else:
            final = update_final_gift_card(sel)
        QMessageBox.information(self, "Info", f"Gift Card Saved!\n{final}")
