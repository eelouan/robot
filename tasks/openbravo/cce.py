"""
Tâche CCE : Test de contrôle des moyens de paiement lors des retours.
Vérifie qu'un retour doit utiliser le même moyen de paiement que l'achat initial.
"""
import time
import os
import logging
import inspect
import pyautogui

from utils.utils import just_fill
from core.openbravo import common, payment_ops, return_ops, order_ops
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche CCE.
    Teste le contrôle des moyens de paiement lors des retours.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'cce',
        'description': 'Test contrôle paiement retours'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: CCE - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test CCE
        cce(browser, desktop)
        
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


def cce(browser, desktop):
    """
    Teste le processus complet CCE.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test CCE - Contrôle moyens de paiement retours...")
    
    try:
        # Étape 1: Création commande avec paiement cash (CCE-001)
        print("  💰 Commande avec paiement cash...")
        ob_select(browser, desktop, '28557203')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method_remaining="cash", case="CCE 001", name=f)
        
        # Récupérer le numéro de ticket
        original_ticket = ticket
        print(f"  ✓ Ticket créé: {original_ticket}")
        
        # Étape 2: Tentative de retour en espèces (CCE-002)
        print(f"  ✅ Test retour en espèces (doit réussir)...")
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, original_ticket)
        return_ops.select_return_items(browser, True)
        return_ops.select_return_reason(browser)
        return_ops.approve_return_with_admin(browser, desktop)
        
        # Tentative de paiement en espèces
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        time.sleep(1)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        
        # Vérifier que la popup d'erreur N'apparaît PAS (le retour espèces est refusé)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_DYNAMIC, 
            f"CCE 002 - Un retour en Espèce est possible", 
            f, 
            visible=False
        )
        
        # Supprimer le paiement espèces
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_DELETE_PAYMENT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_DELETE_PAYMENT)
        print("  ✓ Retour espèces accepté (attendu)")
        
        # Étape 3: Retour en CB (CCE-003)
        print(f"  ✅ Test retour en CB (doit réussir)...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CB)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CB)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        
        # Vérifier que la popup d'erreur N'apparaît PAS (le retour CB est accepté)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_DYNAMIC, 
            f"CCE 003 - Un retour en CB est possible", 
            f, 
            visible=False
        )
        
        # Finaliser le paiement
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
        print("  ✓ Retour CB accepté")
        
        # Récupération du numéro de ticket de retour
        new_ticket = order_ops.extract_new_ticket_number(browser)
        
        if not new_ticket:
            Assert.set_intercept("empty_supplier_number")
            raise Exception("Impossible de récupérer le numéro du ticket de retour")
        
        print(f"  ✓ Ticket de retour: {new_ticket}")
        print("✅ Test CCE terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test CCE: {e}")
        raise