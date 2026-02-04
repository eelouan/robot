import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images


from config.img import *
from utils.utils import *
from utils.Assert import *
from utils.connect_db import *
from utils.request import *

def ego_init():
    wait(certificate)
    click_image(certificate)
    wait(certificate_warning)
    click_image(certificate_warning)
    wait(bo)

def ego_connect(desktop, user = os.getenv('user_ego1')):
    wait(bo, timeout=30)
    click_image(bo)
    time.sleep(0.2)
    wait(user_bo)
    time.sleep(1)
    click_image(user_bo)
    time.sleep(0.5)
    just_fill(desktop, user)
    pyautogui.press('tab')
    time.sleep(1)
    just_fill(desktop, os.getenv('passwd_ego'))
    pyautogui.press('enter')

def pda_connect(desktop):
    skip = False
    click_image(pda)
    time.sleep(0.3)
    wait(pda_connected)
    time.sleep(0.5)
    just_fill(desktop, os.getenv('user_ego2'))
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('passwd_ego'))
    pyautogui.press('enter')

def disconected(desktop):
    wait(bo)
    click_image(logoff)