"""
Tâche de vérification des labels.
"""

import time
import os
import logging
import pyautogui
from RPA.Desktop import Desktop

from web.connect import open_browser
from web.function import change_mag, pay_faster, web_check_label
from utils.Assert import Assert
from utils.utils import json_order
from config.img import environement_web

def task_check_label():
    """Vérifie les labels des produits."""
    start_time = time.time()
    
    browser = None
    desktop = None
    
    try:
        # Initialisation
        browser = open_browser(os.getenv("pp_web_site"))
        desktop = Desktop()
        init(browser, accept_c=True)
        
        # Chargement des commandes
        commandes = json_order(r"2-WEB\001-verification_labels")
        
        # Traitement
        _process_label_checks(browser, desktop, commandes)
        
        print('\n' + '='*100)
        print('✅ TEST RÉUSSI')
        print('='*100 + '\n')
        
    except Exception as e:
        _handle_label_error(e)
    
    finally:
        _cleanup_label_task(start_time, browser, desktop)


def _process_label_checks(browser, desktop, commandes):
    """Traite la vérification des labels pour toutes les commandes."""
    connect_before = False
    
    for commande in commandes:
        # Gestion connexion
        if connect_before and not commande['is_connect']:
            disconnect()
        connect_before = connect(desktop, commande['is_connect'], connect_before)
        
        # Changement magasin
        change_mag(browser, commande['mag'])
        
        # Vérification des labels pour chaque produit
        for produit in commande['produits']:
            _check_product_labels(browser, desktop, produit)
        
        # Paiement rapide
        pay_faster(desktop, browser, commande, commande['is_connect'], None)


def _check_product_labels(browser, desktop, produit):
    """Vérifie les labels d'un produit."""
    from web.function import get_web_code8, select_label
    
    # Récupération du code8
    produit['code8'] = get_web_code8(browser, produit)
    
    # Sélection des labels attendus
    expected_labels = select_label(desktop, produit, produit['code8'])
    
    # Retour accueil
    browser.go_to(os.getenv("pp_web_site"))
    
    # Vérification web
    web_check_label(browser, produit, expected_labels, os.getenv("pp_web_site"))


def _handle_label_error(error):
    """Gère les erreurs de vérification des labels."""
    logging.error("❌ Erreur vérification labels", exc_info=True)
    
    try:
        err_img = os.path.join(os.getcwd(), "logs", "error_label.png")
        os.makedirs(os.path.dirname(err_img), exist_ok=True)
        pyautogui.screenshot(err_img)
    except:
        pass


def _cleanup_label_task(start_time, browser, desktop):
    """Nettoyage de la tâche de vérification labels."""
    duration = time.time() - start_time
    print(f"\n⏱ Durée: {duration:.2f}s\n")
    
    if browser:
        try: browser.close_all_browsers()
        except: pass
    
    if desktop:
        try: desktop.close_all_applications()
        except: pass
    
    Assert.generate(r"2-WEB\001-verification_labels\rapports")