
import math 

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QWidgetItem, QTreeWidgetItem
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator



from modules.dbFunctions import (getAllChmTestsData, getAllChmTestsInfo, getAllChmTestsInfo2, getChmTestData, 
    addChmTestData, getTestsName, getAllParameters, getParameterNum, getChmReportFooter, addChmReportFooter )
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *

#******************************************************************
#    Chemistry Setup 
#****************************************************************** 

def chemistrySetup(self): 
    chmTestsInfoSetup(self)
    chmInputSectionSetup(self)
    #chmDatabaseSetup(self)
    chm_database_setup(self)
    chm_report_setup(self)

    # Connect the chem tab widget change function    
    self.ui.chmTabWidget.currentChanged.connect(lambda index: on_chmTabWidget_currentChanged(self, index))
    
#******************************************************************
#    Chemistry General Functions  
#****************************************************************** 

def on_chmTabWidget_currentChanged(self, index): 
    #TODO: reload in the data for all the sections (new data)? 
    print(f'CHM TAB CHANGE INDEX {index}')
    
    if(index == 0): # Database 
        self.ui.headerTitle.setText('Chemistry Tests Database'); 
        self.ui.headerDesc.setText(''); 
        self.ui.editContainerWidget.setVisible(False)

        
    if(index == 1): # Input Data 
        self.ui.headerTitle.setText('Chemistry Data Entry'); 
        self.ui.headerDesc.setText(''); 
        
    if(index == 2): # Test Info  
        self.ui.headerTitle.setText('Chemistry Tests Information'); 
        self.ui.headerDesc.setText(''); 
        #totalTests = getChmTotalTests(self.db) 
        #self.ui.gcmsSubTitleLabel.setText('Total Tests: ' + str(totalTests))

    if(index == 3): # Report Info 
        self.ui.headerTitle.setText('Chemistry Reports Information')
        self.ui.headerDesc.setText('Total Reports: ') 

        
#******************************************************************
#    Chemistry Database Section 
#****************************************************************** 
    
def chm_database_setup(self): 
    print('[FUNCTION]: icp_history_setup(self)')
     
    # Define the icp history model and table view 
    self.chmHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.chmTableView = DatabaseTableView(self.tempDB, self.ui.chmInputTable, self.ui.chmDatabaseLayout, self.chmHistoryDataModel) 

    # update footer (buttons, page change, filter update) -> update data 
    # update search -> update data and footer 
    # update data -> update table 
    self.chmHistoryDataModel.dataChanged.connect(lambda newData: self.chmTableView.update_table(newData))
    
    #self.ui.chmSearchBtn1.clicked.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))
    #self.ui.chmSearchLine1.returnPressed.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))
    
    #self.ui.icpUploadBtn.clicked.connect(lambda: on_icpUploadBtn_clicked(self.tempDB))
    
    # Connect basic signals 
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))


def createActionWidget(self, row, table): 

    #TODO: add the edit button 
    deleteBtn = QPushButton("Delete")
    editBtn = QPushButton('Edit')

    # Connect the signals
    deleteBtn.clicked.connect(lambda _, row=row: chmTableDeleteRow(self, row));
    editBtn.clicked.connect(lambda _, row=row: chmTableEditRow(self, row, table))

    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editBtn)
    button_layout.addWidget(deleteBtn)
    button_layout.setContentsMargins(5, 0, 0, 0)
    button_layout.setAlignment(Qt.AlignLeft)
    
    return button_widget

def chmTableDeleteRow(self, row): 
    print(f'[FUNCTION]: chmTableDeleteRow, row to delete {row}')
    
    sampleNum = self.ui.chmInputTable.item(row, 0).text()
    testsName = self.ui.chmInputTable.item(row, 1).text()
    print(f'Sample Num: {sampleNum}, Tests Name: {testsName}')
    
    result = deleteBox(self, 'Delete Item?', 'This will delete this from the database. You cannot undo this action!', 'action')
    if(result): 
        print(result)
        self.ui.chmInputTable.removeRow(row)
    #deleteChmData(self.db, sampleNum, testsName)
    #TODO: have the delete implmented from the SQL 
    

