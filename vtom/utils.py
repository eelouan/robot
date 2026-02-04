"""
Module de gestion VTOM et utilitaires.
Gère les interactions avec l'API VTOM pour l'exécution et le monitoring des jobs.
"""

# ============================================================================
# IMPORTS STANDARD LIBRARY
# ============================================================================
import os
import time

# ============================================================================
# IMPORTS THIRD PARTY
# ============================================================================
import cv2
import numpy as np
import pyautogui
import pytesseract
import requests
from dotenv import load_dotenv
from PIL import ImageGrab
from RPA.Desktop import Desktop
from RPA.Images import Images
from selenium.webdriver.common.action_chains import ActionChains

# ============================================================================
# IMPORTS LOCAL
# ============================================================================
from config.img import *
from utils.Assert import *
from utils.connect_db import *
from utils.request import *
from utils.utils import *

# ============================================================================
# CONFIGURATION
# ============================================================================
load_dotenv()

# Création du répertoire de logs
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)

# Configuration VTOM
VTOM_BASE_URL = "https://rec-vtom-admin.carter-cash.com:30002/vtom/public/monitoring/2.0"
VTOM_API_KEY = os.getenv('vtom_api_key')
VTOM_HEADERS = {
    "X-API-Key": VTOM_API_KEY,
    "Content-Type": "application/json"
}

# Statuts VTOM
VTOM_STATUS_FINISHED = 'Finished'
VTOM_STATUS_WAITING = 'Waiting'
VTOM_STATUS_RUNNING = 'Running'

# Timeouts par défaut
DEFAULT_TIMEOUT = 30
POLLING_INTERVAL = 5


# ============================================================================
# FONCTIONS VTOM
# ============================================================================

def reset(env, appli, timeout=DEFAULT_TIMEOUT):
    """
    Réinitialise une application VTOM en changeant son statut à 'Waiting'.
    
    Args:
        env: Environnement VTOM (ex: 'REC', 'PROD')
        appli: Nom de l'application VTOM
        timeout: Temps maximum d'attente en secondes (défaut: 30)
    
    Raises:
        ValueError: Si l'application n'atteint pas le statut 'Finished' dans le délai imparti
    """
    url = f"{VTOM_BASE_URL}/environments/{env}/applications/{appli}/action"
    payload = {
        "type": "ChangeStatus",
        "status": VTOM_STATUS_WAITING
    }
    
    # Envoi de la requête de changement de statut
    response = requests.post(url, headers=VTOM_HEADERS, json=payload)
    response.raise_for_status()
    
    # Attente que l'application atteigne le statut 'Finished'
    if not _wait_for_status(env, appli, timeout=timeout):
        raise ValueError(
            f"L'application {appli} dans l'environnement {env} "
            f"n'a pas atteint le statut terminé en {timeout} secondes"
        )


def execute(env, appli, job, timeout=DEFAULT_TIMEOUT, error=None):
    """
    Exécute un job VTOM en changeant son statut à 'Running'.
    
    Args:
        env: Environnement VTOM (ex: 'WEB', 'WEB_JOUR')
        appli: Nom de l'application VTOM
        job: Nom du job à exécuter
        timeout: Temps maximum d'attente en secondes (défaut: 30)
        error: Code d'erreur personnalisé à enregistrer en cas d'échec
    
    Raises:
        ValueError: Si le job n'atteint pas le statut 'Finished' dans le délai imparti
    """
    url = f"{VTOM_BASE_URL}/environments/{env}/applications/{appli}/jobs/{job}/action"
    payload = {
        "comment": "test",
        "type": "ChangeStatus",
        "status": VTOM_STATUS_RUNNING
    }
    
    # Envoi de la requête de lancement du job
    response = requests.post(url, headers=VTOM_HEADERS, json=payload)
    response.raise_for_status()
    
    # Attente que le job atteigne le statut 'Finished'
    if not _wait_for_status(env, appli, job, timeout):
        if error:
            Assert.set_intercept(error)
        raise ValueError(
            f"Le traitement {job} de {appli} dans l'environnement {env} "
            f"n'a pas atteint le statut terminé en {timeout} secondes"
        )


def get_vtom_status(env, appli, job=None):
    """
    Récupère le statut d'une application ou d'un job VTOM.
    
    Args:
        env: Environnement VTOM (ex: 'REC', 'PROD')
        appli: Nom de l'application VTOM
        job: Nom du job (optionnel, si None vérifie le statut de l'application)
    
    Returns:
        bool: True si le statut est 'Finished', False sinon
    """
    # Construction de l'URL selon si on vérifie un job ou une application
    if job:
        url = f"{VTOM_BASE_URL}/environments/{env}/applications/{appli}/jobs/{job}/status"
    else:
        url = f"{VTOM_BASE_URL}/environments/{env}/applications/{appli}/status"
    
    try:
        response = requests.get(url, headers=VTOM_HEADERS)
        response.raise_for_status()
        
        status = response.json().get('status')
        return status == VTOM_STATUS_FINISHED
    
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du statut: {e}")
        return False


def _wait_for_status(env, appli, job=None, timeout=DEFAULT_TIMEOUT):
    """
    Attend qu'une application ou un job VTOM atteigne le statut 'Finished'.
    
    Args:
        env: Environnement VTOM
        appli: Nom de l'application VTOM
        job: Nom du job (optionnel)
        timeout: Temps maximum d'attente en secondes
    
    Returns:
        bool: True si le statut 'Finished' est atteint, False si timeout
    """
    end_time = time.time() + timeout
    
    while time.time() < end_time:
        if get_vtom_status(env, appli, job):
            return True
        time.sleep(POLLING_INTERVAL)
    
    return False