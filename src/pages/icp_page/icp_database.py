
import math 
import json
import os

from base_logger import logger
from PyQt5 import QtWidgets 
from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt

from PyQt5.QtWidgets import (QDialog, QMessageBox, QPushButton, QWidget, QAbstractItemView, QTableWidgetItem )

from modules.constants import TABLE_ROW_HEIGHT 
from modules.utils.file_utils import openFile
from modules.widgets.dialogs import showErrorDialog
from modules.widgets.TableFooterWidget import TableFooterWidget

from pages.icp_page.icp_upload import icp_upload

#******************************************************************
#    ICP History 
#****************************************************************** 
def icp_history_setup(self): 
    self.logger.info(f'Entering icp_history_setup')
     
    # Define the icp history model and table view 
    self.icpHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.icpTableView = DatabaseTableView(self.tempDB, self.ui.icpTable, self.ui.icpHistoryLayout, self.icpHistoryDataModel) 

    # Set the tool tips 
    self.ui.icpUploadBtn.setToolTip('Upload .txt or .xlsx files into the database from machines') 

    # update footer (buttons, page change, filter update) -> update data 
    # update search -> update data and footer 
    # update data -> update table 
    self.icpHistoryDataModel.dataChanged.connect(lambda newData: self.icpTableView.update_table(newData))
    
    self.ui.icpSearchBtn1.clicked.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))
    self.ui.icpSearchLine1.returnPressed.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))
    
    self.ui.icpUploadBtn.clicked.connect(lambda: on_icpUploadBtn_clicked(self.tempDB))


@pyqtSlot()
def on_icpUploadBtn_clicked(database): 
    logger.info('[SIGNAL]: on_icpUploadBtn_clicked')
    
    fileLocation = openFile()
    logger.debug(f'fileLocation: {fileLocation}')
    icp_upload(fileLocation, database) 


@pyqtSlot()
def on_icpSearchBtn_clicked(self): 
    logger.info('[SIGNAL]: on_icpSearchBtn_clicked')

    jobNum = self.ui.icpSearchInput.text() 
    
    # Reload the initial table 
    if(jobNum == ''):
        loadIcpHistory(self)
    else: 
        inquiry = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData WHERE sampleName LIKE ?' 
        machineData = list(self.tempDB.query(inquiry,('%' + jobNum + '%',)))
        
        # FIXME: streamline the QMessageBox Process 
        if not machineData: 
            msgBox = QMessageBox()  
            msgBox.setText("No Search Results");
            msgBox.setInformativeText("No search results for given job number");
            msgBox.setStandardButtons(QMessageBox.Ok);
            x = msgBox.exec_()  # this will show our messagebox
        else: 
            populateIcpHistoryTable(self, machineData)

def loadIcpHistory(self):   
    self.logger.info(f'Entering loadIcpHistory')
    
    machineDataQuery = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData ORDER BY creationDate DESC'
    machineData = list(self.tempDB.query(machineDataQuery))
    totalItem = len(machineData) 
    #self.ui.headerDesc.setText(f'Total Items in Database: {totalItem}')
        
    populateIcpHistoryTable(self, machineData) 
            
def populateIcpHistoryTable(self, result): 
    self.logger.info(f'Entering loadIcpHistory with parameters: result: {result}')
    
    textLabelUpdate = 'Total Search Results: ' + str(len(result))
    
    TableHeader = ['Sample Number', 'Job Number', 'Machine Type', 'File Location', 'Upload Date', 'Actions']

    self.ui.headerDesc.setText(textLabelUpdate)    
    self.ui.icpTable.setRowCount(len(result)) 
    self.ui.icpTable.setColumnCount(len(TableHeader))
    self.ui.icpTable.setHorizontalHeaderLabels(TableHeader)

    for row , data in enumerate(result):
        #loops thought items in the order sql requested 
        self.ui.icpTable.setRowHeight(row, TABLE_ROW_HEIGHT)
        
        sampleNum = data[0] 
        machineType = data[2]
        
        for col in range(len(data)): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(str(data[col]))
            item.setTextAlignment(Qt.AlignHCenter)
            self.ui.icpTable.setItem(row ,col ,item) 
            
        #FIXME: 
        button = QPushButton("Open") 
        button.setFixedSize(100, 10)  # Set the fixed size of the button (width, height)
       
        button.clicked.connect(lambda _, sampleNum=sampleNum, machineType=machineType: icpOpenButton(self, sampleNum, machineType))
        actionRow = 5 
        self.ui.icpTable.setCellWidget(row, actionRow, button)

    
    self.ui.icpTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

def icpOpenButton(database, sampleNum, machineType): 
    logger.info('Entering icpOpenButton with parameters: sampleNum: {sampleNum}, machineType: {machineType}')

    dialog = viewIcpDataDialog(database, sampleNum, machineType) 
    dialog.exec()
    
