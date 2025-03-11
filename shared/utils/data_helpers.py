# shared/utils/data_helpers.py
import os

def get_data_path(relative_path):
    # Assume PROJECT_ROOT is the parent of the shared folder.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(PROJECT_ROOT, relative_path)
