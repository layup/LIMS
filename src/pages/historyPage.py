import sqlite3 


from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
)


from modules.constants import *; 
#from modules.createExcel import * 
from modules.dbFunctions import searchJobsList, getAllJobsList  
from modules.dialogBoxes import openJobDialog
#from modules.utilities import * 

from pages.createReportPage import createReportPage

def historyPageSetup(self): 
    
    historyTable = self.ui.reportsTable 
    historySearchWidget = self.ui.searchLine
    
    rowHeight = 25; 
    historyHeaders = ['Job Number', 'Report Type', 'Parameter', 'Dilution Factor', 'Date Created', 'Open Report']

    # Format the basic table
    historyTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    historyTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
    historyTable.setHorizontalHeaderLabels(historyHeaders)
    
    historyTable.verticalHeader().setVisible(True)
    historyTable.verticalHeader().setDefaultSectionSize(rowHeight)

    #Disable editing for the entire table 
    historyTable.setEditTriggers(QTableWidget.NoEditTriggers) 

    #load the inital table data 
    loadReportsPage(self); 

    # Connect the signals 
    self.ui.reportsTable.doubleClicked.connect(lambda index: on_table_double_clicked(index))
    self.ui.reportsSearchBtn.clicked.connect(lambda: on_reportsSearchBtn_clicked(self)) 
    

#TODO: could have a model item that keeps tracks of all the histroy
def loadReportsPage(self, searchValue=None): 
    print('[FUNCTION]: historyPageSetup')
    print(f'Search Value: {searchValue}')

    if(searchValue): 
        try: 
            results = searchJobsList(self.db, searchValue)
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            results = []
    else: 
        try: 
            results = getAllJobsList(self.db);
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            results = []

    historyTable = self.ui.reportsTable 
    
    historyTable.clearContents()
    historyTable.setRowCount(len(results))
    
    for row, current in enumerate(results): 
        #(20, 191303, 'ICP', 'Water', 1, '2024-03-05')
        #TODO: could format this into a cheeckly little for loop and remove this setItemFunction 
        jobNumber = str(current[1])
        reportType = str(current[2])
        parameterType = str(current[3])
        dilutionFactor = str(current[4])
        creationDate = str(current[5])
        
        setTableItem(historyTable, row, 0, jobNumber) 
        setTableItem(historyTable, row, 1, reportType)
        setTableItem(historyTable, row, 2, parameterType)
        setTableItem(historyTable, row, 3, dilutionFactor)
        setTableItem(historyTable, row, 4, creationDate) 
            
        openButton = QPushButton("Open")
        openButton.clicked.connect(lambda _, row=row: openExistingReport(self, row));
        historyTable.setCellWidget(row, 5, openButton)

@pyqtSlot()
def on_reportsSearchBtn_clicked(self): 
    print('ReportSearchBtn Clicked:')

    searchValueString = self.ui.reportsSearchLine.text()
    print(f'Searching for Job Number: {searchValueString}')

    #self.ui.reportsTable.clearContents()
    #self.ui.reportsTable.setRowCount(0)
    loadReportsPage(self, searchValueString)
    
def setTableItem(table, row, column, text, alignment=Qt.AlignCenter): 
    item = QTableWidgetItem()
    item.setTextAlignment(alignment)
    item.setText(text)
    table.setItem(row, column, item)
    
#TODO: what is the point of this double click function    
def on_table_double_clicked(index):
# Open the row data
    row = index.row()
    print(f"Double clicked on row {row}")
    
#TODO: save the user data that they have entered? that might be a pain in the ass that will get done later
def openExistingReport(self, row): 
    print('[FUNCTION]: openExistingReport')
    rowData = []
    
    for i in range(4): 
        item =self.ui.reportsTable.item(row, i) 
        if(item): 
            rowData.append(item.text()) 
            
    print(rowData) 
    
    popup = openJobDialog(rowData[0], self)
    result = popup.exec_()
    
    if result == QDialog.Accepted:
        print('Opening Existing Report')
        isExistingReport = True 
        createReportPage(self, rowData[0], rowData[1], rowData[2], rowData[3], isExistingReport) 
        
    else:
        print("Not Opening Existing Report'")
        
        





