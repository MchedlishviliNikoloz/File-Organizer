import os
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Import existing logic directly
import organizer
import utils
import logger
from organizer import (
    load_config, load_default_config, load_user_config,
    save_config, save_user_config, categorize_files, categorize_by_type,
    find_duplicates, duplicates_to_mapping, move_files, move_duplicates,
    save_readme, save_undo_log, undo_last_organize, create_folders
)


# -----------------------------------------------------------
# TQDM Monkeypatching for GUI Progress Integration
# -----------------------------------------------------------
class GUITqdm:
    app_instance = None

    def __init__(self, iterable=None, desc="", total=None, unit="it", **kwargs):
        self.iterable = iterable
        self.desc = desc
        self.total = total if total is not None else (len(iterable) if iterable else 1)
        self.current = 0
        if self.app_instance:
            self.app_instance.update_progress_ui(0, self.total, self.desc)

    def __iter__(self):
        for item in self.iterable:
            yield item
            self.current += 1
            if self.app_instance:
                self.app_instance.update_progress_ui(self.current, self.total, self.desc)

    @classmethod
    def write(cls, text):
        if cls.app_instance:
            cls.app_instance.log_message(text)


organizer.tqdm = GUITqdm

# -----------------------------------------------------------
# Design System & Theme Constants
# -----------------------------------------------------------
BG_BASE = "#07070D"        # ოდნავ softer black (სუფთა შავი ცოტა მკვდარია)
BG_SURFACE = "#14141F"     # უფრო smooth surface
BG_ELEVATED = "#1E1E2A"    # cards / inputs

ACCENT = "#6366F1"         # იგივე indigo (ძალიან კარგი არჩევანია)
ACCENT_HOVER = "#5558EC"   # ოდნავ softer hover (ნაკლებად მკვეთრი)

TEXT_PRIMARY = "#F5F5F7"   # pure white-ის მაგივრად ოდნავ softer
TEXT_MUTED = "#9CA3AF"     # უკეთესი readability

SUCCESS = "#22C55E"        # ცოტა უფრო fresh green
DANGER = "#EF4444"         # უფრო clean red
WARNING = "#F59E0B"        # იგივე კარგია

FONT_MAIN = ("Segoe UI Variable Display", 14)
FONT_HEADING = ("Segoe UI Variable Display", 24, "bold")
FONT_SUBHEADING = ("Segoe UI Variable Display", 18, "bold")
FONT_MONO = ("JetBrains Mono", 12)


