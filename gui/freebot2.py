import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os

class LinkedInAutomationGUI:
    def __init__(self, master):
        self.master = master
        master.title("LinkedIn Automation")
        master.geometry("500x700")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.login_frame = ttk.Frame(self.notebook)
        self.main_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.main_frame, text="Automation")

        self.show_password = tk.BooleanVar()  # Variable to track password visibility
        self.attachment_path = ""  # Variable to store the file path

        self.create_login_widgets()
        self.create_main_widgets()

        self.driver = None

    def create_login_widgets(self):
        ttk.Label(self.login_frame, text="LinkedIn Login", font=("Arial", 16)).pack(pady=10)

        ttk.Label(self.login_frame, text="Email:").pack(pady=5)
        self.email_entry = ttk.Entry(self.login_frame, width=30)
        self.email_entry.pack(pady=5)

        ttk.Label(self.login_frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Button to toggle password visibility
        self.show_password_button = ttk.Checkbutton(self.login_frame, text="Show Password", variable=self.show_password, command=self.toggle_password_visibility)
        self.show_password_button.pack(pady=5)

        ttk.Button(self.login_frame, text="Login", command=self.login).pack(pady=20)

    def toggle_password_visibility(self):
        if self.show_password.get():
            self.password_entry.config(show="")  # Show password
        else:
            self.password_entry.config(show="*")  # Hide password

    def create_main_widgets(self):
        ttk.Label(self.main_frame, text="Automation Settings", font=("Arial", 16)).pack(pady=10)

        self.campaign1_var = tk.BooleanVar()
        self.campaign2_var = tk.BooleanVar()

        ttk.Checkbutton(self.main_frame, text="Campaign 1", variable=self.campaign1_var).pack(pady=5)
        ttk.Checkbutton(self.main_frame, text="Campaign 2", variable=self.campaign2_var).pack(pady=5)

        ttk.Label(self.main_frame, text="Note: Use {first_name} to address the recipient. \n Example: Hi {first_name}").pack(pady=5)
        ttk.Label(self.main_frame, text="Campaign 1 Message:").pack(pady=5)
        self.campaign1_message = tk.Text(self.main_frame, height=3, width=40)
        self.campaign1_message.pack(pady=5)

        ttk.Label(self.main_frame, text="Campaign 2 Message:").pack(pady=5)
        self.campaign2_message = tk.Text(self.main_frame, height=3, width=40)
        self.campaign2_message.pack(pady=5)

        # Attachment feature
        ttk.Label(self.main_frame, text="Attachment:").pack(pady=5)
        ttk.Button(self.main_frame, text="Browse File", command=self.browse_file).pack(pady=5)
        self.attachment_label = ttk.Label(self.main_frame, text="No file selected")
        self.attachment_label.pack(pady=5)

        ttk.Label(self.main_frame, text="Number of Connections:").pack(pady=5)
        self.connections_entry = ttk.Entry(self.main_frame, width=10)
        self.connections_entry.pack(pady=5)

        ttk.Button(self.main_frame, text="Start Automation", command=self.start_automation).pack(pady=20)

    def browse_file(self):
        """ Open a file dialog to choose an attachment """
        self.attachment_path = filedialog.askopenfilename()
        if self.attachment_path:
            self.attachment_label.config(text=self.attachment_path)
        else:
            self.attachment_label.config(text="No file selected")

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email and password:
            try:
                self.driver = webdriver.Firefox()
                self.driver.get('https://www.linkedin.com/login')

                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='session_key']")))

                username = self.driver.find_element("xpath", "//input[@name='session_key']")
                password_field = self.driver.find_element("xpath", "//input[@name='session_password']")

                username.send_keys(email)
                time.sleep(2)
                password_field.send_keys(password)
                time.sleep(2)

                self.driver.find_element("xpath", "//button[@type='submit']").click()
                time.sleep(3)

                self.notebook.select(1)
                messagebox.showinfo("Login Successful", "You have successfully logged in to LinkedIn")
            except Exception as e:
                messagebox.showerror("Login Error", f"An error occurred during login: {str(e)}")
                if self.driver:
                    self.driver.quit()
        else:
            messagebox.showerror("Login Error", "Please enter both email and password")

    def start_automation(self):
        campaign1 = self.campaign1_var.get()
        campaign2 = self.campaign2_var.get()
        campaign1_message = self.campaign1_message.get("1.0", tk.END).strip()
        campaign2_message = self.campaign2_message.get("1.0", tk.END).strip()
        connections = self.connections_entry.get()

        if not connections.isdigit():
            messagebox.showerror("Error", "Please enter a valid number of connections")
            return

        if not self.driver:
            messagebox.showerror("Error", "Please log in first")
            return

        # Start the automation in a separate thread
        threading.Thread(target=self.run_automation, args=(int(connections), campaign1, campaign2, campaign1_message, campaign2_message), daemon=True).start()

    def run_automation(self, num_connections, campaign1, campaign2, campaign1_message, campaign2_message):
        try:
            self.driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            time.sleep(10)
            
                    # Load processed names from connections.txt
            processed_names = set()
            try:
                # Open file in 'a+' mode to append or create if not existing
                with open("connections.txt", "a+") as file:
                    file.seek(0)  # Move the file cursor to the beginning
                    processed_names = {line.strip() for line in file}
            except Exception as e:
                messagebox.showerror(e)  # This won't be necessary since 'a+' mode ensures the file is created

            def scroll_to_bottom():
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            def click_show_more():
                try:
                    show_more_button = self.driver.find_element(By.XPATH, "//button[starts-with(@class, 'artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button')]")
                    show_more_button.click()
                    time.sleep(2)
                except:
                    message.showinfo("No 'Show more results' button found. All connections loaded.")
                    with open("connections.txt", "w") as file:
                        file.write("")

            def save_name_to_file(name):
                with open("connections.txt", "a") as file:
                    file.write(f"{name}\n")

            total_processed = 0

            while total_processed < num_connections:
                try:
                    buttons = self.driver.find_elements(By.XPATH, "//button[starts-with(@class, 'artdeco-button artdeco-button--2 artdeco-button--secondary ember-view')]")
                    names = self.driver.find_elements(By.XPATH, "//span[starts-with(@class, 'mn-connection-card__name t-16 t-black t-bold')]")

                    if len(buttons) != len(names):
                        print("Mismatch between buttons and names. Loading more results.")
                        break

                    for i in range(len(buttons)):
                        if total_processed >= num_connections:
                            return
                        name = names[i].text
                        
                        if name in processed_names:
                            continue
                        
                        first_name = name.split()[0]
                        button = buttons[i]

                        button.click()
                        time.sleep(3)
                        nav_buttons = self.driver.find_elements(By.XPATH, "//div[starts-with(@class, 'msg-overlay-bubble-header__controls display-flex align-items-center')]//div[starts-with(@class, 'artdeco-dropdown msg-thread-actions__dropdown artdeco-dropdown--placement-bottom artdeco-dropdown--justification-right ember-view')]//button[starts-with(@class, 'msg-thread-actions__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--muted artdeco-button--tertiary artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view')]")
                        send_button = self.driver.find_element(By.XPATH, "//button[starts-with(@class, 'msg-form__send-button artdeco-button artdeco-button--1')]")
                        message_area = self.driver.find_element(By.XPATH, "//div[starts-with(@aria-label, 'Write a message…')]")

                        message_area.clear()
                        message_area.click()

                        if nav_buttons:
                            profile_names = self.driver.find_elements(By.XPATH, "//span[starts-with(@class, 'msg-s-message-group__profile-link msg-s-message-group__name t-14 t-black t-bold hoverable-link-text')]")
                            if profile_names:
                                last_profile_name = profile_names[-1].text
                                if last_profile_name == name:
                                    nav_buttons[0].click()
                                    time.sleep(4)
                                    action_buttons = self.driver.find_elements(By.XPATH, "//div[starts-with(@class, 'msg-thread-actions__dropdown-option artdeco-dropdown__item artdeco-dropdown__item--is-dropdown ember-view')]")
                                    if action_buttons[0].text == "Move to Other":
                                        action_buttons[0].click()
                                else:
                                    nav_buttons[0].click()
                                    time.sleep(4)
                                    action_buttons = self.driver.find_elements(By.XPATH, "//div[starts-with(@class, 'msg-thread-actions__dropdown-option artdeco-dropdown__item artdeco-dropdown__item--is-dropdown ember-view')]")
                                    if action_buttons[0].text == "Move to Focused":
                                        action_buttons[0].click()
                                    time.sleep(4)
                            if campaign2:
                                message = campaign2_message.replace("{first_name}", first_name)
                                message_area.send_keys(message)

                        else:
                            if campaign1:
                                message = campaign1_message.replace("{first_name}", first_name)
                                message_area.send_keys(message)



                        # Attachment part
                        if self.attachment_path:
                            attachment_input = self.driver.find_element(By.XPATH, "//input[starts-with(@class, 'msg-form__attachment-upload-input')]")
                            norm_path = os.path.normpath(self.attachment_path)
                            attachment_input.send_keys(norm_path)
                            time.sleep(4)  # Wait for file upload

                        send_button.click()
                        time.sleep(3)
                        close_button = self.driver.find_element(By.XPATH, "//button[starts-with(@class, 'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')]")
                        close_button.click()

                        save_name_to_file(name)
                        time.sleep(5)
                        total_processed += 1

                    scroll_to_bottom()
                    click_show_more()
                except Exception as e:
                    print(f"Error occurred: {str(e)}")
                    break

            messagebox.showinfo("Automation Complete", f"Processed {total_processed} connections")
        except Exception as e:
            messagebox.showerror("Automation Error", f"An error occurred during automation: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedInAutomationGUI(root)
    root.mainloop()
