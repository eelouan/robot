"""
Tâche seller_mode_exp : Mode vendeur avec paiement OpenBravo.
Crée des commandes en mode vendeur puis les paye dans OpenBravo.
"""

import time
import os
import logging
import pyautogui
from RPA.Desktop import Desktop

from web.connect import open_browser
from web.function import init
from ob.function import ob_connect
from core.openbravo.ui_ops import select_menu
from core.openbravo.payment_ops import ob_pay
from utils.utils import just_fill, json_order, wait
# from ob.payment import process_ob_payments
from core.cleanup import cleanup_resources, generate_final_report
from utils.Assert import Assert
from config.img import environement_web
from vtom.commerce_jour import controle_ticket, traitement_ticket_full, ath_recuptic
from config.img import ob
from config.timeouts import DEFAULT_TIMEOUTS
from config.ob_selectors import OpenBravoSelectors
from core.web import web_common, web_order, web_payment


def execute():
    """
    Point d'entrée de la tâche seller_mode_exp.
    Mode vendeur : création commandes web + paiement OpenBravo.
    """
    start_time = time.time()
    
    config = {
        'number': '001',
        'category': '5-TRANSVERSE',
        'name': 'seller_mode_exp',
        'description': 'Mode vendeur avec paiement OB'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🛒 DÉBUT TÂCHE: seller_mode_exp - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop = Desktop()
        
        # Étape 1 : Créer les commandes en mode vendeur
        orders, order_nums = _create_seller_orders(desktop, config)

        cleanup_resources(desktop, browser)
        
        # Étape 2 : Payer les commandes dans OpenBravo
        _pay_orders_in_ob(desktop, order_nums)
        
        # Étape 3 : Traitements VTOM
        _process_vtom_jobs()
        
        # Succès
        _finalize_success(order_nums)
        
    except Exception as e:
        _handle_error(e, config)
        raise
    
    finally:
        _cleanup(start_time, desktop, browser, config)


def _create_seller_orders(desktop, config):
    """
    Crée les commandes en mode vendeur.
    
    Args:
        desktop: Instance du desktop automation
        config: Configuration de la tâche
    
    Returns:
        tuple: (orders, order_nums) - Liste des commandes et numéros
    """
    print("\n📦 ÉTAPE 1 : Création commandes mode vendeur")
    print("="*80)
    
    # Chargement des commandes
    commandes = json_order(f"{config['category']}\\{config['number']}-creation_commande")
    
    # Connexion mode vendeur
    browser = open_browser(os.getenv('pp_seller_mode'))
    web_common.connect(desktop, seller_mode=True)
    init(browser, accept_c=True)
    
    # Création des commandes (réutilise la logique commune)
    orders = web_order.create_order(desktop, browser, commandes, seller_mode='ob')
    # Extraction des numéros de commande
    order_nums = [num for _, num in orders]
    
    print(f"\n✅ {len(order_nums)} commande(s) créée(s)")
    for num in order_nums:
        print(f"  • {num}")
    
    return orders, order_nums


def _pay_orders_in_ob(desktop, order_nums):
    """
    Paye les commandes dans OpenBravo.
    
    Args:
        desktop: Instance du desktop automation
        order_nums: Liste des numéros de commande
    """
    print("\n💳 ÉTAPE 2 : Paiement OpenBravo")
    print("="*80)
    
    # Ouverture OpenBravo
    browser = open_browser(os.getenv('ob_lad'), os.getenv('ob_profil_lad'))
    # browser.wait_until_element_is_visible(OpenBravoSelectors.FORM_LOGIN)
    time.sleep(3)
    
    # Connexion OB
    ob_connect(desktop, first=True, user='adm')
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT, timeout=60)
    
    # # Ouverture du POS
    # _open_pos(browser)
    
    # Paiement de chaque commande
    for i, num in enumerate(order_nums, 1):
        print(f"\n  [{i}/{len(order_nums)}] Paiement ticket {num}")
        _pay_single_order(browser, desktop, num)
        print(f"  ✓ Ticket {num} payé")
    
    print(f"\n✅ {len(order_nums)} ticket(s) payé(s)")
    
    # Fermeture
    browser.close_all_browsers()


