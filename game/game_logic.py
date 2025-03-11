# game/game_logic.py
import os, json, glob, importlib.util, sys
from shared.utils.data_helpers import get_data_path

def normalize_task_type(task_type: str) -> str:
    return task_type.lower().replace(" ", "_")

class GameLogic:
    def __init__(self, project_root):
        self.project_root = project_root
        self.tasks = []
        self.current_task_index = 0
        self.gift_card = {}
        self.discovered_tasks = {}
    
    def load_all_tasks(self):
        tasks_file = get_data_path(os.path.join("builder", "data", "tasks.json"))
        if not os.path.exists(tasks_file):
            self.tasks = []
            return
        try:
            with open(tasks_file, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                for task in data:
                    if "type" in task:
                        task["TASK_TYPE"] = normalize_task_type(task.pop("type"))
                    elif "TASK_TYPE" in task:
                        task["TASK_TYPE"] = normalize_task_type(task["TASK_TYPE"])
                self.tasks = data
            else:
                self.tasks = []
        except Exception as e:
            print("Error loading tasks:", e)
            self.tasks = []
    
    def discover_task_modules(self):
        if getattr(sys, "frozen", False):
            self.discovered_tasks = {
                "location_collection": "shared.tasks.location_collection",
                "multiple_choice": "shared.tasks.multiple_choice",
                "name_collection": "shared.tasks.name_collection",
                "short_answer": "shared.tasks.short_answer"
            }
            return self.discovered_tasks
        task_modules = {}
        tasks_folder = get_data_path(os.path.join("shared", "tasks"))
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
                    task_modules[normalized] = f"shared.tasks.{module_name}"
            except Exception as e:
                print(f"Error importing {filename}: {e}")
        self.discovered_tasks = task_modules
        return task_modules
    
    def load_gift_card_from_config(self):
        config_file = get_data_path(os.path.join("builder", "config.json"))
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
            gift = config_data.get("selected_gift_card", {})
            result = {
                "code": gift.get("code", "XXXX-XXXX-XXXX"),
                "pin": gift.get("pin", "----"),
                "name": gift.get("name", "Gift Card"),
                "pin_required": gift.get("pin_required", True)
            }
            self.gift_card = result
            return result
        except Exception as e:
            print("Error loading gift card config:", e)
            result = {"code": "XXXX-XXXX-XXXX", "pin": "----", "name": "Gift Card", "pin_required": True}
            self.gift_card = result
            return result
