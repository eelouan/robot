"""
Tâche de création de commande.
Gère le cycle complet : création web -> intégration Athena -> préparation EGO -> expédition.
"""

import time
import os
import subprocess
import logging
import pyautogui
from robocorp.tasks import task
from RPA.Desktop import Desktop

from core.cleanup import cleanup_resources, kill_zombie_processes
from core.web import supplier_manager, web_order
from core.ego_processor import process_ego
from web.connect import open_browser
from web.create import *
from web.function import init
from utils.Assert import Assert
from utils.utils import json_order
from utils.connect_db import connect_athena_rec
from ego.connect import ego_init, ego_connect
from vtom.web import vtom_recup_ticket
from vtom.wms import vtom_envoi_commande
# from vtom.web import vtom_envoi_commande
# ... autres imports nécessaires


@task
def task_creation_commande():
    """
    Tâche principale de création de commande.
    Gère le cycle complet : création web -> intégration Athena -> préparation EGO -> expédition.
    """
    start_time = time.time()
    
    # Configuration
    config = {
        'test_number': '001',
        'test_category': '5-TRANSVERSE',
        'test_name': 'creation_commande'
    }
    
    desktop = None
    browser = None
    
    try:
        # Initialisation
        desktop, browser = _initialize_environment(config)
        
        # Création des commandes web
        orders = _create_web_orders(desktop, browser, config)
        
        # Traitement fournisseurs
        to_order = _process_suppliers(orders, desktop, browser)

        browser = open_browser(os.getenv('ego'))
        # desktop = Desktop()

        # orders = [([{'url': 'accessoires/p/desodorisant-aroma-car-skull-with-a-pipe-28160823', 'montage': False, 'dispo': 0, 'mode': {'livraison': 1, 'mode': 2}, 'consigne': False, 'type': 'pa', 'qty': 7, 'code8': '28160823', 'defaultQty': '1', 'transporteur': 'dpd'}, {'url': 'accessoires/p/couvre-siege-racing-panache-sodifac-28677796', 'montage': False, 'dispo': 0, 'mode': {'livraison': 1, 'mode': 2}, 'consigne': False, 'type': 'pa', 'qty': 5, 'code8': '28677796', 'defaultQty': '1', 'transporteur': 'dpd'}], '8019926000749'), ([{'url': 'accessoires/p/desodorisant-aroma-car-skull-with-a-pipe-28160823', 'montage': False, 'dispo': 0, 'mode': {'livraison': 1, 'mode': 2}, 'consigne': False, 'type': 'pa', 'qty': 7, 'code8': '28160823', 'defaultQty': '1', 'transporteur': 'dpd'}, {'url': 'accessoires/p/couvre-siege-racing-panache-sodifac-28677796', 'montage': False, 'dispo': 0, 'mode': {'livraison': 1, 'mode': 2}, 'consigne': False, 'type': 'pa', 'qty': 5, 'code8': '28677796', 'defaultQty': '1', 'transporteur': 'dpd'}], '8019926000750')]
        # to_order = {}
        
        # Préparation et expédition EGO
        _process_ego_workflow(desktop, browser, orders, to_order)
        
        # Succès
        _finalize_success(browser, orders)
        
    except Exception as e:
        _handle_error(e, config)
    
    finally:
        _cleanup_and_report(start_time, desktop, browser, config)


def _initialize_environment(config):
    """Initialise l'environnement de test."""
    from config.img import environement_web
    
    desktop = Desktop()
    browser = open_browser(os.getenv("pp_web_site"))
    init(browser, accept_c=True)
    
    return desktop, browser


def _create_web_orders(desktop, browser, config):
    """Crée les commandes sur le site web."""
    commandes = json_order(f"{config['test_category']}\\{config['test_number']}-{config['test_name']}")
    orders = web_order.create_order(desktop, browser, commandes)
    
    print('Orders créées:')
    print(orders)

    browser.go_to(r"C:\Users\adm-moreau\Documents\Robot\Robocorp\wait.html")
    
    vtom_recup_ticket()
    vtom_envoi_commande()
            
    return orders


def _process_suppliers(orders, desktop, browser):
    """Traite les commandes fournisseurs."""
    
    athena_conn = connect_athena_rec()
    
    while not bool(get_last_order_athena(athena_conn)):
        _try += 1
        time.sleep(5)
        if _try == 3:
            raise ValueError("Commande non intégrée")
        
    # Initialisation
    to_order = supplier_manager.init_supplier(orders, athena_conn)
    
    if to_order:
        supplier_manager.process_supplier_orders(desktop, to_order, athena_conn)
    
    return to_order


def _process_ego_workflow(desktop, browser, orders, to_order):
    """Traite le workflow EGO complet."""
    
    process_ego(desktop, browser, orders, to_order)

def _finalize_success(browser, orders):
    """Finalise en cas de succès."""
    from web.function import write_html
    
    browser.close_all_browsers()
    write_html(orders)
    print('\n' + '='*100)
    print('✅ TEST RÉUSSI')
    print('='*100 + '\n')


def _handle_error(error, config):
    """Gère les erreurs de la tâche."""
    if not Assert.get_intercept():
        Assert.set_intercept("generic")
    
    logging.error(
        f"\n{'='*100}\n"
        f"❌ ERREUR - {config['test_name']}\n"
        f"{'='*100}",
        exc_info=True
    )
    
    # Screenshot
    try:
        err_img = os.path.join(os.getcwd(), "logs", f"error_{config['test_name']}.png")
        os.makedirs(os.path.dirname(err_img), exist_ok=True)
        pyautogui.screenshot(err_img)
        print(f"📸 Screenshot: {err_img}")
    except Exception as e:
        print(f"⚠ Screenshot impossible: {e}")


def _cleanup_and_report(start_time, desktop, browser, config):
    """Nettoyage final et génération du rapport."""
    from core.cleanup import cleanup_resources, generate_final_report
    
    duration = time.time() - start_time
    print(f"\n⏱ Durée: {duration:.2f}s ({duration/60:.1f}min)\n")
    
    # Nettoyage
    cleanup_resources(desktop, browser)
    
    # Rapport
    report_path = f"{config['test_category']}\\{config['test_number']}-{config['test_name']}\\rapports"
    generate_final_report(report_path)