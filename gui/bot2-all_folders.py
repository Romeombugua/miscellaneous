import tkinter as tk
from tkinter import scrolledtext, IntVar
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

def get_all_folders(driver):
    all_folders = []
    page = 1
    while True:
        if page == 1:
            driver.get(f"https://www.linkedin.com/sales/lists/people")
        else:
            driver.get(f"https://www.linkedin.com/sales/lists/people?page={page}")
        time.sleep(8)
        try:
            folders = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@data-control-name='view_list_detail']"))
            )

            if not folders:
                break

            for folder in folders:
                folder_name = folder.text.strip()
                folder_url = folder.get_attribute('href')
                all_folders.append((folder_name, folder_url))

            page += 1
        except TimeoutException:
            output_text.insert(tk.END, "Folder retrieval timed out!")
            break

    return all_folders

def get_paginated_url(base_url, page):
    # Parse the URL into its components
    url_parts = urlparse(current_url)

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

    return new_query

def start_script():
    click_limit = int(click_limit_entry.get())
    folder_name = folder_name_entry.get()
    clicked_count = 0
    clicked_names = set()
    output_text.insert(tk.END, f"Starting bot with a target of: {click_limit} leads\n")

    if click_limit > 20:
        output_text.insert(tk.END, "Input cannot be greater than 20!\n")
        return

    # Download the clicked_names.txt file from Drive
    my_drive = MyDrive()
    output_text.insert(tk.END, "Downloading file from Drive...\n")
    my_drive.download_file('clicked_names.txt', './')
    output_text.insert(tk.END, "Finished downloading file from Drive...\n")

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

    output_text.insert(tk.END, "Retrieving all folders...\n")
    all_folders = get_all_folders(driver)
    output_text.insert(tk.END, f"Found {len(all_folders)} folders.\n")

    folder_url = None
    for name, url in all_folders:
        if name.lower() == folder_name.lower():
            folder_url = url
            break

    if not folder_url:
        output_text.insert(tk.END, f"Folder '{folder_name}' not found. Exiting...\n")
        driver.quit()
        return

    output_text.insert(tk.END, f"Using folder: {folder_name}\n")

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
                    current_url = get_paginated_url(folder_url, n)
                    driver.get(current_url)
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
                    output_text.insert(tk.END, f"Mismatch on page {n}. Moving to the next page.\n")
                    continue

                for i in range(1, len(buttons)):
                    try:
                        name = names[i - 1].text
                        if name in clicked_names:
                            # output_text.insert(tk.END, f"Skipping {name}, already clicked.\n")
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

                            send_button = driver.find_element(By.XPATH, "//button[starts-with(@class, 'ember-view _button_ps32ck _small_ps32ck _primary_ps32ck _left_ps32ck _container_iq15dg ml3')]")
                            time.sleep(8)
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

                            output_text.insert(tk.END, f"Just messaged {name}\n")

                            if clicked_count >= click_limit:
                                output_text.insert(tk.END, f"Leads limit of {click_limit} reached. Exiting...\n")
                                driver.quit()
                                # backup_to_drive()
                                return

                    except Exception as e:
                        # output_text.insert(tk.END, f"Error with button index {i}: {str(e)}\n")
                        continue


    except Exception as e:
        output_text.insert(tk.END, f"An error occurred during automation: {str(e)}\n")
    finally:
        if driver:
            driver.quit()
        output_text.insert(tk.END, "Messaging has been completed.\nSyncing changes with Drive...\n")
        try:
            sync_file()
        except Exception as e:
            output_text.insert(tk.END, f"An error occurred during file upload or backup: {str(e)}\n")

        output_text.insert(tk.END, "Process completed successfully!\n")

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

# Create a checkbox to toggle between default and custom message
use_custom_message = IntVar()
tk.Checkbutton(root, text="Use custom message", variable=use_custom_message, command=toggle_custom_message).pack()

# Create a text area for custom message (initially hidden)
custom_message_label = tk.Label(root, text="Custom message (use {first_name} for personalization):")
custom_message_text = scrolledtext.ScrolledText(root, width=50, height=5)

# Create a scrolled text area to display messages
output_text = scrolledtext.ScrolledText(root, width=50, height=15)
output_text.pack()

# Create a start button to begin the script with styling
start_button = tk.Button(root,
                         text="Start Bot",
                         command=start_script,
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
