
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
from main_ui import MainWindow


def main(): 
    print("Running Application")
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    #win = Mywindow()
    #win.show()
   

   
    sys.exit(app.exec_())
    
    
    #scanDir(fileName)

if __name__ == "__main__":
    main()
    
    