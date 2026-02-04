"""
Point d'entrée Robocorp.
"""
import warnings

warnings.filterwarnings(
    "ignore",
    category=SyntaxWarning,
    message=r"invalid escape sequence.*"
)

import sys, io
import os
import logging
from dotenv import load_dotenv
from PIL import Image

from robocorp.tasks import task

# Import des implémentations

load_dotenv()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
Image.MAX_IMAGE_PIXELS = None

logging.getLogger().setLevel(logging.WARNING)
log_path = os.path.join(os.getcwd(), "logs")
os.makedirs(log_path, exist_ok=True)

debug_file_path = os.path.join("logs", "debug.log")
sys.stdout = open(debug_file_path, "w", encoding="utf-8")

log_file = os.path.join(log_path, "error_log.txt")
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@task
def create_order():
    """Création de commande complète."""
    from tasks.ecommerce.creation_commande import task_creation_commande as _task_creation_commande
    
    _task_creation_commande()


# @task
# def check_label():
#     """Vérification des labels."""
#     from tasks.check_label import task_check_label as _task_check_label

#     _task_check_label()

@task
def cap():
    """Vérification email client OpenBravo - Capency."""
    from tasks.ob_cap import execute
    
    execute()

@task
def seller_mode():
    """Mode vendeur : Création commande + Paiement OpenBravo."""
    from tasks.ecommerce.seller_mode_exp import execute

    execute()


@task
def cvr():
    """Vérification des cumuls OpenBravo - Cumul vente et retour."""
    from tasks.openbravo.cvr import execute
    
    execute()

@task
def ccr():
    """Vérification des cumuls OpenBravo - Cumul commande et retour."""
    from tasks.openbravo.ccr import execute
    
    execute()

@task
def ccv():
    """Vérification des cumuls OpenBravo - Cumul commande et vente."""
    from tasks.openbravo.ccv import execute
    
    execute()

@task
def tfd():
    """Vérification des cumuls OpenBravo - Cumul commande et vente."""
    from tasks.openbravo.tfd import execute
    
    execute()

@task
def ccm():
    """Vérification des cumuls OpenBravo - Cumul commande et vente."""
    from tasks.openbravo.ccm import execute
    
    execute()

@task
def brb():
    """Vérification des cumuls OpenBravo - Cumul commande et vente."""
    from tasks.openbravo.brb import execute
    
    execute()

@task
def tnr():
    """Version simple de l'orchestrateur"""
    from tasks.tasks_orchestrator import get_task_function, cleanup_context

    tasks = [
            # 'cap', 
            # 'cvr',
            # 'ccv',
            # 'ccr',
            # 'tfd',
            # 'rfj',
            'cce',
            'rst',
            # 'rpf',
            # 'rcb',
            # 'res',
            # 'mfc',
            # 'ccw',
            # 'ccm',
            # 'brb'
        ]
        
    try:
        for task_name in tasks:
            logging.info(f"{'='*50}")
            logging.info(f"🚀 Exécution: {task_name}")
            logging.info(f"{'='*50}")
            
            task_func = get_task_function(task_name)
            if task_func:
                task_func()
                logging.info(f"✅ {task_name} terminée")
            else:
                logging.error(f"❌ Tâche inconnue: {task_name}")
    
    finally:
        # Rapport global + cleanup à la fin
        logging.info(f"{'='*50}")
        logging.info("🏁 Toutes les tâches terminées")
        logging.info(f"{'='*50}")
        cleanup_context()