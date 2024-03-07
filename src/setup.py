
__author__ = "Tommy Lay"
__version__ = "0.1.0"
__license__ = "MIT"

import sys
import os 
import re
import csv
import numpy
import json 

import PyQt5 
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtCore  
from app import MainWindow

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

    print(f'\nDisplay Settings')
    print(f"Using AA_EnableHighDpiScaling : {QApplication.testAttribute(QtCore.Qt.AA_EnableHighDpiScaling)}")
    print(f"Using AA_UseHighDpiPixmaps    : {QApplication.testAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)}")
    print()
    
    window = MainWindow()

    sys.exit(app.exec_())
    
    