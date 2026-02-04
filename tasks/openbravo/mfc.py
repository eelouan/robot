"""
Tâche MFC : Test de modification de fiche client OpenBravo.
Vérifie les modifications de données client et d'adresses.
"""
import time
import os
import logging
import inspect
import pyautogui

from utils.utils import just_fill
from core.openbravo import common, customer_ops
from ob.function import update_customer
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche MFC.
    Teste les modifications de fiche client.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'mfc',
        'description': 'Test modification fiche client'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: MFC - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test MFC
        mfc(browser, desktop)
        
        # Succès
        common.finalize_success(config['name'].upper())
        
    except Exception as e:
        common.handle_error(e, config)
        raise
    
    finally:
        if context is None:
            common.clean(start_time, desktop, browser, config)
        else:
            logging.info("⏭️ Tâche terminée")


def mfc(browser, desktop):
    """
    Teste le processus complet MFC.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test MFC - Modification fiche client...")
    
    try:
        # Étape 1: Modification fiche client (MFC-001)
        print("  👤 Modification fiche client...")
        
        # Ouvrir le sélecteur de client
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CUSTOMER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_CUSTOMER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_CUSTOMER, timeout="15 s")
        time.sleep(0.5)
        just_fill(desktop, os.getenv('ob_phone'))
        time.sleep(0.5)
        pyautogui.press('enter')
        
        # Sélectionner et modifier le client
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name')), 
            timeout="15 s"
        )
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_UPDATE_CUSTOMER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE_CUSTOMER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_UPDATE, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE)
        
        # Première modification
        update_customer(browser, desktop, popin_name="customer", update=False, case="MFC 001", name=f)
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_SUBMIT_CUSTOMER)
        browser.click_element(OpenBravoSelectors.BUTTON_SUBMIT_CUSTOMER)
        print("  ✓ Première modification effectuée")
        
        # Fermer et re-chercher avec nouveau téléphone
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CLOSE2, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_CLOSE2)
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_CUSTOMER, timeout="15 s")
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.press('delete')
        time.sleep(0.5)
        just_fill(desktop, os.getenv('ob_phone_update'))
        time.sleep(0.5)
        pyautogui.press('enter')
        
        # Modifier à nouveau avec les données mises à jour
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name_update')), 
            timeout="15 s"
        )
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_UPDATE_CUSTOMER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE_CUSTOMER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_UPDATE, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE)
        
        # Seconde modification (restauration)
        update_customer(browser, desktop, popin_name="customer", update=True, case="MFC 001", name=f)
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_SUBMIT_CUSTOMER)
        browser.click_element(OpenBravoSelectors.BUTTON_SUBMIT_CUSTOMER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CLOSE2, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_CLOSE2)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CLOSE_MODAL, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_CLOSE_MODAL)
        print("  ✓ Fiche client modifiée et restaurée")
        
        # Étape 2: Modification adresse client (MFC-005)
        print("  🏠 Modification adresse client...")
        
        # Ouvrir le sélecteur d'adresse
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_ADDRESS, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_ADDRESS)
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_ADDRESS, timeout="15 s")
        
        # Sélectionner et modifier l'adresse
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.address_by_value(os.getenv('ob_address')), 
            timeout="15 s"
        )
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_UPDATE_ADDRESS, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE_ADDRESS)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_UPDATE_ADDRESS_MENU, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE_ADDRESS_MENU)
        
        # Première modification d'adresse
        update_customer(browser, desktop, popin_name="address", update=False, case="MFC 005", name=f)
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_SUBMIT_ADDRESS)
        browser.click_element(OpenBravoSelectors.BUTTON_SUBMIT_ADDRESS)
        print("  ✓ Première modification d'adresse effectuée")
        
        # Modifier à nouveau l'adresse
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_UPDATE_DETAIL)
        browser.click_element(OpenBravoSelectors.BUTTON_UPDATE_DETAIL)
        update_customer(browser, desktop, popin_name="address", update=True, case="MFC 005", name=f)
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_SUBMIT_ADDRESS)
        browser.click_element(OpenBravoSelectors.BUTTON_SUBMIT_ADDRESS)
        
        # Fermer
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CLOSE_ADDRESS, timeout="15 s")
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_CLOSE_ADDRESS)
        browser.click_element(OpenBravoSelectors.BUTTON_CLOSE_ADDRESS)
        print("  ✓ Adresse modifiée et restaurée")
        
        print("✅ Test MFC terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test MFC: {e}")
        raise