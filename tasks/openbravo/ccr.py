"""
Tâche CCR : Test de retour et multi-commandes OpenBravo.
Vérifie le processus complet de retour avec approbation et multi-commande.
"""
import time
import os
import logging
import inspect
import pyautogui

from config.img import ob
from utils.utils import wait, just_fill
from core.openbravo import common, payment_ops, customer_ops, return_ops
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche CCR.
    Teste le retour et multi-commandes.
    """
    start_time = time.time()
    
    config = {
        'number': '025',
        'category': '4-OB',
        'name': 'ccr',
        'description': 'Test retour et multi-commandes'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: CCR - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test CCR
        ccr(browser, desktop)
        
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



def ccr(browser, desktop):
    """
    Teste le processus complet CCR.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test CCR - Retour et multi-commandes...")
    
    try:
        # Étape 1: Créer et payer la commande initiale
        print("  📦 Création commande initiale...")
        ob_select(browser, desktop, '28557203')
        ob_select(browser, desktop, '21691294')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='CCR 001')
        
        # Récupérer le numéro de ticket
        num = ticket
        print(f"  ✓ Ticket créé: {num}")
        
        # Étape 2: Effectuer le retour
        print(f"  ↩️  Retour ticket {num}...")
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, num)
        return_ops.select_return_items(browser)
        return_ops.select_return_reason(browser)
        return_ops.approve_return_with_admin(browser, desktop)
        print("  ✓ Retour effectué")
        
        # Étape 3: Créer nouvelle commande client
        print("  🆕 Nouvelle commande client...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_NEW, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_NEW)
        customer_ops.modale_customer_order(browser, desktop)
        ob_select(browser, desktop, '21861963')
        ob_select(browser, desktop, '21861963')
        print("  ✓ Commande client créée")
        
        # Étape 4: Traiter multi-commande
        print("  📋 Multi-commande...")
        select_menu(browser, "menuMultiOrders_lbl")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MULTI_ORDER)
        browser.click_element(OpenBravoSelectors.BUTTON_MULTI_ORDER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        time.sleep(0.5)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
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
                except:
                    continue
                if txt.startswith("Tous les tickets ont été correctement enregistrés"):
                    Assert.element_should_visible(browser, OpenBravoSelectors.ALERT_QUEUE, 'CCR 001', f)
                    skip = True
                    break
            if skip:
                break
        
        # Nettoyage
        # wait(ob["save_print_output"])
        # pyautogui.press('esc')
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_DYNAMIC, timeout=30)
        pyautogui.press('esc')
        
        print("✅ Test CCR terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test CCR: {e}")
        raise
