from utils import *
from organizer import *
from logger import setup_logger

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
            log_path = os.path.join(folder_path, "organizer.log")
            logger = setup_logger(log_path)

            while True:
                print("1. Categorize by default\n"
                      "2. Categorize by file type\n"
                      "3. Undo last organize\n")
                choice = input("Enter your choice: ")
                if choice == "1":
                    categorize_type = '1'
                    break
                elif choice == "2":
                    categorize_type = '2'
                    break
                elif choice == "3":
                    categorize_type = '3'
                    break
                else:
                    print("Invalid choice")

            mapping = None
            if categorize_type == "1":
                mapping = categorize_files(files, config)
            elif categorize_type == "2":
                mapping = categorize_by_type(files)
            elif categorize_type == "3":
                undo_last_organize(folder_path, logger)
                break

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
                stats, moves_log = move_files(mapping, folder_path, logger)
                save_undo_log(folder_path, moves_log)
                save_readme(folder_path)
                break
            else:
                print("Operation cancelled.")
                break

if __name__ == '__main__':
    main()