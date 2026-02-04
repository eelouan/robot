"""
Opérations atomiques liées aux retours OpenBravo.
Gestion des retours de tickets, approbations, etc.
"""

import time
import os
import logging
import pyautogui
from selenium.common.exceptions import StaleElementReferenceException

from utils.utils import just_fill
from utils.Assert import Assert
from config.timeouts import DEFAULT_TIMEOUTS
from config.ob_selectors import OpenBravoSelectors


def open_return_modal(browser):
    """
    Ouvre la modale de retour.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Ouverture de la modale de retour...")
    
    # Note: select_menu doit être importé depuis ob_processor ou migré
    from core.openbravo.ui_ops import select_menu
    
    select_menu(browser, "menuReturn_lbl")
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.MODAL_RETURN, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)


def search_ticket(browser, desktop, ticket_number):
    """
    Recherche un ticket par son numéro.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        ticket_number: Numéro du ticket
    """
    logging.info(f"Recherche du ticket: {ticket_number}")
    
    just_fill(desktop, ticket_number)
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    pyautogui.press('enter')
    
    # Attendre que la ligne du ticket soit visible
    line_ticket = OpenBravoSelectors.line_ticket(ticket_number)
    browser.wait_until_element_is_visible(
        line_ticket, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    browser.click_element(line_ticket)


def select_return_items(browser, all=False):
    """
    Sélectionne les articles à retourner.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Sélection des articles à retourner...")
    if all:
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.ALL_LINES, 
            timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
        )
        browser.click_element(OpenBravoSelectors.ALL_LINES)
    else:
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.LINE1_CHECK, 
            timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
        )
        browser.click_element(OpenBravoSelectors.LINE1_CHECK)
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    pyautogui.press('enter')


def select_return_reason(browser):
    """
    Sélectionne la raison du retour.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Sélection de la raison du retour...")
    
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.MODAL_REASON, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    pyautogui.press('enter')


def approve_return_with_admin(browser, desktop):
    """
    Approuve le retour avec les identifiants administrateur.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    logging.info("Approbation du retour avec identifiants admin...")
    
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.MODAL_RETURN_APPROVAL, 
        timeout="30 s"
    )
    
    time.sleep(DEFAULT_TIMEOUTS.VERY_SHORT_WAIT)
    just_fill(desktop, os.getenv('user_ob_adm'))
    time.sleep(DEFAULT_TIMEOUTS.VERY_SHORT_WAIT)
    pyautogui.press("tab")
    just_fill(desktop, os.getenv('passwd_ob_adm'))
    time.sleep(DEFAULT_TIMEOUTS.MEDIUM_WAIT)
    pyautogui.press('enter')


def process_return(browser, desktop, ticket_number):
    """
    Traite un retour de ticket complet.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        ticket_number: Numéro du ticket à retourner
    """
    logging.info(f"Traitement du retour pour le ticket: {ticket_number}")
    
    open_return_modal(browser)
    search_ticket(browser, desktop, ticket_number)
    select_return_items(browser)
    select_return_reason(browser)
    approve_return_with_admin(browser, desktop)


def verify_tickets_saved(browser, case_name, function_name):
    """
    Vérifie que tous les tickets ont été correctement enregistrés.
    
    Args:
        browser: Instance du navigateur
        case_name: Nom du cas de test (ex: 'CCR 001')
        function_name: Nom de la fonction appelante
        
    Raises:
        AssertionError: Si le message de confirmation n'apparaît pas
    """
    logging.info("Vérification de l'enregistrement des tickets...")
    
    success_message = "Tous les tickets ont été correctement enregistrés"
    
    for _ in range(30):
        for el in browser.get_webelements(OpenBravoSelectors.ALERT_QUEUE):
            try:
                txt = (el.text or "").strip()
            except StaleElementReferenceException:
                continue
            
            if txt.startswith(success_message):
                Assert.element_should_visible(
                    browser, 
                    OpenBravoSelectors.ALERT_QUEUE, 
                    case_name, 
                    function_name
                )
                logging.info("✓ Tickets enregistrés avec succès")
                return True
        
        time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    
    raise AssertionError(
        f"Message de confirmation non trouvé après "
        f"{DEFAULT_TIMEOUTS.ALERT_CHECK_ATTEMPTS} tentatives: '{success_message}'"
    )