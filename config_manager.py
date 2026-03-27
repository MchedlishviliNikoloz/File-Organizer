from organizer import save_config, load_config, load_default_config, save_user_config


def list_categories(config: dict):
    print("\n--------------- Current Categories ---------------\n")

    for category, extensions in config.items():
        print(f"📁 {category} ({len(extensions)} extensions)")

        if not extensions:
            print("   (no extensions)\n")
            continue

        line = "   "
        for ext in extensions:
            if len(line) + len(ext) + 2 > 60:  # 60 char limit per line
                print(line)
                line = "   " + ext
            else:
                if line.strip():
                    line += ", " + ext
                else:
                    line += ext

        print(line + "\n")

    print("--------------------------------------------------\n")

def add_category(config: dict):
    name = input("Enter new category name: ").strip().lower()
    if name in config:
        print(f"Category '{name}' already exists.")
        return config
    extensions = input("Enter extensions (comma separated, e.g. .txt,.py,.docx): ").strip()
    ext_list = [e.strip().lower() if e.strip().startswith('.') else f".{e.strip().lower()}" for e in extensions.split(',')]
    config[name] = ext_list
    print(f"New category '{name}' added.")
    return config

def remove_category(config: dict):
    list_categories(config)
    while True:
        name = input("Enter category name to remove: ").strip().lower()
        if name not in config:
            print("Invalid category, Try again.")
            continue
        break
    choice = input(f"Do you want to remove '{name}' from the category? (yes/no): ").lower()
    if choice == 'yes':
        del config[name]
        print(f"Category '{name}' deleted.")
        return config
    else:
        print("Removing Category cancelled.")
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

        if extension and extension[0] != '.':
            extension = f".{extension}"

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

        if extension and extension[0] != '.':
            extension = f".{extension}"

        if extension not in config[category]:
            print(f"Extension '{extension}' does not exists. Type exit to exit or try again.")
        else:
            config[category].remove(extension)
            print(f"Extension '{extension}' removed.")
            break

    return config

def reset_to_default():
    config = load_default_config()
    save_config(config)

def manage_categories_menu(config: dict) -> dict:
    while True:
        list_categories(config)
        print("1. Add new category")
        print("2. Add extension to category")
        print("3. Remove category from config")
        print("4. Remove extension from category")
        print("5. Reset to default configuration")
        print("6. Back")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            config = add_category(config)
            save_config(config)
        elif choice == "2":
            config = add_extension(config)
            save_config(config)
        elif choice == "3":
            config = remove_category(config)
            save_config(config)
        elif choice == "4":
            config = remove_extension(config)
            save_config(config)
        elif choice == "5":
            confirm = input("Are you sure? This will reset all changes in default configuration! (yes/no): ").strip().lower()
            if confirm == "yes":
                reset_to_default()
                config = load_config()
                print("Configuration reset to default.")
            else:
                print("Reset cancelled.")
        elif choice == "6":
            break
        else:
            print("Invalid choice")
    return config

def manage_user_config_menu(config: dict) -> dict:
    while True:
        if not config:
            print("\n--- My Configuration (empty) ---\n")
        else:
            list_categories(config)
        print("1. Add new category")
        print("2. Add extension to category")
        print("3. Remove category from config")
        print("4. Remove extension from category")
        print("5. Clear all (Start fresh)")
        print("6. Back")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            config = add_category(config)
            save_user_config(config)
        elif choice == "2":
            if not config:
                print("WARNING: No categories yet. Add a category first.")
            else:
                config = add_extension(config)
                save_user_config(config)
        elif choice == "3":
            if not config:
                print("WARNING: No categories yet. Add a category first.")
            else:
                config = remove_category(config)
                save_user_config(config)
        elif choice == "4":
            if not config:
                print("WARNING: No categories yet. Add a category first.")
            else:
                config = remove_extension(config)
                save_user_config(config)
        elif choice == "5":
            confirm = input("Are you sure? This will clear your entire configuration! (yes/no): ").strip().lower()
            if confirm == "yes":
                config = {}
                save_user_config(config)
                print("Configuration cleared.")
            else:
                print("Cancelled.")
        elif choice == "6":
            break
        else:
            print("Invalid choice")
    return config