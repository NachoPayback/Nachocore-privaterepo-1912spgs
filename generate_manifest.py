#!/usr/bin/env python3
import os
import json
import glob
import importlib.util
from shared.utils.data_helpers import get_data_path
from builder.utils import normalize_task_type

def generate_static_manifest():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Scan shared/tasks for task modules.
    tasks_folder = get_data_path(os.path.join("shared", "tasks"))
    task_manifest = {}
    for filepath in glob.glob(os.path.join(tasks_folder, "*.py")):
        filename = os.path.basename(filepath)
        if filename == "__init__.py":
            continue
        module_name = os.path.splitext(filename)[0]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "TASK_TYPE"):
                normalized = normalize_task_type(module.TASK_TYPE)
                task_manifest[normalized] = f"shared.tasks.{module_name}"
        except Exception as e:
            print(f"Error importing {filename} for manifest: {e}")
    manifest = {
        "TASK_MANIFEST": task_manifest,
        # For gift card and security settings, you could include static copies if needed.
    }
    manifest_path = os.path.join(project_root, "builder", "static_manifest.py")
    try:
        with open(manifest_path, "w") as f:
            f.write("# Auto-generated static manifest\n")
            f.write("TASK_MANIFEST = ")
            json.dump(task_manifest, f, indent=4)
            f.write("\n")
        print("Static manifest generated successfully.")
    except Exception as e:
        print("Error generating static manifest:", e)

if __name__ == "__main__":
    generate_static_manifest()
