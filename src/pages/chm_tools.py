


from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QWidgetItem, QTreeWidgetItem 
)

from modules.excel.chmExcel import createChmReport
from modules.dbFunctions import loadChmTestsData, deleteChmData, insertChmTests, getAllChmTestsInfo 
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
    

        
#******************************************************************
#    Chemisty Database Section 
#****************************************************************** 
#TODO: reload the data when we add new information (Create a class that deals with this)
def chmDatabaseSetup(self): 
    smalllColWidth = 120; 
    mediumColWidth = 200; 
    
    # Set the column width 
    self.ui.chmInputTable.setColumnWidth(0, smalllColWidth)
    self.ui.chmInputTable.setColumnWidth(1, mediumColWidth)
    self.ui.chmInputTable.setColumnWidth(2, smalllColWidth)
    self.ui.chmInputTable.setColumnWidth(3, smalllColWidth)
    self.ui.chmInputTable.setColumnWidth(4, smalllColWidth)
    self.ui.chmInputTable.setColumnWidth(5, smalllColWidth)
    
    # Set the last column to stretch
    self.ui.chmInputTable.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
    
    # Hide the vertical rows 
    self.ui.chmInputTable.verticalHeader().setVisible(False)
    # Disable Editing of the table 
    self.ui.chmInputTable.setEditTriggers(QTableWidget.NoEditTriggers)
    
    # Load in the inital Database 
    loadChmDatabase(self);    


def loadChmDatabase(self): 
    print('[FUNCTION]: loadChmDatabase, Loading Existing Data'); 
    
    TableHeader = ['Sample Number', 'Tests', 'Test Values', 'Standard Value', 'Unit Value', 'Job Num', 'Actions']
    chmTable = self.ui.chmInputTable 

    results = loadChmTestsData(self.db) 
    
    chmTable.setRowCount(len(results))
    chmTable.setColumnCount(len(TableHeader))
    chmTable.setHorizontalHeaderLabels(TableHeader)
    
    
    for i, result in enumerate(results):
        for j in range(len(TableHeader)-1):
            data = str(result[j]) 
            item = QTableWidgetItem(data)
            item.setTextAlignment(Qt.AlignCenter)
            
            chmTable.setItem(i, j, item)     

        #TODO: add the edit button 
        deleteBtn = QPushButton("Delete")
        editbtn = QPushButton('Edit')

        deleteBtn.clicked.connect(lambda _, row=i: chmTableDeleteRow(self, row));
        editbtn.clicked.connect(lambda _, row=i: chmTableEditRow(self, row))

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addWidget(editbtn)
        button_layout.addWidget(deleteBtn)
        button_layout.setContentsMargins(5, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignLeft)

        chmTable.setCellWidget(i ,6, button_widget)
        

def chmTableDeleteRow(self, row): 
    print(f'[FUNCTION]: chmTableDeleteRow, row to delete {row}')
    
    sampleNum = self.ui.chmInputTable.item(row, 0).text()
    testsName = self.ui.chmInputTable.item(row, 1).text()
    print(f'Sample Num: {sampleNum}, Tests Name: {testsName}')
    
    self.ui.chmInputTable.removeRow(row)
    #deleteChmData(self.db, sampleNum, testsName)

def chmTableEditRow(self, row): 
    sampleNum = self.ui.chmInputTable.item(row, 0).text()
    testsName = self.ui.chmInputTable.item(row, 1).text() 

#******************************************************************
#    Chemisty Input Data
#****************************************************************** 
#TODO: have error handling for duplicates 
#TODO: takes in the values from the 
#TODO: connect from the defined values in gcms Defined Tests Page
#TODO: make sure to add a date for the table so we can sort it by the most recent date
#TODO: duplication error
#TODO: set defaults 

def chmInputSectionSetup(self): 
    print('[FUNCTION]:chmInputSectionSetup(self)')
    self.ui.inputDataTree.clear()
    
    populateNewEntry(self) 
    
    #TODO: rename this 
    # Input Data Page Signals
    #self.ui.gcmsTests.activated.connect(lambda index: on_gcmsTests_activated(self, index))
    self.ui.chmProceedBtn.clicked.connect(lambda: on_chmProceedBtn_clicked(self))
    
