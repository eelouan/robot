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

env = 'WMS'

def vtom_envoi_commande():
    appli = 'C3_ATH_EnvoiCommandes'
    execute(env, appli, 'C3_STB_ATH_EGO_CommandeIntLadPre', timeout=120, error="error_envoi_commandes")
    execute(env, appli, 'C3_FTP_CCA_EGO_TrfFichierORDINL', timeout=120, error="error_envoi_commandes")


def vtom_traitement_reception_commande():
    appli = 'C3_ATH_EnvoiCommandes'
    execute(env, appli, 'C3_XDI_ATH_EGO_CommandeFournisseurOPS', timeout=120, error="error_job_reception_commande")
    execute(env, appli, 'C2_FTP_ATH_EGO_EnvoiFichierOPS', timeout=120, error="error_job_reception_commande")