def chmTableEditRow(self, row, table): 
    sampleNum = table.item(row, 0).text()
    testsName = table.item(row, 1).text() 
    
    print(f'EDIT ROW: {row}')
    
    table.selectRow(row)
    #self.ui.editContainerWidget.setVisible(True)
    
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
            
            inquery = 'SELECT jobNum, sampleNum, testNum, testValue, standardValue, unitValue FROM chemTestsData WHERE jobNum LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?' 
            self.filtered_data = list(self.db.query(inquery,('%' + jobNum + '%', self.total_rows, offSet)))
            
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
    
    def __init__(self, database, table, layout, dataModel): 
        self.db = database 
        self.table = table
        self.data_model = dataModel
        self.layout = layout 
    
        # Footer Widget setup 
        self.footerWidget = MyFooterWidget() 
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

            #loops throught items in the order sql requested 
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
            actionWidget = createActionWidget(self, actionRow, self.table)
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

class MyFooterWidget(QWidget): 
    def __init__(self, parent=None):
        super().__init__(parent)
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'tableFooterWidget.ui')
            
        self.ui = loadUi(file_path, self)  # Pass 'self' as parent
        
    def load_data(self, current_page, total_rows, total_pages): 
        self.current_page = current_page
        self.total_rows = total_rows
        self.total_pages = total_pages
        
        # Update the pages 
        self.QSpinBox.setValue(current_page)
        self.QSpinBox.setMaximum(total_pages)
        self.pageLabel.setText(f'of {total_pages}')
    
        valid_rows = {100: 0, 200:1, 300:2}
        
        if(total_rows in valid_rows): 
            self.QComboBox.setCurrentIndex(valid_rows[total_rows])


#******************************************************************
#    Chemisty Input Data
#****************************************************************** 

#TODO: takes in the values from the 
#TODO: duplication error

def chmInputSectionSetup(self): 
    print('[FUNCTION]:chmInputSectionSetup(self)')
    chmClearEnteredTestsData(self, True)
    
    formatQLineEdits(self)
    
    populateNewEntry(self) 
    
    #TODO: rename this 
    # Input Data Page Signals
    #self.ui.gcmsTests.activated.connect(lambda index: on_gcmsTests_activated(self, index))
    self.ui.chmProceedBtn.clicked.connect(lambda: on_chmProceedBtn_clicked(self))
    self.ui.chmInputClearBtn.clicked.connect(lambda: on_chmClearBtn_clicked(self))
            
def formatQLineEdits(self): 
    # allow only float values 
    float_validator = QDoubleValidator()
    float_validator.setDecimals(10)
    # allow only int values 
    int_validator = QIntValidator()
    # Set validators 
    self.ui.gcmsStandardVal.setValidator(float_validator)
    self.ui.gcmsTestsJobNum.setValidator(int_validator)
    self.ui.gcmsTestsSample.setValidator(int_validator)
    self.ui.gcmsTestsVal.setValidator(float_validator)
    # set the limit to characeters allowed in line edit 
    self.ui.gcmsStandardVal.setMaxLength(20)
    self.ui.gcmsTestsJobNum.setMaxLength(6)
    self.ui.gcmsTestsSample.setMaxLength(6)
    

def populateNewEntry(self): 
    print('[FUNCTION]: populateNewEntry(self)')
    
    self.ui.gcmsTests.clear() 
    self.ui.gcmsUnitVal.clear()
    
    # TODO: move this to another function
    # TODO: could also be using the testManager from TestsInfo
    query = 'SELECT testNum, testName FROM Tests WHERE testName NOT LIKE "%ICP%" AND type = "C" ORDER BY testName ASC'
    results = self.tempDB.query(query)

    chmClearActiveValues(self)
    
    #TODO: find out what the others are (add to the settings section)
    parameterTypes = [parameterItem(item[0], item[1]) for item in results]
    parameterTypes.insert(0, '')
    
    unitTypes = ['', 'TCU', 'ug/L', 'mg/g']    
    
    for item in parameterTypes:
        if isinstance(item, parameterItem):
            self.ui.gcmsTests.addItem(item.testName, userData=item)
        else: 
            self.ui.gcmsTests.addItem('')

    #self.ui.gcmsTests.addItems(parameterTypes)
    self.ui.gcmsUnitVal.addItems(unitTypes)

