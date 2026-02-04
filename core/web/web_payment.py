import os
import re
import pyautogui
import time

from utils.utils import just_fill, click_image, wait, find_element
from utils.Assert import Assert
from config.img import *
from web.create import adr_facturation
from core.web import web_common
from config.ecommerce_selectors import EcommerceSelectors

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

    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, 15)
    if browser.find_elements(EcommerceSelectors.LOGIN_PAGE):
        time.sleep(1)
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(1)
        # browser.click_element(EcommerceSelectors.ADD_ACCOUNT)
        browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, 15)
    
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
    
    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=10)
    
    # Étape 7 : Paiement
    new_order = _handle_payment(browser, mode_liv, code_mag, seller_mode)
    
    return infos, new_order

def _handle_payment(browser, mode_liv, code_mag, send):
    """Gère le paiement et retourne le numéro de commande."""
    
    if not send:
        return _process_test_payment(browser, mode_liv, code_mag)
    elif send == "ob":
        return _process_openbravo_payment(browser)
    
    raise ValueError(f"Type de paiement non reconnu: {send}")


def _process_test_payment(browser, mode_liv, code_mag):
    """Traite un paiement de test."""
    test_card_selector = "xpath=//div[contains(@id, 'krcardsMenu')]"
    browser.wait_until_element_is_visible(test_card_selector)
    browser.click_element(test_card_selector)
    
    wait(pay_card_test)
    click_image(pay_card_test, 0.95)
    time.sleep(2)
    
    # Détermination du code magasin
    if 2 in mode_liv or 3 in mode_liv:
        effective_code_mag = '801'
    else:
        effective_code_mag = code_mag
    
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
    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=30)
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

def _configure_cart(browser, infos):
    """Configure les quantités et options de montage dans le panier."""
    wait(cart)
    click_image(cart, 0.9)
    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, 15)
    
    elements = browser.find_elements('css:.item')
    infos = web_common.sort_cart(browser, infos)
    
    for i, info in enumerate(infos):
        # Gestion du montage
        if info.get("montage"):
            browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=15)
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
    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=10)
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
    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=10)
    
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
        browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=10)


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
    browser.wait_until_element_is_not_visible(EcommerceSelectors.SPINNER, timeout=10)
    
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
    just_fill(desktop, os.getenv(f'{os.getenv("pp_web_site")}_web'))
    pyautogui.press('tab')
    
    # Numéro de téléphone selon le pays
    phone = os.getenv('es_phone') if state == 'es' else os.getenv('phone')
    just_fill(desktop, phone)
    
    click_image(cart_approve)