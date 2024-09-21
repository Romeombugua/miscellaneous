import tkinter as tk
from tkinter import scrolledtext, IntVar, filedialog, simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import os
from googleapiclient.http import MediaIoBaseDownload
import io
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import threading

class MyDrive:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)

    def get_file_id(self, filename):
        results = self.service.files().list(
            q=f"name='{filename}'",
            spaces='drive',
            fields='files(id, name)').execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']
        return None

    def download_file(self, filename, local_path):
        file_id = self.get_file_id(filename)
        if file_id:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            with open(os.path.join(local_path, filename), 'wb') as f:
                f.write(fh.read())
            output_text.insert(tk.END, f"Downloaded {filename} from Drive\n")
        else:
            output_text.insert(tk.END, f"{filename} not found on Drive. Starting with empty file.\n")
            open(os.path.join(local_path, filename), 'w').close()

    def upload_file(self, filename, path):
        folder_id = "1MQ7aF93ic10hA1b8KCfXtGjRzZkxFDFM"
        media = MediaFileUpload(f"{path}{filename}")
        response = self.service.files().list(
                                        q=f"name='{filename}' and parents='{folder_id}'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=None).execute()
        if len(response['files']) == 0:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            output_text.insert(tk.END, f"A new file was created {file.get('id')}\n")
        else:
            for file in response.get('files', []):
                update_file = self.service.files().update(
                    fileId=file.get('id'),
                    media_body=media,
                ).execute()
                output_text.insert(tk.END, f'Updated File {filename}\n')


# class LoginWindow(simpledialog.Dialog):
#     def body(self, master):
#         tk.Label(master, text="Username:").grid(row=0)
#         tk.Label(master, text="Password:").grid(row=1)
#
#         self.username_entry = tk.Entry(master)
#         self.password_entry = tk.Entry(master, show="*")
#
#         self.username_entry.grid(row=0, column=1)
#         self.password_entry.grid(row=1, column=1)
#         return self.username_entry  # initial focus
#
#     def apply(self):
#         self.result = (self.username_entry.get(), self.password_entry.get())
class LoginWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Login")
        self.geometry("300x250")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Creating and packing widgets
        tk.Label(self, text="Username:").pack(pady=(20, 5))
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(padx=10)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(padx=10)

        # Add a checkbox to toggle password visibility
        self.show_password = tk.BooleanVar()
        self.show_password_checkbox = tk.Checkbutton(
            self,
            text="Show password",
            variable=self.show_password,
            command=self.toggle_password_visibility
        )
        self.show_password_checkbox.pack(pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.on_login)
        self.login_button.pack(pady=(10, 20))

        self.result = None

    def toggle_password_visibility(self):
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            self.result = (username, password)
            self.destroy()
        else:
            tk.messagebox.showerror("Error", "Please enter both username and password.")

    def on_close(self):
        self.result = None
        self.destroy()

def get_credentials():
    # Create the login window and wait for it to close
    login_window = LoginWindow()
    login_window.grab_set()  # Ensure only this window is interactive
    login_window.wait_window()  # Wait for the window to close

    return login_window.result  # Return the entered credentials or None if canceled


def toggle_custom_message():
    if use_custom_message.get():
        custom_message_label.pack()
        custom_message_text.pack()
    else:
        custom_message_label.pack_forget()
        custom_message_text.pack_forget()

def sync_file():
    output_text.insert(tk.END, "Starting Google Drive...\n")
    path = "./"
    # files = os.listdir(path)
    my_drive = MyDrive()
    # for item in files:
    item = "clicked_names.txt"
    my_drive.upload_file(item, path)
    output_text.insert(tk.END, "Google Drive syncing completed.\n")


def get_folder_url(driver, target_folder_name):
    page = 1
    while True:
        url = f"https://www.linkedin.com/sales/lists/people"
        if page > 1:
            url = f"https://www.linkedin.com/sales/lists/people?page={page}"

        driver.get(url)
        time.sleep(8)
        try:
            folders = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@data-control-name='view_list_detail']"))
            )

            if not folders:
                break

            for folder in folders:
                folder_name = folder.text.strip()
                if folder_name.lower() == target_folder_name.lower():
                    return folder.get_attribute('href')

            page += 1
        except TimeoutException:
            output_text.insert(tk.END, "Folder retrieval timed out!\n")
            break

    return None


