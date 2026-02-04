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

def woop_connect(desktop):
    wait(woop['first_connect'])
    click_image(woop['first_connect'])
    wait(woop['user'])
    click_image(woop['user'])
    time.sleep(0.3)
    just_fill(desktop,os.getenv('woop_user'))
    time.sleep(0.3)
    pyautogui.press('tab')
    time.sleep(0.3)
    just_fill(desktop,os.getenv('woop_passwd'))
    time.sleep(0.3)
    pyautogui.press('enter')
    wait(woop['lobby'])