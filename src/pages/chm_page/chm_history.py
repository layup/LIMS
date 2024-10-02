
from base_logger import logger
import math 

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt, QAbstractTableModel,Qt, QModelIndex, QVariant, QEvent
from PyQt5.QtWidgets import (
    QHeaderView, QMessageBox, QPushButton, QWidget, QHBoxLayout, QAbstractItemView, 
    QTableWidget, QTableWidgetItem,QLineEdit, QTableView, QStyledItemDelegate
)
from modules.dbFunctions import getTestsName
from modules.constants import  TABLE_ROW_HEIGHT, TABLE_COL_SMALL, TABLE_COL_MED
from modules.utils.chm_utils import getParameterAndUnitTypes, getParameterTypeNum, parameterItem
from modules.widgets.dialogs import deleteBox, saveMessageDialog
from modules.widgets.SideEditWidget import SideEditWidget, hideSideEditWidget
from modules.widgets.TableFooterWidget import TableFooterWidget

#******************************************************************
#    Chemistry Database Section 
#****************************************************************** 
    
def chm_database_setup(self): 
    logger.info('Entering chm_database_setup')

    sideEditSetup2(self)
    
    #Hide the second table that i've been working on
    self.ui.chmTableView.hide()
    
    customTableViewSetup(self)
     
    # Define the icp history model and table view 
    self.chmHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.chmTableView = DatabaseTableView(self.tempDB, self.ui.chmInputTable, self.ui.chmDatabaseLayout, self.chmHistoryDataModel, self.ui.sideEditWidget2) 

    self.chmTableView.dialogAction.connect(lambda row, new_data: chmTestsSaveProcess(self, row, new_data)); 

    # update footer (buttons, page change, filter update) -> update data 
    # update search -> update data and footer 
    # update data -> update table 
    self.chmHistoryDataModel.dataChanged.connect(lambda newData: self.chmTableView.update_table(newData))
    
    # Connect Signals
    self.ui.chmSearchBtn1.clicked.connect(lambda: self.chmTableView.handle_search_text(self.ui.chmSearchLine1.text()))
    self.ui.chmSearchLine1.returnPressed.connect(lambda: self.chmTableView.handle_search_text(self.ui.chmSearchLine1.text()))
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))

    # Table View Setup 
    
def customTableViewSetup(self):
    
    limit, offset = 100, 0 
   
    # get the data and put it in a list    
    testsList = getChemData(self, limit, offset); 

    itemDataList = convertIntoItemDataList(self, testsList)

    # Populating the model with data
    item_data_manager = ItemDataManager()

    # Add the test data to ItemDataManager
    for item_data in itemDataList:
        item_data_manager.add_item(item_data.jobNum, item_data.sampleNum, item_data.testsNum, item_data)

    # Check to see if the items are there 
    print('total items: ', item_data_manager.get_total_items());
    item_data_manager.print_all_items(); 

    # Create the model
    model = CustomTableModel(item_data_manager)
     
    self.ui.chmTableView.setModel(model)
    #self.ui.chmTableView.setSortingEnabled(True)  # Enable sorting

    self.ui.chmTableView.verticalHeader().setHidden(False)
    self.ui.chmTableView.verticalHeader().setVisible(True)    
 
    # set the widths for each column
    self.ui.chmTableView.setColumnWidth(0, 30)
    self.ui.chmTableView.setColumnWidth(1, TABLE_COL_SMALL)
    self.ui.chmTableView.setColumnWidth(2, TABLE_COL_SMALL)
    self.ui.chmTableView.setColumnWidth(3, TABLE_COL_MED)
    self.ui.chmTableView.setColumnWidth(4, TABLE_COL_SMALL)
    self.ui.chmTableView.setColumnWidth(5, TABLE_COL_SMALL)
    self.ui.chmTableView.setColumnWidth(6, TABLE_COL_SMALL)
    self.ui.chmTableView.setColumnWidth(7, TABLE_COL_SMALL)
    self.ui.chmTableView.setColumnWidth(8, TABLE_COL_MED)
    
    # Center the header
    self.ui.chmTableView.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
    self.ui.chmTableView.verticalHeader().setDefaultAlignment(Qt.AlignCenter)


    # Optionally set row heights, selection behavior, etc.
    self.ui.chmTableView.setAlternatingRowColors(True)
    self.ui.chmTableView.setSelectionBehavior(QTableView.SelectRows)
    self.ui.chmTableView.setSelectionMode(QTableView.SingleSelection)

    # Set some styles (optional)
    self.ui.chmTableView.setStyleSheet("QTableView { selection-background-color: #A3C1DA; }")


    # In your main application setup code
    delegate = ButtonDelegate(self.ui.chmTableView)

    # Connect signals to your slot methods
    delegate.edit_clicked.connect(lambda: print('Edit Button'))
    delegate.delete_clicked.connect(lambda: print('Delete button'))

    # Set the delegate for the 8th column
    self.ui.chmTableView.setItemDelegateForColumn(8, delegate)
    self.ui.chmTableView.setColumnHidden(8, False)  # Make sure it's visible


