from utils import *
from organizer import *

def main():
    while True:
        folder_path = input("Enter folder path: ")
        if not validate_path(folder_path):
            print("Folder path does not exist")
        else:
            print(f"Loaded: {folder_path}")
            files = get_files_in_directory(folder_path)
            config = load_config()
            mapping = categorize_files(files, config)
            if not mapping:
                print("Nothing to organize")
                break
            preview_changes(mapping)
            confirm = False
            while True:
                print("1. Confirm\n"
                      "2. Cancel")
                choice = input("Enter your choice: ")
                if choice == "1":
                    confirm = True
                    break
                elif choice == "2":
                    break
                else:
                    print("Invalid choice")

            if confirm:
                create_folders(folder_path, mapping)
                move_files(mapping, folder_path)
                print("Files organized successfully!")
                break

if __name__ == '__main__':
    main()