# 5.07.2023

# General import
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Driver:
    service = None
    options = None
    driver = None
    def __init__(self) -> None:
        self.service = Service(ChromeDriverManager(driver_version='114.0.5735.90').install())
        self.options = webdriver.ChromeOptions()
    def create(self, headless = False):

        if(headless):
            self.options.add_argument("headless")

        self.options.add_experimental_option("useAutomationExtension", True)
        self.options.add_experimental_option("excludeSwitches",["enable-automation"])
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-insecure-localhost')
        self.options.add_argument("--allow-running-insecure-content")
        self.driver = webdriver.Chrome(options=self.options,  service=self.service)
    def get_page(self, url, sleep=1):
        start_time = time.time()
        self.driver.get(url)
        time.sleep(sleep)
        print("GET URL => ", url, " IN", time.strftime("%H:%M:%S",time.gmtime(time.time() - start_time) ))
    def close(self):
        print("Close driver")
        self.driver.close()
        self.driver.quit()
