import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np
import requests


from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images  import Images


from config.img import *
from utils.utils import *
from utils.Assert import *
from utils.connect_db import *
from utils.request import *
from vtom.utils import *

env = 'WMS_JOUR'

def vtom_prepare():
    appli = 'C3_ATH_IntegMep'
    execute(env, appli, 'C3_FTP_EGO_CCA_RecupFileMep', timeout=120, error="error_job_preparation")
    execute(env, appli, 'C3_XDI_EGO_ATH_CreateFileImportMep', timeout=120, error="error_job_preparation")
    execute(env, appli, 'C3_EXE_ATH_ImportFilePreparationMep', timeout=120, error="error_job_preparation")

def vtom_traitement_commande_epo():
    appli = 'C2_ATH_TraitementCommandeEpo'
    execute(env, appli, 'C3_FTP_EGO_EPO_FILE', timeout=120, error="error_job_traitement_epo")
    execute(env, appli, 'C2_XDI_EGO_ATH_IntFicEpo', timeout=120, error="error_job_traitement_epo")
    execute(env, appli, 'C2_EXE_ATH_BatchImportCommandeClientPrepa', timeout=180, error="error_job_traitement_epo")
    
def vtom_traitement_commande_shi():
    appli = 'C2_ATH_TraitementCommandeShi'
    execute(env, appli, 'C3_FTP_EGO_SHI_FILE', timeout=120, error="error_job_traitement_shi")
    execute(env, appli, 'C2_XDI_EGO_ATH_IntFicShi', timeout=120, error="error_job_traitement_shi")
    execute(env, appli, 'C2_EXE_ATH_BatchImportCommandeClientExpedition', timeout=120, error="error_job_traitement_shi")

def vtom_traitement_commande_rbr():
    appli = 'C2_ATH_TraitementCommandeRbr_XDI'
    execute(env, appli, 'C3_FTP_EGO_RBR_FILE', timeout=120, error="error_job_traitement_rbr")
    execute(env, appli, 'C2_XDI_EGO_ATH_IntFicRbr', timeout=120, error="error_job_traitement_rbr")
    execute(env, appli, 'C2_EXE_ATH_ImportCommandeFournisseurReception', timeout=120, error="error_job_traitement_rbr")
    execute(env, appli, 'C2_EXE_ATH_ImportRetourClientReception', timeout=120, error="error_job_traitement_rbr")