def getParameterTypeNum(comboBox): 
    
    index = comboBox.currentIndex()
    if index >= 0:
        item = comboBox.itemData(index)
        if isinstance(item, parameterItem):
            return item.testNum
    return None
    
            
@pyqtSlot()    
def on_chmProceedBtn_clicked(self):            
    print('[SIGNAL]: on_chmProceedBtn_clicked(self)')    
    standards, units, testName = captureNewEntryData(self) 

    errorCheckList = [0,0,0]

    errorCheckList[0] = 0 if (standards != '' and is_real_number(standards)) else 1; 
    errorCheckList[1] = 0 if units != '' else 1; 
    errorCheckList[2] = 0 if testName != '' else 1; 
    
    if(sum(errorCheckList) == 0):
        dataEntryWidgetEnabler(self, True)
        self.ui.gcmsStandardValShow.setText(standards)
        self.ui.gcmsUnitValShow.setText(units)
        self.ui.gcmsTestsShow.setText(testName)  
    else: 
        NewEntryErrorDisplay(self, errorCheckList)

def on_chmClearBtn_clicked(self): 
    chmClearEnteredTestsData(self, False)

    populateNewEntry(self)
     

def NewEntryErrorDisplay(self, errorCheckList): 
    errorTitle = 'Cannot Proceed with CHM Process'
    errorMsg = ''
    
    if(errorCheckList[0] == 1): 
        errorMsg += 'Please Enter a Valid Standard Number\n'
    if(errorCheckList[1] == 1): 
        errorMsg += 'Please Select a Unit\n'
    if(errorCheckList[2] == 1): 
        errorMsg += 'Please Select a Tests\n'
        
    showErrorDialog(self, errorTitle, errorMsg)

def captureNewEntryData(self): 
    standards   = self.ui.gcmsStandardVal.text().strip()
    units       = self.ui.gcmsUnitVal.currentText()
    testName    = self.ui.gcmsTests.currentText()
    
    return standards, units, testName 

def captureEnteredValues(self): 
    jobNum     = self.ui.gcmsTestsJobNum.text().strip()
    sampleNum   = self.ui.gcmsTestsSample.text().strip()
    sampleVal   = self.ui.gcmsTestsVal.text().strip()
    
    return jobNum, sampleNum, sampleVal 
    
        
@pyqtSlot()   
def on_chmSampleDataAdd_clicked(self): 
    print('[FUNCTION]: chmAddTestsBtn clicked')
    
    standards, units, testName = captureNewEntryData(self) 
    jobNum, sampleNum, sampleVal = captureEnteredValues(self)
    testNum = getParameterTypeNum(self.ui.gcmsTests) 
    
    errorCheckList = [0,0,0]
    
    errorCheckList[0] = 0 if (jobNum != '' and is_real_number(jobNum)) else 1; 
    errorCheckList[1] = 0 if (sampleNum != '' and is_real_number(sampleNum)) else 1; 
    errorCheckList[2] = 0 if sampleVal != '' else 1; 
            
    print(f'Input Data Info: {jobNum}-{sampleNum}: {sampleVal}')
            
    if(sum(errorCheckList) == 0): 
        inputTree = self.ui.inputDataTree
        
        existingDataCheck = getChmTestData(self.tempDB, sampleNum, jobNum)
        print('existing_data: ', existingDataCheck)
        
        if(existingDataCheck): 
            response = duplicateSampleOverrideDisplay(sampleNum)

            if(response == QMessageBox.Yes): 
               
                addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum)
                 
                matchingItem = checkMatchingTreeItems(inputTree, sampleNum)
                if not matchingItem: 
                    addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards, jobNum)
                else: 
                    pass; 
                
                chmClearSampleJob(self) 

            if(response == QMessageBox.No):
                chmClearSampleJob(self) 
                
            if(response == QMessageBox.Cancel):
                pass 
            
        else: 
            addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum)
            addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards, jobNum)
            chmClearSampleJob(self)  
    else: 
        addingSampleDataErrorDisplay(self, errorCheckList)


