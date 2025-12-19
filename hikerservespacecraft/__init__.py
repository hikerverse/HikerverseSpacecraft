import json
import os
from pathlib import Path

materials = {}

def load_materials_from_file(file_path: str = '../data/materials.json'):
    global materials
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r') as f:
        materials = json.load(f)


abs_file_path = os.path.abspath(os.path.dirname(__file__))
# Call the function to load materials when the module is imported
load_materials_from_file(os.path.join(abs_file_path, 'data', 'materials.json'))
