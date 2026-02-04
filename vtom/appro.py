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

env = 'APPROVISIONNEMENT'

def vtom_yakaedi():
    appli = 'C3_ATH_Yakaedi'
    execute(env, appli, 'C3_STB_ATH_YKE_CmdeClient', timeout=60, error="error_yakaedi")
    execute(env, appli, 'C3_BSH_YKE_Edi', timeout=60, error="error_yakaedi")
    execute(env, appli, 'C3_STB_YKE_ATH_ImportCmdeFour', timeout=60, error="error_yakaedi")