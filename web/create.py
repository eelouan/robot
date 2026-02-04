import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np
import json

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images

from config.img import state
from config.img import environement_web

from config.img import *
from utils.utils import *
from utils.Assert import *
from utils.connect_db import *
from utils.request import *

def create_cart(browser,product,select):
    info = product.copy()
    if product['type'] == 'tire':
        if product["mode"] == 'sfs' or product["mode"] == 'mr':
            if product["mode"] == 'sfs':
                info['mode'] = {
                    "livraison": 1, "mode": 2
                    }
            else:
                info['mode'] = {
                    "livraison": 1,"mode": 3
                    }
        else:
            info['mode'] = {
                "livraison": 0,"mode": 1
                }
        if product["dispo"] == 'stock':
            info['dispo'] = 1
        else:
            info['dispo'] = 0
        if product["montage"]:
            if product["mode"] != 'cac' or product["consigne"]:
                raise AssertionError('Vous avez selectionné le montage - Le mode de livraison doit être cac, la consigne false et le type tire')
    else:
        if product["mode"] == 'sfs' or product["mode"] == 'mr':
            if product["mode"] == 'sfs':
                info['mode'] = {
                    "livraison": 1, "mode": 2
                    }
            else:
                info['mode'] = {
                    "livraison": 1,"mode": 3
                    }
        else:
            info['mode'] = {
                "livraison": 0,"mode": 1
                }
        if product["dispo"] == 'stock':
            info['dispo'] = 0
        else:
            info['dispo'] = 1
    # print(f'{product["mode"]} , {product["consigne"]} , {product["type"]}')
    if select:
        info = chose_product(browser,info)
    return info

def chose_product(browser,info):
    match state:
        case 'fr':
            if info["url"] == "":
                if info['consigne']:
                    elem = 1
                else:
                    elem = 1
                if info["montage"]:
                    elem = 9
                match info["type"]:
                    case "pa":
                        click_image(nav_pa)
                        wait(nav_voir_tout)
                        if is_existe(store_close_popin):
                            click_image(store_close_popin)
                            wait(nav_voir_tout)
                        click_image(nav_voir_tout)
                        if info['consigne']:
                            browser.wait_until_element_is_visible('css:#car-part', 10)
                            find_element(browser,'css:.category-container:nth-child(6)')
                            click_image(category_demarrage_charge)
                            find_element(browser,'css:.category-link:nth-child(1)')
                            click_image(cat_alternateur)
                        else:
                            browser.wait_until_element_is_visible('css:#car-part', 10)
                            find_element(browser,'css:.category-container:nth-child(1)')
                            wait(category_huile)
                            # wait(category_frein)
                            click_image(category_huile)
                            wait(huile)
                            # wait(freinage)
                            find_element(browser,'css:.category-link:nth-child(1)')
                            wait(cat_huile_moteur)
                            click_image(cat_huile_moteur)
                            # wait(cat_plaquette_frein)
                            # click_image(cat_plaquette_frein)
                        browser.element_should_visible('.lds-ring')
                    case "tire":
                        click_image(nav_pneu)
                        wait(nav_voir_tout)
                        if is_existe(store_close_popin):
                            click_image(store_close_popin)
                            wait(nav_voir_tout)
                        click_image(nav_voir_tout)
                    case "accessoire":
                        click_image(nav_accessory)
                    case _:
                        pass
                # if info['type'] == 'tire':
                #     product = ".listing [data-is-orderable=\""+ str(info['dispo'])+"\"]:nth-child("+str(elem)+")"
                # else:
                #     product = ".listing [data-is-orderable=\""+ str(info['dispo'])+"\"][data-is-ship-from-store=\""+str(info['mode']['livraison'])+"\"]:nth-child("+str(elem)+")"
                # find_element(browser,f'css:{product}')
                selector = '.listing [data-is-orderable="{}"][data-is-ship-from-store="{}"]'.format(
                    info['dispo'], info['mode']['livraison']
                )
                products = browser.find_elements(f'css:{selector}')
                # print(f'dispo :{info['dispo']}')
                # print(f'liv :{info['mode']['livraison']}')
                # print(len(products))
                product = products[elem - 1]
                ctas = browser.find_elements(f'css:{selector} .cta')
                cta = ctas[elem - 1]

                browser.click_element(cta)

                info['code8'] = product.get_attribute('data-reference')
                info['defaultQty'] = product.get_attribute('data-qty')
                wait(popin_add_cart)
                browser.go_to(os.getenv("pp_web_site"))
            else:
                browser.go_to(os.getenv("pp_web_site")+info['url'])
                wait(add_cart_from_product_page)
                info['code8'] = browser.find_element('css:.main-product .main-informations').get_attribute('data-reference')
                info['defaultQty'] = browser.find_element('css:.main-product .main-informations').get_attribute('data-qty')
                click_image(add_cart_from_product_page)
                wait(popin_add_cart, timeout=15)
        case 'es':
            browser.go_to(os.getenv("pp_web_site") + info['url'])
            wait(add_cart_from_product_page)
            info['code8'] = browser.find_element('css:.main-product .main-informations').get_attribute('data-reference')
            info['defaultQty'] = browser.find_element('css:.main-product .main-informations').get_attribute('data-qty')
            click_image(add_cart_from_product_page)
            wait(popin_add_cart, timeout=15)
        case 'it':
            browser.go_to(os.getenv("pp_web_site") + info['url'])
            wait(add_cart_from_product_page)
            info['code8'] = browser.find_element('css:.main-product .main-informations').get_attribute('data-reference')
            info['defaultQty'] = browser.find_element('css:.main-product .main-informations').get_attribute('data-qty')
            click_image(add_cart_from_product_page)
            wait(popin_add_cart, timeout=15)
    return info
    
