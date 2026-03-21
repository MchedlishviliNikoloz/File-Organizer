import json
import os
import shutil

from utils import get_file_extension


def load_config():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def categorize_files(files, config):
    categories = {
        'documents': [],
        'images': [],
        'audio': [],
        'video': [],
        'other': []
    }
    for file in files:
        extension = get_file_extension(file).lower()
        if extension in config['documents']:
            categories['documents'].append(file)
        elif extension in config['images']:
            categories['images'].append(file)
        elif extension in config['audio']:
            categories['audio'].append(file)
        elif extension in config['video']:
            categories['video'].append(file)
        else:
            categories['other'].append(file)

    for key in list(categories.keys()):
        if not categories[key]:
            del categories[key]

    return categories

def categorize_by_type(files):
    categories = {}

    for file in files:
        extension = get_file_extension(file).lower().lstrip('.')
        if extension not in categories:
            categories[extension] = [file]
        else:
            categories[extension].append(file)

    return categories

def create_folders(base_path, categories):
    for category in categories:
        os.makedirs(os.path.join(base_path, category), exist_ok=True)

def preview_changes(mapping):
    print('\n\n--------------- Previewing changes ---------------')
    for category, files in mapping.items():
        for file in files:
            print(f"{file} -> {category}/")

    print('--------------------------------------------------\n')

def move_files(mapping, base_path):
    for category, files in mapping.items():
        for file in files:
            source = os.path.join(base_path, file)
            destination = os.path.join(base_path, category, file)
            if os.path.exists(destination):
                print(f"Skipping {file} — already exists in {category}/")
                continue
            shutil.move(source, destination)