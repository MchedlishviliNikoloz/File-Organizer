import os
IGNORED_FILES = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}

def validate_path(path: str) -> bool:
    if os.path.isdir(path):
        return True
    return False

def get_files_in_directory(path: str) -> list:
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f not in IGNORED_FILES]

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1]