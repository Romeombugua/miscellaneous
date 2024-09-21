from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By

def chrome_webdriver():
 chromedriver_path = '/home/romeo/Downloads/chromed/chromedriver-linux64/chromedriver'
 user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
              'Chrome/123.0.0.0 Safari/537.36'
 options = webdriver.ChromeOptions()
 options.add_argument("--start-maximized")
#  options.add_argument('--headless')
 options.add_argument(f'user-agent={user_agent}')
#  options.add_extension('/home/romeo/Downloads/chromed/vpn.crx')
 service = Service(executable_path=chromedriver_path)
 driver = webdriver.Chrome(service=service, options=options)
 return driver


driver = chrome_webdriver()

# keyword = input("Enter the keyword you want to search: ")
driver.get('https://www.linkedin.com/login')

time.sleep(5)

username = driver.find_element("xpath","//input[@name='session_key']")
password = driver.find_element("xpath","//input[@name='session_password']")

time.sleep(5)



username.send_keys("romeombugua@gmail.com")
password.send_keys('romantic254')

driver.find_element("xpath","//button[@type='submit']").click()
time.sleep(5)

driver.get("https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&sid=YxU")

time.sleep(5)

all_buttons = driver.find_elements(By.TAG_NAME, "button")
message_buttons = [btn for btn in all_buttons if btn.text == 'Message']

message_buttons[0].click()

time.sleep(5)
driver.quit()