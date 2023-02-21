
__author__ = "Tommy Lay"
__version__ = "0.1.0"
__license__ = "MIT"

import sys
import os 
import re
import csv
import numpy
import json 

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

from modules.utilities import *
from main_ui import window


def main(): 
    print("Running Application")
    window()
    
    
    #scanDir(fileName)

if __name__ == "__main__":
    main()
    
    