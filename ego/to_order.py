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
from ego.function import * 

def simple_recip(desktop, to_order):
    chars = []
    for supplier, order in to_order.items():
        wait(enter)
        click_image(enter)
        wait(simple_receip)
        click_image(simple_receip)
        wait(receive_purchase_order)
        click_image(receive_purchase_order)
        pyautogui.press('tab')
        time.sleep(1)
        just_fill(desktop,supplier)
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('enter')
        wait(reception_arrow_select)
        find_row(reception_arrow_select, order[0]['supplier_order'], regex=r"(\d*)",width=70)
        pyautogui.press('enter')
        wait(number_delivery_note)
        click_image(number_delivery_note, offset_x=100)
        just_fill(desktop, 'TEST')
        pyautogui.press('enter')
        wait(bulk_reception)
        click_image(bulk_reception)
        for product in order:
            wait(article)
            click_image(article)
            time.sleep(0.5)
            just_fill(desktop, product['code8'])
            time.sleep(0.5)
            pyautogui.press('tab')
            time.sleep(0.5)
            if is_existe(order_list):
                pyautogui.press('enter')
            wait(unite)
            click_image(all_quantity, offset_x=45)
            time.sleep(0.5)
            just_fill(desktop, str(product['qty']))
            time.sleep(0.5)
            click_image(char, offset_x=45)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            name_char = 'cret1'
            just_fill(desktop, name_char)
            time.sleep(0.5)
            pyautogui.press('tab')
            just_fill(desktop, '1')
            time.sleep(0.5)
            click_image(reception_ok)
            time.sleep(2)
            print(f"bad : {is_existe(bad_char)}")
            if is_existe(bad_char):
                name_char = 'crmult1'
                click_image(ok_bad_reception)
                click_image(char, offset_x=45)
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'a')
                just_fill(desktop, name_char)
                if not name_char in chars:
                    chars.append(name_char)
                time.sleep(0.5)
                pyautogui.press('tab')
                just_fill(desktop, '1')
                time.sleep(0.5)
                click_image(reception_ok)
            else:
                if not name_char in chars:
                    chars.append(name_char)
            time.sleep(1)
        click_image(close_reception)
        wait(enclose)
        click_image(enclose)
        wait(enclose_ok)
        click_image(enclose_ok)
        return chars
            
def addressing_char_reception(chars):
    for char in chars:
        wait(enter)
        click_image(enter)
        wait(addressing_char, 0.9)
        click_image(addressing_char, 0.9)
        wait(arrow_addressing_char)
        find_row(arrow_addressing_char, char, regex=r"([A-Z0-9]+)", width=70)
        time.sleep(0.5)
        click_image(address_char)
        wait(check_all_address)
        click_image(check_all_address)
        time.sleep(0.3)
        click_image(auto_address)
        wait(auto_address_empty)
        right_click_image(auto_address_title)
        wait(close)
        click_image(close)
    time.sleep(1)
    wait(address_title)
    right_click_image(address_title)
    wait(close)
    click_image(close)

def addressing_mission_reception(chars):
    for char in chars:
        wait(enter)
        click_image(enter)
        wait(addressing_mission, 0.9)
        click_image(addressing_mission, 0.9)
        wait(addressing_char_char)
        click_image(addressing_char_char)
        if char == 'cret1':
            wait(cret1)
            click_image(cret1)
        elif char == 'crmult1':
            wait(crmult1)
            click_image(crmult1)
        time.sleep(1)
        click_image(check_all_mission)
        click_image(valid_addressing)
        wait(ego_oui)
        click_image(ego_oui)
        wait(mission_empty)
        time.sleep(1)
    wait(mission_address_title)
    right_click_image(mission_address_title)
    wait(close)
    click_image(close)



