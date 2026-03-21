import json
import os
import shutil

from utils import get_file_extension


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def categorize_files(files, config):
    categories = {
        'documents': [],
        'images': [],
        'audio': [],
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
        else:
            categories['other'].append(file)

    for key in list(categories.keys()):
        if not categories[key]:
            del categories[key]

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
            shutil.move(source, destination)