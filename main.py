from utils import *
from organizer import *
from logger import setup_logger
from config_manager import *

def main():
    while True:
        folder_path = input("Enter folder path: ")
        if not validate_path(folder_path):
            print("Folder path does not exist")
        else:
            print(f"Loaded: {folder_path}")
            files = get_files_in_directory(folder_path)
            config = load_config()
            user_config = load_user_config()
            log_path = os.path.join(folder_path, "organizer.log")
            logger = setup_logger(log_path)

            categorize_type = None
            while True:
                print("1. Categorize by default\n"
                      "2. Categorize by file type\n"
                      "3. Categorize by my configuration\n"
                      "4. Manage categories\n"
                      "5. Manage my categories\n"
                      "6. Undo last organize\n")
                choice = input("Enter your choice: ")
                if choice == "1":
                    categorize_type = '1'
                    break
                elif choice == "2":
                    categorize_type = '2'
                    break
                elif choice == "3":
                    if not user_config:
                        print("WARNING: Your configuration is empty. Please add categories first.")
                        continue
                    categorize_type = '3'
                    break
                elif choice == "4":
                    config = manage_categories_menu(config)
                elif choice == "5":
                    user_config = manage_user_config_menu(user_config)
                elif choice == "6":
                    categorize_type = '6'
                    break
                else:
                    print("Invalid choice")

            mapping = None
            if categorize_type == "1":
                mapping = categorize_files(files, config)
            elif categorize_type == "2":
                mapping = categorize_by_type(files)
            elif categorize_type == "3":
                mapping = categorize_files(files, user_config)
            elif categorize_type == "6":
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