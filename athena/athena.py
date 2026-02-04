import time
import os
import pyperclip
import pytesseract
import pyautogui
import cv2
import psutil
import numpy as np

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images


from config.img import *
from utils.utils import *
from utils.connect_db import *
from utils.request import *


def select_label(desktop, produit, code8):
    expected_labels = []

    connect_and_open_athena(desktop)

    # wait_for_window('Carter Cash Gestion : Aujourd\'hui')
    time.sleep(4)
    click_image(athena_search_article)
    wait(search_article_load)
    pyautogui.press('tab')
    desktop.type_text(code8)
    pyautogui.press('enter')
    click_image(athena_fiche_article, 0.9)
    wait(athena_libelle_web)
    time.sleep(2)
    click_image(athena_libelle_web, offset_y=20)

    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    label = pyperclip.paste()
    # click_image(athena_close)
    print(f'label : {label}')
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == "Athena.UI.exe":
            proc.terminate()
    return label


def connect_and_open_athena(desktop):
    desktop.open_application(appli["athena"])
    wait(athena_connect)
    time.sleep(0.5)
    click_image(logo_connect)
    time.sleep(0.5)
    if os.getenv('env').lower() == 'dev':
        window = gw.getWindowsWithTitle("Athéna : Carter Cash Gestion")[0]
        window.moveTo(-8, -8)
        window.resizeTo(1936, 887)
    time.sleep(2)
    just_fill(desktop,os.getenv('athena_user'))
    time.sleep(0.5)
    pyautogui.press('tab')
    desktop.type_text(os.getenv('athena_passwd'))
    time.sleep(0.5)
    pyautogui.press('enter')

def supplier_orders(cmd):
    print(cmd)
    print(sorted_to_order(cmd))
    wait(athena_to_order)
    time.sleep(2)
    click_image(athena_to_order, confidence=0.9)
    wait(customer_order)
    click_image(customer_order, confidence=0.85)
    wait(is_load)
    click_image(raz)
    time.sleep(2)
    err_img = os.path.join(os.getcwd(), "logs", "error.png")
    os.makedirs(os.path.dirname(err_img), exist_ok=True)
    for _,supplier_cmd in cmd.items():
        for p in supplier_cmd:
            num_tic = p['num_tic']
            a = find_global_row(check, num_tic, regex=r"(99\d{8})", width=105, offset_y=370, confidence=0.9, height=20)
            print(a)
            pyautogui.press('space')
    click_image(transfer_yakaedi)
    wait(athena_ok, confidence=0.85)
    click_image(athena_ok, confidence=0.85)
    time.sleep(3)

def sorted_to_order(to_order):
    for supplier, commandes in to_order.items():
        to_order[supplier] = sorted(commandes, key=lambda x: int(x['num_tic']), reverse=True)
    return to_order