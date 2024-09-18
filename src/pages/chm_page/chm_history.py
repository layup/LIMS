
from base_logger import logger
import math 

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import (
    QHeaderView, QMessageBox, QPushButton, QWidget, QHBoxLayout, QAbstractItemView, 
    QTableWidget, QTableWidgetItem,QLineEdit 
)
from modules.dbFunctions import getTestsName
from modules.constants import  TABLE_ROW_HEIGHT, TABLE_COL_SMALL, TABLE_COL_MED
from modules.widgets.dialogs import deleteBox
from modules.widgets.TableFooterWidget import TableFooterWidget
from modules.widgets.SideEditWidget import SideEditWidget

#******************************************************************
#    Chemistry Database Section 
#****************************************************************** 
    
def chm_database_setup(self): 
    print('[FUNCTION]: icp_history_setup(self)')
     
    # Define the icp history model and table view 
    self.chmHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.chmTableView = DatabaseTableView(self.tempDB, self.ui.chmInputTable, self.ui.chmDatabaseLayout, self.chmHistoryDataModel, self.ui.chmEditWidget) 

    self.chmTableView.dialogAction.connect(lambda row, new_data: chmTestsSaveProcess(self, row, new_data)); 

    # update footer (buttons, page change, filter update) -> update data 
    # update search -> update data and footer 
    # update data -> update table 
    self.chmHistoryDataModel.dataChanged.connect(lambda newData: self.chmTableView.update_table(newData))
    
    # Connect Signals
    self.ui.chmSearchBtn1.clicked.connect(lambda: self.chmTableView.handle_search_text(self.ui.chmSearchLine1.text()))
    self.ui.chmSearchLine1.returnPressed.connect(lambda: self.chmTableView.handle_search_text(self.ui.chmSearchLine1.text()))
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))
    
    # Edit Panel Signals
    #self.ui.ChmTestCancelBtn.clicked.connect(lambda: chmTestsCancelClicked(self))    
    #self.ui.ChmTestSaveBtn.clicked.connect(lambda: chmTestsSaveClicked(self));
    # Import/Export Signals 
    # Export - export all/page 

def sideEditSetup(self): 
    # Side Edit Widget Setup

    # Get the list of parameters and allowed unit types
    self.ui.sideEditWidget2 = SideEditWidget() 
    
    self.ui.sideEditLayout.addWidget(self.ui.sideEditWidget1) #only valid for layouts
    self.ui.sideEditWidget2.setVisible(False)

    parameterType, unitType = getParameterAndUnitTypes(self.tempDB)
    self.ui.sideEditWidget2.set_drop_down(parameterType, unitType) 
    self.ui.sideEditWidget2.set_combo_disabled(True)
    
    #self.ui.sideEditWidget2.cancel_clicked.connect(lambda: sideEditCancelBtnClicked(self))
    #self.ui.sideEditWidget2.cancelBtn.clicked.connect(lambda: sideEditCancelBtnClicked(self))
    #self.ui.sideEditWidget2.save_clicked.connect(lambda tests_info, tree_item: sideEditSaveBtnClicked(self, tests_info, tree_item))



def createActionWidget(self, row): 
    deleteBtn = QPushButton("Delete")
    editBtn = QPushButton('Edit')

    deleteBtn.clicked.connect(lambda: chmTableDeleteRow(self, row));
    editBtn.clicked.connect(lambda: chmTableEditRow(self, row))
    
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editBtn)
    button_layout.addWidget(deleteBtn)
    button_layout.setContentsMargins(5, 0, 0, 0)
    button_layout.setAlignment(Qt.AlignLeft)

    # Connect the signals
    if not hasattr(self, "cancel_button_connected"):
        cancel_button = self.editWidget.findChild(QPushButton, 'ChmTestCancelBtn')
        if(cancel_button): 
            cancel_button.clicked.connect(lambda: chmTestsCancelClicked(self.editWidget))
            self.cancel_button_connected = True

    '''  
    if not hasattr(self, "save_button_connected"):
        save_button = self.editWidget.findChild(QPushButton, 'ChmTestSaveBtn')
        if(save_button): 
            save_button.clicked.disconnect()
            save_button.clicked.connect(lambda: chmTestsSaveClicked(self, row)) 
            self.save_button_connected = True
    '''
        
    return button_widget

