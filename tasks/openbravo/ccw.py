"""
Tâche CCW : Test de Commande Client Web OpenBravo.
Vérifie le processus de livraison et retour de commandes web.
"""
import time
import os
import logging
import inspect
import pyautogui
from RPA.Desktop import Desktop

from config.img import ob
from utils.utils import wait, just_fill
from core.openbravo import common, payment_ops, return_ops
from ob.function import ob_select, select_menu, ob_connect, open_browser
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors
from vtom.web import vtom_recup_ticket
from vtom.web_jour import vtom_order_loader
from utils.utils import json_order
from web.function import init
from core.web import web_common, web_order
from core.cleanup import cleanup_resources

def execute(context=None):
    """
    Point d'entrée de la tâche CCW.
    Teste les commandes client web.
    
    Args:
        context: Contexte partagé entre tâches
        num: Numéro de commande web à traiter
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'ccw',
        'description': 'Test Commande Client Web'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: CCW - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation spéciale pour CCW
        desktop, browser = web_common.initialize(browser, True)
        
        # Test CCW
        ccw(browser, desktop, config, context)
        
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

def ccw(browser, desktop, config, context):
    """
    Teste le processus complet CCW.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        num: Numéro de commande web (si None, utilise num[0])
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test CCW - Commande Client Web...")
    
    try:
        # WEB
        # Étape 1: Création d'une commande web
        num = _create_web_orders(desktop, browser, config)

        cleanup_resources(desktop, browser)
        # num = '0039926000007'
        # OB
        desktop, browser = common.initialize(context)

        # Étape 1: Livraison de la commande client web (CCW-001 à 004)
        print(f"  📦 Livraison commande client web {num}...")
        _deliver_web_order(browser, desktop, num)
        print(f"  ✓ Commande client web {num} livrée")
        
        # Étape 2: Retour de la commande web (CCW-005)
        print(f"  ↩️  Retour commande web {num}...")
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, num)
        return_ops.select_return_items(browser)
        return_ops.select_return_reason(browser)
        return_ops.approve_return_with_admin(browser, desktop)
        
        # Étape 3: Tentative de retour en espèces (CCW-005 suite)
        print(f"  ❌ Test retour en espèces (doit échouer)...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT_CASH)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        time.sleep(0.5)
        
        # Vérifier que la popup d'erreur apparaît
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_DYNAMIC, 
            f"CCW 005 - Un retour par cash n'est pas possible pour commande web {num}", 
            f, 
            visible=True
        )
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MODAL_OK)
        browser.click_element(OpenBravoSelectors.BUTTON_MODAL_OK)
        print("  ✓ Retour espèces refusé pour commande web (attendu)")
        
        # Étape 4: Retour avec CB (CCW-006)
        print(f"  ✅ Test retour en CB (doit réussir)...")
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", name=f, case='CCW 006', order_return=True)
        print("  ✓ Retour CB accepté pour commande web")
        
        print("✅ Test CCW terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test CCW: {e}")
        raise


def _deliver_web_order(browser, desktop, order_number):
    """
    Livre une commande client web.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        order_number: Numéro de la commande web
    """
    # Ouvrir le menu de livraison des commandes web
    select_menu(browser, "menuIssueSO")
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_ORDER_SELECTOR)
    time.sleep(0.5)
    
    # Rechercher la commande web
    just_fill(desktop, order_number)
    print(f"  🔍 Recherche commande web {order_number}")
    time.sleep(0.2)
    
    # Sélectionner et valider la livraison
    browser.wait_until_element_is_visible(
        OpenBravoSelectors.order_checkbox(order_number), 
        timeout="15 s"
    )
    browser.click_element(OpenBravoSelectors.order_checkbox(order_number))
    time.sleep(3)
    browser.click_element(OpenBravoSelectors.BUTTON_PREPARE_SELECTED)
    
    # Attendre l'impression et fermer
    wait(ob["save_print_output"])
    pyautogui.press('esc')
    time.sleep(2)
    pyautogui.press('esc')

def _create_web_orders(desktop, browser, config):
    """Crée les commandes sur le site web."""
    nums = []
    commandes = json_order(f"{config['category']}\\{config['number']}-{config['name']}")
    orders = web_order.create_order(desktop, browser, commandes)

    print(orders)
    
    for _, num in orders:
        nums.append(num)
    print('Numéros de l\'orders créées:')
    print(nums[0])

    browser.go_to(r"C:\Users\adm-moreau\Documents\Robot\Robocorp\wait.html")
    
    vtom_recup_ticket()
    vtom_order_loader()
            
    return nums[0]