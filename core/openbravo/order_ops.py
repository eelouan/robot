"""
Opérations atomiques liées aux commandes OpenBravo.
Création, modification et gestion des commandes.
"""

import time
import os
import logging
import pyautogui
import re

from selenium.common.exceptions import StaleElementReferenceException

from utils.utils import just_fill
from config.timeouts import DEFAULT_TIMEOUTS
from config.ob_selectors import OpenBravoSelectors
from ob.function import ob_select
from utils.Assert import Assert


def create_new_order(browser):
    """
    Crée une nouvelle commande vide.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Création d'une nouvelle commande...")
    
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.BUTTON_NEW, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    browser.click_element(OpenBravoSelectors.BUTTON_NEW)
    
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.BUTTON_CREATE_ORDER, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    time.sleep(DEFAULT_TIMEOUTS.LONG_WAIT)
    browser.click_element(OpenBravoSelectors.BUTTON_CREATE_ORDER)


def select_customer_by_phone(browser, desktop, phone):
    """
    Sélectionne un client par son numéro de téléphone.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        phone: Numéro de téléphone du client
    """
    logging.info(f"Sélection client par téléphone: {phone}")
    
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_CUSTOMER)
    time.sleep(DEFAULT_TIMEOUTS.LONG_WAIT)
    
    just_fill(desktop, phone)
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    pyautogui.press('enter')
    
    # Attendre et cliquer sur le client
    first_name = os.getenv('ob_first_name', 'Elouan')
    customer = OpenBravoSelectors.customer_by_name(first_name)
    
    browser.wait_until_element_is_visible(customer)
    browser.click_element(customer)


def add_products(browser, desktop, product_ids):
    """
    Ajoute une liste de produits à la commande en cours.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        product_ids: Liste des IDs de produits à ajouter
    """
    logging.info(f"Ajout de {len(product_ids)} produits...")
    
    # Note: ob_select doit être importé depuis ob_processor ou migré
    from ob.function import ob_select
    
    for product_id in product_ids:
        ob_select(browser, desktop, product_id)


def extract_new_ticket_number(browser):
    """
    Extrait le numéro du nouveau ticket depuis les alertes.
    
    Args:
        browser: Instance du navigateur
        
    Returns:
        str: Numéro du ticket ou None si non trouvé
    """
    rx = re.compile(r"n[°º]\s*:\s*([\w/\-]+)")
    ticket_number = None
    
    for _ in range(30):
        for el in browser.get_webelements(OpenBravoSelectors.ALERT_QUEUE):
            try:
                txt = (el.text or "").strip()
            except StaleElementReferenceException:
                continue
                
            if txt.startswith("Le ticket n"):
                m = rx.search(txt)
                if m:
                    ticket_number = m.group(1)
                    Assert.set_ob_ticket_number(ticket_number)
                    break
                    
        if ticket_number:
            break
        time.sleep(0.2)
    
    return ticket_number

def delete_order(browser):
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_DELETE_TICKET)
    browser.click_element(OpenBravoSelectors.BUTTON_DELETE_TICKET)
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_DELETE_TICKET)
    pyautogui.press('enter')