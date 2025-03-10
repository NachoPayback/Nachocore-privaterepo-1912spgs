# builder/utils.py
def normalize_task_type(task_type: str) -> str:
    return task_type.lower().replace(" ", "_")

def display_task_type(normalized_type: str) -> str:
    return " ".join(word.capitalize() for word in normalized_type.split("_"))
