import subprocess
import time
import os
import pyautogui 
import pyscreeze
import pytesseract
import tempfile
import cv2
import numpy as np
import win32con, win32print, win32api, win32gui
import ctypes
import sys
import pygetwindow as gw
import re
import math

from RPA.Browser.Selenium import Selenium
from RPA.Desktop import Desktop
from PIL import ImageGrab,Image, ImageDraw
from RPA.Images import Images
from dotenv import load_dotenv
from pyautogui import ImageNotFoundException
from SeleniumLibrary.errors import ElementNotFound
from datetime import datetime
from pytesseract import Output

from config.img import *
from utils.connect_db import *
from utils.Assert import *

log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
if os.getenv('env').lower() == 'dev':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\emoreau\Documents\robot\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Public\Downloads\Tesseract-OCR\tesseract.exe'
    
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()

def sort_ego(orders):
    tab_ego = {
        'dpd': {},
        'tnt': {},
        'mr' : {}
    }
    for products,num_commande in orders:
        transport = products[0]["transporteur"]
        coll_p = []
        for product in products:
            coll_p.append(
                {
                    'code8': product['code8'],
                    'qty': product['qty']
                },
            )
        if transport in tab_ego:
            tab_ego[transport][num_commande] = {
                'products': coll_p
            }
    return tab_ego

def extract_number_below_header(path, confidence=0.8):
    # Chargement de l'image complète et du modèle
    start_time = time.time()
    os.makedirs("screen", exist_ok=True)
    screenshot_path = os.path.join("logs", "screen_colisage.png")
    pyautogui.screenshot(screenshot_path)
    locations = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
    leftmost = min(locations, key=lambda loc: loc.left)

    x, y = leftmost.left, leftmost.top + leftmost.height + 5
    w, h = leftmost.width, 35

    img = cv2.imread(screenshot_path)

    # Ajustement : lire environ 35 px plus bas, et plus large
    roi = img[y:y+h, x:x+w]

    cv2.imwrite("logs/zone_ocr_colisage.png", roi)

    # OCR
    pil_img = Image.fromarray(roi).convert('L')
    text = pytesseract.image_to_string(pil_img, config='--psm 6')
    text = text.replace('.', ' ').replace(',', ' ').replace('\n', ' ').strip()

    match = re.search(r'(\d[\d\s]{5,})', text)
    if match:
        number = match.group(1).replace(' ', '')
        return number
    else:
        print("❌ Aucun numéro trouvé.")
        Assert.set_intercept("empty_number_packaging")
        return None
    
def extract_number(path, regex, confidence=0.8):
    # Chargement de l'image complète et du modèle
    start_time = time.time()
    screenshot_path = os.path.join("logs", "screen_colisage.png")
    pyautogui.screenshot(screenshot_path)
    locations = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
    leftmost = min(locations, key=lambda loc: loc.left)

    x, y = leftmost.left + leftmost.width, leftmost.top*2
    w, h = leftmost.width, leftmost.height

    img = cv2.imread(screenshot_path)

    # Ajustement : lire environ 35 px plus bas, et plus large
    roi = img[y:y+h, x:x+w]

    cv2.imwrite("logs/zone_ocr_colisage.png", roi)

    # OCR
    pil_img = Image.fromarray(roi).convert('L')
    text = pytesseract.image_to_string(pil_img, config='--psm 6')

    text = text.replace('\n', ' ').replace(',', ' ').replace('.', ' ').strip()
    # print(f"[OCR brut] {text}")

    match = re.search(regex, text)
    if match:
        number = match.group(1).strip()
        return number
    else:
        print("❌ Aucun numéro trouvé.")
        return None
    
def find_row(path, target, regex=r'(.*)', confidence=0.9, width = 0, height = None, offset_x = 0, offset_y = 0):
    after = 0
    i = 1
    while True:
        # Screenshot complet
        screenshot_path = "logs/screen_list.png"
        pyautogui.screenshot(screenshot_path)
        img = cv2.imread(screenshot_path)

        # Localisation de la flèche
        matches = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
        if not matches:
            print("❌ Flèche non détectée.")
            return False

        leftmost = min(matches, key=lambda loc: loc.left)

        # Zone à OCR (juste à droite de la flèche)
        x = leftmost.left + leftmost.width
        y = leftmost.top
        w = width  # Largeur estimée du champ de numéro
        if not height:
            h = leftmost.height
        else:
            h = height

        roi = img[y:y+h, x:x+w]
        cv2.imwrite("logs/zone_ocr_num.png", roi)

        pil_img = Image.fromarray(roi).convert("L")
        text = pytesseract.image_to_string(pil_img, config="--psm 6").strip()

        # print(f"[{i}] OCR détecté : '{text}'")
        i += 1

        match = re.search(regex, text)
        if match:
            if type(target) is int:
                detected = int(match.group(1))
            else:
                detected = match.group(1)
            if after == detected:
                raise ValueError("Deux commandes fournisseur identiques")
            after = detected
            detected = re.sub(r"[^\d]", "", match.group(1).strip())
            target = re.sub(r"[^\d]", "", str(target).strip())
            if detected == target:
                return True

        # Passer à la ligne suivante
        pyautogui.press("down")
        time.sleep(0.2)