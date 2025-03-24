from PIL import Image, ExifTags
import tkinter as tk
from tkinter import filedialog

def choose_image():

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Choose an image file",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.bmp")]
    )
    return file_path

def print_exif(file_path):
    try:
        img = Image.open(file_path)
        exif_data = img._getexif()
        if not exif_data:
            print("No EXIF metadata found!")
            return

        for tag, value in exif_data.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            print(f"{decoded}: {value}")
    except Exception as e:
        print("Error reading image metadata:", e)

if __name__ == "__main__":
    file_path = choose_image()
    if file_path:
        print_exif(file_path)
    else:
        print("No file selected.")