def _open_pos(browser):
    """Ouvre le POS dans OpenBravo."""
    open_pos = "xpath=//*[contains(@id, 'btnNavigateToPOS')]"
    main = "xpath=//*[contains(@id, 'terminal_mainContainer')]"
    
    browser.wait_until_element_is_visible(open_pos, timeout="15 s")
    browser.click_element(open_pos)
    browser.wait_until_element_is_visible(main, timeout="15 s")
    browser.click_element(main)
    
    print("  ✓ POS ouvert")


def _pay_single_order(browser, desktop, order_num):
    """
    Paye une commande unique dans le POS.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        order_num: Numéro de commande à payer
    """
    
    # Ouvrir le sélecteur de tickets
    select_menu(browser, "menuReceiptSelector_lbl")
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_RECEIPT, timeout="15 s")
    
    # Rechercher le ticket
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.press('delete')
    just_fill(desktop, order_num)
    time.sleep(0.2)
    pyautogui.press('enter')
    
    # Sélectionner le ticket
    browser.wait_until_element_is_visible(OpenBravoSelectors.line_ticket(order_num), timeout="15 s")
    browser.click_element(OpenBravoSelectors.line_ticket(order_num))
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
    
    # Effectuer le paiement
    ob_pay(
        browser, 
        desktop, 
        payment_method="cash", 
        name='seller_mode_exp',
        case='',
        skip=True
    )
    
    # Fermer les popups
    wait(ob["save_print_output"])
    pyautogui.press('esc')
    
    browser.wait_until_element_is_visible(OpenBravoSelectors.MODAL_DYNAMIC)
    pyautogui.press('esc')
    time.sleep(5)


def _process_vtom_jobs():
    print("\n🔄 ÉTAPE 3 : Traitements VTOM")
    print("="*80)
    
    # Utilisation d'une variable d'environnement
    wait_page = os.getenv('WAIT_PAGE_PATH')
    
    # Si pas définie, chercher dans resources/
    if not wait_page:
        wait_page = os.path.join(os.getcwd(), 'resources', 'wait.html')
    
    # Si le fichier n'existe pas, utiliser about:blank
    if not os.path.exists(wait_page):
        print(f"⚠️  Fichier {wait_page} introuvable, utilisation de about:blank")
        wait_page = "about:blank"
    else:
        print(f"  ℹ️  Utilisation de: {wait_page}")
    
    browser = open_browser(wait_page)
    
    try:
        print("  - Flux vtom...")
        controle_ticket()
        traitement_ticket_full()
        ath_recuptic()
    except Exception as e:                          # ← NOUVEAU !
        print(f"  ❌ Erreur durant les traitements VTOM: {str(e)}")
        raise

def _finalize_success(order_nums):
    """Finalise en cas de succès."""
    print(f"\n{'='*100}")
    print("✅ TÂCHE SELLER_MODE_EXP RÉUSSIE")
    print(f"{'='*100}")
    print(f"\n📊 Résumé:")
    print(f"  • Commandes créées: {len(order_nums)}")
    print(f"  • Tickets payés: {len(order_nums)}")
    print(f"\n{'='*100}\n")


def _handle_error(error, config):
    """Gère les erreurs de la tâche."""
    if not Assert.get_intercept():
        Assert.set_intercept("generic")
    
    logging.error(
        f"\n{'='*100}\n"
        f"❌ ERREUR TÂCHE: {config['name']}\n"
        f"{'='*100}",
        exc_info=True
    )
    
    # Screenshot
    try:
        err_img = os.path.join(os.getcwd(), "logs", f"error_{config['name']}.png")
        os.makedirs(os.path.dirname(err_img), exist_ok=True)
        pyautogui.screenshot(err_img)
        print(f"📸 Screenshot: {err_img}")
    except Exception as e:
        print(f"⚠ Screenshot impossible: {e}")


def _cleanup(start_time, desktop, browser, config):
    """Nettoyage et rapport."""
    duration = time.time() - start_time
    print(f"\n⏱ Durée: {duration:.2f}s ({duration/60:.1f}min)")
    
    cleanup_resources(desktop, browser)
    
    report_path = f"{config['category']}\\{config['number']}-{config['name']}\\rapports"
    generate_final_report(report_path)