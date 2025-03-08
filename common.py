# common.py
import os
import sys

# Determine the project root as the folder containing this file.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure the project root is in sys.path so that all modules are accessible.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def get_path(*paths):
    """
    Returns an absolute path relative to the project root.
    
    Example:
        get_path("shared", "utils", "data_helpers.py")
    """
    return os.path.join(PROJECT_ROOT, *paths)
