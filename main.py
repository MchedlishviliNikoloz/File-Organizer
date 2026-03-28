from utils import *
from organizer import *
from logger import setup_logger
from config_manager import *

def confirm_action():
    while True:
        print("1. Confirm\n2. Cancel")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print("Invalid choice")

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
                print("1. Organize by default categories\n"
                      "2. Organize by file type\n"
                      "3. Organize by my categories\n"
                      "4. Find and move duplicates\n"
                      "5. Manage default categories\n"
                      "6. Manage my categories\n"
                      "7. Undo last organize\n")
                choice = input("Enter your choice: ").strip()
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
                    categorize_type = '4'
                    break
                elif choice == "5":
                    config = manage_categories_menu(config)
                elif choice == "6":
                    user_config = manage_user_config_menu(user_config)
                elif choice == "7":
                    categorize_type = '7'
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
            elif categorize_type == "4":
                duplicates = find_duplicates(files, folder_path)

                if not duplicates:
                    tqdm.write("No duplicates found!")
                else:
                    tqdm.write(f"Found {len(duplicates)} group(s) of duplicates.")

                    mapping = duplicates_to_mapping(duplicates)
                    preview_changes(mapping)

                    if confirm_action():
                        moved, moves_log = move_duplicates(duplicates, folder_path, logger)
                        save_undo_log(folder_path, moves_log)
                    else:
                        print("Operation cancelled.")
                break
            elif categorize_type == "7":
                undo_last_organize(folder_path, logger)
                break

            if mapping is None:
                continue

            if not mapping:
                print("Nothing to organize")
                break
            preview_changes(mapping)

            if confirm_action():
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