def duplicateSampleOverrideDisplay(sampleNum):
    print('[DIALOG]: duplicateSampleOverrideDisplay(sampleNum)')
    msgBox = QMessageBox()  
    msgBox.setText("Duplicate Sample");
    duplicateMsg = "Would you like to overwrite existing sample " + str(sampleNum) + " ?"
    msgBox.setInformativeText(duplicateMsg);
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Yes);
    return msgBox.exec_()

def addingSampleDataErrorDisplay(self, errorList): 
    errorTitle = 'Cannot add Tests '
    errorMsg = ''
    
    if(errorList[0] == 1): 
        errorMsg += 'Please Enter a Valid Job Number\n'

    if(errorList[1] == 1): 
        errorMsg += 'Please Enter a Valid Sample Number\n'
        
    if(errorList[2] == 1): 
        errorMsg += 'Please Enter a Valid Sample Value \n'
    
    showErrorDialog(self, errorTitle, errorMsg)
    
        
def checkMatchingTreeItems(treeWidget, targetText):
    # Iterate through the top-level items
    for index in range(treeWidget.topLevelItemCount()):
        item = treeWidget.topLevelItem(index)
        if item.text(0) == targetText:  # Change 0 to the desired column index
            return item 

    return None

def addInputTreeItem(treeWidget, sampleNum, testName, sampleVal, units, standards, jobNum): 
    print('[FUNCTION]: addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards)')
    topItem = QTreeWidgetItem(treeWidget)  
    
    topItem.setText(0, jobNum)
    topItem.setText(1, sampleNum)           
    topItem.setText(2, testName)
    topItem.setText(3, sampleVal)
    topItem.setText(4, units)
    topItem.setText(5, standards)
    
    row_index = treeWidget.indexOfTopLevelItem(topItem)
    actionWidget = createTreeActionWidget(treeWidget, row_index)
    treeWidget.setItemWidget(topItem, 6, actionWidget)
    
def createTreeActionWidget(treeWidget, row): 

    #TODO: add the edit button 
    deleteBtn = QPushButton("Delete")
    editbtn = QPushButton('Edit')

    # Connect the signals
    deleteBtn.clicked.connect(lambda _, tree=treeWidget, row=row: chmTreeDeleteRow(tree, row));
    editbtn.clicked.connect(lambda _, tree=treeWidget, row=row: chmTreeEditRow(tree, row))

    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editbtn)
    button_layout.addWidget(deleteBtn)
    button_layout.setContentsMargins(5, 0, 0, 0)
    button_layout.setAlignment(Qt.AlignLeft)
    
    return button_widget

def chmTreeDeleteRow(treeWidget, row): 
    print(f'Delete Row: ', row)
    
    parent_item = treeWidget.invisibleRootItem()  # Assuming top-level items
    parent_item.takeChild(row)

def chmTreeEditRow(treeWidget, row): 
    print(f'Edit Row: ', row)
     
    item = treeWidget.topLevelItem(row)
    if item:
        item.setFlags(item.flags() | Qt.ItemIsEditable)

    
def dataEntryWidgetEnabler(self, status): 
    print('[FUNCTION]: dataEntryWidgetEnabler(self, status)')
    if(status): 
        self.ui.newEntryWidget.setEnabled(False)
        self.ui.chmActionWidget.setEnabled(True)
        self.ui.chmTestsValueWidget.setEnabled(True)
    else: 
        self.ui.newEntryWidget.setEnabled(True)
        self.ui.chmActionWidget.setEnabled(False)
        self.ui.chmTestsValueWidget.setEnabled(False)


def chmClearSampleJob(self): 
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear() 

        
def chmClearActiveValues(self): 
    self.ui.gcmsTestsShow.clear()
    self.ui.gcmsUnitValShow.clear()
    self.ui.gcmsStandardValShow.clear()
    
def chmClearNewEntry(self): 

    self.ui.gcmsTests.setCurrentIndex(1)
    self.ui.gcmsUnitVal.setCurrentIndex(1)
    

    # Clear the standards
    self.ui.gcmsStandardVal.clear()
       
