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
import paramiko
import logging

from RPA.Browser.Selenium import Selenium
from RPA.Desktop import Desktop
from PIL import ImageGrab,Image, ImageDraw
from RPA.Images import Images
from dotenv import load_dotenv
from selenium import webdriver

from pyautogui import ImageNotFoundException
from SeleniumLibrary.errors import ElementNotFound
from datetime import datetime
from pytesseract import Output
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from decimal import Decimal

from config.img import *
from utils.connect_db import *
from utils.Assert import *

load_dotenv()

log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
if os.getenv('env').lower() == 'dev':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\emoreau\Documents\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Public\Downloads\Tesseract-OCR\tesseract.exe'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# conn = connect_db()

def wait_visible(browser, locator, timeout_s=15, poll_s=0.2):
    """Attend qu'un élément soit visible. Retourne True/False."""
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            if browser.is_element_visible(locator):
                return True
        except Exception:
            pass
        time.sleep(poll_s)
    return False

def click_when_visible(browser, locator, timeout_s=15, poll_s=0.2):
    """Attend puis clique. Retourne True si cliqué."""
    if wait_visible(browser, locator, timeout_s, poll_s):
        browser.click_element(locator)
        return True
    return False

def click_if_visible(browser, locator):
    """Clique si déjà visible, sinon rien."""
    try:
        if browser.is_element_visible(locator):
            browser.click_element(locator)
            return True
    except Exception:
        pass
    return False

def update_localstorage(browser, key, value):
    browser.execute_javascript(f"window.localStorage.setItem('{str(key)}', '{str(value)}');")

def just_fill(desktop, txt):
    desktop.type_text(txt)

def wait(path, confidence=0.8, timeout=15, seconde = None):
    start_time = time.time()
    found = False

    image = Image.open(path)
    filename = f"template.png"
    dest_path = os.path.join(log_dir, filename)

    # Sauvegarde
    image.save(dest_path)


    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(path, confidence=confidence)
            if location:
                found = True
                break
        except Exception:
            pass
        time.sleep(0.5)
    

    duration = time.time() - start_time
    # print(f"[⏱] Temps d'exécution de wait : {duration:.2f} secondes")

    if found:
        return location
    
    if seconde == False:
        raise TimeoutError(f"Image '{path}' non détectée après {timeout} secondes.")
    else:
        seconde

def ob_except(browser, suite):
    except_time = time.time()
    text = 'Paiement'
    pay = f"xpath=//button[.//div[normalize-space(text())='{text}']]"
    delete_paiement = "xpath=//button[contains(@id, 'removePayment')]"
    ok_delete_paiement = "xpath=//button[contains(@id, 'okbutton_components')]"
    delete_ticket = "xpath=//button[contains(@id, 'buttonDelete')]"
    delete_ticket_ok = "xpath=//button[contains(@id, 'btnModalApplyDelete')]"
    ticket_open = "xpath=//button[contains(@id, 'receiptsCounterButton')]"
    cancel_edit = "xpath=//button[contains(@id, 'cancelEdit')]"
    confirmation_button_cancel = "xpath=//button[contains(@id, 'confirmationPopup_btnAnnuler_components')]"

    # 1) Si on est en mode édition, on annule (pas de boucle 30 fois inutile)
    click_when_visible(browser, cancel_edit, timeout_s=1)

    click_when_visible(browser, confirmation_button_cancel)

    # # 2) ESC plusieurs fois (ok), mais tu peux limiter et éviter 10 si pas nécessaire
    # for _ in range(5):
    #     pyautogui.press("esc")
    #     time.sleep(0.1)

    # # 3) Aller dans Paiement
    # browser.wait_until_element_is_visible(pay, timeout="15 s")
    # browser.click_element(pay)

    # 4) Suppression paiement : d’abord cliquer "remove", ensuite attendre "OK"
    if click_when_visible(browser, delete_paiement, timeout_s=1):
        click_when_visible(browser, ok_delete_paiement, timeout_s=10)
        # 5) Suppression ticket : seulement si le panneau ticket est visible
        if wait_visible(browser, ticket_open, timeout_s=8):
            click_when_visible(browser, delete_ticket, timeout_s=15)
            click_when_visible(browser, delete_ticket_ok, timeout_s=15)

    Assert.write_assert(f"Le test {Assert.trad[suite]} c'est interrompus", suite, False)
    err = os.path.join(os.getcwd(), "logs", "error_ob.png")
    pyautogui.screenshot(err)
    logging.error("\n________________________________________________________________________________________________________________________________________________________________\n\nUne erreur s'est produite :", exc_info=True)
    duration = time.time() - except_time
    print(f"[⏱] Temps d'exécution du except : {duration:.2f} secondes")

