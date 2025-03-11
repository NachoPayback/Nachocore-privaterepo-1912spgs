import os
import shutil

def clean_pycache(root_dir):
    """
    Recursively removes all __pycache__ directories within root_dir.
    """
    print("Starting __pycache__ cleanup in:", root_dir)
    for dirpath, dirnames, _ in os.walk(root_dir):
        # Use a copy of dirnames because we might modify it during iteration.
        for dirname in list(dirnames):
            if dirname == "__pycache__":
                pycache_path = os.path.join(dirpath, dirname)
                print(f"Removing __pycache__ at: {pycache_path}")
                try:
                    shutil.rmtree(pycache_path)
                    print("Removed:", pycache_path)
                    # Remove from the list to prevent os.walk from recursing into it.
                    dirnames.remove(dirname)
                except Exception as e:
                    print(f"Error removing {pycache_path}: {e}")
