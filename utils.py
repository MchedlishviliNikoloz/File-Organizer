import os
import hashlib


IGNORED_FILES = {'.DS_Store', 'Thumbs.db', 'desktop.ini',
                 'organizer.log', '.undo_log.json', 'README.txt'}

def validate_path(path: str) -> bool:
    if os.path.isdir(path):
        return True
    return False

def get_files_in_directory(path: str) -> list:
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f not in IGNORED_FILES]

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1]

def get_file_hash(filepath: str) -> str:
    hash_md5 = hashlib.md5()

    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()