def get_paginated_url(base_url, page):
    # Parse the URL into its components
    url_parts = urlparse(base_url)

    # Convert the query string to a dictionary
    query_params = parse_qs(url_parts.query)
        # Create a new dictionary to ensure the page parameter is first
    updated_query_params = {'page': page}
    updated_query_params.update(query_params)

    # Rebuild the query string
    new_query = urlencode(updated_query_params, doseq=True)

    # Rebuild the URL with the new query string
    new_url = urlunparse((
        url_parts.scheme,
        url_parts.netloc,
        url_parts.path,
        url_parts.params,
        new_query,
        url_parts.fragment
    ))

    return new_url
# def countdown_timer(duration):
#     for remaining in range(duration, 0, -1):
#         update_output(f"Time remaining: {remaining} seconds")
#         time.sleep(1)
#     update_output("Wait time complete. Proceeding...")

def update_output(message):
    output_text.insert(tk.END, message + "\n")
    output_text.see(tk.END)
    root.update_idletasks()

def start_script_thread():
    start_button.config(text="Running...", bg='white', fg='#4CAF50', state=tk.DISABLED)
    threading.Thread(target=run_script, daemon=True).start()

def run_script():
    try:
        start_script()
    finally:
        root.after(0, reset_button)

def reset_button():
    start_button.config(text="Start Bot", bg='#4CAF50', fg='white', state=tk.NORMAL)

def select_attachment():
    global attachment_path
    attachment_path = filedialog.askopenfilename(
        filetypes=[
            ("Document files", "*.doc *.docx *.xls *.xlsx *.pdf *.txt *.rtf *.odf *.html *.csv"),
            ("Image files", "*.png *.jpg")
        ]
    )
    if attachment_path:
        attachment_label.config(text=f"Selected: {os.path.basename(attachment_path)}")
    else:
        attachment_label.config(text="No file selected")
