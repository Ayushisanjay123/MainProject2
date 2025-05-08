from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Path to your Microsoft Edge WebDriver
EDGE_DRIVER_PATH = "C:/path/to/msedgedriver.exe"  # Change this to your actual path

# Your login credentials
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

# Set up the Edge WebDriver
service = Service(EDGE_DRIVER_PATH)
options = webdriver.EdgeOptions()
driver = webdriver.Edge(service=service, options=options)

try:
    # Open the login page
    driver.get("http://localhost:8000/login/")  # Change URL if needed
    time.sleep(2)

    # Fill in the email field
    email_field = driver.find_element(By.NAME, "email")
    email_field.clear()
    email_field.send_keys(EMAIL)

    # Fill in the password field
    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys(PASSWORD)

    # Submit the form
    password_field.send_keys(Keys.RETURN)
    time.sleep(3)

    # You can now add assertions or further navigation here
    print("Login test completed.")
finally:
    driver.quit()
