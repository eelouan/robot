import logging
import time

from core.cleanup import cleanup_resources, generate_final_report
from tasks.ecommerce.seller_mode_exp import execute as execute_seller_mode
from tasks import openbravo

class TaskContext:
    """Contexte partagé entre toutes les tâches"""
    def __init__(self):
        self.desktop = None
        self.browser = None
        self.ob_processor = None
        self.session_data = {}
        self.initialized = False
        self.start_time = None
    
    def cleanup(self):
        """Nettoie les ressources + génère le rapport global"""
        
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"\n⏱ Durée totale: {duration:.2f}s ({duration/60:.1f}min)")
            # Génère un rapport global si besoin
            generate_final_report(r"C:\Users\Public\Documents\Tests\4-OB\027 - TNR\rapports")
        
        logging.info("🧹 Nettoyage des ressources partagées")
        
        if self.browser:
            try:
                logging.info("Fermeture du browser")
                self.browser.close_browser()
            except Exception as e:
                logging.warning(f"Erreur fermeture browser: {e}")
        
        if self.desktop:
            try:
                logging.info("Fermeture du desktop")
                cleanup_resources(self.desktop, None)
            except Exception as e:
                logging.warning(f"Erreur fermeture desktop: {e}")
        
        self.initialized = False
        logging.info("✅ Nettoyage terminé")

_shared_context = None

def get_context():
    """Retourne le contexte partagé (crée si nécessaire)"""
    global _shared_context
    if _shared_context is None:
        logging.info("🎬 Création du contexte partagé")
        _shared_context = TaskContext()
        _shared_context.start_time = time.time()
    return _shared_context

def get_task_function(task_name: str):
    """Retourne la fonction correspondant au nom de tâche"""
    context = get_context()

    task_map = {
        'seller_mode': lambda: execute_seller_mode(context),
        'cap': lambda: openbravo.cap.execute(context),
        'cvr': lambda: openbravo.cvr.execute(context),
        'ccv': lambda: openbravo.ccv.execute(context),
        'ccr': lambda: openbravo.ccr.execute(context),
        'tfd': lambda: openbravo.tfd.execute(context),
        'rfj': lambda: openbravo.rfj.execute(context),
        'cce': lambda: openbravo.cce.execute(context),
        'rst': lambda: openbravo.rst.execute(context),
        'rpf': lambda: openbravo.rpf.execute(context),
        'rcb': lambda: openbravo.rcb.execute(context),
        'res': lambda: openbravo.res.execute(context),
        'mfc': lambda: openbravo.mfc.execute(context),
        'ccw': lambda: openbravo.ccw.execute(context),
        'ccm': lambda: openbravo.ccm.execute(context),
        'brb': lambda: openbravo.brb.execute(context)
    }
    return task_map.get(task_name)

def cleanup_context():
    """Nettoie le contexte à la fin"""
    global _shared_context
    if _shared_context:
        _shared_context.cleanup()
        _shared_context = None

