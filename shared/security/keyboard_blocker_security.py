from pynput import keyboard

ALLOWED_CHARACTERS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " `~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?"
)

def start_keyboard_blocker(mode=1):
    """
    Starts a keyboard blocker.
    mode=1: Block all key events.
    mode=2: Allow only typeable keys (letters, numbers, punctuation, space) and block special keys.
    Returns the listener object.
    """
    if mode == 1:
        listener = keyboard.Listener(
            on_press=lambda key: None,
            suppress=True
        )
    elif mode == 2:
        def on_press(key):
            try:
                if key.char in ALLOWED_CHARACTERS:
                    return  # Allow the key event.
                else:
                    return True  # Suppress the event.
            except AttributeError:
                # If key doesn't have a char attribute (i.e. special keys), suppress.
                return True
        listener = keyboard.Listener(
            on_press=on_press,
            suppress=True
        )
    else:
        listener = None

    if listener:
        listener.start()
    return listener

def stop_keyboard_blocker(listener):
    """
    Stops the keyboard blocker.
    """
    if listener:
        listener.stop()
