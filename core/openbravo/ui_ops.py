"""
Opérations atomiques liées à l'interface OpenBravo.
Gestion des menus, modales, etc.
"""

import time
import logging
import pyautogui

from config.timeouts import DEFAULT_TIMEOUTS
from config.ob_selectors import OpenBravoSelectors


def close_all_modals(browser):
    """
    Ferme toutes les modales ouvertes en envoyant Escape.
    
    Args:
        browser: Instance du navigateur
    """
    for attempt in range(DEFAULT_TIMEOUTS.ESC_KEY_REPEATS):
        try:
            browser.keyboard_key("press", "Escape")
            time.sleep(DEFAULT_TIMEOUTS.ESC_KEY_DELAY)
        except Exception as e:
            logging.debug(f"Erreur lors de l'envoi d'Escape #{attempt + 1}: {e}")

def close_dynamic_popup(browser):
    """
    Ferme la popup dynamique de confirmation.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Fermeture de la popup dynamique...")
    
    try:
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_DYNAMIC)
        pyautogui.press('esc')
    except Exception as e:
        logging.debug(f"Popup dynamique non trouvée: {e}")

def select_menu(browser, menu):
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MENU)
    browser.click_element(OpenBravoSelectors.BUTTON_MENU)
    browser.wait_until_element_is_visible(OpenBravoSelectors.nav_menu(menu))
    browser.click_element(OpenBravoSelectors.nav_menu(menu))

def clear_scrims(browser):
    """
    Nettoie les scrims transparents de l'interface.
    
    Args:
        browser: Instance du navigateur
    """
    browser.execute_javascript("""
    var nodes = document.querySelectorAll("div.onyx-scrim-transparent");
    nodes.forEach(function(e) { e.style.display = 'none'; });
    """)