"""
Tâche RES : Test de retour avec approbation manager et espèces.
Vérifie le processus de retour avec approbation obligatoire.
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
    Point d'entrée de la tâche RES.
    Teste les retours avec approbation manager.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'res',
        'description': 'Test retour avec approbation'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: RES - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test RES
        res(browser, desktop)
        
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


def res(browser, desktop):
    """
    Teste le processus complet RES.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test RES - Retour avec approbation...")
    
    try:
        # Étape 1: Création commande avec paiement cash (RES-001)
        print("  💰 Commande avec paiement cash...")
        ob_select(browser, desktop, '28557203')
        ob_select(browser, desktop, '21691294')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", case="RES 001", name=f)
        
        # Récupérer le numéro de ticket
        original_ticket = ticket
        print(f"  ✓ Ticket créé: {original_ticket}")
        
        # Étape 2: Vérifier que l'approbation est demandée (RES-002)
        print(f"  🔐 Test demande d'approbation manager...")
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, original_ticket)
        return_ops.select_return_items(browser)
        return_ops.select_return_reason(browser)
        
        # Vérifier que la popup d'approbation APPARAÎT
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_RETURN_APPROVAL, timeout=30)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_RETURN_APPROVAL,
            f"RES 002 - L'approbation manager est demandée pour un retour", 
            f, 
            visible=True
        )
        print("  ✓ Approbation demandée (attendu)")
        
        # Étape 3: Saisir les identifiants admin et tenter paiement (RES-003)
        print(f"  ❌ Test paiement automatique après approbation (doit échouer)...")
        time.sleep(0.2)
        just_fill(desktop, os.getenv('user_ob_adm'))
        time.sleep(0.2)
        pyautogui.press("tab")
        just_fill(desktop, os.getenv('passwd_ob_adm'))
        time.sleep(0.4)
        pyautogui.press('enter')
        
        # Ouvrir le paiement et tenter de payer
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        
        # Vérifier que la popup d'erreur apparaît
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MODAL_OK)
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_DYNAMIC, 
            f"RES 003 - Un retour par CB n'est pas possible {original_ticket}", 
            f, 
            visible=True
        )
        browser.click_element(OpenBravoSelectors.BUTTON_MODAL_OK)
        print("  ✓ Paiement par cb refusé (attendu)")
        
        # Étape 4: Retour avec paiement "espèce" (RES-004)
        print(f"  ✅ Test retour avec méthode 'espèce' (doit réussir)...")
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='RES 004')
        print("  ✓ Retour avec méthode 'espèce' accepté")
        
        print("✅ Test RES terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test RES: {e}")
        raise