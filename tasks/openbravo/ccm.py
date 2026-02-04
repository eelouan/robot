"""
Tâche CCM : Test de Commande Client Magasin OpenBravo.
Vérifie la création, livraison et annulation de commandes client.
"""
import time
import os
import logging
import inspect
import pyautogui

from config.img import ob
from utils.utils import wait, just_fill
from core.openbravo import common, payment_ops, ui_ops, customer_ops
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche CCM.
    Teste les commandes client magasin.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'ccm',
        'description': 'Test Commande Client Magasin'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: CCM - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test CCM
        ccm(browser, desktop)
        
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


def ccm(browser, desktop):
    """
    Teste le processus complet CCM.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test CCM - Commande Client Magasin...")
    
    try:
        # Étape 1: Créer commande client avec immatriculation (CCM-001/002)
        print("  🚗 Commande client avec immatriculation...")
        customer_ops.modale_customer_order(browser, desktop)
        ob_select(browser, desktop, '21861963', names=["MONTAGE", "EXPRESS PNEU M2S"])
        ob_select(browser, desktop, '21861963')
        ticket = payment_ops.ob_pay(
            browser, 
            desktop, 
            payment_method="cash", 
            name=f, 
            registration_number={
                "label_register": "AB-123-CD AV",
                "label_mileage": "120123"
            }, 
            case='CCM 002'
        )
        
        order_number = ticket
        print(f"  ✓ Commande créée: {order_number}")
        
        # Étape 2: Livrer la commande (CCM-005)
        print(f"  📦 Livraison commande {order_number}...")
        _deliver_customer_order(browser, desktop, order_number)
        print(f"  ✓ Commande {order_number} livrée")
        
        # Étape 3: Test annulation avec paiement différent - Cash → CB (CCM-010)
        print("  🔄 Test annulation: Commande cash → Annulation CB...")
        customer_ops.modale_customer_order(browser, desktop)
        ob_select(browser, desktop, '21861963')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='CCM 010')
        
        ticket = ticket
        _reopen_and_cancel_order(browser, desktop, ticket, click_line=True)
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", name=f, case='CCM 010', cancel=True)
        print("  ✓ Annulation cash → CB réussie")
        
        # Étape 4: Test annulation CB → CB (CCM-015)
        print("  🔄 Test annulation: Commande CB → Annulation CB...")
        customer_ops.modale_customer_order(browser, desktop)
        ob_select(browser, desktop, '21861963')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", name=f, case='CCM 015')
        
        ticket = ticket
        _reopen_and_cancel_order(browser, desktop, ticket, click_line=True)
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", name=f, case='CCM 015', cancel=True)
        print("  ✓ Annulation CB → CB réussie")
        
        # Étape 5: Test annulation Cash → Cash (CCM-020)
        print("  🔄 Test annulation: Commande cash → Annulation cash...")
        customer_ops.modale_customer_order(browser, desktop)
        ob_select(browser, desktop, '21861963')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='CCM 020')
        
        ticket = ticket
        _reopen_and_cancel_order(browser, desktop, ticket, click_line=False)  # Pas de clic sur la ligne
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='CCM 020', cancel=True)
        print("  ✓ Annulation cash → cash réussie")
        
        # Étape 6: Test annulation CB → CB (CCM-025)
        print("  🔄 Test annulation: Commande CB → Annulation CB...")
        customer_ops.modale_customer_order(browser, desktop)
        ob_select(browser, desktop, '21861963')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", name=f, case='CCM 025')
        
        ticket = ticket
        _reopen_and_cancel_order(browser, desktop, ticket, click_line=True)
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", name=f, case='CCM 025', cancel=True)
        print("  ✓ Annulation CB → CB réussie")
        
        print("✅ Test CCM terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test CCM: {e}")
        raise

def _deliver_customer_order(browser, desktop, order_number):
    """
    Livre une commande client.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        order_number: Numéro de la commande
    """
    select_menu(browser, "menuIssueSO")
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_ORDER_SELECTOR)
    time.sleep(0.5)
    just_fill(desktop, order_number)
    time.sleep(0.2)
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


def _reopen_and_cancel_order(browser, desktop, ticket_number, click_line=True):
    """
    Réouvre un ticket et lance l'annulation.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        ticket_number: Numéro du ticket
        click_line: Si True, clique sur la ligne du ticket après l'avoir trouvé
    """
    select_menu(browser, "menuReceiptSelector")
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_RECEIPT)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.press('delete')
    time.sleep(0.5)
    just_fill(desktop, ticket_number)
    time.sleep(0.5)
    pyautogui.press('enter')
    browser.wait_until_element_is_visible(OpenBravoSelectors.LINE_RECEIPT, timeout="15 s")
    browser.click_element(OpenBravoSelectors.LINE_RECEIPT)
    
    ui_ops.select_menu(browser, "menuCancelLayaway")