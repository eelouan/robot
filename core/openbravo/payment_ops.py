"""
Opérations atomiques liées aux paiements OpenBravo.
Gestion des paiements, multi-commandes, etc.
"""

import re
import time
import logging
import pyautogui
from decimal import Decimal,ROUND_HALF_UP
from selenium.common.exceptions import StaleElementReferenceException

from utils.Assert import *
from config.timeouts import DEFAULT_TIMEOUTS
from config.ob_selectors import OpenBravoSelectors
from utils.utils import just_fill


def select_payment_method(browser, method='cash'):
    """Sélectionne un moyen de paiement."""
    logging.info(f"Sélection du mode de paiement: {method}")
    
    method_map = {
        'cash': OpenBravoSelectors.BUTTON_PAYMENT_CASH,
        'cb': OpenBravoSelectors.BUTTON_PAYMENT_CB,
    }
    
    if method not in method_map:
        raise ValueError(f"Méthode de paiement non supportée: {method}")
    
    selector = method_map[method]
    browser.wait_until_element_is_visible(selector)
    browser.click_element(selector)
    time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)


def execute_payment_flow(browser, use_printer=False):
    """
    Exécute le flux complet de paiement.
    
    Args:
        browser: Instance du navigateur
        use_printer: Si True, active l'impression
    """
    logging.info("Exécution du flux de paiement...")
    
    # Démarrer le paiement
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_START_PAY)
    browser.click_element(OpenBravoSelectors.BUTTON_START_PAY)
    
    # Ouvrir
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_OPEN_PAY)
    browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    
    # Terminer
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY)
    browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
    
    # Configurer impression et valider
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
    
    if use_printer:
        browser.click_element(OpenBravoSelectors.BUTTON_PRINTER)
        time.sleep(DEFAULT_TIMEOUTS.SHORT_WAIT)
    
    time.sleep(DEFAULT_TIMEOUTS.LONG_WAIT)
    browser.click_element(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)


def open_multi_orders(browser):
    """
    Ouvre le menu multi-commandes et valide.
    
    Args:
        browser: Instance du navigateur
    """
    logging.info("Ouverture multi-commandes...")
    
    # Note: select_menu doit être importé depuis ob_processor ou migré
    from core.openbravo.ui_ops import select_menu
    
    select_menu(browser, "menuMultiOrders_lbl")
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_MULTI_ORDER)
    browser.click_element(OpenBravoSelectors.BUTTON_MULTI_ORDER)


def process_multi_order_payment(browser, use_printer=False):
    """
    Traite une multi-commande complète avec paiement.
    
    Args:
        browser: Instance du navigateur
        use_printer: Si True, active l'impression
    """
    logging.info("Traitement multi-commande...")
    
    # Ouvrir multi-commandes
    open_multi_orders(browser)
    
    # Sélectionner le moyen de paiement
    select_payment_method(browser, 'cash')
    
    # Exécuter le paiement
    execute_payment_flow(browser, use_printer)

