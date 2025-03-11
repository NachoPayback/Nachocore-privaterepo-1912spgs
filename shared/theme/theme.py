from ..utils.data_helpers import get_data_path


def load_stylesheet(relative_path="shared/theme/styles.qss"):
    """
    Loads the QSS stylesheet from the specified relative path.
    """
    try:
        path = get_data_path(relative_path)
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""