def chmTableDeleteRow(self, row): 
    logger.info('Entering chmTableDeleteRow with parameters: row: {row}')
    
    jobNum    = self.table.item(row, 0).text()
    sampleNum = self.table.item(row, 1).text()
    testsName = self.table.item(row, 2).text()
    
    logger.debug(f'Job Num: {jobNum}, Sample Num: {sampleNum}, Tests Name: {testsName}')
    
    result = deleteBox(self, 'Delete Item?', 'This will delete this from the database. You cannot undo this action!', 'action')
    
    if(result): 
        print(result)
        self.table.removeRow(row)
        
        #deleteChmData(self.db, sampleNum, testsName)
        
        #TODO: have the delete implemented from the SQL 
        testNumQuery = 'SELECT testNum FROM Tests WHERE testName = ?'
        testNum = self.db.query(testNumQuery, (testsName, ))
        
        if(testNum): 
            testNum = testNum[0][0]

            logger.debug(f'testNum: {testNum}')
            
            checkExistsQuery = 'SELECT 1 FROM chemTestsData WHERE sampleNum = ? AND testNum = ? AND jobNum = ?' 
            self.db.execute(checkExistsQuery, (sampleNum, testNum, jobNum))
            result = self.db.fetchone()
            logger.debug(f'Result: {result}')
            
            if(result != None): 
                pass; 

def chmTableEditRow(self, row): 
    logger.info(f'Entering chmTableEditRow with parameter: row: {row}')
    clearLineEdits(self.editWidget)

    # highlight the current row in the table 
    self.table.selectRow(row)
    self.editWidget.setVisible(True)    
    
    save_button = self.editWidget.findChild(QPushButton, 'ChmTestSaveBtn')
    if(save_button): 
        if save_button.receivers(save_button.clicked):  # Check if there are connections
            save_button.clicked.disconnect()
        save_button.clicked.connect(lambda: chmTestsSaveClicked(self, row)) 
        
    #TODO: have a drop down for the chmTestsNameLine list
    sideWidgetNames = ['chmJobNumLine', 'chmSampleNumLine', 'chmTestsNameLine', 'chmTestsValueLine', 'chmStandardValueLine', 'chmUnitValueLine']

    for col in range(self.table.columnCount() -2): 
        value = self.table.item(row, col).text()
        self.editWidget.findChild(QWidget, sideWidgetNames[col]).setText(value) 
    
@pyqtSlot() 
def chmTestsCancelClicked(widget): 
    clearLineEdits(widget) 
    widget.setVisible(False)
     
@pyqtSlot()
def chmTestsSaveClicked(self, row):
    print('Save Row: ', row)

    # Saving the default row data to be compared with later 
    original_data = [self.table.item(row, col).text() for col in range(self.table.columnCount() - 1)]
        
    # Need to edit the row values and save at the same time
    new_data = getLineEditText(self.editWidget)
    
    # Compare the original_data and the new_data  
    differences = [1 if old_value != new_value else 0 for old_value, new_value in zip(original_data, new_data)]
    
    print(f'Difference: {differences}')

    if(sum(differences) > 0): 
        # Emit a signal to display a dialog
        self.dialogAction.emit(row, new_data)


def chmTestsSaveProcess(self, row, new_data): 
    print('slot function')
    print(f'Row: {row}, New Data: {new_data}')
    
    
    #TODO: check if the new data is valid 
    
    save_result = save_confirmation_dialog(self)
    
    if(save_result): 
        # Update the table row
        updateRowValues(self.ui.chmInputTable, row, new_data)
        
        # Save update to database

 
    
def updateRowValues(table, row, new_data): 
    for col in range(table.columnCount() -2): 
        table.item(row, col).setText(new_data[col])

        
#******************************************************************
#    Dialog 
#****************************************************************** 
    
def save_confirmation_dialog(self):
    reply = QMessageBox.question(self,
        "Confirmation",
        "Are you sure you want to save?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No  # Default button
    )
    if reply == QMessageBox.Yes:
        # Perform save action
        print("Saving...")
        return True
    else:
        print("Save canceled.")
        return False; 



#******************************************************************
#    Helper Functions 
#****************************************************************** 

def clearLineEdits(widget): 
    lineEdits = widget.findChildren(QLineEdit)

    for line in lineEdits: 
        line.clear()    
    
    for child in widget.children(): 
        if(isinstance(child, QLineEdit)): 
            clearLineEdits(child)