def ob_pay(browser, desktop, payment_method_remaining=None, payment_method="cb", 
           registration_number=None, bring_tire=False, name='', case='', 
           cancel=False, order_return=False, skip=False, lui=False, print_ticket=False):
    """Effectue le paiement complet d'une commande."""
    
    mode = None

    print(payment_method)
    
    match payment_method:
        case 'cb':
            mode = 'CB'
        case 'cash':
            mode = 'Espèces'
        case 'fractionne':
            mode = 'Paiement Fractionne'

    # Récupérer le total
    number = browser.get_text(browser.find_elements(OpenBravoSelectors.TOTAL_RECEIPT)).splitlines()[0]
    total = Decimal(number)
    ticket = {"total": total}

    # Ouvrir menu paiement
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_PAYMENT)
    browser.click_element(OpenBravoSelectors.BUTTON_PAYMENT)

    # Sélectionner méthode
    if mode:
        elem = OpenBravoSelectors.payment_method_button(mode)
        browser.wait_until_element_is_visible(elem)
        browser.click_element(elem)
    
    # Exécuter paiement
    match payment_method:
        case 'cb':
            cb(browser, desktop, payment_method_remaining=payment_method_remaining, 
               bring_tire=bring_tire, registration_number=registration_number, cancel=cancel)
        case 'cash':
            cash(browser, desktop, payment_method_remaining=payment_method_remaining, 
                 bring_tire=bring_tire, registration_number=registration_number, cancel=cancel)
        case 'fractionne':
            fractionne(browser, desktop, bring_tire=bring_tire, 
                      registration_number=registration_number, cancel=cancel)
        case 'zero':
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
            browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)

    # Valider montant
    elements = browser.find_elements(OpenBravoSelectors.PAYMENT_LINE_AMOUNT)
    tot = Decimal("0.00")
    for el in elements:
        txt = browser.get_text(el).strip()
        clean = txt.replace("€", "").replace(",", ".").strip()
        tot += Decimal(clean)
    
    total = -abs(Decimal(str(tot))).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP) if ticket["total"] < 0 else tot
    nb_case = f"{case} - " if case else ''
    is_true = True if total == ticket["total"] else False
    str_value = "est" if is_true else "n'est pas"
    Assert.assert_equals(total, ticket["total"], 
                        f"{nb_case}Le prix payé {total} {str_value} égal au prix affiché de {ticket['total']}", 
                        name)
    
    # Finaliser
    if not skip:
        if order_return:
            if not print_ticket:
                browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CANCEL_PRINT, timeout=30)
                browser.click_element(OpenBravoSelectors.BUTTON_CANCEL_PRINT)
        else:
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY, timeout=5)
            if not print_ticket:
                browser.click_element(OpenBravoSelectors.BUTTON_PRINTER)
                time.sleep(0.5)
            browser.click_element(OpenBravoSelectors.BUTTON_CONTINUE_AFTER_PAY)
            
            # Extraire numéro ticket
            rx = re.compile(r"n[°º]\s*:\s*([A-Z0-9/]+)")
            ticket_number = None

            for _ in range(30):
                for el in browser.get_webelements(OpenBravoSelectors.ALERT_QUEUE):
                    try:
                        txt = (el.text or "").strip()
                    except StaleElementReferenceException:
                        continue
                    if txt.startswith("Le ticket n"):
                        m = rx.search(txt)
                        if m:
                            ticket_number = m.group(1)
                            if lui:
                                print(ticket_number)
                            Assert.set_ob_ticket_number(ticket_number)
                            break
                if ticket_number:
                    break
                time.sleep(0.2)

            if not ticket_number and not cancel:
                print("❌ Aucun message de ticket détecté.")
                Assert.set_intercept("empty_supplier_number")

    return ticket_number


def cb(browser, desktop, payment_method_remaining=None, bring_tire=False, 
       registration_number=None, cancel=False):
    """Paiement CB."""
    
    match payment_method_remaining:
        case 'cb':
            mode_remaining = 'CB'
        case 'cash':
            mode_remaining = 'Espèces'
        case _:
            mode_remaining = None

    if payment_method_remaining:
        browser.click_element(OpenBravoSelectors.KEYPAD_ZERO)
        time.sleep(0.5)
        pyautogui.typewrite(".")
        time.sleep(0.1)
        pyautogui.typewrite("1")
        pyautogui.press('enter')
        
        if cancel:
            err = os.path.join(os.getcwd(), "logs", "ob.png")
            pyautogui.screenshot(err)
        
        if not cancel:
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_REMAINING_PAY, timeout=30)
            elem = OpenBravoSelectors.payment_method_button(mode_remaining)
            browser.click_element(elem)
            time.sleep(1)
            browser.click_element(OpenBravoSelectors.BUTTON_REMAINING_PAY)
        
        match payment_method_remaining:
            case 'cb':
                if bring_tire:
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
                    browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
                    browser.click_element(OpenBravoSelectors.BUTTON_BRING_WHEEL)
                    time.sleep(1)
                    pyautogui.press('enter')
            case 'cash':
                browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                if bring_tire:
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
                    browser.click_element(OpenBravoSelectors.BUTTON_BRING_WHEEL)
                    time.sleep(1)
                    pyautogui.press('enter')
                    browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                    browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                if registration_number:
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
                    just_fill(desktop, registration_number["label_register"])
                    time.sleep(0.2)
                    just_fill(desktop, registration_number["label_register"])
                    time.sleep(0.2)
                    pyautogui.press('enter')
                    browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                    browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        print(f'num : {registration_number}')
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
    else:
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
        
        if bring_tire:
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
            browser.click_element(OpenBravoSelectors.BUTTON_BRING_WHEEL)
            time.sleep(1)
            pyautogui.press('enter')
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
            browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
        
        if registration_number:
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
            just_fill(desktop, registration_number["label_register"])
            time.sleep(0.2)
            just_fill(desktop, registration_number["label_register"])
            time.sleep(0.2)
            pyautogui.press('enter')
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
            browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)