def on_edit_button_clicked(self, row):
    print(f"Edit button clicked for row: {row}")
    # Your edit logic here

def on_delete_button_clicked(self, row):
    print(f"Delete button clicked for row: {row}")
    # Your delete logic here

def getChemData(self, limit, offset):  
    query = 'SELECT jobNum, sampleNum, testNum, testValue, unitValue, standardValue, creationDate FROM chemTestsData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
    
    results = self.tempDB.query(query, (limit, offset,))
    results = list(results) 

    return results 

def convertIntoItemDataList(self, data): 
    item_data_list = []
    
    for item in data:
        
        #TODO: search for the testsName in database 
        testNameSearch = 'temp'
          
        item_data_list.append(ItemData(
            jobNum=item[0], 
            sampleNum=item[1], 
            testsNum=item[2], 
            testsName=testNameSearch, 
            testsVal=item[3], 
            unitVal=item[4], 
            standard=item[5], 
            upload=item[6] 
        ))
         
    return item_data_list


#******************************************************************
#    SideEditWidget Functions
#****************************************************************** 

def sideEditSetup2(self): 
    # Side Edit Widget Setup

    # Get the list of parameters and allowed unit types
    self.ui.sideEditWidget2 = SideEditWidget() 
    self.ui.sideEditWidget2.setVisible(False)
    
    # Add our widget to the correct layout
    self.ui.horizontalLayout_64.addWidget(self.ui.sideEditWidget2) 

    # Set the QComboBox Items
    parameterType, unitType = getParameterAndUnitTypes(self.tempDB)
    self.ui.sideEditWidget2.set_drop_down(parameterType, unitType) 
    self.ui.sideEditWidget2.set_combo_disabled(False)
    
    # Connect signals
    self.ui.sideEditWidget2.cancelBtn.clicked.connect(lambda: hideSideEditWidget(self.ui.sideEditWidget2))
    self.ui.sideEditWidget2.saveBtn.clicked.connect(lambda: sideEditWidgetSaveBtnClicked(self))
     
def sideEditWidgetSaveBtnClicked(self): 
    logger.info(f'Entering sideEditWidgetSaveBtnClicked')   
    row = self.ui.sideEditWidget2.get_item()
    new_data = self.ui.sideEditWidget2.get_data()
    updateTableRowValues(self.ui.chmInputTable, row, new_data)

    # check if any data is different 
    jobName = new_data[0] + '-' + new_data[1]
    result = saveMessageDialog(self, 'Overwrite Data?', f'Are you sure you want overwrite existing data for {jobName}?')

    if(result): 
        # update table info 
        for col in range(len(new_data)):
            item.setText(col, new_data[col])
        
        # update database
        query = 'UPDATE chemTestsData SET testVal = ?, standard = ? WHERE '
        
        
        
#******************************************************************
#    ActionWidget Functions
#****************************************************************** 

def createActionWidget(self, row):
     
    deleteBtn = QPushButton("Delete")
    editBtn = QPushButton('Edit')    
    
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editBtn)
    button_layout.addWidget(deleteBtn)
    button_layout.setContentsMargins(5, 0, 0, 0)
    button_layout.setAlignment(Qt.AlignLeft)

    # Connect signals     
    deleteBtn.clicked.connect(lambda: actionDeleteBtn(self, row ))
    editBtn.clicked.connect(lambda: actionEditBtn(self, row))

    return button_widget

