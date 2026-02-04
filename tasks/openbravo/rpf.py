"""
Tâche RPF : Test de retour avec paiement fractionné OpenBravo.
Vérifie qu'un retour d'achat fractionné doit être remboursé de façon fractionnée.
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
    Point d'entrée de la tâche RPF.
    Teste les retours avec paiement fractionné.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'rpf',
        'description': 'Test retour paiement fractionné'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: RPF - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test RPF
        rpf(browser, desktop)
        
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


def rpf(browser, desktop):
    """
    Teste le processus complet RPF.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test RPF - Retour paiement fractionné...")
    
    try:
        # Étape 1: Création commande avec paiement fractionné (RPF-001)
        print("  💳💰 Commande avec paiement fractionné...")
        ob_select(browser, desktop, '28557203')
        ob_select(browser, desktop, '21691294')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="fractionne", case="RPF 001", name=f)
        
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
        
        # Étape 2: Tentative de retour en espèces (RPF-001 suite)
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
            f"RPF 001 - Un retour en Espèce n'est pas possible", 
            f, 
            visible=True
        )
        browser.click_element(OpenBravoSelectors.BUTTON_MODAL_OK)
        print("  ✓ Retour espèces refusé (attendu)")
        
        # Étape 3: Tentative de retour en CB (RPF-002)
        print(f"  ❌ Test retour en CB (doit échouer)...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CB)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CB)
        time.sleep(1)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        
        # Vérifier que la popup d'erreur apparaît
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MODAL_OK)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_DYNAMIC, 
            f"RPF 002 - Un retour en CB n'est pas possible", 
            f, 
            visible=True
        )
        browser.click_element(OpenBravoSelectors.BUTTON_MODAL_OK)
        print("  ✓ Retour CB refusé (attendu)")
        
        # Étape 4: Retour avec paiement fractionné (RPF-003)
        print(f"  ✅ Test retour en paiement fractionné (doit réussir)...")
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="fractionne", case="RPF 003", name=f)
        print("  ✓ Retour fractionné accepté")
        
        print("✅ Test RPF terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test RPF: {e}")
        raise