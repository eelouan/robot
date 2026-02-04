import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import zxingcpp


from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images
from decimal import Decimal,ROUND_HALF_UP
from selenium.common.exceptions import StaleElementReferenceException



from config.img import state as State
from config.img import environement_web

from utils.utils import *
from utils.connect_db import *
from utils.Assert import *
from utils.request import *
from web.connect import *

load_dotenv()

def ob_connect(desktop, first=True, user="adm"):
    time.sleep(4)
    # try:
    #     if first:
    #         print(ob["user_connect_adm"] if user == "adm" else (ob["user_connect_sell"]))
    #         wait(ob["user_connect_adm"], confidence=0.9, timeout=15) if user == "adm" else wait(ob["user_connect_sell"], confidence=0.9, timeout=15)
    #     else:
    #         wait(ob["user_connect_adm"], confidence=0.95, timeout=5) if user == "adm" else wait(ob["user_connect_sell"], confidence=0.95, timeout=5)
    #     click_image(ob["user_connect_adm"], confidence=0.95) if user == "adm" else click_image(ob["user_connect_sell"], confidence=0.95)
    # except Exception:
    if first:
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
    just_fill(desktop, os.getenv('user_ob_adm')) if user == "adm" else just_fill(desktop, os.getenv('user_ob_sell'))
    pyautogui.press("tab")
    time.sleep(0.5)
    just_fill(desktop, os.getenv('passwd_ob_adm')) if user == "adm" else just_fill(desktop, os.getenv('passwd_ob_sell'))
    time.sleep(0.5)
    pyautogui.press('enter')
    # if first and user == 'adm':
        # wait_and_click(ob["ok"])
        # wait_and_click(ob["web_pos"])

def cash_register_closing(browser):
    try_ = 0
    double = False
    while True:
        try:
            text = 'Supprimer Tout'
            browser.click_element(f"xpath=//button[.//div[normalize-space(text())='{text}']]")
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(1)
            double = True
            wait_and_click(ob["close_next"])
            break
        except Exception:
            try_ += 1
        if try_ == 3:
            break
        time.sleep(1)
    wait_and_click(ob["close_next"])
    if double:
        wait_and_click(ob["close_next"])
    retries = 3
    for attempt in range(1, retries+1):
        try:
            click_image(ob["ok"])
            return
        except Exception:
            if attempt < retries:
                time.sleep(1)
    time.sleep(2)
    click_all_checks(ob["count_register"], confidence=0.82)
    click_image(ob["close_next"])
    time.sleep(1)
    if browser.is_element_visible("css:#terminal_containerWindow_cashUp_OBPOS_modalApprovalReason_control"):
        pyautogui.press("right")
        pyautogui.press("tab")
        pyautogui.press("space")
    wait_and_click(ob["total_amount"], confidence=0.8)
    click_image(ob["close_next"])
    time.sleep(1)
    wait_and_click(ob["close_next"])
    wait_and_click(ob["ok"])

def select_menu(browser, menu):
    button_menu = "xpath://button[contains(@id, 'mainMenu_menuHolder_mainMenuButton')]"
    # nav_menu = f"xpath=//div[contains(@id,'{menu}')]"
    nav_menu = (
        "xpath=//div[contains(@id,'{name}')]"
    ).format(name=menu)

    browser.wait_until_element_is_visible(button_menu)
    # browser.wait_until_element_is_enabled(button_menu)
    browser.click_element(button_menu)
    browser.wait_until_element_is_visible(nav_menu)
    browser.click_element(nav_menu)

def ob_leave():
    time.sleep(1)
    pyautogui.typewrite('0')
    time.sleep(0.2)
    pyautogui.press('enter')

def ob_select_family(browser, family):
    text = 'FAMILLE'
    browser.wait_until_element_is_visible(f"xpath=//button[.//div[normalize-space(text())='{text}']]")
    browser.click_element(f"xpath=//button[.//div[normalize-space(text())='{text}']]")
    browser.wait_until_element_is_visible(f"xpath=//button[.//div[normalize-space(text())='{family}']]")
    browser.click_element(f"xpath=//button[.//div[normalize-space(text())='{family}']]")
    browser.click_element("xpath=(//ul[@class='obUiScrollableTable-scrollArea-tbody']//li)[1]")