def chmClearEnteredTestsData(self, clearTable=False): 
    dataEntryWidgetEnabler(self, False) 
    
    chmClearNewEntry(self) 
    chmClearActiveValues(self) 
    
    # Clear Enter values Section 
    self.ui.gcmsTestsJobNum.clear()
    chmClearSampleJob(self) 
    
    if(clearTable):  
        self.ui.inputDataTree.clear()

#******************************************************************
#    Chemistry Input Data Classes 
#*****************************************************************

class parameterItem: 
    def __init__(self,testNum, testName): 
        self.testNum = testNum
        self.testName = testName 

#******************************************************************
#    Chemistry Tests Info 
#*****************************************************************
#TODO: integrate everything into one database 
def chmTestsInfoSetup(self): 
    treeWidget = self.ui.chmTestTree
    
    # Setup the tree headers and columns
    chmSetupTreeColumns(treeWidget)
    
    # Tree Data Manager and Tree UI Handler 
    self.testsModel = TestsDataModel(self.tempDB) 
    self.testsViewer = TestsDataView(treeWidget) 
    
    # Populate the Tests Model and Update the Tests View 
    chmLoadTestsData(self.testsModel, self.testsViewer)
    
    # TODO: Setup search functionality

    #TODO: Connect other signals 
    self.ui.chmTestTree.itemSelectionChanged.connect(lambda: chmTestTreeItemChanged(self))
    self.ui.chmTestSaveBtn.clicked.connect(lambda: chmTestSaveBtnClicked(self))
    self.ui.chmTestCancelBtn.clicked.connect(lambda: chmTestCancelBtnClicked(self))

    #TODO: wtf is this 
    self.ui.chmAddTestsBtn.clicked.connect(lambda: on_chmSampleDataAdd_clicked(self))

def chmSetupTreeColumns(treeWidth): 
    columnHeaders = ['Test #', 'Tests Name', 'Text Name', 'Report Name', 'Recovery Value', 'Unit Type']
    
    treeWidth.setHeaderLabels(columnHeaders)

    #TODO: make this a global variable
    smallCol = 70
    medCol = 200 
    bigCol = 300 
    
    # Set Tree Width 
    treeWidth.setColumnWidth(0, smallCol) 
    treeWidth.setColumnWidth(1, bigCol)
    treeWidth.setColumnWidth(2, medCol)
    treeWidth.setColumnWidth(3, bigCol)
    treeWidth.setColumnWidth(4, 100)
    treeWidth.setColumnWidth(5, smallCol)
    
def chmLoadTestsData(model, view): 
    print('[FUNCTION]: chmLoadTestsData(model, view)')
    tests_data = model.loadTestsData()
    view.populateTree(tests_data)

def chmTestTreeItemChanged(self): 
    print('[SIGNAL]: chmTestTreeItemChanged(self)')    
    loadTestDataInfo(self) 

def chmTestCancelBtnClicked(self): 
    print('[SIGNAL]: chmTestTreeItemChanged(self, testItem)')    
    loadTestDataInfo(self) 

def loadTestDataInfo(self): 
    testData = self.testsViewer.getTreeData()
    
    if(testData): 
        print(testData)
        testNum     = testData[0]
        testName    = testData[1] 
        textName    = testData[2]
        reportName  = testData[3]
        recoveryVal = testData[4]
        unitType    = testData[5]
        
        # Set the header name 
        nameString = f'{testName} ({testNum})'
        self.ui.chmTestsNameHeader.setText(nameString)
        
        self.ui.chmDisplayName.setText(testName)
        self.ui.chmTxtName.setText(textName)
        self.ui.chmDisplayName.setText(reportName)
        self.ui.chmRefValue.setText(recoveryVal)
        self.ui.chmUnitName.setText(unitType)

def chmTestSaveBtnClicked(self): 
    print('[SIGNAL]: chmSaveTestChanges(self)')

    newData = chmGetTestsLineEditValues(self)
    print(f'New Tree Data: {newData}')
    
    if(newData):  
        # Update the tests Model 
        updatedData = self.testsModel.updateTestsData(newData)
        print(updatedData)
        # Update the tests viewer to dispplay the updated Data
        self.testsViewer.updateTreeData(updatedData)


