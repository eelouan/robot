import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np

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

env = 'COMMERCE_JOUR'

def controle_ticket():
    appli = 'C1_OPB_ControlTicket'
    execute(env, appli, 'C1_STB_OPB_ATH_CtrlFiles', timeout=600, error="error_yakaedi")

def traitement_ticket_full():
    appli = 'C1_OPB_Traitement_Ticket_full'
    execute(env, appli, 'C1_STB_OPB_ATH_IntegFiles', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C3_VTO_SetRessourceOK', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C1_STB_OPB_ATH_InfoComptoir', timeout=600, error="error_yakaedi")
    # execute(env, appli, 'C1_PS1_OPB_VerifIntegFiles', timeout=600, error="error_yakaedi")

    execute(env, appli, 'C1_SQL_OPB_ATH_VerifCoherenceData', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C1_STB_OPB_ATH_TransformToXml', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C3_SQL_OPB_ATH_CorrectionDataLiv', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C3_SQL_OPB_ATH_CorrectionDataAnn', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C3_SQL_OPB_ATH_CorrectionDataSer', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C1_STB_OPB_ATH_GenerateXML', timeout=100000, error="error_yakaedi")
    execute(env, appli, 'C3_VTO_SetRessourceKO', timeout=60, error="error_yakaedi")

def ath_recuptic():
    appli = 'C1_ATH_RECUPTIC'
    execute(env, appli, 'C1_FTP_TYT_SAR_TrfTickets', timeout=600, error="error_yakaedi")
    execute(env, appli, 'C1_EXE_ATH_RecupTic', timeout=600, error="error_yakaedi")