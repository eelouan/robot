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

def expedition(desktop, orders, array_nums):
    wait(pda_lobby)
    pyautogui.press('7')
    wait(pda_menu_expe)
    pyautogui.press('1')
    wait(pda_expe_cmd)
    for transport, nums in array_nums.items():
        if nums:
            pyautogui.press('1')
            wait(show_store)
            pyautogui.press('right')
            pyautogui.press('down')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.press('enter')
            wait(show_carrier)
            pyautogui.press('right')
            if transport == 'dpd':
                wait(carrier_dpd)
                double_click_image(carrier_dpd)
            elif transport == 'tnt':
                wait(carrier_tnt)
                double_click_image(carrier_tnt)
            else:
                wait(carrier_mr)
                double_click_image(carrier_mr)
            time.sleep(0.5)
            pyautogui.press('enter')
            wait(carrier_informations)
            match transport:
                case 'dpd':
                    just_fill(desktop,'DPD')
                case 'tnt':
                    just_fill(desktop,'TNT')
                case 'mr':
                    just_fill(desktop,'MONDIAL')
            time.sleep(0.5)
            pyautogui.press('f1')
            wait(print_cargo)
            just_fill(desktop,'PDF')
            time.sleep(0.5)
            pyautogui.press('enter')
            wait(cargo)
            pyautogui.press('enter')
            for num in nums:
                wait(cb_support,confidence=0.9)
                just_fill(desktop,num)
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(1)
            wait(cb_support)
            time.sleep(5)
            pyautogui.press('f1')
            wait(take_done)
            pyautogui.press('f4')
            wait(pda_expe_cmd)
    pyautogui.press('f4')
    wait(pda_menu_expe)
    pyautogui.press('f4')
    wait(pda_lobby)
    click_image(pda_quit)
    time.sleep(2)