def ob_finally(browser, desktop, start_time, number):
    duration = time.time() - start_time  # ⏱ Fin
    print(f"[⏱] Temps d'exécution du test : {duration:.2f} secondes")
    
    try: browser.close_all_browsers()
    except: pass
    try: desktop.close_all_applications()
    except: pass

    # 2) Killer les zombies courants (sans pitié)
    try:
        subprocess.run(
            'taskkill /F /T /IM chromedriver.exe /IM chrome.exe /IM node.exe /IM msedge.exe',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except: pass

    # 3) Vider les logs et buffers I/O
    try: logging.shutdown()
    except: pass
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except: pass

    # 4) Génération du rapport en dernier (puis flush encore)
    try: Assert.generate(f"4-OB\\{number} - {Assert.get_trad()[f]}\\rapports")
    except: pass
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except: pass

    Assert.generate(f"4-OB\\{number} - {Assert.get_trad()[f]}\\rapports")
    
def wait_and_click(image_path, timeout=10, delay=0.3, confidence=0.8):
    start = time.time()
    while time.time() - start < timeout:
        try:
            click_image(image_path, confidence=confidence)
            return True
        except pyautogui.ImageNotFoundException:
            time.sleep(delay)
        except FileNotFoundError as e:
            # print(f"Chemin image invalide: {image_path} -> {e}")
            return False
        except Exception as e:
            # Ne PAS avaler tout : log minimal
            # print(f"[wait_and_click] Exception: {e} - {image_path}")
            time.sleep(delay)
    debug = os.path.join(os.getcwd(), "logs", "debug_wait_click.png")
    pyautogui.screenshot(debug)
    return False

def click_image(path, confidence=0.8, skip=False, offset_x=0, offset_y=0):
    start_time = time.time()
    try:
        locations = list(pyautogui.locateAllOnScreen(path, confidence=confidence, grayscale=True))
    except Exception as e:
        if skip:
            return
        raise e
    leftmost = min(locations, key=lambda loc: loc.left)

    center_x, center_y = pyautogui.center(leftmost)
    click_x = center_x + offset_x
    click_y = center_y + offset_y

    pyautogui.click(click_x, click_y)

    screenshot = pyautogui.screenshot()
    draw = ImageDraw.Draw(screenshot)
    left, top, width, height = leftmost
    right = left + width
    bottom = top + height + offset_y
    draw.rectangle([left, top, right, bottom], outline="red", width=3)

    image_path = os.path.join(log_dir, "debug_click.png")
    screenshot.save(image_path)
    duration = time.time() - start_time
    # print(f"[⏱] Temps d'exécution de click_image : {duration:.2f} secondes")

def move_image(path, confidence=0.8, skip=False):
    start_time = time.time()
    try:
        locations = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
    except Exception as e:
        if skip:
            return
        raise e
    leftmost = min(locations, key=lambda loc: loc.left)

    pyautogui.moveTo(pyautogui.center(leftmost))


def right_click_image(path, confidence=0.8):
    start_time = time.time()
    locations = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
    leftmost = min(locations, key=lambda loc: loc.left)

    pyautogui.click(pyautogui.center(leftmost), button='right')

    screenshot = pyautogui.screenshot()
    draw = ImageDraw.Draw(screenshot)
    left, top, width, height = leftmost
    right = left + width
    bottom = top + height
    draw.rectangle([left, top, right, bottom], outline="red", width=3)

    image_path = os.path.join(log_dir, "debug_rightclick.png")
    screenshot.save(image_path)

def double_click_image(path, confidence=0.8, pos='left'):
    start_time = time.time()
    locations = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
    if pos == 'left':
        leftmost = min(locations, key=lambda loc: loc.left)
    else:
        leftmost = max(locations, key=lambda loc: loc.left)

    pyautogui.doubleClick(pyautogui.center(leftmost))

    screenshot = pyautogui.screenshot()
    draw = ImageDraw.Draw(screenshot)

    for i, loc in enumerate(locations):
        left, top, width, height = loc
        right = left + width
        bottom = top + height
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        draw.text((left, top - 10), f"#{i+1}", fill="red")

    image_path = os.path.join(log_dir, "debug_doubleclick.png")
    screenshot.save(image_path)

def open_browser(url, data=None):
    """
    Ouvre un navigateur Chrome configuré pour l'automatisation RPA.
    
    Args:
        url: URL à ouvrir au démarrage
        data: Argument Chrome supplémentaire optionnel
        
    Returns:
        Instance Selenium du navigateur
    """
    browser = Selenium()
    options = webdriver.ChromeOptions()
    
    # Argument personnalisé si fourni
    if data:
        options.add_argument(data)
    
    # Arguments Chrome depuis variable d'environnement
    chrome_args = os.environ.get("CHROME_OPTIONS")
    if chrome_args:
        for arg in chrome_args.split():
            options.add_argument(arg)
    
    # Arguments Chrome standards
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-pinch")
    options.add_argument("--high-dpi-support=1")
    
    # ========== NOUVEAUX ARGUMENTS POUR ÉVITER LA POPUP RESTORE ==========
    options.add_argument("--disable-session-crashed-bubble")  # Désactive popup de crash
    options.add_argument("--disable-restore-session-state")   # Désactive restauration de session
    options.add_argument("--no-first-run")                    # Désactive message première exécution
    options.add_argument("--no-default-browser-check")        # Désactive vérification navigateur par défaut
    # =====================================================================
    
    # Préférences Chrome
    prefs = {
        "profile.default_content_setting_values.clipboard": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 1,
        "extensions.theme": "light",
        # ========== NOUVELLES PRÉFÉRENCES ==========
        "profile.exit_type": "Normal",                      # Force une sortie "normale"
        "profile.default_content_settings.popups": 0,       # Bloque les popups
        "credentials_enable_service": False,                # Désactive gestionnaire mots de passe
        "profile.password_manager_enabled": False           # Désactive sauvegarde mots de passe
        # ===========================================
    }
    options.add_experimental_option("prefs", prefs)
    
    # ========== OPTIONS SUPPLÉMENTAIRES POUR MASQUER L'AUTOMATISATION ==========
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # ===========================================================================
    
    # Exécutable Chrome
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    # Création du navigateur Selenium
    browser.create_webdriver("Chrome", options=options)
    browser.go_to(url)
    
    # Ajustement taille en mode dev
    if os.getenv('env', '').lower() == 'dev':
        from RPA.Browser.Selenium import set_viewport_exactly
        set_viewport_exactly(browser, 1920, 859)
        browser.set_window_position(0, 0)
    
    return browser

def elem_is_exist(browser,selector, nb=3):
    is_existe = False
    for _ in range(nb):
        elem = browser.find_element(selector)
        if elem:
            is_existe = True
            break
        time.sleep(0.5)
    return is_existe

def find_element(browser,locator, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            element = browser.find_element(locator)
            browser.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )
            return element
        except (ElementNotFound):
            time.sleep(0.2)
    raise ElementNotFound(f"❌ Impossible de trouver : {locator} après {timeout}s")

def call_back_find_elem(browser,plocator):
    try:
        element = browser.find_element(plocator)
        browser.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
    except ElementNotFound:
        element = None
    return element

def click_all_checks(template_path, confidence=0.85, delay=0.3, tol=6):
    """
    Clique une fois par check en dédupliquant les matches proches.
    tol = rayon de proximité (en px) pour fusionner les doublons.
    """
    try:
        boxes = list(pyautogui.locateAllOnScreen(
            template_path,
            confidence=confidence,
            grayscale=True,
        ))
    except pyautogui.ImageNotFoundException:
        boxes = []

    if not boxes:
        # print("❌ Aucun check trouvé.")
        return 0

    # Centres triés du haut vers le bas puis gauche -> droite
    centers = [pyautogui.center(b) for b in boxes]
    centers.sort(key=lambda p: (p[1], p[0]))

    # Déduplication par proximité (regroupe les centres à ±tol px)
    unique = []
    for x, y in centers:
        if not unique or (abs(x - unique[-1][0]) > tol or abs(y - unique[-1][1]) > tol):
            unique.append((x, y))

    # Clique une fois par position unique
    for _, (x, y) in enumerate(unique, 1):
        pyautogui.click(x, y)
        # print(f"👉 Click {i} sur ({x}, {y})")
        time.sleep(delay)

    # print(f"✅ {len(unique)} check(s) cliqué(s) (dédupliqué).")
    return len(unique) 

def is_existe(tpl, confidence=0.9):
    """Retourne True si l'image est trouvée à l'écran, sinon False (sans crash)."""
    try:
        loc = pyautogui.locateOnScreen(tpl, confidence=confidence)
        return loc is not None
    except pyautogui.ImageNotFoundException:
        return False

def find_global_row(path, target, regex=r'(.*)', confidence=0.9, width = None, height = None, offset_x = 0, offset_y = 0, top = False, left = False, right = False):
    i = 1
    while True:
        # Screenshot complet
        screenshot_path = "logs/screen_list.png"
        pyautogui.screenshot(screenshot_path)
        img = cv2.imread(screenshot_path)

        # Localisation de la flèche
        matches = list(pyautogui.locateAllOnScreen(path, confidence=confidence))
        if not matches:
            raise ValueError('image non trouvé')

        leftmost = min(matches, key=lambda loc: loc.left)

        if left:
            x = leftmost.left
        else:
            x = leftmost.left + leftmost.width + offset_y
        if top:
            y = leftmost.top + leftmost.height
        else:
            y = leftmost.top 
        if not width:
            w = leftmost.width
        else:
            w = width
        if not height:
            h = leftmost.top + leftmost.height
        else:
            h = height

        roi = img[y:y+h, x:x+w]
        cv2.imwrite("logs/zone_ocr_num.png", roi)

        pil_img = Image.fromarray(roi).convert("L")
        text = pytesseract.image_to_string(pil_img, config="--psm 6").strip()

        print(f"[{i}] OCR détecté : '{text}'")
        i += 1

        match = re.search(regex, text)
        if match:
            if type(target) is int:
                detected = int(match.group(1))
            else:
                detected = match.group(1)
            detected = '801' + re.sub(r"[^\d]", "", match.group(1).strip())
            target = re.sub(r"[^\d]", "", str(target).strip())
            print(f'{detected} -> {target} est attendu')
            if detected == target:
                return True
            else:
                pyautogui.press('down')

def open_win(title):
    wins = gw.getWindowsWithTitle(title)
    if wins:
        win = wins[0]
        if win.isMinimized:
            win.restore()
        time.sleep(0.2)
        win.activate()
    return win


def json_order(path):
    if os.getenv('env').lower() == 'dev':
        json_path = json_path = Path(__file__).parent / "json" / "fichier_commande.json"
    elif os.getenv('env').lower() == 'test':
        json_path = json_path = Path(__file__).parent.parent / "json" / "fichier_commande.json"
    else:
        json_path = os.path.join(r"C:\Users\Public\Documents\Tests",path, "fichier_commande.json")
    # time.sleep(60)
    with open(json_path, "r", encoding="utf-8") as f:
        commandes = json.load(f)

    return commandes

def read_xml(order: str):
    host = os.getenv('sftp_pp_web_host')
    port_str = os.getenv('sftp_pp_web_port', '22')
    user = os.getenv('sftp_pp_web_user')
    password = os.getenv('sftp_pp_web_passwd')

    if not host or not user or not password:
        raise RuntimeError("Variables d'env SFTP manquantes: sftp_pp_web_host/user/passwd")

    try:
        port = int(port_str)
    except ValueError:
        raise RuntimeError(f"Port SFTP invalide: {port_str!r} (doit être un entier)")

    transport = None
    sftp = None
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_file = f"/shared/var/TicketXml/{order}.xml"

        # Lire en binaire et laisser le parser/decoder gérer l'encodage XML
        with sftp.open(remote_file, "rb") as f:   # équivalent moderne de sftp.file(...)
            data = f.read()

        # Si tu veux juste afficher le texte (en supposant UTF-8) :
        try:
            contenu = data.decode("utf-8")
        except UnicodeDecodeError:
            # Si l'encodage n'est pas UTF-8, ET.fromstring gérera via le prologue XML
            contenu = data.decode(errors="replace")

        # print("Contenu du fichier distant :")
        # print(contenu)

        # Exemple parsing direct (respecte l'encodage déclaré dans le XML)
        # root = ET.fromstring(data)
        # ... exploiter le XML ...

        return contenu  # ou retourner root si tu parses
    finally:
        if sftp:
            sftp.close()
        if transport:
            transport.close()

def _txt(node, tag):
    el = node.find(tag)
    return el.text.strip() if (el is not None and el.text is not None) else None

def _to_int(x):
    try:
        return int(x) if x is not None and x != "" else None
    except ValueError:
        return None

def _to_decimal(x):
    try:
        # Tes nombres sont déjà avec un point (.), donc pas besoin de remplacer la virgule.
        return Decimal(x) if x is not None and x != "" else None
    except Exception:
        return None

def _to_bool(x):
    if x is None:
        return None
    x = x.strip().lower()
    return x in ("true", "1", "oui", "vrai", "y")

def _parse_date_rfc2822(x):
    try:
        return parsedate_to_datetime(x) if x else None
    except Exception:
        return None

def _parse_date_fr(x):  # ex: "02/10/2025"
    try:
        return datetime.strptime(x, "%d/%m/%Y").date() if x else None
    except Exception:
        return None

def parse_ticket_vente(xml_text_or_bytes):
    """Retourne un dict: {'header': {...}, 'lines': [ {...}, ... ]}"""
    root = ET.fromstring(xml_text_or_bytes)

    # --- Entête ---
    header = {
        "genre": _txt(root, "Genre"),
        "num_commande_web": _txt(root, "NumCommandeWeb"),
        "num_ticket": _txt(root, "NumTicket"),
        "num_magasin": _to_int(_txt(root, "NumMagasin")),
        "date": _parse_date_rfc2822(_txt(root, "Date")),
        # Attention aux tags avec casse incohérente dans le XML (CLient)
        "civilite_client": _txt(root, "CiviliteCLient"),
        "nom_client": _txt(root, "NomCLient"),
        "prenom_client": _txt(root, "PrenomClient"),
        "tel_client": _txt(root, "TelClient"),
        "cp_client": _txt(root, "CPClient"),
        "ville_client": _txt(root, "VilleClient"),
        "mail_client": _txt(root, "MailClient"),
        "total_cde": _to_decimal(_txt(root, "TotalCde")),
        "passer_aujourdhui": _to_bool(_txt(root, "PasserAujourdHui")),
        "mode_com_client": _to_int(_txt(root, "ModeComClient")),
        "mode_livraison": _to_int(_txt(root, "ModeLivraison")),
        "adresse_liv_1": _txt(root, "AdresseLiv1Client"),
        "adresse_liv_2": _txt(root, "AdresseLiv2Client"),
        "cp_liv": _txt(root, "CPLivClient"),
        "ville_liv": _txt(root, "VilleLivClient"),
        "adresse_fac_1": _txt(root, "AdresseFac1Client"),
        "adresse_fac_2": _txt(root, "AdresseFac2Client"),
        "cp_fac": _txt(root, "CPFacClient"),
        "ville_fac": _txt(root, "VilleFacClient"),
        "adresse_cmd_1": _txt(root, "AdresseCmd1Client"),
        "adresse_cmd_2": _txt(root, "AdresseCmd2Client"),
        "cp_cmd": _txt(root, "CPCmdClient"),
        "ville_cmd": _txt(root, "VilleCmdClient"),
        "uuid_transac": _txt(root, "UUIDTransac"),
    }

    # --- Lignes ---
    lines = []
    consigne = []
    transport = []
    lignes_parent = root.find("LignesTicketVente")
    if lignes_parent is not None:
        for ln in lignes_parent.findall("LigneTicketVente"):
            line = {
                "genre": _txt(ln, "Genre"),
                "num_ticket": _txt(ln, "NumTicket"),
                "num_ligne_ticket": _txt(ln, "NumLigneTicket"),
                "statut": _txt(ln, "Statut"),
                "taux_tva": _to_decimal(_txt(ln, "TauxTVA")),
                "code_fournisseur": _txt(ln, "CodeFournisseur"),
                "code_art_fournisseur": _txt(ln, "CodeArtFournisseur"),
                "code_interne_article": _txt(ln, "CodeInterneArticle"),
                "code_transaction": _to_int(_txt(ln, "CodeTransaction")),
                "qte": _to_int(_txt(ln, "Qte")),
                "libelle_court": _txt(ln, "LibelleCourt"),
                "remise_client": _to_decimal(_txt(ln, "RemiseClient")),
                "prix_vente_ht": _to_decimal(_txt(ln, "PrixVenteHT")),
                "prix_vente_ttc": _to_decimal(_txt(ln, "PrixVenteTTC")),
                "solde": _to_decimal(_txt(ln, "Solde")),
                "montant_verse": _to_decimal(_txt(ln, "MontantVerse")),
                "date_livraison": _parse_date_fr(_txt(ln, "DateLivraison")),
                "livraison_express": _to_bool(_txt(ln, "LivraisonExpress")),
                "num_br": _txt(ln, "NumBR"),
            }
            if line['genre'] == 'TRANSPORT':
                transport.append(line)
            elif line['genre'] == 'CONSIGNE':
                consigne.append(line)
            else:
                lines.append(line)



    return {"header": header, "lines": lines, 'transport': transport, 'consigne': consigne}

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