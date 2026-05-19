import os

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class AbstractPages:
    def __init__(self, driver):
        self.host = os.getenv('HOST', 'http://127.0.0.1:5000/')
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_current_site_host(self):
        return self.driver.current_url

    def is_on_correct_host(self):
        return self.host in self.get_current_site_host()

    def open(self, url):
        return self.driver.get(url)

    def find(self, by, value):
        return self.wait.until(EC.visibility_of_element_located((by, value)))

    def finds(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        self.find(by, value).click()

    def typing(self, by, value, text):
        e = self.find(by, value)
        e.clear()
        e.send_keys(text)