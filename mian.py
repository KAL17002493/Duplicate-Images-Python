import os
import hashlib
import shutil
import tkinter as tk
from tkinter import filedialog

def file_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_duplicates(folder, extensions=None, delete=False):
    if extensions:
        extensions = set(ext.lower() for ext in extensions)

    seen = {}
    total_files = 0
    duplicate_count = 0
    deleted_count = 0
    duplicate_list = []

    keep_folder = os.path.join(folder, "!Keep")
    os.makedirs(keep_folder, exist_ok=True)

    report_file = os.path.join(folder, "!Report.txt")

    for root, _, files in os.walk(folder):
        # Skip the !Keep folder to avoid infinite loop
        if root == keep_folder:
            continue  

        for name in files:
            if name == "!Report.txt":  # skip report file if re-running
                continue
            if extensions and not name.lower().endswith(tuple(extensions)):
                continue  

            total_files += 1
            filepath = os.path.join(root, name)
            try:
                h = file_hash(filepath)
                if h in seen:
                    duplicate_count += 1
                    duplicate_list.append(filepath)

                    if delete:
                        os.remove(filepath)
                        deleted_count += 1
                else:
                    seen[h] = filepath
                    # Move unique file to !Keep
                    dest_path = os.path.join(keep_folder, name)
                    # Prevent overwriting if same name exists
                    base, ext = os.path.splitext(name)
                    counter = 1
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(keep_folder, f"{base}_{counter}{ext}")
                        counter += 1
                    shutil.move(filepath, dest_path)

            except Exception as e:
                print(f"Error with {filepath}: {e}")

    # Write report
    with open(report_file, "w") as f:
        f.write(f"Folder Scanned: {folder}\n")
        f.write(f"Total images checked: {total_files}\n")
        f.write(f"Duplicates found: {duplicate_count}\n")
        f.write(f"Images deleted: {deleted_count}\n")
        f.write("\nList of duplicates:\n")
        for dup in duplicate_list:
            f.write(f"{dup}\n")

    print("\nSummary:")
    print(f"Total images checked: {total_files}")
    print(f"Duplicates found: {duplicate_count}")
    print(f"Images deleted: {deleted_count}")
    print(f"Report saved to: {report_file}")
    print(f"Unique files moved to: {keep_folder}")


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Target Folder")
    root.destroy()
    return folder_selected

# Usage
folder = select_folder()
if folder:
    remove_duplicates(
        folder,
        extensions=[".jpg", ".jpeg", ".png"],
        delete=True  # change to True to actually delete duplicates
    )
else:
    print("No folder selected.")
