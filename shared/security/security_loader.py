# shared/security/security_loader.py
"""
Dynamic Security Module Loader

This module scans the shared/security folder for Python files ending in
'_security.py' and dynamically imports them. This allows new security
modules to be added without modifying parent code.
"""

import os
import importlib.util

def load_security_modules(directory):
    """
    Dynamically imports all security modules in the given directory that match
    the naming pattern.

    Args:
        directory (str): The directory to scan (should be shared/security).

    Returns:
        list: A list of imported module objects.
    """
    loaded_modules = []
    for filename in os.listdir(directory):
        if filename.endswith("_security.py"):
            module_path = os.path.join(directory, filename)
            module_name = filename[:-3]  # Strip '.py'
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                loaded_modules.append(module)
                print(f"Loaded security module: {module_name}")
            except Exception as e:
                print(f"Error loading security module '{module_name}': {e}")
    return loaded_modules

if __name__ == "__main__":
    # For testing purposes:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    modules = load_security_modules(current_dir)
    print("Imported security modules:", [mod.__name__ for mod in modules])
