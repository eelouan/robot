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


def valid_preparation(desktop, orders, transport, array_num):
    wait(out)
    click_image(out)
    wait(link_valid)
    click_image(link_valid)
    wait(attente_prepare, confidence=0.9)
    time.sleep(0.5)
    click_image(all_ordre)
    time.sleep(0.4)
    click_image(valid_prepare)
    time.sleep(2)
    just_fill(desktop, os.getenv('user_ego1'))
    time.sleep(2)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(0.2)
    just_fill(desktop,'CA13')
    time.sleep(2)
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(0.2)
    just_fill(desktop,'EXPE1')
    time.sleep(2)
    pyautogui.press('tab')
    if transport == 'tnt':
        t = 'TNT B2B'
    elif transport == 'dpd':
        t = 'DPD'
    else:
        t = 'MR L'
    just_fill(desktop,t)
    pyautogui.press('tab')
    time.sleep(2)
    if len(orders) > 1:
        click_image(valid_woop)
    else:
        click_image(valid_woop_single)
    time.sleep(1)
    just_fill(desktop,'TEST')
    time.sleep(2)
    pyautogui.press('tab')
    pyautogui.press("enter")
    # click_image(valid_valid)
    if len(orders) > 1:
        wait(popin_information, timeout=180)
        pyautogui.press("enter")
        # click_image(ego_ok)
    wait(valid_vide, timeout=280)
    right_click_image(title_valid)
    wait(close)
    click_image(close)

    wait(out)
    click_image(out)
    wait(link_colisage)
    click_image(link_colisage)
    wait(colisage)
    pyautogui.press('tab')
    for order in orders:
        just_fill(desktop,order)
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('enter')
        wait(consult_colisage)
        time.sleep(1)
        array_num[transport].append(extract_number_below_header(colisage_number)) 
        click_image(update_colisage)
        # wait(ego_ok)
        # click_image(ego_ok)
        time.sleep(2)
        pyautogui.press("enter")
        wait(ego_oui)
        click_image(ego_oui)
        wait(update_colisage, timeout=20)
        wait(consult_colisage)
        right_click_image(consult_colisage)
        wait(close)
        click_image(close)
    wait(colisage)
    right_click_image(colisage)
    wait(close)
    click_image(close)
    return array_num

def prepare_multi(desktop, orders):
    wait(pda_lobby)
    pyautogui.press('5')
    wait(pda_preparation)
    pyautogui.press('1')
    wait(pda_preparation_cmd)
    pyautogui.press('5')
    wait(preparation_cmd)
    pyautogui.press('enter')
    wait(cb_chariot)
    pyautogui.press('tab')
    just_fill('CP3')
    pyautogui.press('enter')
    wait(affectation)
    pyautogui.press('enter')
    for _, products in orders.items():
        i = 0
        i += 1
        for product in products.items():
            wait(affectation_adresse)
            adr = extract_number(ocr_affectation_adresse, r'(\d{2}(?:\s\d{2})+)')
            just_fill(adr)
            pyautogui.press('enter')
            wait(affectation_code)
            code8 = extract_number(ocr_affectation_code, r'\b\d{7,}\b')
            just_fill(code8)
            pyautogui.press('enter')
            wait(depose_compartiment)
            just_fill('CP3#'+str(i))
    wait(end_depose)
    pyautogui.press('enter')
    wait(create_support)
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('right')
    wait(contenant)
    click_image(contenant)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('enter')
    wait(etiquette_support)
    just_fill('TEST')
    pyautogui.press('enter')
    wait(unité_colisage)
    just_fill(product['code8'])