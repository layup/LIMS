
__author__ = "Tommy Lay"
__version__ = "0.1.0"
__license__ = "MIT"

import sys
import os 
import re
import csv
import numpy
import json 

from PyQt5.QtWidgets import QApplication
from main_ui import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec_())
    
    