# -----------------------------------------------------------
# Custom UI Components
# -----------------------------------------------------------
class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, message, type="info", duration=3500, **kwargs):
        super().__init__(master, corner_radius=5, bg_color=BG_BASE, **kwargs)

        colors = {
            "info": (ACCENT, ACCENT_HOVER),
            "success": (SUCCESS, "#059669"),
            "warning": (WARNING, "#D97706"),
            "error": (DANGER, "#E11D48")
        }
        bg_color = colors.get(type, colors["info"])[0]
        self.configure(fg_color=bg_color, border_width=1, border_color="#ffffff")

        lbl = ctk.CTkLabel(self, text=message, text_color="#ffffff", font=(FONT_MAIN[0], 15, "bold"))
        lbl.pack(padx=25, pady=15)

        self.place(relx=0.97, rely=0.04, anchor="ne")
        self.master.after(duration, self.destroy)


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, on_confirm):
        super().__init__(master)
        self.title("")
        self.geometry("450x220")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=BG_SURFACE)
        self.on_confirm = on_confirm

        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (450 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (220 // 2)
        self.geometry(f"+{x}+{y}")

        ctk.CTkLabel(self, text=title, font=FONT_SUBHEADING, text_color=TEXT_PRIMARY).pack(pady=(25, 5))
        ctk.CTkLabel(self, text=message, font=FONT_MAIN, text_color=TEXT_MUTED, wraplength=400).pack(pady=(0, 25))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40)

        ctk.CTkButton(btn_frame, text="CANCEL", height=45, fg_color=BG_ELEVATED, hover_color="#2A2A35",
                      font=(FONT_MAIN[0], 14, "bold"), command=self.destroy).pack(side="left", expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="PROCEED", height=45, fg_color=SUCCESS, hover_color="#059669",
                      font=(FONT_MAIN[0], 14, "bold"), command=self.confirm).pack(side="right", expand=True, padx=10)

    def confirm(self):
        self.on_confirm()
        self.destroy()


# -----------------------------------------------------------
# Main Application Class
# -----------------------------------------------------------
class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart File Organizer")
        self.geometry("1100x750")
        self.minsize(1000, 700)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color=BG_BASE)

        self.current_folder = ""
        self.app_logger = None
        self.current_mapping = None
        self.current_duplicates = None
        self.current_action = None
        self.config = load_config()
        self.user_config = load_user_config()

        GUITqdm.app_instance = self
        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=280) # WIDER SIDEBAR
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=BG_SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(30, 40), padx=20)
        """ctk.CTkLabel(logo_frame, text="SMART", font=(FONT_MAIN[0], 28, "bold"), text_color=ACCENT, anchor="w").pack(fill="x")"""
        ctk.CTkLabel(logo_frame, text="FILE ORGANIZER", font=(FONT_MAIN[0], 21, "bold"), text_color=TEXT_MUTED, anchor="w").pack(fill="x")

        # Nav Buttons Mapping
        self.nav_btns = {}
        self.nav_btns["organize"] = self.create_nav_button("     Dashboard", lambda: self.show_frame("organize"))
        self.nav_btns["default_config"] = self.create_nav_button("     Core Config", lambda: self.show_frame("default_config"))
        self.nav_btns["user_config"] = self.create_nav_button("     My Layouts", lambda: self.show_frame("user_config"))

        # 2. Main Container
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.setup_organize_view()
        self.setup_config_view("default_config", "CORE CONFIGURATION", is_user=False)
        self.setup_config_view("user_config", "CUSTOM LAYOUTS", is_user=True)

        self.show_frame("organize")

    def create_nav_button(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", height=50, fg_color="transparent",
                            text_color=TEXT_MUTED, hover_color=BG_ELEVATED, font=(FONT_MAIN[0], 15, "bold"),
                            command=command)
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def show_frame(self, frame_name):
        # View Switching
        for name, frame in self.frames.items():
            if name == frame_name:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_remove()

        # Update Sidebar Active State
        for name, btn in self.nav_btns.items():
            if name == frame_name:
                btn.configure(fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_MUTED)

    # -----------------------------------------------------------
    # View 1: Dashboard
    # -----------------------------------------------------------
    def setup_organize_view(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames["organize"] = frame

        header = ctk.CTkLabel(frame, text="DASHBOARD", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        header.pack(anchor="w", pady=(0, 20))

        # Folder Selection
        path_card = ctk.CTkFrame(frame, fg_color=BG_SURFACE, corner_radius=16)
        path_card.pack(fill="x", pady=(0, 20))

        self.path_entry = ctk.CTkEntry(path_card, placeholder_text="Select target directory...",
                                       height=55, font=FONT_MAIN, fg_color=BG_ELEVATED, border_width=0, corner_radius=8)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=20)

        ctk.CTkButton(path_card, text="BROWSE", height=55, width=120, font=(FONT_MAIN[0], 14, "bold"),
                      fg_color=ACCENT, hover_color=ACCENT_HOVER, corner_radius=8, command=self.browse_folder).pack(side="right", padx=(0, 20))

        # FIXED Action Buttons Grid
        action_card = ctk.CTkFrame(frame, fg_color=BG_SURFACE, corner_radius=16)
        action_card.pack(fill="x", pady=(0, 20))

        btn_font = (FONT_MAIN[0], 13, "bold")
        actions = [
            ("Organize (Core)", "default", ACCENT),
            ("Organize (Type)", "type", ACCENT),
            ("Organize (Mine)", "user", ACCENT),
            ("Find Duplicates", "duplicates", ACCENT),
            ("Undo System", "undo", BG_ELEVATED)
        ]

        # Ensure all columns have equal weight
        for i in range(len(actions)):
            action_card.grid_columnconfigure(i, weight=1)

        for idx, (text, act, color) in enumerate(actions):
            text_col = TEXT_PRIMARY if act != "undo" else TEXT_MUTED
            hover = "#2A2A35" if act == "undo" else ACCENT_HOVER
            btn = ctk.CTkButton(action_card, text=text.upper(), height=50, font=btn_font, fg_color=color,
                                hover_color=hover, text_color=text_col, corner_radius=8,
                                command=lambda a=act: self.process_action(a))
            btn.grid(row=0, column=idx, sticky="ew", padx=10, pady=20) # Grid for perfect alignment

        # Terminal
        term_card = ctk.CTkFrame(frame, fg_color=BG_SURFACE, corner_radius=16)
        term_card.pack(fill="both", expand=True)

        term_header = ctk.CTkFrame(term_card, fg_color="transparent", height=40)
        term_header.pack(fill="x", padx=20, pady=(15, 0))
        ctk.CTkLabel(term_header, text="SYSTEM LOG", font=(FONT_MAIN[0], 12, "bold"), text_color=TEXT_MUTED).pack(side="left")
        self.status_lbl = ctk.CTkLabel(term_header, text="IDLE", font=(FONT_MAIN[0], 12, "bold"), text_color=SUCCESS)
        self.status_lbl.pack(side="right")

        self.log_box = ctk.CTkTextbox(term_card, font=("JetBrains Mono", 13), fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY, border_width=0, corner_radius=8)
        self.log_box.pack(fill="both", expand=True, padx=20, pady=15)
        self.log_box.configure(state="disabled")

        self.progress = ctk.CTkProgressBar(term_card, mode="determinate", height=8, fg_color=BG_ELEVATED, progress_color=ACCENT)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=20, pady=(0, 20))

        self.exec_frame = ctk.CTkFrame(term_card, fg_color="transparent")
        ctk.CTkButton(self.exec_frame, text="ABORT", height=50, fg_color=BG_ELEVATED, hover_color="#2A2A35",
                      font=btn_font, command=self.cancel_operation).pack(side="left", expand=True, padx=(20, 10), pady=(0, 20))
        self.btn_confirm = ctk.CTkButton(self.exec_frame, text="EXECUTE PROTOCOL", height=50, fg_color=SUCCESS, hover_color="#059669",
                                         font=btn_font, command=self.execute_operation)
        self.btn_confirm.pack(side="right", expand=True, padx=(10, 20), pady=(0, 20))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
            self.current_folder = folder
            self.app_logger = logger.setup_logger(os.path.join(folder, "organizer.log"))
            ToastNotification(self, "TARGET LOCKED", "success")

    # -----------------------------------------------------------
    # View 2 & 3: Config
    # -----------------------------------------------------------
    def setup_config_view(self, frame_name, title, is_user):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames[frame_name] = frame
        frame.is_user = is_user

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))
        ctk.CTkLabel(header, text=title, font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(side="left")

        # Header Action Buttons
        actions_frame = ctk.CTkFrame(header, fg_color="transparent")
        actions_frame.pack(side="right")

        btn_add = ctk.CTkButton(actions_frame, text="+ ADD CATEGORY", height=36, font=(FONT_MAIN[0], 12, "bold"),
                                fg_color=ACCENT,
                                hover_color=ACCENT_HOVER, corner_radius=6, command=lambda: self.add_cat_gui(is_user))
        btn_add.pack(side="left", padx=(0, 10))

        reset_cmd = self.clear_user_config if is_user else self.reset_default_config
        reset_txt = "PURGE ALL" if is_user else "RESTORE DEFAULTS"
        ctk.CTkButton(actions_frame, text=reset_txt, height=36, font=(FONT_MAIN[0], 12, "bold"), fg_color="transparent",
                      border_color=DANGER, border_width=1,
                      text_color=DANGER, hover_color="#451a1a", corner_radius=6, command=reset_cmd).pack(side="left")

        # Scrollable container for Category Cards
        scroll_container = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True)

        frame.scroll_container = scroll_container
        self.refresh_config_view(frame_name)

    # -----------------------------------------------------------
    # Logic Processing
    # -----------------------------------------------------------
    def process_action(self, action):
        self.current_folder = self.path_entry.get().strip()
        if not utils.validate_path(self.current_folder):
            ToastNotification(self, "INVALID TARGET DIRECTORY", "error")
            return

        if self.app_logger is None:
            self.app_logger = logger.setup_logger(os.path.join(self.current_folder, "organizer.log"))

        self.current_action = action
        self.current_mapping = None
        self.current_duplicates = None

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.configure(state="disabled")
        self.exec_frame.pack_forget()

        if action == "undo":
            threading.Thread(target=self._thread_undo, daemon=True).start()
        else:
            threading.Thread(target=self._thread_preview, args=(action,), daemon=True).start()

    def _thread_preview(self, action):
        files = utils.get_files_in_directory(self.current_folder)
        mapping = None

        if action == "default":
            mapping = categorize_files(files, self.config)
        elif action == "type":
            mapping = categorize_by_type(files)
        elif action == "user":
            if not self.user_config:
                self.after(0, lambda: ToastNotification(self, "USER CONFIG EMPTY", "warning"))
                return
            mapping = categorize_files(files, self.user_config)
        elif action == "duplicates":
            duplicates = find_duplicates(files, self.current_folder)
            if not duplicates:
                self.after(0, lambda: ToastNotification(self, "NO DUPLICATES DETECTED", "info"))
                return
            self.current_duplicates = duplicates
            mapping = duplicates_to_mapping(duplicates)

        if not mapping:
            self.after(0, lambda: ToastNotification(self, "SYSTEM CLEAR. NO ACTIONS REQUIRED.", "info"))
            return

        self.current_mapping = mapping
        self.after(0, self._show_preview_ui)

    def _show_preview_ui(self):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, ">>> SYSTEM PREVIEW GENERATED\n\n")

        count = 0
        for category, files in self.current_mapping.items():
            for f in files:
                self.log_box.insert(tk.END, f"[MAP] {f}  -->  {category}/\n")
                count += 1

        self.log_box.insert(tk.END, f"\n>>> TOTAL QUEUED: {count} OPERATIONS\n")
        self.log_box.configure(state="disabled")

        self.exec_frame.pack(fill="x")
        ToastNotification(self, f"PREVIEW READY: {count} FILES", "info")

    def cancel_operation(self):
        self.exec_frame.pack_forget()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.insert(tk.END, ">>> OPERATION ABORTED BY USER.\n")
        self.log_box.configure(state="disabled")
        self.status_lbl.configure(text="IDLE", text_color=SUCCESS)
        self.progress.set(0)

    def execute_operation(self):
        ConfirmDialog(self, "AUTHORIZATION REQUIRED", "Initiate physical file relocation protocol?",
                      self._start_execution)

    def _start_execution(self):
        self.exec_frame.pack_forget()
        threading.Thread(target=self._thread_execute, daemon=True).start()

    def _thread_execute(self):
        try:
            moves_log = []
            if self.current_action == "duplicates":
                moved, moves_log = move_duplicates(self.current_duplicates, self.current_folder, self.app_logger)
                msg = f"SUCCESS: {moved} DUPLICATES MOVED."
            else:
                create_folders(self.current_folder, self.current_mapping)
                stats, moves_log = move_files(self.current_mapping, self.current_folder, self.app_logger)
                msg = f"SUCCESS: {stats['moved']} MOVED, {stats['skipped']} SKIPPED."

            save_undo_log(self.current_folder, moves_log)
            save_readme(self.current_folder)

            self.after(0, lambda: ToastNotification(self, msg, "success"))
            self.after(0, lambda: self.status_lbl.configure(text="COMPLETED", text_color=SUCCESS))
        except Exception as e:
            self.after(0, lambda: ToastNotification(self, f"SYSTEM ERROR", "error"))

    def _thread_undo(self):
        import os

        log_path = os.path.join(self.current_folder, ".undo_log.json")

        # UI update (start)
        self.after(0, lambda: self.status_lbl.configure(text="REVERSING...", text_color=WARNING))

        if not os.path.exists(log_path):
            self.after(0, lambda: ToastNotification(self, "No undo history found.", "warning"))
            self.after(0, lambda: self.status_lbl.configure(text="IDLE", text_color=SUCCESS))
            return

        # 👉 ეს ფუნქცია შესრულდება მხოლოდ CONFIRM-ზე
        def run_undo():
            undo_last_organize(self.current_folder, self.app_logger)

            self.after(0, lambda: ToastNotification(self, "Undo completed successfully.", "success"))
            self.after(0, lambda: self.status_lbl.configure(text="IDLE", text_color=SUCCESS))

        # 👉 Dialog უნდა გაეშვას main thread-ზე
        self.after(0, lambda: ConfirmDialog(
            self,
            "Undo Last Operation",
            "This will restore all moved files to their original locations.\n\nAre you sure you want to continue?",
            run_undo
        ))

    def update_progress_ui(self, current, total, desc):
        def update():
            pct = current / total if total > 0 else 0
            self.progress.set(pct)
            self.status_lbl.configure(text=f"PROCESSING ({current}/{total})", text_color=WARNING)

        self.after(0, update)

    def log_message(self, text):
        def update():
            self.log_box.configure(state="normal")
            self.log_box.insert(tk.END, f"> {text}\n")
            self.log_box.see(tk.END)
            self.log_box.configure(state="disabled")

        self.after(0, update)

    # -----------------------------------------------------------
    # Configuration Management (Card Layout Logic)
    # -----------------------------------------------------------
    def refresh_config_view(self, frame_name):
        frame = self.frames[frame_name]
        is_user = frame.is_user
        cfg = self.user_config if is_user else self.config

        # Clear existing cards
        for widget in frame.scroll_container.winfo_children():
            widget.destroy()

        if not cfg:
            empty_lbl = ctk.CTkLabel(frame.scroll_container,
                                     text="No categories configured yet. Add one to get started.",
                                     text_color=TEXT_MUTED, font=FONT_MAIN)
            empty_lbl.pack(pady=40)
            return

        for category, extensions in cfg.items():
            # Build individual UI Cards for each category
            card = ctk.CTkFrame(frame.scroll_container, fg_color=BG_SURFACE, border_width=1,
                                corner_radius=12)
            card.pack(fill="x", pady=(0, 12), padx=4)

            # Card Header (Title, Badge, and Buttons)
            header = ctk.CTkFrame(card, fg_color="transparent", height=40)
            header.pack(fill="x", padx=20, pady=(16, 8))

            title = ctk.CTkLabel(header, text=category.upper(), font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
            title.pack(side="left")

            count_badge = ctk.CTkLabel(header, text=f"{len(extensions)} formats", font=(FONT_MAIN[0], 12, "bold"),
                                       text_color=TEXT_MUTED, corner_radius=6)
            count_badge.pack(side="left", padx=12, ipadx=8, ipady=2)

            btn_del_cat = ctk.CTkButton(header, text="Delete", width=60, height=28, fg_color="transparent",
                                        text_color=DANGER, hover_color="#451a1a",
                                        font=(FONT_MAIN[0], 12, "bold"),
                                        command=lambda c=category: self.request_remove_cat(is_user, c))
            btn_del_cat.pack(side="right", padx=(8, 0))

            btn_rem_ext = ctk.CTkButton(header, text="- Format", width=80, height=28, fg_color="transparent", border_width=1,
                                        text_color=TEXT_PRIMARY, font=(FONT_MAIN[0], 12, "bold"),
                                        command=lambda c=category: self.remove_ext_gui_direct(is_user, c))
            btn_rem_ext.pack(side="right", padx=4)

            btn_add_ext = ctk.CTkButton(header, text="+ Format", width=80, height=28,
                                        text_color=TEXT_PRIMARY,
                                        font=(FONT_MAIN[0], 12, "bold"),
                                        command=lambda c=category: self.add_ext_gui_direct(is_user, c))
            btn_add_ext.pack(side="right", padx=4)

            # Card Body (Extensions Preview)
            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="x", padx=20, pady=(0, 20))

            ext_str = ", ".join(extensions) if extensions else "No formats assigned."
            ext_label = ctk.CTkLabel(body, text=ext_str, font=FONT_MAIN, text_color=TEXT_MUTED, justify="left",
                                     wraplength=650)
            ext_label.pack(side="left", fill="x")

    def _get_active_cfg(self, is_user):
        return self.user_config if is_user else self.config

    def _save_active_cfg(self, is_user):
        if is_user:
            save_user_config(self.user_config)
        else:
            save_config(self.config)
        self.refresh_config_view("user_config" if is_user else "default_config")

    def add_cat_gui(self, is_user):
        dialog = ctk.CTkInputDialog(text="Enter new directory name:", title="ADD CATEGORY")
        name = dialog.get_input()
        if not name: return
        name = name.strip().lower()

        cfg = self._get_active_cfg(is_user)
        if name in cfg:
            ToastNotification(self, "DIRECTORY ALREADY EXISTS.", "warning")
            return

        ext_dialog = ctk.CTkInputDialog(text="Enter formats (comma separated, e.g. .txt,.md):", title="ADD FORMATS")
        exts = ext_dialog.get_input()
        if exts is None: return

        ext_list = [e.strip().lower() if e.strip().startswith('.') else f".{e.strip().lower()}" for e in exts.split(',')
                    if e.strip()]
        cfg[name] = ext_list
        self._save_active_cfg(is_user)
        ToastNotification(self, f"DIRECTORY '{name.upper()}' CREATED.", "success")

    def request_remove_cat(self, is_user, cat):
        ConfirmDialog(self, "CONFIRM DELETION", f"Purge directory '{cat.upper()}'?",
                      lambda: self._execute_remove_cat(is_user, cat))

    def _execute_remove_cat(self, is_user, cat):
        cfg = self._get_active_cfg(is_user)
        if cat in cfg:
            del cfg[cat]
            self._save_active_cfg(is_user)
            ToastNotification(self, "DIRECTORY PURGED.", "success")

    def add_ext_gui_direct(self, is_user, cat):
        dialog = ctk.CTkInputDialog(text=f"Enter format for {cat.upper()}:", title="ADD FORMAT")
        ext = dialog.get_input()
        if not ext: return

        ext = ext.strip().lower()
        if ext and ext[0] != '.': ext = f".{ext}"

        cfg = self._get_active_cfg(is_user)
        if ext in cfg[cat]:
            ToastNotification(self, "FORMAT ALREADY REGISTERED.", "warning")
            return

        cfg[cat].append(ext)
        self._save_active_cfg(is_user)
        ToastNotification(self, "FORMAT REGISTERED.", "success")

    def remove_ext_gui_direct(self, is_user, cat):
        cfg = self._get_active_cfg(is_user)
        if not cfg[cat]:
            ToastNotification(self, "NO FORMATS TO REMOVE.", "warning")
            return

        # Shows available extensions directly in the prompt for ease of use
        available = ", ".join(cfg[cat])
        dialog = ctk.CTkInputDialog(text=f"Enter format to remove from {cat.upper()}:\n(Available: {available})",
                                    title="REMOVE FORMAT")
        ext = dialog.get_input()
        if not ext: return

        ext = ext.strip().lower()
        if ext and ext[0] != '.': ext = f".{ext}"

        if ext not in cfg[cat]:
            ToastNotification(self, "FORMAT NOT FOUND.", "warning")
            return

        cfg[cat].remove(ext)
        self._save_active_cfg(is_user)
        ToastNotification(self, "FORMAT PURGED.", "success")

    def reset_default_config(self):
        ConfirmDialog(self, "FACTORY RESET", "Wipe custom changes and restore core system?",
                      self._execute_reset_default)

    def _execute_reset_default(self):
        self.config = load_default_config()
        save_config(self.config)
        self.refresh_config_view("default_config")
        ToastNotification(self, "CORE SYSTEM RESTORED.", "success")

    def clear_user_config(self):
        ConfirmDialog(self, "PURGE CUSTOM LAYOUTS", "Permanently delete all custom configurations?",
                      self._execute_clear_user)

    def _execute_clear_user(self):
        self.user_config = {}
        save_user_config(self.user_config)
        self.refresh_config_view("user_config")
        ToastNotification(self, "CUSTOM DATA PURGED.", "success")


if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()