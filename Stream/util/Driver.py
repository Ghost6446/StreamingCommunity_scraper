# 5.07.2023 -> 12.09.2023 -> 17.09.2023

# General import
import os, time, subprocess, sys
from sys import platform
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Class import
from Stream.util.util import console, close_chrome


class Driver:

    service = None
    options = None
    driver = None

    def __init__(self) -> None:
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        close_chrome()
            
    def create(self, headless=False, minimize=False):

        if(headless): 
            self.options.add_argument("headless")

        self.options.add_argument("--window-size=1280,1280")
        self.options.add_argument('--user-data-dir=C:/Users/'+os.getlogin()+'/AppData/Local/Google/Chrome/User Data')

        self.options.add_experimental_option("useAutomationExtension", True)
        self.options.add_experimental_option("excludeSwitches",["enable-automation"])
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-insecure-localhost')
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(options=self.options,  service=self.service)
    
        if(minimize):
            self.driver.minimize_window()

    def get_page(self, url, sleep=1):
        try:
            self.driver.get(url)
            time.sleep(sleep)
        except:
            console.log("[red]Cant get the page")
            sys.exit(0)

    def get_soup(self):
        return BeautifulSoup(self.driver.page_source, "lxml")

    def close(self): 
        console.log("[green]Close driver")
        self.driver.close()
        self.driver.quit()