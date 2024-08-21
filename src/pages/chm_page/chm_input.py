
from base_logger import logger
import math 

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QWidgetItem, QTreeWidgetItem
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator


from modules.dbFunctions import (getChmTestData, addChmTestData)
from modules.constants import CHM_REPORT
#TODO: move the error dialog
from modules.utilities import is_real_number, showErrorDialog 



#******************************************************************
#    Chemistry Input Data
#****************************************************************** 

#TODO: takes in the values from the 
#TODO: duplication error
def chm_input_setup(self): 
    logger.info(f'Entering chmInputSectionSetup')

    chmClearEnteredTestsData(self, True)
    
    formatQLineEdits(self)
    
    populateNewEntry(self) 
    

    # Input Data Page Signals
    #self.ui.gcmsTests.activated.connect(lambda index: on_gcmsTests_activated(self, index))
    self.ui.chmProceedBtn.clicked.connect(lambda: on_chmProceedBtn_clicked(self))
    self.ui.chmInputClearBtn.clicked.connect(lambda: on_chmClearBtn_clicked(self))
            
def formatQLineEdits(self): 
    logger.info('Entering formatQLineEdits')
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

    # set the limit to characters allowed in line edit 
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
    editBtn = QPushButton('Edit')

    # Connect the signals
    deleteBtn.clicked.connect(lambda _, tree=treeWidget, row=row: chmTreeDeleteRow(tree, row));
    editBtn.clicked.connect(lambda _, tree=treeWidget, row=row: chmTreeEditRow(tree, row))

    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editBtn)
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