def ob_select(browser, desktop, product, names=None, nb=1):
    text = 'RECHERCHER'
    browser.wait_until_element_is_visible(f"xpath=//button[.//div[normalize-space(text())='{text}']]", timeout=30)
    browser.click_element(f"xpath=//button[.//div[normalize-space(text())='{text}']]")
    button_search = 'css:#terminal_containerWindow_pointOfSale_multiColumn_rightPanel_toolbarpane_searchCharacteristic_searchCharacteristicTabContent_searchProductCharacteristicHeader_productSearchButton'
    product_line = (
        "xpath=//*[contains(@id,'_product') and contains(normalize-space(.), '21861963')]"
        "/../following-sibling::button[contains(@id,'showServicesButton')]"
    ).format(p=product)

    time.sleep(2)
    just_fill(desktop, product)
    pyautogui.press('enter')
    browser.wait_until_element_is_enabled(button_search)
    time.sleep(0.5)
    # for _ in range(nb):
    browser.click_element("xpath=(//ul[contains(@id,'searchCharacteristicTabContent_products_tbody')]//li)[1]")
        # time.sleep(1)
    if names:
        for name in names:
            service_line = (
                "xpath=(//*[contains(@id, 'searchCharacteristicTabContent_products_tbody_control') and contains(normalize-space(.), '{title}')])"
            ).format(title=name)
            
            browser.wait_until_page_contains_element(product_line, timeout=10)
            browser.wait_until_element_is_visible(product_line, timeout=10)
            browser.wait_until_element_is_enabled(product_line, timeout=10)
            browser.click_element(product_line)
            browser.wait_until_page_contains_element(service_line, timeout=10)
            browser.wait_until_element_is_visible(service_line, timeout=10)
            browser.wait_until_element_is_enabled(service_line, timeout=10)
            browser.click_element(service_line)
            
            time.sleep(1)

def go_to_menu(browser, name):
    menu = "xpath=//div[contains(@id,'mainMenu_menuHolder_mainMenuButton_components')"

    elem_menu = (
        "xpath=//div[contains(@id,'mainMenu') "
        "and contains(., '{name}')]"
    ).format(name=name)

    browser.wait_until_page_contains_element(menu, timeout=15)
    browser.click_element(menu)
    browser.wait_until_page_contains_element(elem_menu, timeout=15)
    browser.click_element(elem_menu)

def client():
    pass

def open_ticket():
    pass

def return_no_ticket():
    pass
    
def wait_init(browser):
    locator = "xpath=//div[contains(@id,'terminal_alertQueue')]"
    for _ in range(30):
            for el in browser.get_webelements(locator):
                try:
                    txt = (el.text or "").strip()
                    print(txt)
                except StaleElementReferenceException:
                    continue
    return True

