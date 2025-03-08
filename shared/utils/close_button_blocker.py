# shared/utils/close_button_blocker.py
from PyQt6.QtCore import Qt

def disable_close_button(window):
    """
    Removes the entire title bar (and thus the close button) by setting the frameless hint.
    """
    flags = window.windowFlags()
    window.setWindowFlags(flags | Qt.WindowType.FramelessWindowHint)
    window.show()

def enable_close_button(window):
    """
    Restores the default window frame and title bar.
    """
    # Clear the frameless flag.
    flags = window.windowFlags()
    # Remove the frameless flag.
    window.setWindowFlags(flags & ~Qt.WindowType.FramelessWindowHint)
    window.show()
