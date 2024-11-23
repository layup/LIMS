import sqlite3 

from base_logger import logger

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QHeaderView, QDialog, QPushButton, QAbstractItemView, QTableWidgetItem, QCompleter

from modules.constants import TABLE_ROW_HEIGHT, REPORT_NAME, REPORT_STATUS 
from modules.dbFunctions import searchJobsList, getAllJobsList, getAllJobNumbersList, getFrontHistory, getParameterName
from modules.widgets.dialogs import openJobDialog, showErrorDialog
from modules.widgets.TableFooterWidget import TableFooterWidget

from pages.reports_page.create_report_page import createReportPage

#TODO: add in errors that will have to fix 

def historyPageSetup(self): 
    self.logger.info(f'Entering historyPageSetup ...')
    
    historyHeaders = ['Job Number', 'Report Type', 'Parameter', 'Dilution Factor', 'Creation Date', 'Status', 'Action']
    frontHistoryHeaders = ['Job Number', 'Client Name', 'Creation Date', 'Status']

    formatHistoryDatabaseTable(self.ui.reportsTable , historyHeaders)
    formatHistoryDatabaseTable(self.ui.frontDeskTable, frontHistoryHeaders)

    footer_widget = TableFooterWidget()
    self.ui.historyLayout.addWidget(footer_widget)
    
    #load the initialize table data 
    historySearchSetup(self)
    loadReportsPage(self); 

    # Add tool tips 
    self.ui.reportsSearchBtn.setToolTip('This is a tooltip for the button')

    # Connect the signals 
    self.ui.reportsTable.doubleClicked.connect(lambda index: on_table_double_clicked(index))
    self.ui.reportsSearchBtn.clicked.connect(lambda: on_reportsSearchBtn_clicked(self)) 
    self.ui.reportsSearchLine.returnPressed.connect(lambda: on_reportsSearchBtn_clicked(self))
    self.ui.createReportBtn.clicked.connect(lambda: self.change_index(1))
    

def formatHistoryDatabaseTable(table, headers, tooltips=None): 
    
    rowHeight = 25
    
    # Disable editing for the entire table 
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    # Set the column count 
    table.setColumnCount(len(headers))

    # Set the column names and info 
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
    table.setHorizontalHeaderLabels(headers)
    
    ''' OPT: Setting the tool tips for the headers 
    
    for col in range(table.columnCount()): 
        header_item = QTableWidgetItem(headers[col])
        header_item.setToolTip('This is a test')
        table.setHorizontalHeaderItem(col, header_item)
    
    ''' 
    
    table.verticalHeader().setVisible(True)
    table.verticalHeader().setDefaultSectionSize(rowHeight)
    

def historySearchSetup(self): 
    self.logger.info(f'Entering historyPageSetup')
    # Get the all of the jobNums for the completer
    jobList = getAllJobNumbersList(self.tempDB) 
    jobList_as_strings = [str(item) for item in jobList]

    # Sets the completers
    completer = QCompleter(jobList_as_strings)
    completer.setCompletionMode(QCompleter.PopupCompletion)  # Set completion mode to popup
    completer.setMaxVisibleItems(10)
    
    self.ui.reportsSearchLine.setCompleter(completer)
    self.ui.reportsSearchLine.setPlaceholderText("Enter Job Number...") 
    
#******************************************************************
#   Chemistry History 
#******************************************************************

def loadReportsPage(self, searchValue=None): 
    self.logger.info(f'Entering loadReportsPage with parameter of searchValue: {searchValue}') 

    # When user uses the search bar 
    if(searchValue): 
        try: 
            results = searchJobsList(self.tempDB, searchValue)
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            results = []
    else: 
        try: 
            results = getAllJobsList(self.tempDB);            
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            results = []

    historyTable = self.ui.reportsTable 
    
    historyTable.clearContents()
    historyTable.setRowCount(len(results))
    
    for row, current in enumerate(results): 
        historyTable.setRowHeight(row, TABLE_ROW_HEIGHT)
        
        # Define the table data by breaking down the SQL results
        jobNumber = str(current[0])
        reportType = REPORT_NAME[current[1]]
        parameterType = getParameterName(self.tempDB, int(current[2]))
        dilutionFactor = str(current[3])
        creationDate = str(current[4])
        
        if(current[5] is not None):  
            try:
                status = REPORT_STATUS[int(current[5])]  # Attempt conversion to int
            except (ValueError, TypeError):  # Catch potential conversion errors
                self.logger.error("Error: Invalid value for REPORT STATUS. Setting Status to 'N/A'.")
                status = 'N/A'
        else: 
            status = 'N/A' 
    
        setTableItem(historyTable, row, 0, jobNumber) 
        setTableItem(historyTable, row, 1, reportType)
        setTableItem(historyTable, row, 2, parameterType)
        setTableItem(historyTable, row, 3, dilutionFactor)
        setTableItem(historyTable, row, 4, creationDate) 
        setTableItem(historyTable, row, 5, status)  
            
        openButton = QPushButton("Open")
        openButton.clicked.connect(lambda _, row=row: openExistingReport(self, row));
        historyTable.setCellWidget(row, 6, openButton)

    if(searchValue == None): 
        return None

    return results


def actionButtons(): 
    
    pass;


@pyqtSlot()
def on_reportsSearchBtn_clicked(self): 
    try: 
        self.logger.info('ReportSearchBtn Clicked:')

        searchValueString = self.ui.reportsSearchLine.text()
        self.logger.info(f'Searching for Job Number: {searchValueString}')

        results = loadReportsPage(self, searchValueString)

        
        if(results == None): 
            errorTitle = "No Search Results"
            errorMsg = "Couldn't find any jobs that matched the job num" 
            showErrorDialog(self, errorTitle, errorMsg)
        
    except Exception as error: 
        print(error)
    
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
    self.logger.info(f'Entering openExistingReport on row: {row}')
    rowData = []
    
    for i in range(4): 
        item =self.ui.reportsTable.item(row, i) 
        if(item): 
            rowData.append(item.text()) 
            
    print(rowData) 
    
    popup = openJobDialog(rowData[0], self)
    result = popup.exec_()
    
    if result == QDialog.Accepted:
        self.logger.info('Opening Existing Report')
        existingReport = True 
        createReportPage(self, rowData[0], rowData[1], rowData[2], rowData[3], existingReport) 
        
    else:
        self.logger.info("Report doesn't exist in database'")
        



