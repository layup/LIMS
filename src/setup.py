
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

from modules.SplashScreen import SplashScreen
from PyQt5.QtCore import QTimer

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

    splash = SplashScreen()
    splash.show()

    print(f'\nDisplay Settings')
    print(f"Using AA_EnableHighDpiScaling : {QApplication.testAttribute(QtCore.Qt.AA_EnableHighDpiScaling)}")
    print(f"Using AA_UseHighDpiPixmaps    : {QApplication.testAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)}")
    print()
    
    QTimer.singleShot(1000, lambda: show_main_window())
    
    #TODO: load in all of the settings prior  
    def show_main_window():
        # Create and show the main window
        window = MainWindow()
        window.show()

        # Finish the splash screen
        splash.finish(window)
        
    sys.exit(app.exec_())
    
    