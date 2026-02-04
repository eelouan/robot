"""
Tâche BRB : Test de Bon de Retour Batterie OpenBravo.
Vérifie le système de vouchers pour la reprise de batteries usagées.
"""
import time
import os
import logging
import inspect
import pyautogui
from decimal import Decimal, ROUND_HALF_UP

from config.img import ob
from utils.utils import just_fill, elem_is_exist
from core.openbravo import common, payment_ops, return_ops
from ob.function import ob_select, select_menu, open_win, click_image, screenshot_and_decode, wait
from utils.Assert import Assert
from config.ob_selectors import OpenBravoSelectors


def execute(context=None):
    """
    Point d'entrée de la tâche BRB.
    Teste les bons de retour batterie.
    """
    start_time = time.time()
    
    config = {
        'number': 'XXX',  # À définir
        'category': '4-OB',
        'name': 'brb',
        'description': 'Test Bon de Retour Batterie'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"🔄 DÉBUT TÂCHE: BRB - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test BRB
        brb(browser, desktop)
        
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


def brb(browser, desktop):
    """
    Teste le processus complet BRB.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    f = inspect.currentframe().f_code.co_name
    print("\n🔄 Test BRB - Bon de Retour Batterie...")
    
    try:
        # Étape 1: Créer les vouchers (BRB-001)
        print("  🔋 Création des bons de retour batterie...")
        voucher1, voucher2 = _create_battery_vouchers(browser, desktop, f)
        print(f"  ✓ Voucher 1: {voucher1}")
        print(f"  ✓ Voucher 2: {voucher2}")
        
        # Étape 2: Test condition d'application du bon (BRB-005)
        print("  💰 Test montant minimum pour application bon...")
        win = open_win("Openbravo POS")
        _apply_voucher(browser, desktop, voucher1)
        
        # Ajouter produits (montant insuffisant)
        ob_select(browser, desktop, '28557203')
        for _ in range(4):
            time.sleep(1.5)
            pyautogui.typewrite('1')
            time.sleep(0.2)
            pyautogui.press('enter')
        time.sleep(1)
        
        # Vérifier que la réduction N'apparaît PAS
        _check_voucher_line_visibility(browser, visible=False, case="BRB 005", name=f)
        print("  ✓ Bon non appliqué - montant insuffisant (attendu)")
        
        # Étape 3: Supprimer ligne et ajouter produit (BRB-006)
        print("  🔄 Test après suppression ligne...")
        _delete_product_line(browser, "MONT. PNEU+VALVE+EQU")
        time.sleep(1)
        ob_select(browser, desktop, '28557203')
        time.sleep(1)
        _check_voucher_line_visibility(browser, visible=False, case="BRB 006", name=f)
        print("  ✓ Bon toujours non appliqué (attendu)")
        
        # Étape 4: Ajouter encore des produits (BRB-007)
        print("  ➕ Ajout produits supplémentaires...")
        for _ in range(2):
            time.sleep(1.5)
            pyautogui.typewrite('2')
            time.sleep(0.2)
            pyautogui.press('enter')
        time.sleep(1)
        _check_voucher_line_visibility(browser, visible=False, case="BRB 007", name=f)
        print("  ✓ Bon toujours non appliqué (attendu)")
        
        # Étape 5: Compléter commande (BRB-010, BRB-011)
        print("  📦 Complétion de la commande...")
        time.sleep(2)
        ob_select(browser, desktop, '21861963')
        time.sleep(2)
        ob_select(browser, desktop, '21861963')
        time.sleep(2)
        ob_select(browser, desktop, '21691294')
        print("  ✓ Commande complétée")
        
        # Étape 6: Test réutilisation voucher sur nouveau ticket (BRB-015)
        print("  ❌ Test réutilisation voucher (doit échouer)...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_NEW, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_NEW)
        _apply_voucher(browser, desktop, voucher1)
        
        # Vérifier message d'erreur
        is_existe = elem_is_exist(browser, OpenBravoSelectors.MODAL_DYNAMIC_BODY)
        str_value = "est affiché" if is_existe else "n'est pas affiché"
        Assert.assert_equals(
            is_existe, 
            True, 
            f"BRB 015 - Le message indiquant que le bon de retour est utilisé {str_value}", 
            f
        )
        pyautogui.press('esc')
        print("  ✓ Réutilisation bloquée (attendu)")
        
        # Étape 7: Test voucher2 après suppression ticket (BRB-020)
        print("  🗑️ Test voucher2 après suppression ticket...")
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_DELETE_TICKET, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_DELETE_TICKET)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MODAL_DELETE, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_MODAL_DELETE)
        
        _apply_voucher(browser, desktop, voucher2)
        is_existe = elem_is_exist(browser, OpenBravoSelectors.MODAL_DYNAMIC_BODY)
        str_value = "est affiché" if is_existe else "n'est pas affiché"
        Assert.assert_equals(
            is_existe, 
            True, 
            f"BRB 020 - Le message indiquant que le bon de retour est utilisé {str_value}", 
            f
        )
        pyautogui.press('esc')
        print("  ✓ Voucher2 également bloqué (attendu)")
        
        # Étape 8: Payer avec apport pneu (BRB-025)
        print("  🚗 Paiement avec apport pneu...")
        ticket = ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, bring_tire=True, case='BRB 025')
        print("  ✓ Paiement avec apport pneu effectué")
        
        # Étape 9: Test voucher1 à nouveau (BRB-030)
        print("  ❌ Re-test voucher1 (doit échouer)...")
        ob_select(browser, desktop, '21861963')
        time.sleep(1)
        ob_select(browser, desktop, '21861963')
        time.sleep(1)
        _apply_voucher(browser, desktop, voucher1)
        
        is_existe = elem_is_exist(browser, OpenBravoSelectors.MODAL_DYNAMIC_BODY)
        str_value = "est affiché" if is_existe else "n'est pas affiché"
        Assert.assert_equals(
            is_existe, 
            True, 
            f"BRB 030 - Le message indiquant que le bon de retour est utilisé {str_value}", 
            f
        )
        pyautogui.press('esc')
        print("  ✓ Voucher1 toujours bloqué (attendu)")
        
        # Étape 10: Retour avec calcul remise (BRB-035)
        print("  ↩️  Retour et calcul avec remise bon...")
        _test_return_with_voucher_discount(browser, desktop, ticket, f)
        print("  ✓ Calcul remise vérifié")
        
        # Étape 11: Paiement final (BRB-036)
        print("  💰 Paiement final...")
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="cash", name=f, case='BRB 036')
        print("  ✓ Paiement final effectué")
        
        print("✅ Test BRB terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur test BRB: {e}")
        raise


def _create_battery_vouchers(browser, desktop, name):
    """
    Crée 2 vouchers de retour batterie.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        name: Nom du test
        
    Returns:
        tuple: (voucher1, voucher2)
    """
    vouchers = []
    
    for i in range(2):
        # Acheter vieille batterie à 0€
        ob_select(browser, desktop, os.getenv('ob_old_battery'))
        ticket = payment_ops.ob_pay(browser, desktop, payment_method="zero", name=name, case='BRB 001', print_ticket=True)
        
        # Scanner le QR code du voucher
        win = open_win("POS Hardware Manager")
        wait(ob["hardware_manager"])
        click_image(ob["printer"])
        wait(ob["print_page"])
        win.maximize()
        voucher = screenshot_and_decode()
        print(f"    Voucher {i+1}: {voucher}")
        vouchers.append(voucher)
        
        if i == 0:
            win = open_win("Openbravo POS")
    
    return vouchers[0], vouchers[1]


def _apply_voucher(browser, desktop, voucher_code):
    """
    Applique un voucher sur le ticket courant.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        voucher_code: Code du voucher à appliquer
    """
    select_menu(browser, "_menuCoupons")
    time.sleep(1)
    just_fill(desktop, voucher_code)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(5)


def _check_voucher_line_visibility(browser, visible, case, name):
    """
    Vérifie si la ligne de réduction du voucher est visible.
    
    Args:
        browser: Instance du navigateur
        visible: True si doit être visible, False sinon
        case: Nom du cas de test
        name: Nom du test
    """
    xpath_voucher = (
        "xpath://div[contains(@id, 'listOrderLines_tbody_control')"
        "and contains(., '-- Bon 10€ pour reprise batterie')]"
    )
    
    try:
        browser.is_element_visible(xpath_voucher)
        is_visible = True
    except:
        is_visible = False
    
    str_value = "est visible" if is_visible else "n'est pas visible"
    Assert.element_should_visible(
        browser, 
        xpath_voucher, 
        f"{case} - La réduction du bon de retour {str_value}", 
        name, 
        visible=visible
    )


def _delete_product_line(browser, product_name):
    """
    Supprime une ligne de produit du ticket.
    
    Args:
        browser: Instance du navigateur
        product_name: Nom du produit à supprimer
    """
    product_line = (
        "xpath=(//*[contains(@id,'listOrderLines_tbody_control')]"
        f"[.//*[contains(@id,'_product') and contains(normalize-space(.), '{product_name}')]])"
    )
    button_delete_line = (
        "xpath=//button[contains(@id,'actionButtonsContainer') "
        "and contains(., 'Supprimer la ligne')]"
    )
    
    browser.wait_until_element_is_enabled(product_line)
    browser.click_element(product_line)
    browser.wait_until_element_is_enabled(button_delete_line)
    browser.click_element(button_delete_line)


def _test_return_with_voucher_discount(browser, desktop, ticket, name):
    """
    Teste le retour avec calcul de la remise du bon.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
        ticket: Dict contenant le ticket avec total
        name: Nom du test
    """
    # Supprimer ticket courant
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_DELETE_TICKET, timeout=30)
    browser.click_element(OpenBravoSelectors.BUTTON_DELETE_TICKET)
    time.sleep(0.5)
    pyautogui.press("enter")
    
    # Processus de retour
    return_ops.open_return_modal(browser)
    return_ops.search_ticket(browser, desktop, ticket)
    return_ops.select_return_items(browser)
    return_ops.select_return_reason(browser)
    return_ops.approve_return_with_admin(browser, desktop)
    
    # Ajouter produit et vérifier calcul
    time.sleep(2)
    ob_select(browser, desktop, '21691294')
    
    price_product = (
        "xpath=//*[contains(@id,'renderProduct')]"
        "[.//*[contains(@id,'renderProduct_identifier') and contains(normalize-space(.), 'CHAUFFAGE CERAMIQUE')]]"
        "//*[contains(@id,'_price')]"
    )
    
    browser.wait_until_page_contains_element(price_product, timeout="15 s")
    time.sleep(1)
    
    # Récupérer les montants
    line_text = browser.get_text(price_product).strip()
    total_line = Decimal(line_text).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
    
    total_ticket = -abs(Decimal(str(ticket["total"]))).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
    
    number = browser.get_text(
        browser.find_elements('css:#terminal_containerWindow_pointOfSale_multiColumn_leftPanel_receiptview_orderview_totalReceiptLine_totalgross')
    ).splitlines()[0]
    total = Decimal(number)
    
    print(f"    Total attendu: {total_ticket + total_line}")
    print(f"    Total réel: {total}")
    
    # Vérification
    is_true = (total == total_ticket + total_line)
    str_value = "est" if is_true else "n'est pas"
    price = f"- Le prix devrait être {total_ticket + total_line}, il est à {total}" if not is_true else ""
    Assert.assert_equals(
        total, 
        total_ticket + total_line, 
        f"BRB 035 - Le montant de l'article {str_value} celui de l'article moins la remise du bon {price}", 
        name
    )