def tunnel_achat(desktop, browser, infos, is_connect, mode_liv, code_mag, seller_mode=False):
    """
    Gère le tunnel d'achat complet depuis le panier jusqu'à la confirmation de commande.
    
    Args:
        desktop: Instance du desktop automation
        browser: Instance du navigateur (Selenium/Robot Framework)
        infos: Liste des informations des produits
        is_connect: Boolean indiquant si l'utilisateur est connecté
        mode_liv: Liste des modes de livraison (1=magasin, 2=domicile, 3=mondialrelay)
        code_mag: Code du magasin
        seller_mode: Boolean pour le mode vendeur
        send: Type d'envoi ('ob' pour OpenBravo, None pour paiement test)
    
    Returns:
        tuple: (infos enrichies, numéro de commande)
    """
    a = Assert()
    print(infos)
    
    # Étape 1 : Accès et configuration du panier
    _configure_cart(browser, infos)
    
    # Étape 2 : Mode vendeur si nécessaire
    if seller_mode:
        _handle_seller_mode(desktop, browser)
    
    # Étape 3 : Configuration de la livraison
    _configure_delivery(browser, infos, mode_liv)
    
    # Étape 4 : Choix du transporteur
    transporteur = _select_transporteur(desktop, browser, mode_liv)
    
    # Mise à jour des infos avec le transporteur
    for info in infos:
        info['transporteur'] = transporteur
    
    # Étape 5 : Adresses de livraison et facturation
    _handle_addresses(desktop, browser, is_connect, mode_liv)
    
    # Étape 6 : Informations de suivi (si non connecté)
    if not is_connect:
        _handle_contact_info(desktop, browser)
    else:
        click_image(cart_approve)
    
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    
    # Étape 7 : Paiement
    new_order = _handle_payment(browser, infos, mode_liv, code_mag, seller_mode)
    
    return infos, new_order


def _configure_cart(browser, infos):
    """Configure les quantités et options de montage dans le panier."""
    wait(cart)
    click_image(cart, 0.9)
    browser.wait_until_element_is_not_visible('css:.lds-ring', 15)
    
    elements = browser.find_elements('css:.item')
    infos = sort_cart(browser, infos)
    
    for i, info in enumerate(infos):
        # Gestion du montage
        if info.get("montage"):
            browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=15)
            checkbox = browser.find_element(f'css:.form-check:nth-child({i+1})')
            browser.click_element(checkbox)
        
        # Sélection de la quantité
        qty_selector = f'.item[data-reference="{info["code8"]}"] select.quantity-on-cart'
        browser.wait_until_element_is_visible(f"css:{qty_selector}")
        
        # Double tentative en cas d'échec
        try:
            find_element(browser, f'css:{qty_selector}')
        except:
            find_element(browser, f'css:{qty_selector}')
        
        browser.select_from_list_by_value(f'css:{qty_selector}', str(info['qty']))
    
    click_image(cart_approve)
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    pyautogui.press('enter')


def _handle_seller_mode(desktop, browser):
    """Gère l'authentification en mode vendeur."""
    input_selector = 'css:#impersonate_email'
    browser.wait_until_element_is_visible(input_selector, timeout=30)
    browser.click_element(input_selector)
    time.sleep(0.1)
    just_fill(desktop, os.getenv('fr_mail'))
    time.sleep(0.5)
    pyautogui.press("enter")


