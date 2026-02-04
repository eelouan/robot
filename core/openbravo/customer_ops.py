"""
Opérations atomiques liées aux clients OpenBravo.
Briques réutilisables de bas niveau pour la gestion des clients.
"""

import time
import os
import logging
import pyautogui
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from utils.utils import just_fill
from config.timeouts import DEFAULT_TIMEOUTS
from config.ob_selectors import OpenBravoSelectors


def open_customer_form(browser, desktop):
    """
    Ouvre le formulaire de modification d'un client.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    logging.info("Ouverture du formulaire client...")
    
    # Ouvrir la popup clients
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.BUTTON_CUSTOMER, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    browser.click_element(OpenBravoSelectors.BUTTON_CUSTOMER)
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.MODAL_CUSTOMER, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    
    # Rechercher par téléphone
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    just_fill(desktop, os.getenv('ob_phone'))
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    pyautogui.press('enter')
    
    # Sélectionner le client
    customer = OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name'))
    browser.wait_until_element_is_visible(
        customer, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.BUTTON_UPDATE_CUSTOMER, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    browser.click_element(OpenBravoSelectors.BUTTON_UPDATE_CUSTOMER)
    
    # Ouvrir en édition
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.BUTTON_UPDATE, 
        timeout=f"{DEFAULT_TIMEOUTS.ELEMENT_VISIBLE} s"
    )
    browser.click_element(OpenBravoSelectors.BUTTON_UPDATE)
    time.sleep(DEFAULT_TIMEOUTS.LONG_WAIT)
    
    logging.info("Formulaire client ouvert")


def set_email(browser, desktop, email):
    """
    Modifie l'email du client dans le formulaire.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        email: Email à saisir
    """
    browser.click_element(OpenBravoSelectors.INPUT_EMAIL)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.press('delete')
    time.sleep(0.5)
    just_fill(desktop, email)


def submit_customer_form(browser):
    """
    Soumet le formulaire client.
    
    Args:
        browser: Instance du navigateur
    """
    # Masquer le scrim pour voir l'alerte
    browser.execute_javascript("""
        var nodes = document.querySelectorAll("div.obUiFormElement-messageArea-scrim");
        nodes.forEach(function(e) { e.style.display = 'none'; });
    """)
    browser.wait_until_element_is_not_visible(OpenBravoSelectors.MESSAGE_SCRIM, timeout="5 s")
    
    browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_SUBMIT)
    browser.click_element(OpenBravoSelectors.BUTTON_SUBMIT)


def check_validation_error(browser, timeout_seconds=3):
    """
    Vérifie si une erreur de validation est affichée.
    
    Args:
        browser: Instance du navigateur
        timeout_seconds: Temps d'attente maximum en secondes
    
    Returns:
        bool: True si une erreur de validation est visible
    """
    max_attempts = int(timeout_seconds * 10)  # 10 tentatives par seconde
    
    for attempt in range(max_attempts):
        try:
            browser.element_should_be_visible(OpenBravoSelectors.ALERT_QUEUE)
            logging.debug(f"Erreur de validation détectée après {attempt + 1} tentatives")
            return True
        except (NoSuchElementException, TimeoutException):
            time.sleep(0.1)
        except Exception as e:
            logging.warning(f"Erreur inattendue lors de la vérification: {e}")
            time.sleep(0.1)
    
    logging.debug(f"Aucune erreur de validation après {max_attempts} tentatives")
    return False


def close_customer_form(browser):
    """
    Ferme le formulaire client.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Fermeture du formulaire client...")
    
    # Essayer de cliquer sur Annuler
    try:
        browser.wait_until_element_is_enabled(
            OpenBravoSelectors.BUTTON_CANCEL,
            timeout=f"{DEFAULT_TIMEOUTS.SHORT_WAIT} s"
        )
        browser.click_element(OpenBravoSelectors.BUTTON_CANCEL)
        browser.wait_until_element_is_enabled(
            OpenBravoSelectors.BUTTON_CLOSE_MODAL,
            timeout=f"{DEFAULT_TIMEOUTS.SHORT_WAIT} s"
        )
        browser.click_element(OpenBravoSelectors.BUTTON_CLOSE_MODAL)
        logging.info("Formulaire fermé via bouton Annuler")
    except (NoSuchElementException, TimeoutException) as e:
        logging.debug(f"Bouton Annuler non trouvé: {e}")
    except Exception as e:
        logging.warning(f"Erreur lors du clic sur Annuler: {e}")
    
    # Fermer les popups avec Échap
    for _ in range(DEFAULT_TIMEOUTS.ESC_KEY_REPEATS):
        try:
            browser.keyboard_key("press", "Escape")
            time.sleep(DEFAULT_TIMEOUTS.ESC_KEY_DELAY)
        except Exception as e:
            logging.debug(f"Erreur lors de l'envoi d'Escape: {e}")
    
    logging.info("Formulaire client fermé")

def modale_customer_order(browser, desktop):
    """
    Ouvre la modal de création de commande client.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CREATE_ORDER, timeout="15 s")
    browser.click_element(OpenBravoSelectors.BUTTON_CREATE_ORDER)
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_CUSTOMER)
    # browser.wait_until_element_is_visible(OpenBravoSelectors.INPUT_CUSTOMER)
    # browser.click_element(OpenBravoSelectors.INPUT_CUSTOMER)
    time.sleep(1)
    just_fill(desktop, "0611221122")
    time.sleep(0.2)
    pyautogui.press('enter')
    browser.wait_until_element_is_visible(OpenBravoSelectors.customer_by_name('Elouan'))
    browser.click_element(OpenBravoSelectors.customer_by_name('Elouan'))
