# 17.09.2023

# Import
import os, time, subprocess, sys
from rich.console import Console
from rich.prompt import Prompt

# Variable
msg = Prompt()
console = Console()

# [ func ]

def close_chrome():
    console.log("[green]Close all instance of chrome")


    if sys.platform == "linux" or sys.platform == "linux2":
        try: subprocess.check_output("kill -9 chrome.exe",  shell=True, creationflags=0x08000000) 
        except: pass

    # For win
    elif sys.platform == "win32":
        try: subprocess.check_output("TASKKILL /IM chrome.exe /F",  shell=True, creationflags= 0x08000000) 
        except: pass

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)