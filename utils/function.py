import subprocess
import time
import os
import pyautogui 
import pyscreeze
import tempfile
import cv2
import numpy as np
import win32con, win32gui
import ctypes
import sys

from RPA.Browser.Selenium import Selenium
from RPA.Desktop import Desktop
from PIL import ImageGrab,Image
from RPA.Images import Images
from dotenv import load_dotenv
from pyautogui import ImageNotFoundException
from SeleniumLibrary.errors import ElementNotFound
from datetime import datetime

from config.img import *
from utils.connect_db import *
from utils.Assert import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()
conn = connect_db()

def sort_cart(browser,actual):
    expected = []
    elements = browser.find_elements('css:.item')
    for element in elements:
        expected.append(browser.get_element_attribute(element, 'data-reference'))
    actual_sorted = sorted(
        actual,
        key=lambda x: expected.index(x["code8"])
    )
    return actual_sorted

def finally_task(desktop, browser, start_time, test_cat, number, logging):
    # ⏱ Temps d'exécution
    duration = time.time() - start_time
    print(f"\n{'='*80}\n⏱ Temps d'exécution : {duration:.2f}s ({duration/60:.1f}min)\n{'='*80}\n")
    
    # 1) Fermeture des applications (avec feedback)
    cleanup_errors = []
    
    if 'browser' in locals() and browser:
        try:
            browser.close_all_browsers()
        except Exception as e:
            cleanup_errors.append(f"Browser: {e}")
    
    if 'desktop' in locals() and desktop:
        try:
            desktop.close_all_applications()
        except Exception as e:
            cleanup_errors.append(f"Desktop: {e}")
    
    # 2) Kill processus zombies (avec timeout)
    try:
        subprocess.run(
            'taskkill /F /T /IM chromedriver.exe /IM chrome.exe /IM node.exe /IM msedge.exe',
            shell=True,
            capture_output=True,
            timeout=10  # IMPORTANT : évite les blocages
        )
    except Exception as e:
        cleanup_errors.append(f"Taskkill: {e}")
    
    # 3) Génération du rapport AVANT le shutdown des logs
    report_generated = False
    try:
        # Construire le chemin si les variables existent
        if 'number' in locals() and 'f' in locals():
            report_path = f"{test_cat}\\{number} - {Assert.get_trad()[f]}\\rapports"
        else:
            report_path = None
        
        # Générer le rapport
        if report_path:
            Assert.generate(report_path)
            print(f"✅ Rapport généré : {report_path}")
        else:
            Assert.generate()
            print("✅ Rapport généré (défaut)")
        
        report_generated = True
        
    except Exception as e:
        print(f"❌ ERREUR génération rapport : {e}")
        # Dernière tentative avec chemin par défaut
        if report_path:  # Si on avait essayé un chemin custom
            try:
                Assert.generate()
                print("✅ Rapport généré (défaut après échec)")
                report_generated = True
            except Exception as e2:
                print(f"❌ Échec total génération rapport : {e2}")
    
    # 4) Shutdown des logs APRÈS le rapport
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        logging.shutdown()
    except Exception as e:
        print(f"⚠ Erreur flush/shutdown : {e}")
    
    # 5) Afficher les erreurs de cleanup s'il y en a
    if cleanup_errors:
        print(f"\n⚠ {len(cleanup_errors)} erreur(s) de nettoyage:")
        for err in cleanup_errors:
            print(f"  - {err}")
    
    # 6) Message final
    if report_generated:
        print("\n🏁 Terminé avec succès")
    else:
        print("\n⚠ Terminé avec erreurs (rapport non généré)")