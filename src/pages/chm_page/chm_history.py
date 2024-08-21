
from base_logger import logger
import math 
import os 

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QWidgetItem, QTreeWidgetItem
)
from modules.dbFunctions import getTestsName
from modules.constants import  TABLE_ROW_HEIGHT
from modules.utilities import icp_upload
from modules.widgets.dialogs import deleteBox
from modules.widgets.TableFooterWidget import TableFooterWidget

 
#******************************************************************
#    Chemistry Database Section 
#****************************************************************** 
    
def chm_database_setup(self): 
    print('[FUNCTION]: icp_history_setup(self)')
     
    # Define the icp history model and table view 
    self.chmHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.chmTableView = DatabaseTableView(self.tempDB, self.ui.chmInputTable, self.ui.chmDatabaseLayout, self.chmHistoryDataModel, self.ui.chmEditWidget) 

    # update footer (buttons, page change, filter update) -> update data 
    # update search -> update data and footer 
    # update data -> update table 
    self.chmHistoryDataModel.dataChanged.connect(lambda newData: self.chmTableView.update_table(newData))
    
    #self.ui.chmSearchBtn1.clicked.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))
    #self.ui.chmSearchLine1.returnPressed.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))
    
    #self.ui.icpUploadBtn.clicked.connect(lambda: on_icpUploadBtn_clicked(self.tempDB))
    
    # Connect basic signals 
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))
 
    self.ui.ChmTestCancelBtn.clicked.connect(lambda: self.ui.chmEditWidget.setVisible(False))    


def createActionWidget(self, row, table): 

    deleteBtn = QPushButton("Delete")
    editBtn = QPushButton('Edit')

    # Connect the signals
    deleteBtn.clicked.connect(lambda: chmTableDeleteRow(self, row, table));
    editBtn.clicked.connect(lambda: chmTableEditRow(self, row, table))

    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editBtn)
    button_layout.addWidget(deleteBtn)
    button_layout.setContentsMargins(5, 0, 0, 0)
    button_layout.setAlignment(Qt.AlignLeft)
    
    return button_widget

def chmTableDeleteRow(self, row, table): 
    logger.info('Entering chmTableDeleteRow with parameters: row: {row}, table: {table}')
    
    sampleNum = table.item(row, 0).text()
    testsName = table.item(row, 1).text()
    logger.debug(f'Sample Num: {sampleNum}, Tests Name: {testsName}')
    
    result = deleteBox(self, 'Delete Item?', 'This will delete this from the database. You cannot undo this action!', 'action')
    if(result): 
        print(result)
        table.removeRow(row)
    #deleteChmData(self.db, sampleNum, testsName)
    #TODO: have the delete implemented from the SQL 
    checkExistsQuery = 'SELECT 1 FROM chemTestsData WHERE sampleNum = ? AND testNum = ? AND jobNum = ?' 
    
def delete_chm_sample_tests_data(self): 
    checkExistsQuery = 'SELECT 1 FROM chemTestsData WHERE sampleNum = ? AND testNum = ? AND jobNum = ?'  
    

def chmTableEditRow(self, row, table): 
    sampleNum = table.item(row, 0).text()
    testsName = table.item(row, 1).text() 
    
    print(f'EDIT ROW: {row}')
    
    table.selectRow(row)
    self.editWidget.setVisible(True)

