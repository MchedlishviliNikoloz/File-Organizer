import json
import os
import shutil
from tqdm import tqdm
from utils import get_file_extension, get_file_hash


def load_config():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def load_default_config():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'config.default.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def load_user_config():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'user_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config: dict):
    """Saves the updated config back to config.json."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    print("Config saved.")

def save_user_config(config: dict):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'user_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def categorize_files(files, config):
    categories = {category: [] for category in config}
    categories['other'] = []
    for file in files:
        extension = get_file_extension(file).lower()
        matched = False
        for category, extensions in config.items():
            if extension in extensions:
                categories[category].append(file)
                matched = True
                break
        if not matched:
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

def find_duplicates(files, base_path):
    hashes = {}

    for file in tqdm(files, desc="Scanning files", unit="file"):
        filepath = os.path.join(base_path, file)
        file_hash = get_file_hash(filepath)

        if file_hash not in hashes:
            hashes[file_hash] = [file]
        else:
            hashes[file_hash].append(file)

    found_duplicates = []
    for group in hashes.values():
        if len(group) > 1:
            found_duplicates.append(group)

    tqdm.write("")
    return found_duplicates

def duplicates_to_mapping(duplicates):
    mapping = {"duplicates": []}

    for group in duplicates:
        mapping["duplicates"].extend(group[1:])  # პირველს ვტოვებთ (original)

    return mapping

def preview_changes(mapping):
    print('\n\n--------------- Previewing changes ---------------')
    for category, files in mapping.items():
        for file in files:
            print(f"{file} -> {category}/")

    print('--------------------------------------------------\n')

def move_files(mapping, base_path, logger) -> tuple[dict, list]:
    stats = {"moved": 0, "skipped": 0}
    moves_log = []

    for category, files in mapping.items():
        for file in tqdm(files, desc=f"Moving {category}", unit="file"):
            source = os.path.join(base_path, file)
            destination = os.path.join(base_path, category, file)
            if os.path.exists(destination):
                tqdm.write(f"Skipping {file} — already exists in {category}/")
                logger.warning(f"Skipped: {file} — already exists in {category}/")
                stats["skipped"] += 1
                continue
            shutil.move(source, destination)
            logger.info(f"Moved: {file} -> {category}/")
            stats["moved"] += 1
            moves_log.append({"source": source, "destination": destination})
    tqdm.write(f"\nDone! Moved: {stats['moved']} files, Skipped: {stats['skipped']} files.")
    return stats, moves_log

def move_duplicates(duplicates, base_path, logger):
    duplicates_folder = os.path.join(base_path, 'duplicates')
    os.makedirs(duplicates_folder, exist_ok=True)

    moved = 0
    moves_log = []

    # tqdm აქ!
    all_duplicates = [file for group in duplicates for file in group[1:]]

    for file in tqdm(all_duplicates, desc="Moving duplicates", unit="file"):
        source = os.path.join(base_path, file)
        destination = os.path.join(duplicates_folder, file)

        if os.path.exists(destination):
            tqdm.write(f"Skipping {file} — already exists in duplicates/")
            continue

        shutil.move(source, destination)
        logger.info(f"Moved: {file} -> duplicates/")
        moved += 1
        moves_log.append({"source": source, "destination": destination})

    tqdm.write(f"\nDone! Moved {moved} duplicate file(s) to duplicates/")
    return moved, moves_log

def save_readme(base_path: str):
    """Creates a README file explaining the organizer's generated files."""
    readme_path = os.path.join(base_path, "README.txt")
    content = """FILE ORGANIZER - GENERATED FILES
=================================

This folder contains files generated by File Organizer:

  organizer.log
    - A log of all file operations (moves, skips, undos)
    - Safe to delete if you no longer need the history

  .undo_log.json
    - Used to undo the last organize operation
    - Automatically deleted after undo is performed
    - If you don't need undo functionality, it is safe to delete 

To undo the last organize operation, run File Organizer
and select option 3 (Undo last organize).
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def save_undo_log(base_path: str, moves_log: list):
    """Saves move history to a JSON file for undo support."""
    log_path = os.path.join(base_path, ".undo_log.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(moves_log, f, indent=2)

def undo_last_organize(base_path: str, logger):
    """Reverts the last organize operation using the undo log."""
    log_path = os.path.join(base_path, ".undo_log.json")
    if not os.path.exists(log_path):
        print("No undo history found.")
        return

    with open(log_path, 'r', encoding='utf-8') as f:
        moves_log = json.load(f)

    undone = 0
    for entry in moves_log:
        if os.path.exists(entry["destination"]):
            shutil.move(entry["destination"], entry["source"])
            logger.info(f"Undone: {entry['destination']} -> {entry['source']}")
            undone += 1
        else:
            logger.warning(f"Could not undo: {entry['destination']} not found.")

    # წაშალე ცარიელი საქაღალდეები
    for entry in moves_log:
        folder = os.path.dirname(entry["destination"])
        if os.path.isdir(folder) and not os.listdir(folder):
            os.rmdir(folder)

    os.remove(log_path)
    print(f"Undo complete! Restored {undone} files.")
    logger.info(f"Undo complete. Restored {undone} files.")