#******************************************************************
#    ICP History Classes 
#******************************************************************  

class DatabaseTableModel(QObject): 
    #TODO: allow for filter search via the footer somehow
    dataChanged = pyqtSignal(list)

    def __init__(self, database, current_page=1, total_rows=100):
        super().__init__()
        self.db = database 

        self.data = []
        self.filtered_data = self.data
    
        #TODO: introduce a filter system that we can use 
        self.filter_by = None; 
          
        self.current_page = current_page
        self.total_rows = total_rows
        self.total_pages = self.get_total_rows()

        self.load_init_data()
        
    def get_data(self): 
        self.data = self.fetch_data()
    
    def get_total_rows(self): 
        query = 'SELECT COUNT(*) FROM icpData' 

        totalPages = self.db.query(query)[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));  
        
        return totalPages
    
    def get_total_rows_filter(self, text): 
        query = f'SELECT COUNT(*) FROM icpData WHERE sampleName LIKE ?'
        sample_text = '%' + text + '%'

        totalPages = self.db.query(query, (sample_text, ))[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));  
        
        return totalPages
        
    def get_footer_info(self): 
        return {
            'current_page': self.current_page, 
            'total_rows': self.total_rows, 
            'total_pages': self.total_pages, 
        }
        
    def load_init_data(self): 
        self.data = self.fetch_data() 

    def fetch_data(self):
        machineDataQuery = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
        
        offSet = (self.current_page -1) * self.total_rows
        
        self.db.execute(machineDataQuery, (self.total_rows, offSet,))  # Pass offset as a single value
        self.data = list(self.db.fetchall())
        
        self.dataChanged.emit(self.data)
        return self.data
    
    def set_filter(self, jobNum):
        self.current_page = 1;     
        
        if(jobNum == ''): 
            # Reset the search to normal 
            self.total_pages = self.get_total_rows()
            self.fetch_data()
        else:  
            self.total_pages = self.get_total_rows_filter(jobNum)
            offSet = (self.current_page -1) * self.total_rows
            
            inquiry = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData WHERE sampleName LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?' 
            self.filtered_data = list(self.db.query(inquiry,('%' + jobNum + '%', self.total_rows, offSet)))
            
            if(self.filtered_data): 
                self.dataChanged.emit(self.filtered_data)
                return self.filtered_data
            else: 
                return None; 
    
    def set_page(self, page_number): 
        self.current_page = page_number 
        logger.info(f'DatabaseTableModel set_page, changed page to {self.current_page} of {self.total_pages}')
        # offset will be updated
        self.fetch_data()
        
    def set_rows(self, index): 
        valid_rows = {0: 100, 1: 200, 2:300}

        if(index in valid_rows): 
            self.total_rows = valid_rows[index]
            self.fetch_data()
        