def getLineEditText(widget): 
    lineEdits = widget.findChildren(QLineEdit)

    text_list = []
    for line in lineEdits: 
        text_list.append(line.text())
    
    for child in widget.children(): 
        if(isinstance(child, QLineEdit)): 
            text_list.extend(getLineEditText(child))

    return text_list


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
        return self.data
    
    def get_total_rows(self): 
        query = 'SELECT COUNT(*) FROM chemTestsData' 

        totalPages = self.db.query(query)[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));  
        
        return totalPages
    
    def get_total_rows_filter(self, text: str) -> int: 
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

    def fetch_data(self) -> list:
        #TODO: redo this and add the creation date 
        machineDataQuery = 'SELECT jobNum, sampleNum, testNum, testValue, standardValue, unitValue, creationDate FROM chemTestsData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
        offSet = (self.current_page -1) * self.total_rows
        
        self.db.execute(machineDataQuery, (self.total_rows, offSet,))  # Pass offset as a single value
        self.data = list(self.db.fetchall())
        
        self.dataChanged.emit(self.data)
        return self.data
    
    def set_filter(self, jobNum):
        
        print(f'set_filter: {jobNum}');
        
        self.current_page = 1;     
        
        if(jobNum == ''): 
            # Reset the search to normal 
            self.total_pages = self.get_total_rows()
            return 1, self.fetch_data()
        else:  
            self.total_pages = self.get_total_rows_filter(jobNum)
            offSet = (self.current_page -1) * self.total_rows
            
            inquiry = 'SELECT jobNum, sampleNum, testNum, testValue, standardValue, unitValue, creationDate FROM chemTestsData WHERE jobNum LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?' 
            self.filtered_data = list(self.db.query(inquiry,('%' + jobNum + '%', self.total_rows, offSet)))
            
            if(self.filtered_data): 
                self.dataChanged.emit(self.filtered_data)
                return 2, self.filtered_data
            else: 
                return 0, None
    
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


class DatabaseTableView(QObject): 

    footerAction = pyqtSignal(int)
    dialogAction = pyqtSignal(int, list)
    
    def __init__(self, database, table, layout, dataModel, editWidgetSection): 
        super().__init__()
        self.db = database 
        self.table = table
        self.data_model = dataModel
        self.layout = layout
        self.editWidget = editWidgetSection 
    
        # Footer Widget setup 
        self.footerWidget = TableFooterWidget() 
        self.layout.addWidget(self.footerWidget)   
        
        self.setup_table()
        self.populate_table()
        
        self.setup_footer()

        self.footerWidget.nextBtn.clicked.connect(self.handle_next_page)
        self.footerWidget.prevBtn.clicked.connect(self.handle_prev_page)
        self.footerWidget.QSpinBox.valueChanged.connect(self.handle_spinBox_change)
        self.footerWidget.QComboBox.currentIndexChanged.connect(self.handle_row_filter_change)
            
    def setup_table(self): 
        # Define table columns 
        column_headers = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Standard Value', 'Unit Value', 'Upload Date' , 'Actions']
        
        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.horizontalHeader().setStretchLastSection(True) 
       
        # Show the vertical rows  
        self.table.verticalHeader().setVisible(True)
                
        # Disable Editing of the table 
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set the width of the tables 
        self.table.setColumnWidth(0, TABLE_COL_SMALL)
        self.table.setColumnWidth(1, TABLE_COL_SMALL)
        self.table.setColumnWidth(2, TABLE_COL_MED)
        self.table.setColumnWidth(3, TABLE_COL_SMALL)
        self.table.setColumnWidth(4, TABLE_COL_SMALL)
        self.table.setColumnWidth(5, TABLE_COL_SMALL)
        self.table.setColumnWidth(6, TABLE_COL_SMALL)

        # Set the last column to stretch
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)

    def populate_table(self): 
        # Get the init data to populate table 
        init_data = self.data_model.fetch_data()
        self.update_table(init_data)
        
    def setup_footer(self): 
        self.update_footer() 
                
    def update_table(self, results): 
        logger.info('DatabaseTableView Update Table')

        self.clear_table()
        
        # Bring the vertical scroll bar back to the top 
        self.table.verticalScrollBar().setValue(0)
        
        # Define table rows 
        total_results = len(results) 
        self.table.setRowCount(total_results)  
        
        for row , data in enumerate(results):
            logger.debug(f'Row: {row}, Data: {data}')

            # Set the row height of each item
            self.table.setRowHeight(row, TABLE_ROW_HEIGHT) 
            
            for col in range(len(data)): 
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(data[col]))
                item.setTextAlignment(Qt.AlignCenter)
                            
                # Get the Job Name 
                if(col == 2): 
                    convert_data = str(data[col]) 
                    testName = getTestsName(self.db, convert_data)
         
                    if(testName): 
                        item = QTableWidgetItem(testName[0][0])
                        item.setTextAlignment(Qt.AlignCenter)     
                        
                if(col == 6): 
                    if(data[col] == None): 
                        item.setText('N/A'); 
                
                self.table.setItem(row ,col ,item) 
                
            actionRow = 7 
            actionWidget = createActionWidget(self, row)
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
        status, result = self.data_model.set_filter(text)
        
        if(status == 0): 
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

class SideEditWidget(QWidget): 
    pass; 