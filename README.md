# 📁 File Organizer

A simple yet powerful command-line tool to automatically organize files in any folder by type, extension, or custom rules — with support for duplicate detection and undo functionality.

🇺🇸 English | 🇬🇪 [ქართული](README.ka.md)
---

## ✨ Features

- 📂 **Categorize by default** — organizes files into predefined categories (images, documents, audio, video, code, archives)
- 🔤 **Categorize by file type** — groups files by their extension (`.jpg`, `.pdf`, etc.)
- ⚙️ **Custom configuration** — create and manage your own organization rules
- 👤 **Personal configuration** — build a completely separate set of rules just for you
- 🔍 **Duplicate detection** — finds and moves duplicate files using MD5 hashing
- ↩️ **Undo** — revert the last organize operation at any time
- 📊 **Progress bar** — real-time progress while files are being moved
- 📝 **Logging** — every operation is logged to `organizer.log`
- 🔄 **Reset to default** — restore the original configuration at any time

---

## 📋 Requirements

- Python 3.10+
- tqdm

---

## 🚀 Installation

**1. Clone the repository:**
```bash
git clone https://github.com/MchedlishviliNikoloz/file-organizer.git
cd file-organizer
```

**2. Install dependencies:**
```bash
pip install tqdm
```

**3. Run the program:**
```bash
python main.py
```

---

## 📖 Usage

Run the program and enter the path to the folder you want to organize:

```
📂 Enter folder path: /Users/username/Desktop/MyFolder

1. Organize by default categories
2. Organize by file type
3. Organize by my categories
4. Find and move duplicates
5. Manage default categories
6. Manage my categories
7. Undo last organize
```

### Categorize by default

Files are sorted into the following folders:

| Category | Extensions |
|----------|-----------|
| 📷 images | .jpg, .jpeg, .png, .gif, .webp, .svg, .bmp ... |
| 📄 documents | .pdf, .docx, .txt, .xlsx, .pptx, .md ... |
| 🎵 audio | .mp3, .wav, .flac, .aac, .ogg ... |
| 🎬 video | .mp4, .mov, .avi, .mkv, .wmv ... |
| 💻 code | .py, .js, .html, .css, .ts, .json ... |
| 🗜️ archives | .zip, .rar, .7z, .tar, .gz |
| 📦 other | everything else |

### Undo

After organizing, you can always undo the last operation by selecting option **7. Undo last organize**. The undo history is saved in `.undo_log.json`.

### Duplicate Detection

The program scans files using **MD5 hashing** to detect files with identical content (regardless of filename). Duplicates are moved to a `duplicates/` folder, keeping the original file in place.

---

## 🗂 Project Structure

```
file-organizer/
│
├── main.py              # Entry point
├── organizer.py         # Core logic
├── config_manager.py    # Category management
├── utils.py             # Helper functions
├── logger.py            # Logging setup
│
├── config.json          # Default configuration
├── config.default.json  # Backup of default config
├── user_config.json     # User personal configuration
│
└── README.md
```

---

## 📄 Generated Files

After organizing a folder, the following files may appear inside it:

| File | Description |
|------|-------------|
| `organizer.log` | Log of all operations |
| `.undo_log.json` | Undo history (deleted after undo) |
| `README.txt` | Explanation of generated files |

---

## 🛠 Built With

- [Python](https://www.python.org/)
- [tqdm](https://github.com/tqdm/tqdm)