def start_script():
    credentials = get_credentials()
    if not credentials:
        update_output("Login cancelled. Bot terminated.")
        return

    username_input, password_input = credentials


    click_limit = int(click_limit_entry.get())
    folder_name = folder_name_entry.get()
    clicked_count = 0
    clicked_names = set()
    update_output(f"Starting bot with a target of: {click_limit} leads")


    # Download the clicked_names.txt file from Drive
    my_drive = MyDrive()
    update_output("Downloading file from Drive...")
    my_drive.download_file('clicked_names.txt', './')
    update_output("Finished downloading file from Drive...")

    if use_custom_message.get():
        message_template = custom_message_text.get("1.0", tk.END).strip()
    else:
        message_template = "Hi, {first_name}.\n\nAfter assessment, it is key to train balance and gait.\nUsing multi-directional gait perturbations with the balanceTutor is a fun and effective way to improve balance and gait.\nhttps://bit.ly/423Ngx9"

    driver = webdriver.Firefox()
    driver.get('https://www.linkedin.com/login')
    time.sleep(5)

    username = driver.find_element(By.XPATH, "//input[@name='session_key']")
    password = driver.find_element(By.XPATH, "//input[@name='session_password']")

    time.sleep(5)
    username.send_keys(username_input)
    time.sleep(4)
    password.send_keys(password_input)
    time.sleep(4)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # If 2FA checkbox is checked, wait for 30 seconds
    if two_fa_var.get():
        update_output("Waiting for 1 minute to allow you to verify my session ;) \n")
        time.sleep(60)
        # timer_thread = threading.Thread(target=countdown_timer, args=(60,))
        # timer_thread.start()
        # timer_thread.join()

    else:
        time.sleep(5)

    update_output(f"Searching for folder: {folder_name}")
    folder_url = get_folder_url(driver, folder_name)

    if not folder_url:
        update_output(f"Folder '{folder_name}' not found. Exiting...")
        driver.quit()
        return

    update_output(f"Found folder: {folder_name}")

    pages = 10

    try:
        with open('clicked_names.txt', 'a+') as file:
            file.seek(0)
            for line in file:
                clicked_names.add(line.strip())

            for n in range(1, pages + 1):
                if n == 1:
                    driver.get(folder_url)
                else:
                    driver.get(f"{folder_url}?page={n}&sortCriteria=CREATED_TIME&sortOrder=DESCENDING")
                time.sleep(15)

                buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'artdeco-dropdown__trigger'))
                )
                degrees = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//li[starts-with(@class,'list-lead-detail__degree-badge')]//span[@class='a11y-text']"))
                )
                names = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[@data-anonymize='person-name']"))
                )

                if len(buttons) - 1 != len(degrees) or len(degrees) != len(names):
                    update_output(f"Mismatch on page {n}. Moving to the next page.")
                    continue

                for i in range(1, len(buttons)):
                    try:
                        name = names[i - 1].text
                        if name in clicked_names:
                            continue

                        first_name = name.split(" ")[0]
                        if degrees[i - 1].text == "1st degree contact":
                            trigger_button = buttons[i]
                            trigger_button.click()
                            time.sleep(3)

                            items = WebDriverWait(driver, 3).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, 'artdeco-dropdown__item'))
                            )
                            text = "Message"
                            for item in items:
                                if text.lower() in item.text.lower():
                                    item.click()
                                    break
                                else:
                                    update_output(f"Couldn't message {name}")
                            time.sleep(7)
                            profile_images = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, "//img[starts-with(@class,'_entity_shcpvh _person_shcpvh _medium_shcpvh ml4 absolute z-index-1')]"))
                            )


                            # Check if all image sources are the same
                            image_srcs = [img.get_attribute('src') for img in profile_images]
                            if len(set(image_srcs)) == 1:
                                # All images are the same, proceed with messaging
                                message_area = driver.find_element(By.TAG_NAME, 'textarea')
                                message_area.click()


                                message = message_template.format(first_name=first_name)
                                message_area.send_keys(message)

                                time.sleep(5)

                                # Add attachment if selected
                                if attachment_path:
                                    norm_path = os.path.normpath(attachment_path)
                                    file_input = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.ID, "attachment"))
                                    )
                                    file_input.send_keys(norm_path)
                                    time.sleep(5)

                                # Optional: Click the send button if you want to send the message
                                send_button = driver.find_element(By.XPATH, "//button[starts-with(@class, 'ember-view _button_ps32ck _small_ps32ck _primary_ps32ck _left_ps32ck _container_iq15dg ml3')]")

                                if send_button:
                                    send_button.click()

                                time.sleep(5)  # Wait for the message to send (if applicable)
                                                    # Close the message form
                                close_button = WebDriverWait(driver, 7).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@data-control-name, 'overlay.close_overlay')]"))
                                )
                                close_button.click()

                                time.sleep(5)  # Wait for the form to close before moving to the next dropdown button
                                update_output(f"Just messaged {name}")
                            else:
                                # Images are different, close the message form and try "Add to another list"
                                close_button = WebDriverWait(driver, 7).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@data-control-name, 'overlay.close_overlay')]"))
                                )
                                close_button.click()
                                time.sleep(5)

                                # Click the dropdown button again
                                trigger_button.click()
                                time.sleep(3)

                                # Check if "Add to another list" option exists and click it
                                items = WebDriverWait(driver, 3).until(
                                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'artdeco-dropdown__item'))
                                )

                                try:
                                    text = "Add to another list"
                                    for item in items:
                                        if text.lower() in item.text.lower():
                                            item.click()
                                            break
                                        else:
                                            update_output(f"Couldn't move {name}")
                                    time.sleep(2)
                                    answered_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class, 'artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view entity-lists-ta__select-list Sans-14px-black-90% button--unstyled p1')]//span[contains(@class, 'artdeco-button__text')]//b[contains(text(), 'Answered')]"))
                                    )
                                    answered_button.click()

                                    time.sleep(3)
                                        # Find the div containing the buttons
                                    list_container = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'entity-lists-ta entity-lists-ta__ta-container flex flex-wrap')]"))
                                    )
                                    # Find all buttons within the container
                                    list_buttons = list_container.find_elements(By.XPATH, ".//button")
                                    for button in list_buttons:
                                        # Find the span element within the button
                                        span_element = button.find_element(By.TAG_NAME, "span")

                                        # Check if the span contains the text "Answered"
                                        if "Answered" not in span_element.text:
                                            # Click the button
                                            button.click()
                                            time.sleep(2)  # Short delay to allow the UI to update

                                    save_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@class, 'artdeco-button artdeco-button--2 artdeco-button--pro artdeco-button--primary ember-view edit-entity-lists-modal__save-btn ml1')]"))
                                    )
                                    if save_button:
                                        save_button.click()
                                        update_output(f"Added {name} to the 'Answered' list.")
                                    time.sleep(5)
                                except Exception as e:
                                    update_output(f"An error occurred: {str(e)}")

                            file.write(name + '\n')
                            clicked_names.add(name)
                            clicked_count += 1


                            if clicked_count >= click_limit:
                                update_output(f"Leads limit of {click_limit} reached. Exiting...")
                                driver.quit()
                                return

                    except Exception as e:
                        update_output(f"Error: {str(e)}")
                        continue

    except Exception as e:
        update_output(f"An error occurred during automation: {str(e)}")
    finally:
        if driver:
            driver.quit()
        update_output("Messaging has been completed.\nSyncing changes with Drive...")
        try:
            sync_file()
        except Exception as e:
            update_output(f"An error occurred during file upload or backup: {str(e)}")

        update_output("Process completed successfully!")