class DatabaseTableView(): 
    
    footerAction = pyqtSignal(int)
    
    def __init__(self, database, table, layout, dataModel): 
        self.db = database 
        self.table = table
        self.data_model = dataModel
        self.layout = layout 
    
        # Footer Widget setup 
        self.footerWidget = TableFooterWidget() 
        self.layout.addWidget(self.footerWidget)   
        
        # Populate the table and footer 
        self.init_table()
        self.init_footer()

        self.footerWidget.nextBtn.clicked.connect(self.handle_next_page)
        self.footerWidget.prevBtn.clicked.connect(self.handle_prev_page)
        self.footerWidget.QSpinBox.valueChanged.connect(self.handle_spinBox_change)
        self.footerWidget.QComboBox.currentIndexChanged.connect(self.handle_row_filter_change)
        
        #self.footerWidget.QSpinBox.valueChanged.connect(lambda newValue: self.handle_spinBox_change(newValue))
        #self.footerWidget.QComboBox.currentIndexChanged.connect(lambda newIndex: self.handle_row_filter_change(newIndex))
                
    def init_table(self): 
        # Define table columns
        column_headers = ['Sample Number', 'Job Number', 'Machine Type', 'File Location', 'Upload Date', 'Actions'] 
        
        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.horizontalHeader().setStretchLastSection(True) 
        
        self.table.verticalHeader().setVisible(True)

        smallCol = 140
        medCol = 240 
        bigCol = 340 

        # Set the width of the tables 
        self.table.setColumnWidth(0, smallCol)
        self.table.setColumnWidth(1, smallCol)
        self.table.setColumnWidth(2, smallCol)
        self.table.setColumnWidth(3, medCol)
        self.table.setColumnWidth(4, smallCol)
        self.table.setColumnWidth(5, medCol)
        
        # Get the init data to populate table 
        init_data = self.data_model.fetch_data()
        self.update_table(init_data)
        
    def init_footer(self): 
        self.update_footer() 
                
    def update_table(self, results): 
        print('update_table')
        # Clear existing data 
        self.clear_table()
        
        # Bring the vertical scroll bar back to the top 
        self.table.verticalScrollBar().setValue(0)
        
        # Define table rows 
        total_results = len(results) 
        self.table.setRowCount(total_results)  
        
        for row , data in enumerate(results):
            #loops thought items in the order sql requested 
            self.table.setRowHeight(row, TABLE_ROW_HEIGHT)
            
            sampleNum = data[0] 
            machineType = data[2]
            
            for col in range(len(data)): 
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(data[col]))
                item.setTextAlignment(Qt.AlignHCenter)
                self.table.setItem(row ,col ,item) 
                
            button = QPushButton("Open") 
            button.setFixedSize(100, 10)  # Set the fixed size of the button (width, height)

            button.clicked.connect(lambda _, sampleNum=sampleNum, machineType=machineType: icpOpenButton(self.db, sampleNum, machineType))
            actionRow = 5 
            self.table.setCellWidget(row, actionRow, button)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.update_footer()
    
    def clear_table(self): 
        # Get the number of rows
        num_rows = self.table.rowCount()

        # Iterate through all rows (in reverse order to avoid index shifting)
        for i in range(num_rows - 1, -1, -1):
            self.table.removeRow(i)
                
    def update_footer(self): 
        footer_info = self.data_model.get_footer_info()
        print(f'Footer Info: {footer_info}')
        self.footerWidget.load_data(footer_info['current_page'], footer_info['total_rows'], footer_info['total_pages'])
        #self.layoutChanged.emit()
    
    def handle_search_text(self, text): 
        result = self.data_model.set_filter(text)
        
        if(result == None): 
            # Throw an error if result is none 
            errorTitle = "Not Search Results"
            errorMsg = "Couldn't find any jobs that matched the job num" 
            showErrorDialog(self, errorTitle, errorMsg)
            
    
    def handle_row_filter_change(self, index): 
        self.data_model.set_rows(index)
        
    def handle_spinBox_change(self, newValue): 
        self.data_model.set_page(newValue)
    
    def handle_next_page(self): 
        footer_info = self.data_model.get_footer_info()
        
        if((footer_info['current_page']) != footer_info['total_pages']): 
            self.data_model.set_page(footer_info['current_page']+1)
        
    def handle_prev_page(self): 
        footer_info = self.data_model.get_footer_info()
        
        if((footer_info['current_page']) != 0): 
            self.data_model.set_page(footer_info['current_page']-1)
    
    
    
class viewIcpDataDialog(QDialog): 
    
    def __init__(self, db, sampleNum,  machineType):
        super().__init__()
        
        self.db = db 
        self.sampleNum = sampleNum
        self.jobNum = sampleNum[0:6]
        self.machineType = machineType
        
        # load UI
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'icpViewDataDialog.ui')
        loadUi(file_path, self)

        # Connect Signals 
        self.saveBtn.clicked.connect(lambda: print('save button clicked'))
        self.cancelBtn.clicked.connect(self.close)

        self.init_data()
     
    def init_data(self): 
        # Get the data from the database 
        query = f"SELECT * FROM icpData WHERE jobNum = '{self.jobNum}' AND machineNum = '{int(self.machineType)}'"
        results = self.db.query(query)

        fileName = results[0][2]
        uploadDate = results[0][4]
        sampleNames = [item[0] for item in results]
        sampleNames.insert(0, 'Elements')
        elementNames = list(json.loads(results[0][3]).keys())
        
        # Lod the preset data 
        self.jobNumberLabel.setText(self.jobNum)
        self.textFileLabel.setText(fileName)
        self.uploadedDateLabel.setText(uploadDate)
        self.machineNumLabel.setText(str(self.machineType))
    
        # Prepare the table 
        self.tableWidget.setRowCount(len(elementNames))
        self.tableWidget.setColumnCount(len(sampleNames))
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)
    
        # Set the table headers 
        self.tableWidget.setHorizontalHeaderLabels(sampleNames)

        # Assign elements row and disable editing of them
        for row, element in enumerate(elementNames): 
            item = QTableWidgetItem(element)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 0, item) 

        for col, data in enumerate(results, start=1): 

            if isinstance(data[3], str):  # Check if it's a string
                try:
                    element_data = json.loads(data[3])  # Load JSON into a dictionary
                    
                    for row, (key, value) in enumerate(element_data.items()): 
                        #print(f'col: {col}, row: {row}, key: {key} data: {value}')
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, value)
                        self.tableWidget.setItem(row, col, item)
                        
                except json.JSONDecodeError:
                    print("Error: Invalid JSON data")  # Handle potential invalid JSON
                    
    def updateSampleData(): 
        pass; 
   
   
