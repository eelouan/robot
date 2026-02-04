"""
Tâche RCB : Test de retour avec paiement carte bancaire.
Vérifie le trop-perçu CB et les contraintes de retour pour paiement CB.
"""
import time
import os
import logging
import inspect
import pyautogui

from utils.utils import just_fill
from core.openbravo import common, payment_ops, return_ops
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche RCB.
    Teste les retours avec paiement CB.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'rcb',
        'description': 'Test retour paiement CB'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: RCB - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test RCB
        rcb(browser, desktop)
        
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


def rcb(browser, desktop):
    """
    Teste le processus complet RCB.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test RCB - Retour paiement CB...")
    
    try:
        # Étape 1: Test trop-perçu CB (RCB-001)
        print("  💳 Test trop-perçu CB (doit être refusé)...")
        ob_select(browser, desktop, '28557203')
        ob_select(browser, desktop, '21691294')
        
        # Ouvrir le paiement et tenter de payer 100 (trop-perçu)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        time.sleep(0.5)
        pyautogui.typewrite("1")
        time.sleep(0.2)
        pyautogui.typewrite("0")
        time.sleep(0.2)
        pyautogui.typewrite("0")
        time.sleep(0.2)
        pyautogui.press('enter')
        
        # Vérifier que la popup de trop-perçu apparaît
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_OVERPAYMENT_OK)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.BUTTON_OVERPAYMENT_OK,
            f"RCB 001 - Le trop perçu par CB n'est pas possible", 
            f, 
            visible=True
        )
        browser.click_element(OpenBravoSelectors.BUTTON_OVERPAYMENT_OK)
        print("  ✓ Trop-perçu CB refusé (attendu)")
        
        # Étape 2: Paiement CB normal (RCB-002)
        print("  💳 Paiement CB normal...")
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", case="RCB 002", name=f)
        time.sleep(1)
        
        # Récupérer le numéro de ticket
        original_ticket = ticket
        print(f"  ✓ Ticket créé: {original_ticket}")
        
        # Processus de retour commun
        print(f"  ↩️  Retour ticket {original_ticket}...")
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, original_ticket)
        return_ops.select_return_items(browser)
        return_ops.select_return_reason(browser)
        return_ops.approve_return_with_admin(browser, desktop)
        
        # Étape 3: Tentative de retour en espèces (RCB-003)
        print(f"  ❌ Test retour en espèces (doit échouer)...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        time.sleep(1)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        
        # Vérifier que la popup d'erreur apparaît
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MODAL_OK)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_DYNAMIC, 
            f"RCB 003 - Un retour en Espèce n'est pas possible", 
            f, 
            visible=True
        )
        browser.click_element(OpenBravoSelectors.BUTTON_MODAL_OK)
        print("  ✓ Retour espèces refusé (attendu)")
        
        # Étape 4: Retour avec CB (RCB-004)
        print(f"  ✅ Test retour en CB (doit réussir)...")
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", case="RCB 004", name=f)
        print("  ✓ Retour CB accepté")
        
        print("✅ Test RCB terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test RCB: {e}")
        raise