# Initialize the Tkinter root window
root = tk.Tk()
root.title("Automation Bot")

# Create the input field for click limit
tk.Label(root, text="How many leads do you want to message:").pack()
click_limit_entry = tk.Entry(root)
click_limit_entry.pack()

# Create the input field for folder name
tk.Label(root, text="Enter the name of the folder:").pack()
folder_name_entry = tk.Entry(root)
folder_name_entry.pack()

# Add file attachment selection
attachment_path = ""
tk.Button(root, text="Select Attachment", command=select_attachment, bg='#4CAF50',fg='white').pack()
attachment_label = tk.Label(root, text="No file selected")
attachment_label.pack()

# Create a checkbox to toggle between default and custom message
use_custom_message = IntVar()
tk.Checkbutton(root, text="Use custom message", variable=use_custom_message, command=toggle_custom_message).pack()

# Create and pack the 2FA checkbox
two_fa_var = tk.BooleanVar()
two_fa_checkbox = tk.Checkbutton(root, text="Enable 2FA wait time (1 minute)", variable=two_fa_var)
two_fa_checkbox.pack()

# Create a text area for custom message (initially hidden)
custom_message_label = tk.Label(root, text="Custom message (use {first_name} for personalization):")
custom_message_text = scrolledtext.ScrolledText(root, width=75, height=5)

# Create a scrolled text area to display messages
output_text = scrolledtext.ScrolledText(root, width=75, height=15)
output_text.insert(tk.END, "Note: Do not type in this box. It will display messages from the bot.\nIf you want to type a custom message, check the 'use_custom_message' checkbox above and another field will appear. Cheers :)\nIf you have enabled 2 factor authentication on LinkedIn, please check the Enable 2FA checkbox\n\n")
output_text.pack()

# Modify the start button to use the threaded version
start_button = tk.Button(
    root,
    text="Start Bot",
    command=start_script_thread,
    bg='#4CAF50',
    fg='white',
    font=('Helvetica', 12, 'bold'),
    padx=10,
    pady=5,
    relief='raised',
    borderwidth=3
)
start_button.pack(pady=10)

# Start the Tkinter main loop
if __name__ == '__main__':
    try:
        root.mainloop()
    except Exception as e:
        exit()
