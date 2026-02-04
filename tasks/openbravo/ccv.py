"""
Tâche CCV : Test de facturation et multi-commandes OpenBravo.
Vérifie le processus complet de création commande, facturation et multi-commande.
"""
import time
import os
import logging
import inspect
import pyautogui
from RPA.Desktop import Desktop
from selenium.common.exceptions import StaleElementReferenceException

from config.img import ob
from utils.utils import wait, just_fill
from core.openbravo import common
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche CCV.
    Teste la facturation et multi-commandes.
    """
    start_time = time.time()
    
    config = {
        'number': '024',
        'category': '4-OB',
        'name': 'ccv',
        'description': 'Test facturation et multi-commandes'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: CCV - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test CCV
        ccv(browser, desktop)
        
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

def ccv(browser, desktop):
    """
    Teste le processus complet CCV.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test CCV - Facturation et multi-commandes...")
    
    try:
        # Étape 1: Créer première commande client
        print("  📦 Création première commande client...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CREATE_ORDER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_CREATE_ORDER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_CUSTOMER)
        time.sleep(1)
        just_fill(desktop, "0611221122")
        time.sleep(0.2)
        pyautogui.press('enter')
        browser.wait_until_element_is_visible(OpenBravoSelectors.customer_by_name('Elouan'))
        browser.click_element(OpenBravoSelectors.customer_by_name('Elouan'))
        ob_select(browser, desktop, '21861963')
        ob_select(browser, desktop, '21861963')
        print("  ✓ Première commande créée")
        
        # Étape 2: Créer deuxième commande
        print("  🆕 Création deuxième commande...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_NEW, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_NEW)
        ob_select(browser, desktop, '28557203')
        ob_select(browser, desktop, '21691294')
        print("  ✓ Deuxième commande créée")
        
        # Étape 3: Scanner et facturer
        print("  📸 Scanner et facturation...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_SCANNER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_SCANNER)
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_FACTURE)
        browser.click_element(OpenBravoSelectors.BUTTON_FACTURE)
        time.sleep(0.5)
        just_fill(desktop, os.getenv('ob_phone'))
        time.sleep(0.5)
        pyautogui.press('enter')
        browser.wait_until_element_is_visible(OpenBravoSelectors.customer_by_name('Elouan'), timeout="15 s")
        browser.click_element(OpenBravoSelectors.customer_by_name('Elouan'))
        print("  ✓ Facturation effectuée")
        
        # Étape 4: Traiter multi-commande
        print("  📋 Multi-commande...")
        select_menu(browser, "menuMultiOrders_lbl")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MULTI_ORDER)
        browser.click_element(OpenBravoSelectors.BUTTON_MULTI_ORDER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        time.sleep(0.5)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_START_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_PRINTER)
        time.sleep(0.5)
        browser.click_element(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
        print("  ✓ Multi-commande traitée")
        
        # Étape 5: Vérifier l'enregistrement
        print("  ✓ Vérification enregistrement...")
        skip = False
        for _ in range(30):
            for el in browser.get_webelements(OpenBravoSelectors.ALERT_QUEUE):
                try:
                    txt = (el.text or "").strip()
                except StaleElementReferenceException:
                    continue
                if txt.startswith("Tous les tickets ont été correctement enregistrés"):
                    Assert.element_should_visible(browser, OpenBravoSelectors.ALERT_QUEUE, 'CCV 001', f)
                    skip = True
                    break
            if skip:
                break
        # # Nettoyage
        # wait(ob["save_print_output"])
        # pyautogui.press('esc')
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_DYNAMIC, timeout=30)
        pyautogui.press('esc')
        time.sleep(5)
        
        print("✅ Test CCV terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test CCV: {e}")
        raise