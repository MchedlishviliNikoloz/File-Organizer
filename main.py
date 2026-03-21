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
            categorize_type = None
            while True:
                print("1. Categorize by default\n"
                      "2. Categorize by file type\n")
                choice = input("Enter your choice: ")
                if choice == "1":
                    categorize_type = '1'
                    break
                elif choice == "2":
                    categorize_type = '2'
                    break
                else:
                    print("Invalid choice")

            mapping = None
            if categorize_type == "1":
                mapping = categorize_files(files, config)
            elif categorize_type == "2":
                mapping = categorize_by_type(files)

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
            else:
                print("Operation cancelled.")
                break

if __name__ == '__main__':
    main()