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

def create_ordre_de_sortie(desktop,orders,mode=1):
    count = len(orders)
    wait(out)
    click_image(out)
    wait(link_create_ordre)
    click_image(link_create_ordre)
    wait(create_ordre)
    click_image(filter_num)
    wait(popin_filter)
    if count > 1:
        click_image(plage)
        time.sleep(0.5)
        just_fill(desktop, list(orders.keys())[0])
        pyautogui.press('tab')
        just_fill(desktop, list(orders.keys())[count-1])
        pyautogui.press('enter')
        wait(create_ordre)
        click_image(all_ordre)
        time.sleep(0.4)
        click_image(create_ordre)
    else:
        just_fill(desktop, list(orders.keys())[0])
        pyautogui.press('enter')
        wait(create_ordre)
        click_image(create_ordre)
    wait(ego_ok)
    click_image(ego_ok)
    wait(choix_reservation,confidence=0.95, timeout=count*5)
    # click_image(ok_cut)
    pyautogui.press("enter")
    pyautogui.press("enter")
    # wait(popin_information)
    # click_image(ok_large)
    wait(information_ok)
    pyautogui.press('enter')
    wait(qualif)
    click_image(all_ordre)
    time.sleep(0.4)
    click_image(qualif)
    time.sleep(2)
    match mode:
        case 1:
            click_image(qualif1)
        case 2:
            click_image(qualif_multi)
    time.sleep(0.5)
    pyautogui.press('enter')
    wait(title_os, confidence=0.9)
    right_click_image(title_os, confidence=0.9)
    wait(close)
    click_image(close)
    time.sleep(1)
    