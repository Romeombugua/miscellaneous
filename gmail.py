from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Replace with the path to your WebDriver


# Gmail credentials
email = 'debianhero5@gmail.com'
password = '#debianhero254'

# Initialize WebDriver
driver = webdriver.Chrome()

# Navigate to Gmail login page
driver.get('https://accounts.google.com/signin/v2/identifier')

# Enter email
email_field = driver.find_element(By.ID, 'identifierId')
email_field.send_keys(email)
email_field.send_keys(Keys.RETURN)
time.sleep(2)  # Adjust the sleep time as necessary

# Enter password
password_field = driver.find_element(By.NAME, 'password')
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)
time.sleep(5)  # Adjust the sleep time as necessary

# At this point, you should be logged into Gmail (if no additional security checks are triggered)
# Navigate to the inbox
driver.get('https://mail.google.com/mail/u/0/#inbox')

# Add more logic to read emails, if necessary

# Close the browser
time.sleep(5)  # Adjust the sleep time as necessary
driver.quit()