def populateNewEntry(self): 
    print('[FUNCTION]: populateNewEntry(self)')
    
    # TODO: move this to another function 
    query = 'SELECT testName FROM Tests WHERE testName NOT LIKE "%ICP%" AND type = "C" ORDER BY testName ASC'
    results = self.preferencesDB.query(query)

    chmClearActiveValues(self)
    
    #TODO: find out what the others are (add to the settings section)
    parameterTypes = [item[0] for item in results]
    parameterTypes.insert(0, '')
    unitTypes = ['', 'TCU', 'ug/L', 'mg/g']    
    
    self.ui.gcmsTests.addItems(parameterTypes)
    self.ui.gcmsUnitVal.addItems(unitTypes)
    

def on_gcmsTests_activated(self, index): 
    if(index in self.chmParameters): 
        unitVal = self.chmParameters[index]
        print(unitVal) 

        if(unitVal == ''):
            print("nothing") 
            self.ui.gcmsUnitVal.setCurrentIndex(0); 
            
        else: 
            print("something else")
            index = self.ui.gcmsUnitVal.findText(unitVal) 
            print(index)
            
            self.ui.gcmsUnitVal.setCurrentIndex(index)
            
@pyqtSlot()    
def on_chmProceedBtn_clicked(self):            
    standards = self.ui.gcmsStandardVal.text().strip()
    units = self.ui.gcmsUnitVal.currentText()
    tests = self.ui.gcmsTests.currentText()

    errorCheck = [0,0,0]

    errorCheck[0] = 0 if (standards != '' and is_real_number(standards)) else 1; 
    errorCheck[1] = 0 if units != '' else 1; 
    errorCheck[2] = 0 if tests != '' else 1; 
    
    if(sum(errorCheck) == 0):
    
        self.ui.chmTestsValueWidget.setEnabled(True)
        self.ui.chmActionWidget.setEnabled(True)
        #TODO: rename the widget thing
        self.ui.widget_29.setEnabled(False)
        self.ui.gcmsStandardValShow.setText(standards)
        self.ui.gcmsUnitValShow.setText(units)
        self.ui.gcmsTestsShow.setText(tests)  
    else: 
        errorTitle = 'Cannot Proceed with CHM Process'
        errorMsg = ''
        
        if(errorCheck[0] == 1): 
            errorMsg += 'Please Enter a Valid Standard Number\n'
        if(errorCheck[1] == 1): 
            errorMsg += 'Please Select a Unit\n'
        if(errorCheck[2] == 1): 
            errorMsg += 'Please Select a Tests\n'
            
        showErrorDialog(self, errorTitle, errorMsg)
        