#******************************************************************
#    Chemistry Database Classes   
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
        query = 'SELECT COUNT(*) FROM chemTestsData' 

        totalPages = self.db.query(query)[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));  
        
        return totalPages
    
    def get_total_rows_filter(self, text): 
        query = f'SELECT COUNT(*) FROM chemTestsData WHERE sampleNum LIKE ?'
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
        #TODO: redo this and add the creation date 
        machineDataQuery = 'SELECT jobNum, sampleNum, testNum, testValue, standardValue, unitValue FROM chemTestsData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
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
            
            inquiry = 'SELECT jobNum, sampleNum, testNum, testValue, standardValue, unitValue FROM chemTestsData WHERE jobNum LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?' 
            self.filtered_data = list(self.db.query(inquiry,('%' + jobNum + '%', self.total_rows, offSet)))
            
            if(self.filtered_data): 
                self.dataChanged.emit(self.filtered_data)
                return self.filtered_data
            else: 
                return None; 
    
    def set_page(self, page_number): 
        self.current_page = page_number 
        print(f'Changed Page to {self.current_page} of {self.total_pages}')
        # offset will be updated
        self.fetch_data()
        
    def set_rows(self, index): 
        valid_rows = {0: 100, 1: 200, 2:300}

        if(index in valid_rows): 
            self.total_rows = valid_rows[index]
            self.fetch_data()


class DatabaseTableView(): 
    
    footerAction = pyqtSignal(int)
    
    def __init__(self, database, table, layout, dataModel, editWidgetSection): 
        self.db = database 
        self.table = table
        self.data_model = dataModel
        self.layout = layout
        self.editWidget = editWidgetSection 
    
        # Footer Widget setup 
        self.footerWidget = TableFooterWidget() 
        self.layout.addWidget(self.footerWidget)   
        
        # Populate the table and footer 
        self.init_table()
        self.init_footer()

        self.footerWidget.nextBtn.clicked.connect(self.handle_next_page)
        self.footerWidget.prevBtn.clicked.connect(self.handle_prev_page)
        self.footerWidget.QSpinBox.valueChanged.connect(lambda newValue: self.handle_spinBox_change(newValue))
        self.footerWidget.QComboBox.currentIndexChanged.connect(lambda newIndex: self.handle_row_filter_change(newIndex))
            
    def init_table(self): 
        # Define table columns
        
        column_headers = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Standard Value', 'Unit Value', 'Actions']
        
        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.horizontalHeader().setStretchLastSection(True) 
       
        # Show the vertical rows  
        self.table.verticalHeader().setVisible(True)
                
        # Disable Editing of the table 
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        smallColWidth = 140
        medColWidth = 240 

        # Set the width of the tables 
        self.table.setColumnWidth(0, smallColWidth)
        self.table.setColumnWidth(1, smallColWidth)
        self.table.setColumnWidth(2, medColWidth)
        self.table.setColumnWidth(3, smallColWidth)
        self.table.setColumnWidth(4, smallColWidth)
        self.table.setColumnWidth(5, smallColWidth)

        # Set the last column to stretch
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
                
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
            print(f'Row: {row}, Data: {data}')

            #loops thought items in the order sql requested 
            self.table.setRowHeight(row, TABLE_ROW_HEIGHT)
            
            jobNum = data[0] 
            sampleNum = data[1]
            testNum = data[2]
            testVal = data[3]
            standardVal = data[4]
            unitVal = data[5]
            
            for col in range(len(data)): 
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(data[col]))
                item.setTextAlignment(Qt.AlignHCenter)
                            
                # Get the Job Name 
                if(col == 2): 
                    convert_data = str(data[col]) 
                    testName = getTestsName(self.db, convert_data)
         
                    if(testName): 
                        item = QTableWidgetItem(testName[0][0])
                        #item.setTextAlignment(Qt.AlignHCenter)
                        item.setTextAlignment(Qt.AlignCenter)       
                
                self.table.setItem(row ,col ,item) 
                

            actionRow = 6 
            actionWidget = createActionWidget(self, row, self.table)
            self.table.setCellWidget(row, actionRow, actionWidget)

            
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
            msgBox = QMessageBox()  
            msgBox.setText("No Search Results");
            msgBox.setInformativeText("No search results for given job number");
            msgBox.setStandardButtons(QMessageBox.Ok);
            x = msgBox.exec_()  
            
    
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
    

def chmOpenButton(database, sampleNum, machineType): 
    print(f'Sample: {sampleNum} Machine: {machineType}')
    
    
    #dialog = viewIcpDataDialog(database, sampleNum, machineType) 
    #dialog.exec()

