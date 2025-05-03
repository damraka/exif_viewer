from PIL import Image, ExifTags, ImageTk
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import piexif
from datetime import datetime

def choose_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Choose an image file",
        filetypes=[("JPEG files", "*.jpg;*.jpeg")]
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
            print("No EXIF metadata found.")
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



def show_exif_gui(exif_data, image_path):
    global tree, exif_dict, current_file_path
    if not exif_data:
        messagebox.showinfo("No EXIF", "No EXIF metadata found in the selected image!")
        return

    current_file_path = image_path
    exif_dict = piexif.load(image_path)

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

    right_frame = tk.Frame(top_frame)
    right_frame.pack(side="left", padx=10)

    tree = ttk.Treeview(right_frame, columns=("Tag", "Value"), show="headings", height=20)
    tree.heading("Tag", text="Tag")
    tree.heading("Value", text="Value")
    tree.pack(fill="both", expand=True)

    for ifd in exif_dict:
        if isinstance(exif_dict[ifd], dict):
            for tag, value in exif_dict[ifd].items():
                tag_name = piexif.TAGS[ifd][tag]["name"]
                try:
                    display_value = value.decode("utf-8") if isinstance(value, bytes) else str(value)
                except:
                    display_value = str(value)
                tree.insert("", "end", values=(f"{ifd}:{tag_name}", display_value))

    def on_double_click(event):
        item = tree.selection()[0]
        column = tree.identify_column(event.x)
        if column != "#2":
            return
        tag_str, current_value = tree.item(item, "values")
        ifd, tag_name = tag_str.split(":", 1)
        new_value = simpledialog.askstring("Edit Value", f"New value for {tag_name}:", initialvalue=current_value)
        if new_value is not None:
            tree.set(item, column="Value", value=new_value)
            try:
                for tag_num, tag_info in piexif.TAGS[ifd].items():
                    if tag_info["name"] == tag_name:
                        
                        type_name = tag_info.get("type_name", None)
                        
                        
                        if not type_name:
                            if tag_name in ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]:
                                
                                encoded = new_value.encode("utf-8")
                            else:
                                messagebox.showwarning("Warning", f"'type_name' not found for tag: {tag_name}. Skipping update.")
                                return 
                        else:
                            
                            if type_name in ("ASCII", "Undefined"):
                                encoded = new_value.encode("utf-8")
                            elif type_name in ("Short", "Long"):
                                encoded = int(new_value)
                            elif type_name == "Rational":
                                numerator, denominator = map(int, new_value.split("/"))
                                encoded = (numerator, denominator)
                            else:
                                raise ValueError(f"Unsupported type_name: {type_name}")
                        
                        exif_dict[ifd][tag_num] = encoded
                        break
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update tag:\n{e}")

    tree.bind("<Double-1>", on_double_click)

    def save_exif():
        try:
            exif_bytes = piexif.dump(exif_dict)
            img = Image.open(current_file_path)
            output_path = current_file_path.replace(".jpg", "_edited.jpg")
            img.save(output_path, "jpeg", exif=exif_bytes)
            messagebox.showinfo("Success", f"EXIF updated and saved to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Saving failed:\n{e}")

    save_button = tk.Button(gui, text="Save EXIF", command=save_exif)
    save_button.pack(pady=5)

    close_button = tk.Button(gui, text="Close", command=gui.destroy)
    close_button.pack(pady=5)

    gui.mainloop()

if __name__ == "__main__":
    file_path = choose_image()
    if file_path:
        exif_data = extract_exif(file_path)
        if exif_data:
            print_exif(exif_data)
            show_exif_gui(exif_data, file_path)
        else:
            print("No EXIF metadata found.")
    else:
        print("No file selected.")
