import os
import hashlib
import tkinter as tk
from tkinter import filedialog

def file_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_duplicates(folder, extensions=None):
    if extensions:
        extensions = set(ext.lower() for ext in extensions)

    seen = {}
    for root, _, files in os.walk(folder):
        for name in files:
            if extensions and not name.lower().endswith(tuple(extensions)):
                continue  # skip non-matching files

            filepath = os.path.join(root, name)
            try:
                h = file_hash(filepath)
                if h in seen:
                    print(f"Duplicate found: {os.path.basename(filepath)} == {os.path.basename(seen[h])}")
                    os.remove(filepath)  # <- disabled for testing
                else:
                    seen[h] = filepath
            except Exception as e:
                print(f"Error with {filepath}: {e}")

# Show a popup for folder selection
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title="Select Target Folder")
    root.destroy()
    return folder_selected

# Usage
folder = select_folder()
if folder:
    remove_duplicates(
        folder,
        extensions=[".jpg", ".jpeg", ".png"]
    )
else:
    print("No folder selected.")

#python -m tkinter
#pip install tk
