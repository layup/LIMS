

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget,
    QHBoxLayout,QLineEdit
)



'''
    - header/report info
    - client info
    - sample widget info
    - table info
    - create excel report
'''



class ReportManager:

    def __init__(self, jobNum, parameter, dilution, status, client_manager, controller):

        # general report info
        self.jobNum = jobNum
        self.parameter = parameter
        self.dilution =  dilution
        self.status = status

        self.db = None;

        # samples
        self.samplesNames = None;

        # client information
        self.client_manager = client_manager

        # deal with the table and table info
        self.controller = controller;