def _configure_delivery(browser, infos, mode_liv):
    """Configure les modes de livraison pour chaque produit."""
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    
    # URL de livraison selon le pays
    url_mapping = {
        'fr': f"{os.getenv("pp_web_site")}livraison/etape/1",
        'es': f"{os.getenv("pp_web_site")}entrega/escenario/1",
        'it': f"{os.getenv("pp_web_site")}livraison/etape/1"
    }
    url_liv = url_mapping.get(state, url_mapping['fr'])
    
    # Boucle jusqu'à sortir de la page de configuration
    while browser.get_location() == url_liv:
        elements = browser.find_elements('css:#shipment_cart_items .item')
        
        for i, element in enumerate(elements):
            if i >= len(infos):
                break
                
            mode = infos[i]['mode']['mode']
            
            # Mode 1 : Click & Collect
            if mode == 1:
                livraison = browser.find_element('css:input[value="click_and_collect"]', element)
                browser.select_checkbox(livraison)
            
            # Mode 2 ou 3 : Livraison à domicile ou point relais
            elif mode in [2, 3]:
                if infos[i]['type'] == 'tire':
                    livraison = browser.find_element('css:input[value="drop_shipping"]', element)
                else:
                    livraison = browser.find_element('css:input[value="ship_from_store"]', element)
                browser.select_checkbox(livraison)
        
        click_image(cart_1_approve)
        browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)


def _select_transporteur(desktop, browser, mode_liv):
    """Sélectionne le transporteur selon le mode de livraison."""
    transporteur = ''
    
    for mode in mode_liv:
        if mode == 1:
            # Magasin - pas de transporteur spécifique
            pass
        
        elif mode == 2:
            # Domicile
            click_image(cart_domicile)
            transporteur = 'dpd' if browser.get_element_count("css:#cart_carrier_dpd_classic") > 0 else 'tnt'
        
        elif mode == 3:
            # Mondial Relay
            click_image(cart_mr)
            wait(popin_mr)
            time.sleep(1)
            
            # Navigation et recherche du point relais
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('tab')
            just_fill(desktop, 'lil')
            
            wait(woosmap_mr)
            click_image(woosmap_mr)
            wait(default_mr)
            click_image(default_mr)
            pyautogui.press('esc')
            
            transporteur = 'mr'
    
    return transporteur


def _handle_addresses(desktop, browser, is_connect, mode_liv):
    """Gère les adresses de livraison et facturation."""
    # Adresse de livraison si non connecté et livraison à domicile
    if not is_connect and 2 in mode_liv:
        adr_liv(desktop, os.getenv('same_factu'))
    
    click_image(cart_1_approve)
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    
    # Adresse de facturation si différente
    if not is_connect and not os.getenv('same_factu'):
        browser.wait_until_element_is_visible('css:.billing-container', 10)
        adr_facturation(browser, desktop)
        click_image(valid_factu)


def _handle_contact_info(desktop, browser):
    """Gère les informations de contact pour le suivi."""
    print(f"is_connect: False")
    browser.wait_until_element_is_visible('css:.booking-follow-container', 10)
    
    click_image(suivi_email)
    just_fill(desktop, os.getenv(f'{environement_web["url"]}_web'))
    pyautogui.press('tab')
    
    # Numéro de téléphone selon le pays
    phone = os.getenv('es_phone') if state == 'es' else os.getenv('phone')
    just_fill(desktop, phone)
    
    click_image(cart_approve)


def _handle_payment(browser, infos, mode_liv, code_mag, send):
    """Gère le paiement et retourne le numéro de commande."""
    
    if not send:
        return _process_test_payment(browser, infos, mode_liv, code_mag)
    elif send == "ob":
        return _process_openbravo_payment(browser)
    
    raise ValueError(f"Type de paiement non reconnu: {send}")


def _process_test_payment(browser, infos, mode_liv, code_mag):
    """Traite un paiement de test."""
    test_card_selector = "xpath=//div[contains(@id, 'krcardsMenu')]"
    browser.wait_until_element_is_visible(test_card_selector)
    browser.click_element(test_card_selector)
    
    wait(pay_card_test)
    click_image(pay_card_test, 0.95)
    time.sleep(2)
    
    # Détermination du code magasin
    if 2 in mode_liv or 3 in mode_liv:
        code_mag = 801
    else:
        code_mag = infos.get('code_mag', code_mag)
    
    # Double tentative de validation
    for attempt in range(2):
        try:
            # time.sleep(3 if attempt == 0 else 2)
            click_image(pay_approve)
            time.sleep(0.2)
            browser.wait_until_element_is_visible('css:.order-confirmation', 10)
            
            url = browser.get_location()
            new_order = url.split('/')[-1]
            browser.go_to(os.getenv("pp_web_site"))
            
            return new_order
        except Exception as e:
            if attempt == 1:
                raise


