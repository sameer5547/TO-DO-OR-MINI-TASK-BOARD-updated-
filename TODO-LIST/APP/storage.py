import json
from pathlib import Path


DATA_FILE = Path(__file__).parent.parent / "data" / "tasks.json"


def load_tasks():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)




def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)