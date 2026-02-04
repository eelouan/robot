import pyautogui
import logging
import os
import time

from RPA.Desktop import Desktop

from utils.Assert import Assert
from core import cleanup
from utils import utils
from ob import function
from config.ob_selectors import OpenBravoSelectors

def handle_error(error, config):
    """Gère les erreurs de la tâche."""
    if not Assert.get_intercept():
        Assert.set_intercept("generic")
    
    logging.error(
        f"\n{'='*100}\n"
        f"❌ ERREUR TÂCHE: {config['name']}\n"
        f"{'='*100}",
        exc_info=True
    )
    
    try:
        err_img = os.path.join(os.getcwd(), "logs", f"error_{config['name']}.png")
        os.makedirs(os.path.dirname(err_img), exist_ok=True)
        pyautogui.screenshot(err_img)
        print(f"📸 Screenshot: {err_img}")
    except Exception as e:
        print(f"⚠ Screenshot impossible: {e}")


def clean(start_time, desktop, browser, config):
    """Nettoyage et rapport."""
    duration = time.time() - start_time
    print(f"\n⏱ Durée: {duration:.2f}s ({duration/60:.1f}min)")
    
    cleanup.cleanup_resources(desktop, browser)
    
    report_path = f"{config['category']}\\{config['number']}-{config['name']}\\rapports"
    cleanup.generate_final_report(report_path)

def initialize(context=None):
    ob_url = os.getenv('ob')
    ob_profil = os.getenv('ob_profil')

    if context and context.desktop and context.browser:
        return context.desktop, context.browser
    
    desktop = Desktop()
    browser = utils.open_browser(ob_url, ob_profil)
    function.ob_connect(desktop, True, 'sell')
    
    # 🔧 FIX : Stocke dans le contexte
    if context:
        context.desktop = desktop
        context.browser = browser
        context.initialized = True
    
    return desktop, browser

def finalize_success(task):
    """Finalise en cas de succès."""
    print(f"\n{'='*100}")
    print(f"✅ TÂCHE {task} RÉUSSIE")
    print(f"{'='*100}\n")