def cash(browser, desktop, payment_method_remaining=None, bring_tire=False, 
         registration_number=None, cancel=False):
    """Paiement espèces."""
    
    match payment_method_remaining:
        case 'cb':
            mode_remaining = 'CB'
        case 'cash':
            mode_remaining = 'Espèces'
        case _:
            mode_remaining = None

    if payment_method_remaining:
        browser.click_element(OpenBravoSelectors.KEYPAD_ZERO)
        time.sleep(0.5)
        pyautogui.typewrite(".")
        time.sleep(0.1)
        pyautogui.typewrite("1")
        pyautogui.press('enter')
        
        if not cancel:
            browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_REMAINING_PAY, timeout=30)
            elem = OpenBravoSelectors.payment_method_button(mode_remaining)
            browser.click_element(elem)
            time.sleep(1)
            browser.click_element(OpenBravoSelectors.BUTTON_REMAINING_PAY)
        
        match payment_method_remaining:
            case 'cb':
                pass
            case 'cash':
                if bring_tire:
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
                    browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
                    browser.click_element(OpenBravoSelectors.BUTTON_BRING_WHEEL)
                    time.sleep(1)
                    pyautogui.press('enter')
                    browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                    browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                if registration_number:
                    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
                    just_fill(desktop, registration_number["label_register"])
                    time.sleep(0.2)
                    just_fill(desktop, registration_number["label_register"])
                    time.sleep(0.2)
                    pyautogui.press('enter')
                    browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
                    browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    else:
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
        browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
        time.sleep(0.5)
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    
    if bring_tire:
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_BRING_WHEEL)
        time.sleep(1)
        pyautogui.press('enter')
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    
    if registration_number:
        time.sleep(0.5)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
        just_fill(desktop, registration_number["label_register"])
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)
        just_fill(desktop, registration_number["label_mileage"])
        time.sleep(0.2)
        pyautogui.press('enter')
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
    browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)


def fractionne(browser, desktop, bring_tire=False, registration_number=None, cancel=False):
    """Paiement fractionné."""
    
    browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT, timeout=15)
    browser.click_element(OpenBravoSelectors.BUTTON_START_PAY_EXACT)
    
    if bring_tire:
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
        browser.click_element(OpenBravoSelectors.BUTTON_BRING_WHEEL)
        time.sleep(1)
        pyautogui.press('enter')
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    
    if registration_number:
        time.sleep(0.5)
        browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_BRING_WHEEL, timeout=30)
        just_fill(desktop, registration_number["label_register"])
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)
        just_fill(desktop, registration_number["label_mileage"])
        time.sleep(0.2)
        pyautogui.press('enter')
        browser.wait_until_page_contains_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
        browser.click_element(OpenBravoSelectors.BUTTON_OPEN_PAY)
    
    browser.wait_until_element_is_visible(OpenBravoSelectors.BUTTON_FINISH_PAY, timeout=30)
    browser.click_element(OpenBravoSelectors.BUTTON_FINISH_PAY)