import os
import hashlib
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from moviepy import VideoFileClip

def file_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def write_to_file(total_files, total_image_duplicate_count, keep_folder_path, total_image_files, total_relevant_video_files):
    report_file = os.path.join(keep_folder_path, "!Report.txt")

    file_exists_and_not_empty = (
        os.path.exists(report_file) and os.path.getsize(report_file) > 0
    )

    with open(report_file, "a", encoding="utf-8") as f:
        if file_exists_and_not_empty:
            f.write("\n")  # empty line before appending

        f.write(f"Folder Scanned: {folder}\n")
        f.write(f"Files checked: {total_files}\n")
        f.write(f"Image files checked: {total_image_files}\n")
        f.write(f"Relevent video files kept (>= 30s): {total_relevant_video_files}\n")
        f.write(f"Total IMAGE duplicates: {total_image_duplicate_count}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def remove_duplicates(folder, img_extensions=None, delete=False, vid_extensions=None):
    if img_extensions:
        img_extensions = set(ext.lower() for ext in img_extensions)

    if vid_extensions:
        vid_extensions = set(ext.lower() for ext in vid_extensions)

    seen = {}
    total_files = 0
    total_image_files = 0
    total_relevant_video_files = 0
    total_image_duplicate_count = 0

    keep_folder = os.path.join(folder, "!Keep")

    keep_folder_img_exists = False
    keep_folder_vid_exists = False

    # If !Keep folder does not exist create it 
    if os.path.isdir('!Keep') == False: 
        os.makedirs(keep_folder, exist_ok=True)

    # Check if keep_folder_img and _vid exists
    if os.path.isdir(f"{keep_folder}/Images"):
        keep_folder_img_exists = True

    if os.path.isdir(f"{keep_folder}/Videos"):
        keep_folder_vid_exists = True

    for root, directories, files in os.walk(folder):

        # Exclude any directory named "!Keep"
        directories[:] = [d for d in directories if d != '!Keep']

        for name in files:
            total_files += 1

            # This for check and only affects image files
            if img_extensions and name.lower().endswith(tuple(img_extensions)):
                total_image_files += 1
                source_folder_filepath = os.path.join(root, name)
                try:
                    h = file_hash(source_folder_filepath)
                    if h in seen:
                        # Delete true duplicates
                        total_image_duplicate_count += 1

                        if delete:
                            os.remove(source_folder_filepath)
                    else:
                        target_folder = f"{keep_folder}/Images"

                        if keep_folder_img_exists == False:
                            os.makedirs(target_folder, exist_ok=True)
                            keep_folder_img_exists = True

                        seen[h] = source_folder_filepath
                        # Move unique file to !Keep
                        dest_path = os.path.join(target_folder, name)

                        # Prevent overwriting if same name exists
                        base, ext = os.path.splitext(name)
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
                            counter += 1
                            
                        shutil.move(source_folder_filepath, dest_path)
                except Exception as e:
                    print(f"Error with: {e}")
            
            # Thish block of code only affects video files!
            if vid_extensions and name.lower().endswith(tuple(vid_extensions)):
                filepath = os.path.join(root, name)

                #continue   #UNCOMMENT THIS IF VIDEOS SHOULD BE DELETED IF THEY ARE UNDER 30 SEC

                #Delete video if it's less than 30 seconds
                with VideoFileClip(filepath) as clip:
                    if clip.duration <= 30:
                        os.remove(filepath)
                        continue

                total_relevant_video_files += 1

                target_folder = f"{keep_folder}/Videos"

                if keep_folder_vid_exists == False:
                    os.makedirs(target_folder, exist_ok=True)
                    keep_folder_vid_exists = True

                dest_path = os.path.join(target_folder, name)
                # Prevent overwriting if same name exists
                base, ext = os.path.splitext(name)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
                    counter += 1
                shutil.move(filepath, dest_path)

    write_to_file(total_files, total_image_duplicate_count, keep_folder, total_image_files, total_relevant_video_files)


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Target Folder")
    root.destroy()
    return folder_selected

# Usage
folder = select_folder()
if folder:
    remove_duplicates(folder, img_extensions=[".jpg", ".jpeg", ".png"], delete = True, vid_extensions=[".mp4", ".avi", ".mov", "wmv"])
else:
    print("No folder selected.")




#Rando package I just installed, no idea if it works or if I am going to keep it uet "pip install moviepy"