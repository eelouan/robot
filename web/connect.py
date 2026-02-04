import time
import os

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv

from config.img import state as State

from config.img import *
from utils.utils import *

load_dotenv()

def connect_with_good_id(desktop):
    if State == 'fr':
        pyautogui.press('tab')
        time.sleep(0.5)
    just_fill(desktop,os.getenv(f'{State}_mail'))
    time.sleep(0.5)
    pyautogui.press('tab')
    just_fill(desktop,os.getenv(f'{State}_passwd'))
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2)

def tryConnectBadEmailGoodPasswd(desktop):
    best_match_scale_on_screen_and_click(connect_menu,0.9)
    selectInputAndFillForBrowser(desktop,None,os.getenv('bad_user_mail'))
    select_input_and_fill_for_browser(desktop,connect_passwd,os.getenv('userPasswd'))
    best_match_scale_on_screen_and_click(connect_connect,0.9)
    if r:
        time.sleep(1)
        reset(browser,desktop)

def tryConnectGoodEmailBadPasswd(desktop):
    best_match_scale_on_screen_and_click(connect_menu,0.9)
    selectInputAndFillForBrowser(desktop,None,os.getenv('userMail'))
    select_input_and_fill_for_browser(desktop,connect_passwd,os.getenv('bad_user_passwd'))
    best_match_scale_on_screen_and_click(connect_connect,0.9)
    if r:
        time.sleep(1)
        reset(browser,desktop) 
