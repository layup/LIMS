
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

from modules.widgets.SplashScreenWidget import SplashScreen
from PyQt5.QtCore import QTimer

from base_logger import logger 

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


    
def setup_logging(): 

    logger_level_meaning = {
        10: 'DEBUG', 
        20: 'INFO', 
        30: 'WARNING', 
        40: 'ERROR', 
        50: 'CRITICAL'
    } 
    
    print('*Starting Program')
    print(f'*Logging Level: {logger_level_meaning[logger.level]}')
    print(f"*Logger Propagation: {logger.propagate}")

    logger.info(f'Display Settings')
    logger.info(f"Using AA_EnableHighDpiScaling : {QApplication.testAttribute(QtCore.Qt.AA_EnableHighDpiScaling)}")
    logger.info(f"Using AA_UseHighDpiPixmaps    : {QApplication.testAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)}")

if __name__ == "__main__":

    setup_logging()

    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

    splash = SplashScreen()
    splash.show()

    
    QTimer.singleShot(1000, lambda: show_main_window())
    
    #TODO: load in all of the settings prior  
    def show_main_window():
        # Create and show the main window
        window = MainWindow(logger)
        window.show()

        # Finish the splash screen
        splash.finish(window)
        
    sys.exit(app.exec_())
    

    