def screenshot_and_decode(
    region: Optional[Tuple[int, int, int, int]] = None,
    grayscale: bool = True,
    try_rotations: bool = True,
    save_debug_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Prend une capture de l'écran (ou d'une région) et tente de décoder tous les codes-barres/QR.

    Params
    ------
    region: (left, top, width, height) en pixels. None => plein écran.
    grayscale: convertit l'image en niveau de gris (souvent plus robuste).
    try_rotations: si aucun résultat, retente en 90/180/270° (certes un peu lent).
    save_debug_path: si fourni, sauvegarde le screenshot pour debug (ex: "last_capture.png").

    Retour
    ------
    Liste de dicts: [{format, text, position, orientation, symbology_identifier}, ...]
    """
    # 1) Screenshot
    img: Image.Image = pyautogui.screenshot(region=region)  # PIL.Image
    if grayscale:
        img = img.convert("L")

    if save_debug_path:
        img.save(save_debug_path)

    # 2) Première passe
    results = zxingcpp.read_barcodes(img)
    parsed = _parse_zxing_results(results)
    if parsed:
        return parsed

    # 3) Rotations si rien trouvé
    if try_rotations:
        for angle in (90, 180, 270):
            img_rot = img.rotate(angle, expand=True)
            results = zxingcpp.read_barcodes(img_rot)
            parsed = _parse_zxing_results(results)
            if parsed:
                return parsed

    return []

def _parse_zxing_results(results):
    for r in results or []:
        text = r.text
    return text

def update_customer(browser, desktop, popin_name, update, name, case):
    nb_case = f"{case} - " if case else ''
    if popin_name == "customer":
        mandatory = {
            "select": {
                "ob_category": "customerCategory",
                "ob_civility": "greeting",
                "ob_langage": "customerLanguage",
            },
            "input": {
                "ob_last_name": "lastName",
                "ob_first_name": "firstName",
                "ob_phone": "customerPhone",
                "ob_mail": "customerEmail",
                "ob_tax_id": "customerTaxId",
                "ob_other_number": "alternativePhone",
                "ob_comment": "comments",
                "ob_ice_number": "cCFLDSICE",
            },
            "button": {
                "ob_invoice": "invoiceViaEmail",
                "ob_commercial_auth": "commercialauth",
                "ob_agree": "isCustomerConsent",
            }
        }
        trad = {
            "ob_category":"Catégorie de tiers",
            "ob_civility":"Civilité",
            "ob_langage":"Langage",
            "ob_last_name":"Nom",
            "ob_first_name":"Prénom",
            "ob_phone":"Téléphone",
            "ob_mail":"Email",
            "ob_tax_id":"Identifiant fiscal",
            "ob_other_number":"Autre numéro de téléphone",
            "ob_comment":"Commentaires",
            "ob_ice_number":"Numéro ICE",
        }
    else:
        mandatory = {
            "select": {
                "ob_country": "customerAddrCountry",
            },
            "input": {
                "ob_zip_code": "customerAddrPostalCode",
                "ob_city": "customerAddrCity",
                "ob_address": "customerAddrName",
            }
        }
        trad = {
            "ob_country":"Pays",
            "ob_address":"Adresse",
            "ob_zip_code":"Code postal",
            "ob_city":"Ville"
        }
    
    popin_update = "xpath//*[contains(@id, 'customerCreateAndEdit')]"

    # browser.wait_until_element_is_visible(popin_update, timeout="15 s")
    time.sleep(2)


    for champs, items in mandatory.items():
        for key, xpath in items.items():
            value = os.getenv(f"{key}_update") if update else os.getenv(key)
            value_update = os.getenv(f"{key}_update") if not update else os.getenv(key)
            step = "Premier passage" if not update else "Second passage"

            match champs:
                case "select":
                    select = f"xpath=//select[contains(@id,'{xpath}')]"

                    options = browser.get_list_items(select)
                    Assert.assert_equals(browser.get_selected_list_label(select), value, f"{nb_case} Le selecteur \"{trad[key]}\" contenait {browser.get_selected_list_label(select)} avant modification {value} est attendu ({step})", name)

                    for opt in options:
                        if value_update in opt:
                            browser.select_from_list_by_label(select, opt)
                            break
                case "input":
                    # if os.getenv(key) != "null":
                    elem = ("xpath://input[contains(@id, '{selector}')]").format(selector=xpath)
                    val = browser.get_element_attribute(elem, "value")
                    exp = value

                    if exp and val:
                        Assert.assert_equals(val,exp,f"{nb_case} Le champ \"{trad[key]}\" contenait {val} avant modification {exp} est attendu ({step})",name)
                    browser.click_element(elem)
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.5)
                    pyautogui.press('delete')
                    if value_update != "null":
                        time.sleep(0.5)
                        just_fill(desktop, value_update)
                    if key == "ob_mail" or key == "ob_zip_code":
                        time.sleep(2)
                        browser.execute_javascript("""
                        var nodes = document.querySelectorAll("div.obUiFormElement-messageArea-scrim");
                        nodes.forEach(function(e) { e.style.display = 'none'; });
                        """)
                        browser.execute_javascript("""
                        var nodes = document.querySelectorAll("div.obUiFormElement-messageArea-suggestionList");
                        nodes.forEach(function(e) { e.style.display = 'none'; });
                        """)

                        scrim = "xpath=//div[contains(@class,'obUiFormElement-messageArea-scrim')]"
                        browser.wait_until_element_is_not_visible(scrim, timeout="5 s")
                
                case "button":
                    browser.click_element(f"xpath://button[contains(@id, '{xpath}')]")