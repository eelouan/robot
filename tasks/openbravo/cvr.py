"""
Tâche CVR : Test de retour et multi-commandes OpenBravo.
Vérifie le processus complet de retour avec approbation et multi-commande.
"""
import time
import os
import logging
import inspect
import pyautogui
from RPA.Desktop import Desktop

from config.img import ob
from utils.utils import open_browser, wait
from core.openbravo import order_ops, payment_ops, return_ops, ui_ops, common
from core.openbravo.payment_ops import ob_pay
from core.cleanup import cleanup_resources, generate_final_report
from ob.function import ob_connect, ob_select
from utils.Assert import Assert


def execute(context=None):
    """
    Point d'entrée de la tâche CVR.
    Teste le retour et multi-commandes.
    """
    start_time = time.time()
    
    config = {
        'number': '025',
        'category': '4-OB',
        'name': 'cvr',
        'description': 'Test retour et multi-commandes'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: CVR - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test CVR
        cvr(browser, desktop)
        
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

def cvr(browser, desktop):
    """
    Teste le processus complet CVR.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test CVR - Retour et multi-commandes...")
    
    try:
        # Étape 1: Créer et payer la commande initiale
        print("  📦 Création commande initiale...")
        ob_select(browser, desktop, '28557203')
        ob_select(browser, desktop, '21691294')
        ob_pay(browser, desktop, payment_method="cash", name=f, case='CVR 001')
        
        # Récupérer le numéro de ticket
        ticket_num = ticket
        print(f"  ✓ Ticket créé: {ticket_num}")
        
        # Étape 2: Effectuer le retour
        print(f"  ↩️  Retour ticket {ticket_num}...")
        return_ops.process_return(browser, desktop, ticket_num)
        print("  ✓ Retour effectué")
        
        # Étape 3: Créer nouvelle commande client
        print("  🆕 Nouvelle commande client...")
        order_ops.create_new_order(browser)
        order_ops.select_customer_by_phone(browser, desktop, "0611221122")
        ob_select(browser, desktop, '21861963')
        ob_select(browser, desktop, '21861963')
        print("  ✓ Commande client créée")
        
        # Étape 4: Traiter multi-commande
        print("  📋 Multi-commande...")
        payment_ops.process_multi_order_payment(browser, use_printer=False)
        print("  ✓ Multi-commande traitée")
        
        # Étape 5: Vérifier l'enregistrement
        print("  ✓ Vérification enregistrement...")
        return_ops.verify_tickets_saved(browser, 'CVR 001', f)
        
        # Nettoyage
        wait(ob["save_print_output"])
        pyautogui.press('esc')
        ui_ops.close_dynamic_popup(browser)
        
        print("✅ Test CVR terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test CVR: {e}")
        raise