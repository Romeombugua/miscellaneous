import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
import os
from tkinter import scrolledtext, IntVar


class MyDrive():
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/drive']
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, page_size=10):
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

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
            print(f"A new file was created {file.get('id')}")

        else:
            for file in response.get('files', []):
                # Process change

                update_file = self.service.files().update(
                    fileId=file.get('id'),
                    media_body=media,
                ).execute()
                print(f'Updated File')

def sync_changes():
    path = "./file_sync/"
    files = os.listdir(path)
    my_drive = MyDrive()
    #my_drive.list_files()

    for item in files:
        my_drive.upload_file(item, path)


def start_script():
    # Get the click limit from the input field
    click_limit = int(click_limit_entry.get())
    clicked_count = 0
    clicked_names = set()
    output_text.insert(tk.END, f"Starting bot with a target of: {click_limit} leads\n")


    # Set up the WebDriver
    # options = webdriver.ChromeOptions()
    # options.add_argument(--)
    driver = webdriver.Firefox()
    driver.get('https://www.linkedin.com/login')
    time.sleep(5)

    # Log in
    username = driver.find_element(By.XPATH, "//input[@name='session_key']")
    password = driver.find_element(By.XPATH, "//input[@name='session_password']")
    
    time.sleep(5)
    
    username.send_keys("alan@meditouch.co.il")
    
    time.sleep(4)
    
    password.send_keys('Alan_770770770')
    
    time.sleep(4)
    
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    time.sleep(5)

    pages = 10  # Number of pages to navigate

    # Open the file in append mode to keep track of clicked names
    with open('clicked_names.txt', 'a+') as file:
        # Load previously clicked names into a set to avoid duplicates
        file.seek(0)
        for line in file:
            clicked_names.add(line.strip())
        
        for n in range(1, pages + 1):
            if n == 1:
                driver.get("https://www.linkedin.com/sales/lists/people/7152301656594919424?sortCriteria=CREATED_TIME&sortOrder=DESCENDING")
            else:
                driver.get(f"https://www.linkedin.com/sales/lists/people/7152301656594919424?page={n}&sortCriteria=CREATED_TIME&sortOrder=DESCENDING")
            time.sleep(15)
            
            # Locate all dropdown buttons
            buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'artdeco-dropdown__trigger'))
            )
                        
            # Locate all degree spans
            degrees = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[starts-with(@class,'list-lead-detail__degree-badge')]//span[@class='a11y-text']"))
            )
                        
            # Locate all names
            names = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@data-anonymize='person-name']"))
            )
                        
            # Check if the number of spans and buttons are equal
            if len(buttons) - 1 != len(degrees) or len(degrees) != len(names):
                output_text.insert(tk.END, f"Mismatch on page {n}. Moving to the next page.\n")
                continue
            
            # Loop through buttons starting from index 1
            for i in range(1, len(buttons)):
                try:
                    name = names[i - 1].text
                    if name in clicked_names:
                        output_text.insert(tk.END, f"Skipping {name}, already clicked.\n")
                        continue

                    first_name = name.split(" ")[0]
                    # Check if the corresponding span has "1st degree contact"
                    if degrees[i - 1].text == "1st degree contact":
                        # Click the dropdown button to open the menu
                        trigger_button = buttons[i]
                        trigger_button.click()

                        time.sleep(3)
                        
                        # Wait for dropdown items to be visible and locate the first item ("Message")
                        items = WebDriverWait(driver, 3).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'artdeco-dropdown__item'))
                        )
                        items[0].click()  # Click the first item (Message)
            
                        time.sleep(7)
            
                        # Locate and click the message textarea (or other field as required)
                        message_area = driver.find_element(By.TAG_NAME, 'textarea')
                        message_area.click()
                        
                        time.sleep(3)
                        # Type a message into the textarea
                        message_area.send_keys(f"Hi, {first_name}.\n\nAfter assessment, it is key to train balance and gait.\nUsing multi-directional gait perturbations with the balanceTutor is a fun and effective way to improve balance and gait.\nhttps://bit.ly/423Ngx9")
            
                        # Click the send button if you want to send the message
                        send_button = driver.find_element(By.XPATH, "//button[starts-with(@class, 'ember-view _button_ps32ck _small_ps32ck _primary_ps32ck _left_ps32ck _container_iq15dg ml3')]")
                        time.sleep(8)
                        if send_button:
                            send_button.click()
            
                        time.sleep(3)
            
                        # Close the message form
                        close_button = WebDriverWait(driver, 7).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@data-control-name, 'overlay.close_overlay')]"))
                        )
                        close_button.click()
            
                        time.sleep(5)
                        
                        # Record the clicked name and increment the count
                        file.write(name + '\n')
                        clicked_names.add(name)
                        clicked_count += 1
                        
                        # Update the GUI with progress
                        output_text.insert(tk.END, f"Just messaged {name}\n")
                        
                        if clicked_count >= click_limit:
                            output_text.insert(tk.END, f"Leads limit of {click_limit} reached. Exiting...\n")
                            driver.quit()
                            return
        
                except Exception as e:
                    output_text.insert(tk.END, f"Error with button index {i}: {str(e)}\n")
                    continue

    driver.quit()
    output_text.insert(tk.END, "The process has been completed. Now syncing changes...\n")
    sync_changes()
    output_text.insert(tk.END, "Finished syncing changes...\n")

# Initialize the Tkinter root window
root = tk.Tk()
root.title("Automation Bot")

# Create the input field for click limit
tk.Label(root, text="How many leads do you want to message:").pack()
click_limit_entry = tk.Entry(root)
click_limit_entry.pack()


# Create a scrolled text area to display messages
output_text = scrolledtext.ScrolledText(root, width=50, height=15)
output_text.pack()

# Create a start button to begin the script
start_button = tk.Button(root, text="Start Bot", command=start_script)
start_button.pack()

# Start the Tkinter main loop
if __name__ == '__main__':
    try:
        root.mainloop()
    except Exception as e:
        exit()
