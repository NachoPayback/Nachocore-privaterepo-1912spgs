import sys, os

def get_data_path(relative_path):
    """
    Returns the absolute path to a data file.
    When running under PyInstaller (sys._MEIPASS exists), files are located there;
    otherwise, uses the project root (assumed to be two levels up from shared/utils).
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)