def chmGetTestsLineEditValues(self): 
    print('[FUNCTION]: chmGetTestsLineEditValues(self)')
    # Get values from the TestsViewer object
    testsNum    = self.testsViewer.getTreeValue(0)
    testName    = self.testsViewer.getTreeValue(1)

    # Get values from QLineEdit widgets directly
    textName    = self.ui.chmTxtName.text()
    reportName  = self.ui.chmDisplayName.text()
    recoveryVal = self.ui.chmRefValue.text()
    unitType    = self.ui.chmUnitName.text()
    
    if(testsNum): 
        return [testsNum, testName, textName, reportName, recoveryVal, unitType]  

def chmClearTestsInfo(self): 
    print('[FUNCTION]: chmClearTestsInfo(self)')
    # Reset Title 
    self.ui.chmTestsNameHeader.setText('Tests Name (#)')
    
    # Clear QLineEdits widgets 
    self.ui.chmDisplayName.clear()
    self.ui.chmTxtName.clear()
    self.ui.chmUnitName.clear()
    self.ui.chmRefValue.clear()
    self.ui.chmTestsComment.clear()

#******************************************************************
#    Chemisty Report Info
#****************************************************************** 
def chm_report_setup(self): 
    # Load the init data on the setup
    loadChmReports(self); 
     
    # Connect Report signals 
    self.ui.chmReportList.itemSelectionChanged.connect(lambda: chmReportItemSelected(self))
    self.ui.chmReportCancelBtn.clicked.connect(lambda: on_chmReportCancelBtn_clicked(self))
    self.ui.chmReportSaveBtn.clicked.connect(lambda: on_chmSaveFooterBtn_clicked(self))
    
def loadChmReports(self): 
    parameters = getAllParameters(self.tempDB)    
    parameterNames = [item[1] for item in parameters]    
    self.ui.chmReportList.addItems(parameterNames); 

def chmReportItemSelected(self): 
    selectedReport = self.ui.chmReportList.currentItem() 
    
    if(selectedReport):
        reportName = selectedReport.text()
        reportNum = getParameterNum(self.tempDB, reportName)       
         
        # Set the report Name Label 
        self.ui.chmReportNameLabel.setText(f'[{reportNum}] {reportName.upper()}')

        chmReportLoadComment(self, reportNum)
        
def chmReportLoadComment(self, reportNum): 
    # Clear the Text Edit Widget 
    self.ui.chmFooterComment.clear()
    
    footerComment = getChmReportFooter(self.tempDB, reportNum)
    
    if(footerComment): 
        self.ui.chmFooterComment.setPlainText(footerComment) 

@pyqtSlot()
def on_chmReportCancelBtn_clicked(self): 
    selected_item = self.ui.chmReportList.currentItem() 
    
    if(selected_item): 
        reportName = selected_item.text()
        reportNum = getParameterNum(self.tempDB, reportName)     

        chmReportLoadComment(self, reportNum)
         
@pyqtSlot()
def on_chmSaveFooterBtn_clicked(self): 
    print('Save Footer button Clicked')
    footerComment = self.ui.chmFooterComment.toPlainText()
    selectedReport = self.ui.chmReportList.currentItem() 
    
    if(selectedReport and footerComment): 
        reportName = selectedReport.text()
        reportNum = getParameterNum(self.tempDB, reportName)  
           
        # Insert or Replace the current Footer into the thing 
        addChmReportFooter(self.tempDB, reportNum, footerComment)
        




#******************************************************************
#    Chemisty Class Definitions
#****************************************************************** 

# Tests Data Object 
class TestData(): 
    def __init__(self, testNum, testName, textName, reportName, recoveryVal, unitType): 
        self.testNum     = testNum
        self.testName    = testName
        self.textName    = textName
        self.reportName  = reportName       
        self.recoveryVal = recoveryVal
        self.unitType    = unitType

