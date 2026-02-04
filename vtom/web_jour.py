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

env = 'WEB_JOUR'

def vtom_order_loader():
    appli = 'C1_OPB_OrderLoader'
    execute(env, appli, 'C1_STB_ATH_OPB_OrderLoader', timeout=180, error="error_job_order_loader")