@pyqtSlot()   
def on_chmSampleDataAdd_clicked(self): 
    print('[FUNCTION]: chmAddTestsBtn clicked')
    standards = self.ui.gcmsStandardValShow.text().strip()
    units = self.ui.gcmsUnitValShow.text().strip()
    testName = self.ui.gcmsTestsShow.text().strip()  
    
    testNum = self.ui.gcmsTestsJobNum.text().strip()
    sampleNum = self.ui.gcmsTestsSample.text().strip()
    sampleVal = self.ui.gcmsTestsVal.text().strip()
    
    errorCheck = [0,0,0]
    
    errorCheck[0] = 0 if (testNum != '' and is_real_number(testNum)) else 1; 
    errorCheck[1] = 0 if (sampleNum != '' and is_real_number(sampleNum)) else 1; 
    errorCheck[2] = 0 if sampleVal != '' else 1; 
            
    print(f'Input Data Info: {testNum} {sampleNum} {sampleVal}')
            
    if(sum(errorCheck) == 0): 
        sampleNum = testNum + '-' + sampleNum; 
        inputTree = self.ui.inputDataTree
        
        #TODO: move to own function 
        checkInquery = 'SELECT EXISTS(SELECT 1 FROM gcmsTestsData WHERE sampleNum = ? and testsName = ?)'
        self.db.execute(checkInquery, (sampleNum, testName))
        result = self.db.fetchone()[0]
        
        if(result == 1): 
            #TODO: message box in own function 
            msgBox = QMessageBox()  
            msgBox.setText("Duplicate Sample");
            duplicateMsg = "Would you like to overwrite existing sample " + str(sampleNum) + " ?"
            msgBox.setInformativeText(duplicateMsg);
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);
            msgBox.setDefaultButton(QMessageBox.Yes);
            x = msgBox.exec_()

            if(x == QMessageBox.Yes): 
                addToChmTestsData(self.db, sampleNum, testName, sampleVal, standards, units, testNum)
                 
                matchingItem = checkMatchingTreeItems(inputTree, sampleNum)
                if not matchingItem: 
                    addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards)
                else: 
                    pass; 
                
                chmClearSampleJob(self) 

            if(x == QMessageBox.No):
                chmClearSampleJob(self) 
                
            if(x == QMessageBox.Cancel):
                pass 
            
        else: 
            addToChmTestsData(self.db, sampleNum, testName, sampleVal, standards, units, testNum)
            addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards)
            chmClearSampleJob(self) 
            
    else: 
        errorTitle = 'Cannot add Tests '
        errorMsg = ''
        
        if(errorCheck[0] == 1): 
            errorMsg += 'Please Enter a Valid Job Number\n'

        if(errorCheck[1] == 1): 
            errorMsg += 'Please Enter a Valid Sample Number\n'
            
        if(errorCheck[2] == 1): 
            errorMsg += 'Please Enter a Valid Sample Value \n'
        
        showErrorDialog(self, errorTitle, errorMsg)
        
        
def checkMatchingTreeItems(treeWidget, targetText):
    # Iterate through the top-level items
    for index in range(treeWidget.topLevelItemCount()):
        item = treeWidget.topLevelItem(index)
        if item.text(0) == targetText:  # Change 0 to the desired column index
            return item 

    return None

def addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards): 
    print('[FUNCTION]: addInputTreeItem(inputTree, sampleNum, testName, sampleVal, units, standards)')
    topItem = QTreeWidgetItem(inputTree)  
    
    topItem.setText(0, sampleNum)           
    topItem.setText(1, testName)
    topItem.setText(2, sampleVal)
    topItem.setText(3, units)
    topItem.setText(4, standards)
    
    #TODO: connect the delete button, maybe add an edit button
    deleteTreeBtn = QPushButton('Delete')

    # Create a widget container for the button
    widget_container = QWidget()
    layout = QVBoxLayout(widget_container)
    layout.addWidget(deleteTreeBtn)

def chmClearSampleJob(self): 
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear() 
        
#FIXME: not used anywhere 
def chmClearActiveValues(self): 
    self.ui.gcmsStandardVal.clear()
    self.ui.gcmsUnitVal.clear()
    self.ui.gcmsTests.clear() 
        
def chmClearEnteredTestsData(self): 
    self.ui.chmTestsValueWidget.setEnabled(False)
    self.ui.chmActionWidget.setEnabled(False)
    self.ui.widget_29.setEnabled(True)
 
    chmClearActiveValues(self)
    
    # Clear Enter values Section 
    self.ui.gcmsTestsJobNum.clear()
    chmClearSampleJob(self) 
    
    self.ui.inputDataTree.clear()

#TODO: move this function to the other area 
def addToChmTestsData(database, sampleNum, testName, sampleVal, standards, units, jobNum ): 
    addInquery = 'INSERT OR REPLACE INTO gcmsTestsData (sampleNum, testsName, testsValue, StandardValue, unitValue, jobNum) VALUES (?,?,?,?,?, ?)'
    
    try:
        database.execute(addInquery, (sampleNum, testName, sampleVal, standards, units, jobNum,) )
        database.commit()

    except sqlite3.IntegrityError as e:
        print(e) 


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
        testsList = getAllChmTestsInfo(self.db) 
 
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
    