def actionEditBtn(self, row): 
    logger.info(f'Entering actionEditBtn with parameter: row: {row}')

    # Clear the existing data
    self.editWidget.clear_data()

    # highlight the current row in the table 
    self.table.selectRow(row)
    self.editWidget.setVisible(True)    
    
    current_data = []
    
    for col in range(self.table.columnCount() -2): 
        value = self.table.item(row, col).text()
        current_data.append(value)
        
    self.editWidget.set_data(current_data)
    self.editWidget.set_item(row);
    
def actionDeleteBtn(self, row): 
    logger.info(f'Entering actionDeleteBtn with parameter: row: {row}')    

    jobNum    = self.table.item(row, 0).text()
    sampleNum = self.table.item(row, 1).text()
    testsName = self.table.item(row, 2).text()
    
    logger.debug(f'Job Num: {jobNum}, Sample Num: {sampleNum}, Tests Name: {testsName}')

    result = deleteBox(self, 'Delete Item?', 'This will delete this from the database. You cannot undo this action!', 'action')
    
    if(result): 
        print(result)
        
        self.table.removeRow(row)

        #Lazy way or resolving the issue 
        update_buttons(self)
        update_side_edit(self, row)
        
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

def update_buttons(self): 
    # Re-create the delete buttons after a row has been deleted
    for row in range(self.table.rowCount()): 
        actionWidgetCol = 7 
        actionWidget = createActionWidget(self, row)
        self.table.setCellWidget(row, actionWidgetCol, actionWidget)
        
def update_side_edit(self, removed_row): 
    print(f'EDIT ROWS: {removed_row}')
    
    side_edit_row = self.editWidget.get_item()
    
    # Equal the same row as the edit thing
    if(removed_row == side_edit_row): 
        self.editWidget.clear_data()
        self.editWidget.hide()
        
    elif(removed_row <= side_edit_row): 
        self.editWidget.set_item(side_edit_row - 1)

    else: 
        print('Nothing')
            

#******************************************************************
#    Table Functions
#****************************************************************** 

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


def updateTableRowValues(table, row, new_data): 
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
        machineDataQuery = 'SELECT jobNum, sampleNum, testNum, testValue, unitValue, standardValue, creationDate FROM chemTestsData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
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
            
            inquiry = 'SELECT jobNum, sampleNum, testNum, testValue, unitValue, standardValue, creationDate FROM chemTestsData WHERE jobNum LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?' 
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
        column_headers = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Unit Value', 'Standard Value', 'Upload Date' , 'Actions']
        
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
                
            actionWidgetCol = 7 
            actionWidget = createActionWidget(self, row)
            self.table.setCellWidget(row, actionWidgetCol, actionWidget)

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


#******************************************************************
#    Chemistry Database Classes Take 2    
#****************************************************************** 

# 
class ItemData: 
    def __init__(self, jobNum, sampleNum, testsName, testsNum, testsVal, unitVal, standard, upload): 
        self.jobNum = jobNum
        self.sampleNum = sampleNum 
        self.testsName = testsName 
        self.testsNum = testsNum 
        self.testsVal = testsVal 
        self.unitVal = unitVal 
        self.standard = standard 
        self.upload = upload
        
# Focuses on data management, including adding, removing, updating, and retrieving items.
class ItemDataManager:
    def __init__(self):
        self.data_dict = {}

    def add_item(self, jobNum, sampleNum, testsNum, item_data):
        key = (jobNum, sampleNum, testsNum)
        self.data_dict[key] = item_data

    def remove_item(self, jobNum, sampleNum, testsNum):
        key = (jobNum, sampleNum, testsNum)
        if key in self.data_dict:
            del self.data_dict[key]

    def get_item(self, jobNum, sampleNum, testsNum):
        key = (jobNum, sampleNum, testsNum)
        return self.data_dict.get(key, None)

    def update_item(self, jobNum, sampleNum, testsNum, updated_data):
        key = (jobNum, sampleNum, testsNum)
        if key in self.data_dict:
            self.data_dict[key] = updated_data

    def get_all_keys(self): 
        return list(self.data_dict.keys())

    def get_all_items(self):
        return list(self.data_dict.values())

    def get_total_items(self): 
        return len(self.data_dict.values())
    
    def print_all_items(self): 
        logger.info(f'Entering print_all_items')
        
        for i, item in enumerate(self.data_dict.values()): 
            print(f'{i}) {item.jobNum}-{item.sampleNum} {item.upload}')    
            print(f'  - Test Name     : ({item.testsNum}){item.testsName}')
            print(f'  - Test Value    : {item.testsVal} {item.unitVal}')
            print(f'  - Test Standard : {item.standard}')
    
        
