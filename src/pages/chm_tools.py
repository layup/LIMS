


from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QWidgetItem, QTreeWidgetItem 
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator


from modules.excel.chmExcel import createChmReport
from modules.dbFunctions import (loadChmTestsData, deleteChmData, getAllChmTestsData, getAllChmTestsInfo,
                                getAllChmTestsInfo2, getChmTestData, addChmTestData, getTestsName )
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *


#******************************************************************
#    Chemisty Setup 
#****************************************************************** 

def chemistySetup(self): 
    chmTestsInfoSetup(self)
    chmInputSectionSetup(self)
    chmDatabaseSetup(self)
    
    database_page = 1; 
        
#******************************************************************
#    Chemisty Database Section 
#****************************************************************** 

def chmDatabaseSetup(self): 
    print('[FUNCTION]: chmDatabaseSetup(self)')
    # Column Width
    smallColWidth = 100; 
    mediumColWidth = 200; 
    
    TableHeader = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Standard Value', 'Unit Value', 'Actions']    

    tableWidget = self.ui.chmInputTable

    # Set the column Headers 
    tableWidget.setColumnCount(len(TableHeader))
    tableWidget.setHorizontalHeaderLabels(TableHeader)
 
    # Set the column width 
    tableWidget.setColumnWidth(0, smallColWidth)
    tableWidget.setColumnWidth(1, smallColWidth)
    tableWidget.setColumnWidth(2, mediumColWidth)
    tableWidget.setColumnWidth(3, smallColWidth)
    tableWidget.setColumnWidth(4, smallColWidth)
    tableWidget.setColumnWidth(5, smallColWidth)

    # Set the last column to stretch
    tableWidget.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
    
    # Show the vertical rows 
    tableWidget.verticalHeader().setVisible(True)
    
    # Disable Editing of the table 
    tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

    # Connect basic signals 
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))
     
    # Load in the inital Database 
    populateChmDatabase(self);  
    
   

def populateChmDatabase(self): 
    print('[FUNCTION]: loadChmDatabase, Loading Existing Data'); 
    
    chmTable = self.ui.chmInputTable 
    columnCount = chmTable.columnCount()
    results = getAllChmTestsData(self.tempDB) 
    chmTable.setRowCount(len(results))


    # The order for the data is defined in the dbFunction
    for i, result in enumerate(results):

        for j in range(columnCount-1):
            data = str(result[j]) 
            
            if(j == 2): 
                testName = getTestsName(self.preferencesDB, data)
                print(testName)
                if(testName): 
                    item = QTableWidgetItem(testName[0][0])
                    item.setTextAlignment(Qt.AlignCenter)       
                
                    chmTable.setRowHeight(i, 18)
                    chmTable.setItem(i, j, item)    
            else: 
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)       
                
                chmTable.setRowHeight(i, 18)
                chmTable.setItem(i, j, item)     

        actionWidget = createActionWidget(self, i)
        chmTable.setCellWidget(i, 6, actionWidget)
        
def createActionWidget(self, row): 

    #TODO: add the edit button 
    deleteBtn = QPushButton("Delete")
    editbtn = QPushButton('Edit')

    # Connect the signals
    deleteBtn.clicked.connect(lambda _, row=row: chmTableDeleteRow(self, row));
    editbtn.clicked.connect(lambda _, row=row: chmTableEditRow(self, row))

    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editbtn)
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
    

def chmTableEditRow(self, row): 
    sampleNum = self.ui.chmInputTable.item(row, 0).text()
    testsName = self.ui.chmInputTable.item(row, 1).text() 
    
    print(f'EDIT ROW: {row}')
    
    for column in range(self.ui.chmInputTable.columnCount()-1):
        item = self.ui.chmInputTable.item(row, column)
        if(item): 
            print(item) 
            item.setBackground(QColor(125,125,125))
        

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
    results = self.preferencesDB.query(query)

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
#    Chemisty Input Data Classes 
#*****************************************************************

class parameterItem: 
    def __init__(self,testNum, testName): 
        self.testNum = testNum
        self.testName = testName 

#******************************************************************
#    Chemisty Tests Info 
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
#TODO: implment something here


        
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
        testsList = getAllChmTestsInfo2(self.db) 
 
        print('Total Tests: ', len(testsList))

        if(testsList): 
            for test in testsList: 
                testNum     = test[0]
                testName    = test[1]
                textName    = test[2]
                displayName = test[3]
                recoveryVal = test[4]
                unitType    = test[5]

                self.tests[testNum] = TestData(testNum, testName, textName, displayName, recoveryVal, unitType)

            return testsList 

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

        if(testsResults): 
            for testInfo in testsResults: 
                item = QTreeWidgetItem(self.tree) 
                item.setData(0, 0, testInfo[0])
                item.setData(1, 0, testInfo[1])
                item.setData(2, 0, testInfo[2])    
                
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
        ui_path = QDir.currentPath() + '/ui/macroDialog.ui'
        self.ui = loadUi(ui_path, self)
        
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
        ui_path = QDir.currentPath() + '/ui/addTestsDialog.ui'
        self.ui = loadUi(ui_path, self)

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
    
