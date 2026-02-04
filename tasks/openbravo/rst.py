"""
Tâche RST : Test de retour sans ticket OpenBravo.
Vérifie les différents scénarios de retour sans ticket selon les rôles utilisateur.
"""
import time
import logging
import inspect
import pyautogui

from utils.utils import just_fill
from core.openbravo import common, payment_ops, return_ops, ui_ops, order_ops
from ob.function import ob_select, select_menu, ob_connect
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche RST.
    Teste les retours sans ticket.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'rst',
        'description': 'Test retour sans ticket'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: RST - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test RST
        rst(browser, desktop)
        
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


def rst(browser, desktop):
    """
    Teste le processus complet RST.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test RST - Retour sans ticket...")
    
    try:
        # Étape 1: Vérifier que le menu n'est pas visible en mode normal (RST-001)
        print("  🔒 Vérification accès menu retour sans ticket (utilisateur normal)...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MENU)
        browser.click_element(OpenBravoSelectors.BUTTON_MENU)
        
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.NAV_MENU_RETURN_WITHOUT_TICKET,
            f"RST 001 - Le menu \"Retour sans ticket\" n'est pas présent", 
            f, 
            visible=False
        )
        print("  ✓ Menu retour sans ticket non visible (attendu)")
        
        # Fermer le menu (nettoyer les scrims)
        time.sleep(0.5)
        ui_ops.clear_scrims(browser)
        browser.wait_until_element_is_not_visible(OpenBravoSelectors.SCRIM, timeout="5 s")
        browser.click_element(OpenBravoSelectors.BUTTON_MENU)
        
        # Réinitialiser l'interface
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_SCAN_ZERO)
        browser.click_element(OpenBravoSelectors.BUTTON_SCAN_ZERO)
        time.sleep(0.5)
        pyautogui.press('enter')
        
        # Étape 2: Test retour sans ticket en mode admin (RST-005)
        print("  👤 Connexion administrateur...")
        ob_connect(desktop, first=False, user='adm')
        time.sleep(10)
        
        print("  📦 Retour sans ticket (mode admin)...")
        select_menu(browser, "menuReturn2")
        ob_select(browser, desktop, '21691294')
        
        # Sélectionner le produit et définir son état
        browser.wait_until_element_is_visible(OpenBravoSelectors.LINE1_PRODUCT)
        browser.click_element(OpenBravoSelectors.LINE1_PRODUCT)
        
        browser.wait_until_element_is_visible(OpenBravoSelectors.SELECT_PRODUCT_STATE)
        browser.click_element(OpenBravoSelectors.SELECT_PRODUCT_STATE)
        
        # Sélectionner l'état "1- Neuf"
        options = browser.get_list_items(OpenBravoSelectors.SELECT_PRODUCT_STATE)
        for opt in options:
            if "1- Neuf" in opt:
                browser.select_from_list_by_label(OpenBravoSelectors.SELECT_PRODUCT_STATE, opt)
                break
        
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", case="RST 005", name=f)
        print("  ✓ Retour sans ticket effectué")
        
        # Étape 3: Test retour avec utilisateur identifié (RST-010)
        print("  👥 Test retour utilisateur identifié (sans approbation)...")
        ob_select(browser, desktop, '28557203')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", case="", name=f, lui=True)
        
        num = ticket
        print(f"  ✓ Ticket créé: {num}")
        
        # Tenter le retour
        return_ops.open_return_modal(browser)
        return_ops.search_ticket(browser, desktop, num)
        return_ops.select_return_items(browser)
        return_ops.select_return_reason(browser)
        
        # Vérifier que l'approbation N'est PAS demandée
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.MODAL_RETURN_APPROVAL,
            f"RST 010 - L'approbation n'est pas demandé", 
            f, 
            visible=False
        )
        print("  ✓ Approbation non requise (attendu)")
        
        # Étape 4: Simple commande (RST-011)
        print("  💳 Commande simple...")
        ob_select(browser, desktop, '21861963')
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cb", case="RST 011", name=f)
        print("  ✓ Commande effectuée")
        
        # Étape 5: Test interdiction retour+vente sur même ticket (RST-015)
        print("  🚫 Test interdiction retour+vente même ticket...")
        
        # Réinitialiser
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_SCAN_ZERO)
        browser.click_element(OpenBravoSelectors.BUTTON_SCAN_ZERO)
        time.sleep(0.5)
        pyautogui.press('enter')
        
        # Connexion vendeur
        print("  👤 Connexion vendeur...")
        ob_connect(desktop, first=False, user='sell')
        time.sleep(5)
        
        # Ajouter un produit
        ob_select(browser, desktop, '21861963')
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_SCANNER, timeout="15 s")
        browser.click_element(OpenBravoSelectors.BUTTON_SCANNER)
        
        # Taper 11 (code pour retour)
        time.sleep(0.3)
        pyautogui.typewrite("1")
        time.sleep(0.3)
        pyautogui.typewrite("1")
        time.sleep(0.3)
        
        # Cliquer sur le bouton moins (retour)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MINUS)
        browser.click_element(OpenBravoSelectors.BUTTON_MINUS)
        
        # Vérifier que l'erreur s'affiche
        browser.wait_until_element_is_visible(OpenBravoSelectors.ALERT_NO_MIX_RETURN_SALE, timeout="5 s")
        Assert.element_should_visible(
            browser, 
            OpenBravoSelectors.ALERT_NO_MIX_RETURN_SALE,
            f"RST 015 - Il est impossible de combiner retour et vente sur le même ticket", 
            f, 
            visible=True
        )
        print("  ✓ Erreur de combinaison affichée (attendu)")

        # Suppression du ticket
        order_ops.delete_order(browser)
        
        print("✅ Test RST terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test RST: {e}")
        raise