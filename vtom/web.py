import time
import os
import pytesseract
import pyautogui
import cv2
import numpy as np

from RPA.Desktop import Desktop
from PIL import ImageGrab
from dotenv import load_dotenv
from RPA.Images import Images

from config.img import *
from utils.utils import *
from utils.Assert import *
from utils.connect_db import *
from utils.request import *
from vtom.utils import *

env = 'WEB'

def vtom_recup_ticket():
    appli = 'C1_WEB_RecupTicket'
    # reset(env,appli)
    # execute(env, appli, 'C1_FTP_WEB_TYT_GetTicketXML', timeout=60, execution='C1_EXE_ATH_RecupTicWeb')
    execute(env, appli, 'C1_FTP_WEB_TYT_GetTicketXML', timeout=60, error="error_job_recuptic")
    execute(env, appli, 'C1_MOV_TYT_SAR_TicketXML', timeout=60, error="error_job_recuptic")
    execute(env, appli, 'C1_EXE_ATH_RecupTicWeb', timeout=60, error="error_job_recuptic")