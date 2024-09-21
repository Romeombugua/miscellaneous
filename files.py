import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class ImageUploaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Uploader")
        master.geometry("400x200")

        self.label = tk.Label(master, text="Select an image file to upload:")
        self.label.pack(pady=10)

        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(master, textvariable=self.path_var, width=50)
        self.path_entry.pack(pady=5)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.upload_button = tk.Button(master, text="Upload", command=self.upload_image)
        self.upload_button.pack(pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        self.path_var.set(filename)

    def upload_image(self):
        path = self.path_var.get()
        if not path:
            messagebox.showerror("Error", "Please select an image file.")
            return

        try:
            driver = webdriver.Firefox()
            driver.implicitly_wait(10)
            driver.get("https://imgbb.com/upload")

            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "anywhere-upload-input"))
            )

            # Convert the path to the correct format for the current OS
            path = os.path.normpath(path)

            upload_input.send_keys(path)
            messagebox.showinfo("Success", "Image upload initiated. Please check the browser window.")

            # Keep the browser window open for 10 seconds
            time.sleep(10)
            driver.quit()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    gui = ImageUploaderGUI(root)
    root.mainloop()