# Manages the data displayed in the table, acts as an interface between the data
class CustomTableModel(QAbstractTableModel):
    def __init__(self, item_data_manager, parent=None):
        super().__init__(parent)
        self.item_data_manager = item_data_manager
        self.headers = ['', 'Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Standard Value', 'Unit Value', 'Upload Date', 'Actions']

    def init_table_setup(self): 
        pass; 

    def rowCount(self, parent=None):
        return self.item_data_manager.get_total_items()

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            # QVariant is a class that can hold a variety of data types in a single object, 
            # allowing for flexibility in handling different types of data
            return QVariant()

        if role == Qt.DisplayRole:
            item_data = self.item_data_manager.get_all_items()[index.row()]
            column = index.column()

            if column == 0: 
                return int(index.row())
            elif column == 1:
                return item_data.jobNum
            elif column == 2:
                return item_data.sampleNum
            elif column == 3:
                return item_data.testsName
            elif column == 4:
                return item_data.testsVal
            elif column == 5:
                return item_data.standard
            elif column == 6:
                return item_data.unitVal
            elif column == 7:
                return item_data.upload
            elif column == 8: 
                #return '' #placeholder 
                return QVariant()  # Return QVariant for button column

            
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter


        elif role == Qt.UserRole:  # Use UserRole for the action widget
            return self.createActionWidget(index.row())

        return QVariant()
    
    def createActionWidget(self, row):
        deleteBtn = QPushButton("Delete")
        editBtn = QPushButton('Edit')    

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addWidget(editBtn)
        button_layout.addWidget(deleteBtn)
        button_layout.setContentsMargins(5, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignLeft)

        # Connect signals     
        deleteBtn.clicked.connect(lambda: self.actionDeleteBtn(row))
        editBtn.clicked.connect(lambda: self.actionEditBtn(row))

        return button_widget

    def actionDeleteBtn(self, row):
        print(f"Delete button clicked for row {row}")

    def actionEditBtn(self, row):
        print(f"Edit button clicked for row {row}")

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]
        return QVariant()

    def sort(self, column, order):
        """Sort the table based on a column."""
        if column == 6:  # Upload date
            self.item_data_manager.data_dict = dict(sorted(
                self.item_data_manager.data_dict.items(),
                key=lambda x: x[1].upload,
                reverse=(order == Qt.DescendingOrder)
            ))
        self.layoutChanged.emit()


class ButtonDelegate(QStyledItemDelegate):
    edit_clicked = pyqtSignal(int)  # Signal for edit action
    delete_clicked = pyqtSignal(int)  # Signal for delete action

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == 8:  # Assuming buttons are in the 8th column
            button_widget = QWidget(parent)
            layout = QHBoxLayout(button_widget)
            
            edit_btn = QPushButton("Edit", button_widget)
            delete_btn = QPushButton("Delete", button_widget)

            layout.addWidget(edit_btn)
            layout.addWidget(delete_btn)
            layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn.clicked.connect(lambda: self.editClicked(index.row()))
            delete_btn.clicked.connect(lambda: self.deleteClicked(index.row()))

            return button_widget
        return super().createEditor(parent, option, index)

    # Signals for button clicks
    editClicked = pyqtSignal(int)
    deleteClicked = pyqtSignal(int)

    def editClicked(self, row):
        # Handle edit action
        print(f"Edit clicked for row {row}")

    def deleteClicked(self, row):
        # Handle delete action
        print(f"Delete clicked for row {row}")


    def paint(self, painter, option, index):
        # Leave this empty for now; we will handle button drawing in the sizeHint
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        # Set size for the button area
        return QSize(100, 30)  # Adjust as needed

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if index.column() == 8:  # Assuming column 8 has the buttons
                if event.button() == Qt.LeftButton:
                    # Emit the signal for edit or delete action
                    self.edit_clicked.emit(index.row())  # Emit edit signal
                    self.delete_clicked.emit(index.row())  # Emit delete signal

        return super().editorEvent(event, model, option, index)
