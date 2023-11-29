# 5.07.2023 -> 12.09.2023 -> 17.09.2023

# FOR CERTIFICATION ERROR -> python -m seleniumwire extractcert !!! 

# General import
import os, time, subprocess, sys
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Class import
from Stream.util.console import console


def close_chrome():
    console.log("[green]Close all instance of chrome")

    if sys.platform == "linux" or sys.platform == "linux2":
        try: 
            subprocess.check_output("kill -9 chrome.exe",  shell=True, creationflags=0x08000000) 
        except: 
            pass

    # For win
    elif sys.platform == "win32":
        try: 
            subprocess.check_output("TASKKILL /IM chrome.exe /F",  shell=True, creationflags= 0x08000000) 
        except: 
            pass


class Driver:

    service = None
    options = None
    driver = None

    def __init__(self) -> None:

        # Create service and option and close all other chrome 
        console.log("[green]Install chrome driver")
        if sys.platform in ("linux", "linux2"):
            self.service = Service(ChromeDriverManager(driver_version='119.0.6045.159').install())

        elif sys.platform == "win32":
            self.service = Service(ChromeDriverManager().install())
        
        self.options = webdriver.ChromeOptions()
        close_chrome()
            
    def create(self, headless=False, minimize=False):

        if(headless): self.options.add_argument("headless")
        self.options.add_argument("--window-size=1280,1280")

        # Set user data for Linux
        if sys.platform in ("linux", "linux2"):
            self.options.add_argument('--user-data-dir='+os.path.join(os.path.curdir, 'chrome-user-data'))

        # For Windows
        elif sys.platform == "win32":
            self.options.add_argument('--user-data-dir='+os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'))

        # Enable automation
        self.options.add_experimental_option("useAutomationExtension", True)
        self.options.add_experimental_option("excludeSwitches",["enable-automation"])
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Bypass certificate
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-insecure-localhost')
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-proxy-certificate-handler")
        self.options.add_argument("--disable-content-security-policy")

        # Create driver
        console.log("[green]Create driver")
        self.driver = webdriver.Chrome(options=self.options,  service=self.service)
        
        if(minimize): self.driver.minimize_window()

    def get_page(self, url, sleep=1):
        try:
            console.log(f"[blue]Get page => [green]{url}")
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