def _process_openbravo_payment(browser):
    """Traite un envoi vers OpenBravo."""
    button_send = "xpath=//a[contains(normalize-space(.),'Envoyer vers OpenBravo')]"
    browser.wait_until_element_is_visible(button_send, timeout=30)
    browser.click_element(button_send)
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=30)
    browser.wait_until_element_is_visible('css:.order-confirmation', 30)
    
    num_order_selector = "xpath=//div[contains(normalize-space(.), '99')]"
    order_text = browser.get_text(num_order_selector).strip()
    new_order = re.search(r'\d{13}', order_text).group()
    return new_order

def adr_liv(desktop, same_factu):
    click_image(add_address_liv)
    wait(firstname_liv)
    click_image(firstname_liv)
    time.sleep(0.2)
    just_fill(desktop, os.getenv('firstname'))
    time.sleep(0.2)
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('lastname'))
    time.sleep(0.2)
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('address'))
    time.sleep(0.2)
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('address2'))
    time.sleep(0.2)
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('cp'))
    time.sleep(0.2)
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('city'))
    time.sleep(0.2)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')
    wait(cart_1_approve)

def pay_faster(desktop, browser, order, is_connect, label_expected):
    browser.wait_until_element_is_not_visible('css:.lds-ring', 15)
    elements = browser.find_elements('css:.item')
    Assert.assert_equals(label_expected, browser.find_element('css:.card-border .name').text, f"Nom du produit dans le panier est {label_expected}", 'check_libelle')
    click_image(cart_approve)
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    if is_connect == False:
        browser.wait_until_element_is_visible('css:.card-border',10)
        click_image(cart_no_account)
    else:
        pass
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    elements = browser.find_elements('css:#shipment_cart_items .item')
    name = browser.find_element('css:.informations-container .name').text
    for element in elements:
        if order['produits'][0]['mode'] == 'cac':
            livraison = browser.find_element('css:input[value="click_and_collect"]', element)
            browser.select_checkbox(livraison)
            # click_image(cart_no_livraison)
        elif order['produits'][0]['mode'] == 'sfs':
            if order['produits'][0]['type'] == 'tire':
                livraison = browser.find_element('css:input[value="drop_shipping"]',element)
            else:
                livraison = browser.find_element('css:input[value="ship_from_store"]',element)
            browser.select_checkbox(livraison)
    Assert.assert_equals(name, label_expected, f"Nom du produit dans l\'étape 1 est {label_expected}", 'check_libelle')
    click_image(cart_1_approve)
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    if browser.get_location() == f"{os.getenv("pp_web_site")}livraison/etape/1":
        pay_faster(desktop,browser,order, label_expected)
        return
    if order['produits'][0]['mode'] == 'sfs':
        click_image(cart_domicile)
    else:
        pass
    elements = browser.find_elements('css:.listing-items .listing-item .informations')
    for el in elements:
        txt = browser.get_text(el).strip()
        lines = txt.splitlines()

        if lines and lines[0].strip().upper() == "EXCLUSIVITÉ WEB":
            selected_line = lines[1] if len(lines) > 1 else ""
        else:
            selected_line = lines[0] if lines else ""

    Assert.assert_equals(label_expected, selected_line, f"Nom du produit dans l\'étape 2 est {selected_line}", 'check_libelle')

    click_image(cart_1_approve)
    browser.wait_until_element_is_visible('css:.booking-follow-container',10)
    browser.wait_until_element_is_not_visible('css:.lds-ring', timeout=10)
    if is_connect == False:
        click_image(suivi_email)
        just_fill(desktop, os.getenv('mail_tmp'))
        pyautogui.press('tab')
        just_fill(desktop, os.getenv('phone'))
    click_image(cart_approve)
    wait(test_card)
    browser.click_button('css:.listing-item-button')
    time.sleep(1)
    elements = browser.find_elements('css:.listing-items-container .informations')
    for el in elements:
        txt = browser.get_text(el).strip()
        lines = txt.splitlines()

        if lines and lines[0].strip().upper() == "EXCLUSIVITÉ WEB":
            selected_line = lines[1] if len(lines) > 1 else ""
        else:
            selected_line = lines[0] if lines else ""
    Assert.assert_equals(label_expected, selected_line, f"Nom du produit dans l\'étape de paiement est {selected_line}", 'check_libelle')

        # click_image(cart_approve)
    wait(test_card)
    click_image(test_card)
    time.sleep(0.5)
    click_image(pay_card_test)
    time.sleep(2)
    click_image(pay_approve)

def adr_facturation(browser, desktop):
    click_image(firstname_factu, y_offset=1.5)
    just_fill(desktop, os.getenv('firstname'))
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('lastname'))
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('address'))
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('address2'))
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('cp'))
    pyautogui.press('tab')
    just_fill(desktop, os.getenv('city'))
    click_image(valid_factu)
