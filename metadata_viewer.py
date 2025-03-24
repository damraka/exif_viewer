from PIL import Image, ExifTags, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def choose_image():

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Choose an image file",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.bmp")]
    )
    return file_path

def format_datetime(datetime_str):
    try:

        return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S').strftime('%B %d, %Y, %H:%M:%S')
    except Exception:
        return datetime_str

def extract_exif(file_path):
    try:
        img = Image.open(file_path)
        exif_data = img._getexif()
        if not exif_data:
            print("No EXIF metadata found! Your image is keeping its secrets well.")
            return None


        processed_data = {}
        for tag, value in exif_data.items():
            decoded = ExifTags.TAGS.get(tag, tag)

            if decoded == 'DateTime':
                value = format_datetime(value)
            processed_data[decoded] = value
        return processed_data
    except Exception as e:
        print("Error reading image metadata:", e)
        return None

def print_exif(exif_data):
    if not exif_data:
        return
    print("---- EXIF Metadata ----")
    for key, value in exif_data.items():
        print(f"{key}: {value}")

def save_metadata(exif_data, output_file="exif_metadata.txt"):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for key, value in exif_data.items():
                f.write(f"{key}: {value}\n")
        print(f"Metadata saved to {output_file}")
    except Exception as e:
        print("Error saving metadata to file:", e)

def show_exif_gui(exif_data, image_path):
    if not exif_data:
        messagebox.showinfo("No EXIF", "No EXIF metadata found in the selected image!")
        return


    gui = tk.Tk()
    gui.title("Image EXIF Metadata")


    top_frame = tk.Frame(gui)
    top_frame.pack(pady=10)

    try:

        img = Image.open(image_path)
        img.thumbnail((150, 150))
        tk_img = ImageTk.PhotoImage(img)
        img_label = tk.Label(top_frame, image=tk_img)
        img_label.image = tk_img  
        img_label.pack(side="left", padx=10)
    except Exception as e:
        print("Error displaying thumbnail:", e)

    text_area = tk.Text(top_frame, height=20, width=50, wrap="word")
    text_area.pack(side="left", padx=10)
    for key, value in exif_data.items():
        text_area.insert(tk.END, f"{key}: {value}\n")
    text_area.config(state="disabled")

    close_button = tk.Button(gui, text="Close", command=gui.destroy)
    close_button.pack(pady=10)

    gui.mainloop()

if __name__ == "__main__":
    file_path = choose_image()
    if file_path:
        exif_data = extract_exif(file_path)
        if exif_data:

            print_exif(exif_data)

            save_metadata(exif_data)

            show_exif_gui(exif_data, file_path)
        else:
            print(" ")
    else:
        print("No file selected.")
