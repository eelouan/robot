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

def search_lobby(browser,desktop,orders):
    click_image(woop['lobby_search'])
    for order, content in orders.items():
        just_fill(desktop,order)
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(2)
        rows = browser.find_elements("css:table tbody tr")
        for row in rows:
            tds = browser.find_elements("css:td", parent=row)
            transporteur = tds[4].text.strip()
            if transporteur != "-":
                order = browser.find_elements("css:span", parent=tds[0])
                browser.click_element_when_visible(order)
                update_status(browser, content['status'])
                break
        browser.driver.switch_to.window(browser.driver.window_handles[0])
        wait(woop['search'])
        click_image(woop['search'])
        pyautogui.hotkey('ctrl','a')
        time.sleep(0.4)
        pyautogui.press('suppr')
        time.sleep(0.4)

def sort_only_order(orders, commandes):
    woop_order = {}

    for i, (_, num) in enumerate(orders):
        status = commandes[i].get('woop_status', 'Inconnu')
        woop_order[num] = {'status': status}

    return woop_order


def update_status(browser, status):
    wait(woop['action'])
    click_image(woop['action'])
    wait(woop['update'])
    click_image(woop['update'])
    wait(woop['select_action'])
    click_image(woop['select_action'])
    wait(woop['action_select_open'])
    if status == 'Livraison réalisée avec succès':
        pyautogui.press('l')
        time.sleep(0.5)
        pyautogui.press('enter')
    else:
        while True:
            try:
                match status:
                    case 'Echec de la livraison avec retour expéditeur': 
                        click_image(woop['error_return_sender'])
                    case 'Echec de la livraison - client absent':
                        click_image(woop['delivery_failure-customer_absent'])
                break
            except Exception:
                pyautogui.press('down')
                time.sleep(0.2)


    time.sleep(1)
    click_image(woop['register_action'])