# Handles data logic & Interacts with database   
class TestsDataModel(): 
    def __init__(self, database):
        self.db = database
        self.tests = {}
        
    def loadTestsData(self):
        # special to get ride of the all the ICP names 
        #testsList = getAllChmTestsInfo2(self.db) 
        testsList = getAllChmTestsInfo2(self.db) 
 
        print('Total Tests: ', len(testsList))
        print(testsList[0])

        if(testsList): 
            for test in testsList: 
                testNum     = test[0]
                testName    = test[1]
                textName    = test[2]
                displayName = test[3]
                recoveryVal = test[4]
                unitType    = test[5]

                self.tests[testNum] = TestData(testNum, testName, textName, displayName, recoveryVal, unitType)

            return self.tests 

    def getTestData(self, testNum): 
        if(testNum in self.tests): 
            return self.tests[testNum]

    def getsAllTestsData(self): 
        if(self.tests): 
            return self.tests 
        
        return None 

    def addTestsData(self): 
        pass; 
    
    def updateTestsData(self, newData): 
        testNum = newData[0]

        if(testNum in self.tests): 
            self.tests[testNum] = newData 
            return self.tests[testNum] 
        
    def deleteTestsData(self): 
        pass; 
   
# Handles Tree Widget UI data
class TestsDataView():
    def __init__(self, tree_widget):
        self.tree = tree_widget

    def populateTree(self, testsResults): 

        #if(testsResults): 
        #    for testInfo in testsResults: 
        #        item = QTreeWidgetItem(self.tree) 
        #        item.setData(0, 0, testInfo[0])
        #        item.setData(1, 0, testInfo[1])
        #        item.setData(2, 0, testInfo[2])    
        
        if(testsResults): 
            for test in testsResults.values(): 
                item = QTreeWidgetItem(self.tree) 
                item.setData(0, 0, test.testNum)
                item.setData(1, 0, test.testName)
                item.setData(2, 0, test.textName)
                item.setData(3, 0, test.reportName)
                
    def getTreeData(self): 
        testItem = self.tree.currentItem() 

        if testItem:
            return [testItem.data(i, 0) for i in range(6)]
        
    def getTreeValue(self, row): 
        testItem = self.tree.currentItem()

        if(testItem): 
            return testItem.data(row, 0)
            #return testItem.text(row)

    def getCurrentRowIndex(self): 
        testsItem = self.tree.currentItem()
        if(testsItem):
            return self.tree.indexOfTopLevelItem(testsItem)
        else:
            return -1  # No current item selected
        
    def updateTreeData(self, newData): 
        testsItem = self.tree.currentItem()
        
        if(testsItem and newData): 
            testsItem.setData(0, 0, newData[0])
            testsItem.setData(1, 0, newData[1])
            testsItem.setData(2, 0, newData[2])
            testsItem.setData(3, 0, newData[3])
            testsItem.setData(4, 0, newData[4])
            testsItem.setData(5, 0, newData[5])

class MacroDialog(QDialog): 
    # Define Signals 
    dataUpdate = pyqtSignal(dict)
    testsUpdate = pyqtSignal(list)
     
    def __init__(self, data, item, title):
        super().__init__()
        # Load the UI file

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'macroDialog.ui')
        
        self.ui = loadUi(file_path, self)
        
        #set the titles 
        self.setWindowTitle(title) 
        self.title.setText(title)

        #set the data
        self.data = data 
        self.item = item
        self.processData()

        # Connect button signals to slots
        self.saveButton.clicked.connect(self.handleSave)
        self.cancelButton.clicked.connect(self.handleCancel) 

class CreateTestsDialog(QDialog): 
     
    def __init__(self, database, title): 
        super().__init__()
        
        # Load the UI File 
        #ui_path = QDir.currentPath() + '/ui/addTestsDialog.ui'
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'addTestsDialog.ui')
        self.ui = loadUi(file_path, self)

        #set the titles 
        self.setWindowTitle('Add New Chemical') 
        self.title.setText(title)
        
        # Assign data 
        self.db = database 
        self.processRequest()
        
        # Connect the buttons     
        self.cancelBtn.clicked.connect(self.handleCancelBtn)
        self.saveBtn.clicked.connect(self.handleSaveBtn)
        
    def processRequest(): 
        pass; 
            
        
    def handleCancelBtn(self): 
        pass; 
    
    
    def handleSaveBtn(self): 
        pass; 
    
