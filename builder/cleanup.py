# builder/cleanup.py
import os
import shutil

def clean_pycache(root):
    """
    Recursively remove all __pycache__ directories under the given root.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        for dirname in dirnames:
            if dirname == "__pycache__":
                full_path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(full_path)
                    print(f"Removed __pycache__ at {full_path}")
                except Exception as e:
                    print(f"Error removing __pycache__ at {full_path}: {e}")

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    clean_pycache(root)
