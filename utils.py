import os
def validate_path(path: str) -> bool:
    if os.path.isdir(path):
        return True
    return False

def get_files_in_directory(path: str) -> list:
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1]