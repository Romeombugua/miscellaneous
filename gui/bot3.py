import tkinter as tk
from tkinter import scrolledtext, IntVar, filedialog
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
    click_limit = int(click_limit_entry.get())
    folder_name = folder_name_entry.get()
    clicked_count = 0
    clicked_names = set()
    update_output(f"Starting bot with a target of: {click_limit} leads")

    if click_limit > 20:
        update_output("Input cannot be greater than 20!")
        return

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
    username.send_keys("alan@meditouch.co.il")
    time.sleep(4)
    password.send_keys('Alan_770770770')
    time.sleep(4)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
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
                            items[0].click()
                            time.sleep(7)

                            message_area = driver.find_element(By.TAG_NAME, 'textarea')
                            message_area.click()
                            time.sleep(3)

                            message = message_template.format(first_name=first_name)
                            message_area.send_keys(message)

                            time.sleep(5)
                            # Add attachment if selected
                            if attachment_path:
                                file_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "attachment"))
                                )
                                file_input.send_keys(attachment_path)
                                time.sleep(5)

                            send_button = driver.find_element(By.XPATH, "//button[starts-with(@class, 'ember-view _button_ps32ck _small_ps32ck _primary_ps32ck _left_ps32ck _container_iq15dg ml3')]")

                            # if send_button:
                            #     send_button.click()

                            time.sleep(3)

                            close_button = WebDriverWait(driver, 7).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@data-control-name, 'overlay.close_overlay')]"))
                            )
                            close_button.click()

                            time.sleep(5)

                            file.write(name + '\n')
                            clicked_names.add(name)
                            clicked_count += 1

                            update_output(f"Just messaged {name}")

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
tk.Button(root, text="Select Attachment", command=select_attachment).pack()
attachment_label = tk.Label(root, text="No file selected")
attachment_label.pack()

# Create a checkbox to toggle between default and custom message
use_custom_message = IntVar()
tk.Checkbutton(root, text="Use custom message", variable=use_custom_message, command=toggle_custom_message).pack()

# Create a text area for custom message (initially hidden)
custom_message_label = tk.Label(root, text="Custom message (use {first_name} for personalization):")
custom_message_text = scrolledtext.ScrolledText(root, width=50, height=5)

# Create a scrolled text area to display messages
output_text = scrolledtext.ScrolledText(root, width=50, height=15)
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
