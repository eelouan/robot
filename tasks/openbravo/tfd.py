"""
Tâche TFD : Test de facturation et retours OpenBravo.
Vérifie le processus de facturation, réouverture de ticket et retours.
"""
import time
import os
import logging
import inspect
import pyautogui

from config.img import ob
from utils.utils import just_fill
from core.openbravo import common, payment_ops
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors
from core.openbravo import return_ops


def execute(context=None):
    """
    Point d'entrée de la tâche TFD.
    Teste la facturation et les retours.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'tfd',
        'description': 'Test facturation et retours'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: TFD - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test TFD
        tfd(browser, desktop)
        
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


def tfd(browser, desktop):
    """
    Teste le processus complet TFD.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test TFD - Facturation et retours...")
    
    try:
        # Étape 1: Facturation avec scanner (TFD-001)
        print("  📋 Facturation client...")
        ob_select(browser, desktop, '27425060')
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_SCANNER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_SCANNER)
        browser.wait_until_element_is_enabled(OpenBravoSelectors.BUTTON_FACTURE)
        browser.click_element(OpenBravoSelectors.BUTTON_FACTURE)
        time.sleep(0.5)
        just_fill(desktop, os.getenv('ob_phone'))
        time.sleep(0.5)
        pyautogui.press('enter')
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name')), 
            timeout="15 s"
        )
        browser.click_element(OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name')))
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='TFD 001')
        print("  ✓ Facturation effectuée")
        
        # Récupérer le numéro de ticket
        num = ticket
        print(f"  ✓ Ticket créé: {num}")
        
        # Étape 2: Réouverture et paiement supplémentaire (TFD-002)
        print(f"  🔓 Réouverture ticket {num}...")
        select_menu(browser, "menuReceiptSelector")
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_RECEIPT)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.press('delete')
        time.sleep(0.5)
        just_fill(desktop, num)
        time.sleep(0.5)
        pyautogui.press('enter')
        browser.wait_until_element_is_visible(OpenBravoSelectors.LINE_RECEIPT, timeout="15 s")
        browser.click_element(OpenBravoSelectors.LINE_RECEIPT)
        
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CASH, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY, timeout=5)
        browser.click_element(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
        time.sleep(1)
        print("  ✓ Paiement supplémentaire effectué")
        
        # Étape 3: Retour avec approbation (TFD-003)
        print(f"  ↩️  Retour ticket {num}...")
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, num)
        return_ops.select_return_items(browser)
        return_ops.select_return_reason(browser)
        return_ops.approve_return_with_admin(browser, desktop)
        print("  ✓ Retour approuvé")
        
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='TFD 003')
        time.sleep(3)
        print("  ✓ Paiement final effectué")

        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CANCEL_MODAL, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_CANCEL_MODAL)
        
        print("✅ Test TFD terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test TFD: {e}")
        raise