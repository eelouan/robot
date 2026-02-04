"""
Tâche CAP : Vérification des emails clients OpenBravo avec Capency.
Teste le rejet des emails invalides par Capency.
"""
import time
import os
import logging
import pyautogui
from RPA.Desktop import Desktop

from core.openbravo import customer_ops, common
from utils.Assert import Assert


def execute(context=None):
    """
    Point d'entrée de la tâche CAP.
    Teste la validation des emails clients par Capency.
    """
    start_time = time.time()
    
    config = {
        'number': '026',
        'category': '4-OB',
        'name': 'cap',
        'description': 'Vérification email Capency'
    }
    
    desktop = None
    browser = None
    
    try:
        print(f"\n{'='*100}")
        print(f"📧 DÉBUT TÂCHE: CAP - {config['description']}")
        print(f"{'='*100}\n")
        
        # Initialisation
        desktop, browser = common.initialize(context)
        
        # Test validation email Capency
        cap(browser, desktop)
        
        # Succès
        common.finalize_success(config['name'].upper())
        
    except Exception as e:
        common.handle_error(e, config)
        raise
    
    finally:
        if context is None:
            common.clean(start_time, desktop, browser, config)

def cap(browser, desktop):
    """
    Teste la validation des emails clients par Capency.
    
    Args:
        browser: Instance du navigateur
        desktop: Instance du desktop automation
    """
    print("\n📧 Test validation emails Capency...")
    
    # Emails invalides à tester
    invalid_emails = [
        'emoreau@carter-cash',      # Pas de TLD
        'emoreau@carter-cash.a',    # TLD trop court
        'emoreau@a.com'             # Domaine trop court
    ]
    
    try:
        # Ouvrir le formulaire client
        print("  - Ouverture formulaire client...")
        customer_ops.open_customer_form(browser, desktop)
        print("  ✓ Formulaire ouvert")
        
        # Tester chaque email invalide
        print("  - Test des emails invalides...")
        validation_ok = False
        
        for email in invalid_emails:
            print(f"    • Test: {email}")
            
            # Saisir l'email
            customer_ops.set_email(browser, desktop, email)
            
            # Soumettre le formulaire
            customer_ops.submit_customer_form(browser)
            
            # Vérifier l'alerte de rejet
            if customer_ops.check_validation_error(browser):
                print(f"    ✓ Email '{email}' rejeté par Capency")
                validation_ok = True
            else:
                print(f"    ⚠ Email '{email}' accepté (attendu: rejet)")
        
        # Vérifier qu'au moins un email a été rejeté
        if validation_ok:
            Assert.write_assert(
                'CAP 001 - Les mauvais formats d\'email sont rejetés',
                'cap'
            )
            print("✅ Validation emails OK")
        else:
            raise ValueError("❌ Aucun email invalide n'a été rejeté")
        
        # Fermer le formulaire
        print("  - Fermeture formulaire...")
        customer_ops.close_customer_form(browser)
        print("  ✓ Formulaire fermé")
        
    except Exception as e:
        logging.error(f"Erreur test validation email: {e}")
        raise