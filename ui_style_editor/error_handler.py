# ui_style_editor/error_handler.py
import traceback

class ErrorHandler:
    def __init__(self):
        pass
    
    def log_error(self, message, exception):
        error_message = f"{message}: {str(exception)}\n{traceback.format_exc()}"
        print(error_message)
        with open("ui_style_editor/error_log.txt", "a") as f:
            f.write(error_message + "\n")
