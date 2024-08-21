
import os 

from base_logger import logger

from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QTreeWidgetItem, QDialog

from modules.dbFunctions import (getAllChmTestsInfo2, addChmTestData)
from modules.constants import CHM_REPORT

#******************************************************************
#    Chemistry Tests Info 
#*****************************************************************
def chm_tests_setup(self): 
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
    #self.ui.chmAddTestsBtn.clicked.connect(lambda: on_chmSampleDataAdd_clicked(self))

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
        # Update the tests viewer to display the updated Data
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
#    Chemistry Class Definitions
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
    
