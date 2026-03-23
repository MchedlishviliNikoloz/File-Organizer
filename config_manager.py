from organizer import save_config


def list_categories(config: dict):
    print("\n--- Current Categories ---")
    for category, extensions in config.items():
        print(f"  {category}: {', '.join(extensions)}")
    print("--------------------------\n")

def add_category(config: dict):
    name = input("Enter new category name: ").strip().lower()
    if name in config:
        print(f"Category '{name}' already exists.")
        return config
    extensions = input("Enter extensions (comma separated, e.g. .txt,.py,.docx): ").strip()
    ext_list = [e.strip().lower() for e in extensions.split(',')]
    config[name] = ext_list
    print(f"New category '{name}' added.")
    return config

def add_extension(config: dict):
    list_categories(config)
    while True:
        target_category = input("Enter category name to add extension: ").strip().lower()
        if target_category not in config:
            print("Invalid category, Try again.")
            continue
        break

    print(config[target_category]) if config[target_category] else print("Category is empty.")

    while True:
        extension = input("Enter extension (e.g. .pdf): ").strip()
        if extension == "exit":
            break
        if extension in config[target_category]:
            print(f"Extension '{extension}' already exists. Type exit to exit or try again.")
        else:
            found_in = None
            for category, extensions in config.items():
                if extension in extensions:
                    found_in = category
                    break

            if found_in:
                print(f"WARNING: '{extension}' already exists in '{found_in}' category!")
                choice = input("Add to this category also? (yes/no): ").strip().lower()
                if choice != "yes":
                    break

            config[target_category].append(extension)
            print(f"Extension '{extension}' added.")
            break

    return config

def remove_extension(config: dict):
    list_categories(config)
    while True:
        category = input("Enter category name to remove extension: ").strip().lower()
        if category not in config:
            print("Invalid category, Try again.")
            continue
        break

    if not config[category]:
        print("Category is already empty.")
        return config
    else:
        print(config[category])

    while True:
        extension = input("Enter extension (e.g. .pdf): ").strip()
        if extension == "exit":
            break
        if extension not in config[category]:
            print(f"Extension '{extension}' does not exists. Type exit to exit or try again.")
        else:
            config[category].remove(extension)
            print(f"Extension '{extension}' removed.")
            break

    return config

def manage_categories_menu(config: dict) -> dict:
    while True:
        list_categories(config)
        print("1. Add new category")
        print("2. Add extension to category")
        print("3. Remove extension from category")
        print("4. Back")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            config = add_category(config)
            save_config(config)
        elif choice == "2":
            config = add_extension(config)
            save_config(config)
        elif choice == "3":
            config = remove_extension(config)
            save_config(config)
        elif choice == "4":
            break
        else:
            print("Invalid choice")
    return config