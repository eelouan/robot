"""
Tâche RFJ : Test de remplacement de facture avec immatriculation.
Vérifie le processus d'annulation/remplacement avec données véhicule.
"""
import time
import os
import logging
import inspect
import pyautogui


from utils.utils import just_fill
from core.openbravo import common, payment_ops, order_ops
from ob.function import ob_select, select_menu
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche RFJ.
    Teste le remplacement de facture avec immatriculation.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'rfj',
        'description': 'Test remplacement facture avec immatriculation'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: RFJ - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test RFJ
        rfj(browser, desktop)
        
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


def rfj(browser, desktop):
    """
    Teste le processus complet RFJ.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test RFJ - Remplacement facture avec immatriculation...")
    
    try:
        # Étape 1: Création commande avec immatriculation (RFJ-001/002)
        print("  🚗 Commande avec immatriculation...")
        ob_select(browser, desktop, '21861963', names=['MONTAGE'])
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
            case='RFJ 001 - RFJ 002'
        )
        
        # Récupérer le numéro de ticket
        original_ticket = ticket
        print(f"  ✓ Ticket initial créé: {original_ticket}")
        
        # Étape 2: Annulation et remplacement du ticket (RFJ-003)
        print(f"  🔄 Annulation/remplacement ticket {original_ticket}...")
        
        # Réouverture du ticket
        select_menu(browser, "menuReceiptSelector")
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_RECEIPT)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.press('delete')
        time.sleep(0.5)
        just_fill(desktop, original_ticket)
        time.sleep(0.5)
        pyautogui.press('enter')
        browser.wait_until_element_is_visible(OpenBravoSelectors.LINE_RECEIPT, timeout="15 s")
        browser.click_element(OpenBravoSelectors.LINE_RECEIPT)
        
        # Annulation et remplacement
        select_menu(browser, "menuScroller_menuCancelAndReplace_lbl")
        
        # Ajout du client
        browser.click_element(OpenBravoSelectors.BUTTON_CUSTOMER)
        browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_CUSTOMER, timeout="15 s")
        time.sleep(0.5)
        just_fill(desktop, os.getenv('ob_phone'))
        time.sleep(0.5)
        pyautogui.press('enter')
        browser.wait_until_element_is_visible(
            OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name')), 
            timeout="15 s"
        )
        browser.click_element(OpenBravoSelectors.customer_by_name(os.getenv('ob_first_name')))
        
        # Paiement du ticket de remplacement
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
        print("  ✓ Ticket de remplacement créé")
        
        # Étape 3: Récupération et vérification du numéro (RFJ-004)
        print("  🔍 Vérification du nouveau numéro de ticket...")
        new_ticket = order_ops.extract_new_ticket_number(browser)
        
        if not new_ticket:
            Assert.set_intercept("empty_supplier_number")
            raise Exception("Impossible de récupérer le numéro du ticket de remplacement")
        
        print(f"  ✓ Nouveau ticket: {new_ticket}")
        
        # Vérification du format (ancien-1)
        expected_ticket = f"{original_ticket}-1"
        str_value = "possède" if new_ticket == expected_ticket else "ne possède pas"
        Assert.assert_equals(
            new_ticket,
            expected_ticket,
            f"RFJ 004 - Le ticket {str_value} la valeur du ticket précédent suivit d'un -1",
            f
        )
        print(f"  ✓ Format vérifié: {new_ticket} == {expected_ticket}")
        
        print("✅ Test RFJ terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test RFJ: {e}")
        raise


