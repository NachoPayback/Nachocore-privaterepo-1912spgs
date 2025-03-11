import ctypes
import ctypes.wintypes
from PyQt6.QtCore import QTimer

mouse_locker_timer = None

def clip_cursor_to_window(window):
    try:
        hwnd = int(window.winId())
        rect = ctypes.wintypes.RECT()
        if ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            ctypes.windll.user32.ClipCursor(ctypes.byref(rect))
    except Exception as e:
        print("Error in clip_cursor_to_window:", e)

def start_mouse_locker(window):
    global mouse_locker_timer
    mouse_locker_timer = QTimer(window)
    mouse_locker_timer.timeout.connect(lambda: clip_cursor_to_window(window))
    mouse_locker_timer.start(200)
    return mouse_locker_timer

def stop_mouse_locker():
    global mouse_locker_timer
    if mouse_locker_timer:
        mouse_locker_timer.stop()
        mouse_locker_timer = None
    ctypes.windll.user32.ClipCursor(None)
