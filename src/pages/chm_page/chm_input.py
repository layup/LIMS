
from base_logger import logger
import math 

from datetime import date
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox,  QPushButton, QWidget, QHBoxLayout, QTreeWidgetItem
from PyQt5.QtGui import QDoubleValidator, QIntValidator

from modules.dbFunctions import (getChmTestData, addChmTestData, checkChmTestsExist)
from modules.constants import CHM_REPORT
from modules.utils.logic_utils import is_real_number
from modules.widgets.dialogs import showErrorDialog, duplicateSampleOverrideDialog, deleteBox, saveMessageDialog
from modules.widgets.SideEditWidget import SideEditWidget



#******************************************************************
#   General Functions 
#****************************************************************** 

#TODO: takes in the values from the 
#TODO: duplication error
#TODO: center all of the table items 
def chm_input_setup(self): 
    logger.info(f'Entering chmInputSectionSetup')

    sideEditSetup(self)

    chmClearEnteredTestsData(self, True)
    
    formatQLineEdits(self)
    
    populateNewEntry(self) 
    
    # Input Data Page Signals
    self.ui.chmProceedBtn.clicked.connect(lambda: on_chmProceedBtn_clicked(self))
    self.ui.chmInputClearBtn.clicked.connect(lambda: on_chmClearBtn_clicked(self))
    self.ui.chmAddTestsBtn.clicked.connect(lambda:on_chmSampleDataAdd_clicked(self)) 

def sideEditSetup(self): 
    # Side Edit Widget Setup

    # Get the list of parameters and allowed unit types
    self.ui.sideEditWidget1 = SideEditWidget() 
    
    self.ui.sideEditLayout.addWidget(self.ui.sideEditWidget1) #only valid for layouts
    self.ui.sideEditWidget1.setVisible(False)
    
    parameterType, unitType = getParameterAndUnitTypes(self.tempDB)
    self.ui.sideEditWidget1.set_drop_down(parameterType, unitType) 
    self.ui.sideEditWidget1.set_combo_disabled(True)
    
    self.ui.sideEditWidget1.cancel_clicked.connect(lambda: sideEditCancelBtnClicked(self))
    self.ui.sideEditWidget1.cancelBtn.clicked.connect(lambda: sideEditCancelBtnClicked(self))
    self.ui.sideEditWidget1.save_clicked.connect(lambda tests_info, tree_item: sideEditSaveBtnClicked(self, tests_info, tree_item))

    
def sideEditCancelBtnClicked(self): 
    
    # Clear the data 
    self.ui.sideEditWidget1.clear_data()

    # set not visible
    self.ui.sideEditWidget1.setVisible(False) 
    
def sideEditSaveBtnClicked(self, new_data, item):
    print(f'Entering sideEditSaveBtnClicked with parameters: data: {new_data}, row: {item}') 
    
    
    # check if any data is different 
    
    
    
    jobName = new_data[0] + '-' + new_data[1]
    result = saveMessageDialog(self, 'Overwrite Data?', f'Are you sure you want overwrite existing data for {jobName}?')

    if(result): 
        # update table info 
        for col in range(len(new_data)):
            item.setText(col, new_data[col])
        
        # update database
        query = 'UPDATE chemTestsData SET testName = ? '
        
    
    
        
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
    

#TODO: add some cool CS to make it look cooler
def populateNewEntry(self): 
    self.logger.info('Entering populateNewEntry')
   
    self.ui.gcmsTests.clear() 
    self.ui.gcmsUnitVal.clear() 
    chmClearActiveValues(self)
    
    parameterTypes, unitTypes = getParameterAndUnitTypes(self.tempDB) 
    parameterTypes.insert(0, '') 
    unitTypes.insert(0, '')
    
    for item in parameterTypes:
        if isinstance(item, parameterItem):
            self.ui.gcmsTests.addItem(item.testName, userData=item)
        else: 
            self.ui.gcmsTests.addItem('')

    self.ui.gcmsUnitVal.addItems(unitTypes)
    
    
def getParameterAndUnitTypes(database): 
    query = 'SELECT testNum, testName FROM Tests WHERE testName NOT LIKE "%ICP%" AND type = "C" ORDER BY testName ASC'
    results = database.query(query) 
    
    unitTypes =  ['TCU', 'ug/L', 'mg/g']
   
    # Convert results into readable 
    parameterTypes = [parameterItem(item[0], item[1]) for item in results]

    return parameterTypes, unitTypes 
    
            
@pyqtSlot()    
def on_chmProceedBtn_clicked(self):            
    self.logger.info('Entering on_chmProceedBtn_clicked')
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
    self.logger.info('Entering on_chmSampleDataAdd_clicked ')
    
    standards, units, testName = captureNewEntryData(self) 
    jobNum, sampleNum, sampleVal = captureEnteredValues(self)
    testNum = getParameterTypeNum(self.ui.gcmsTests) 
    
    edit_data = [jobNum, sampleNum, testName, sampleVal, units]; 
    
    errorCheckList = [0,0,0]
    
    errorCheckList[0] = 0 if (jobNum != '' and is_real_number(jobNum)) else 1; 
    errorCheckList[1] = 0 if (sampleNum != '' and is_real_number(sampleNum)) else 1; 
    errorCheckList[2] = 0 if sampleVal != '' else 1; 
            
    self.logger.debug(f'Input Data Info: {jobNum}-{sampleNum}: {sampleVal}')
            

    #FIXME: problem arises if reading something to an existing list we can't then delete it afterwords
    if(sum(errorCheckList) == 0):  
        inputTree = self.ui.inputDataTree #remove this bs 
        todaysDate = date.today()
        
        existingDataCheck = checkChmTestsExist(self.tempDB, sampleNum, testNum, jobNum)
        
        if(existingDataCheck): 
            response = duplicateSampleOverrideDialog(jobNum, sampleNum)

            if(response):  
                addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum, todaysDate)
                 
                matchingItem = checkMatchingTreeItems(inputTree, sampleNum)
                if not matchingItem: 
                    addInputTreeItem(self, inputTree, sampleNum, testName, sampleVal, units, standards, jobNum)

                chmClearSampleJob(self) 

            if(response == False):
                chmClearSampleJob(self) 
            
        else: 
            addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum, todaysDate)
            addInputTreeItem(self, inputTree, sampleNum, testName, sampleVal, units, standards, jobNum)
            chmClearSampleJob(self)  
    else: 
        self.logger.error(f'errorCheckList: {errorCheckList}')
        addingSampleDataErrorDisplay(self, errorCheckList)


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


def dataEntryWidgetEnabler(self, status): 
    logger.info(f'Entering dataEntryWidgetEnabler with parameter: status {repr(status)}')
    
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

    # disable/enable the new entry widget section 
    dataEntryWidgetEnabler(self, False) 
    
    # clear the new entry widget section 
    chmClearNewEntry(self) 
    
    # clear the active values section
    chmClearActiveValues(self) 
    
    # clear Enter values Section 
    self.ui.gcmsTestsJobNum.clear()
    chmClearSampleJob(self) 
    
    if(clearTable):  
        self.ui.inputDataTree.clear()


#******************************************************************
#  Action Widget 
#****************************************************************** 

def addInputTreeItem(self, treeWidget, sampleNum, testName, sampleVal, units, standards, jobNum): 
    logger.info('Entering addInputTreeItem')
    
    topItem = QTreeWidgetItem(treeWidget)  
    
    topItem.setText(0, jobNum)
    topItem.setText(1, sampleNum)           
    topItem.setText(2, testName)
    topItem.setText(3, sampleVal)
    topItem.setText(4, units)
    topItem.setText(5, standards)
    
    row_index = treeWidget.indexOfTopLevelItem(topItem)

    actionWidget = TreeActionWidget(row_index, topItem)
    actionWidget.edit_clicked.connect(lambda tree_item: editTreeRowClicked(self, tree_item));
    actionWidget.delete_clicked.connect(lambda tree_item: deleteTreeRowClicked(self, tree_item))

    treeWidget.setItemWidget(topItem, 6, actionWidget)
    

def editTreeRowClicked(self, item): 
    row_index = self.ui.inputDataTree.indexOfTopLevelItem(item)
    
    self.logger.debug(f"Edit clicked for row: {row_index}")
    
    data = [item.text(i) for i in range(6)]
    self.logger.debug('Current Tree Item: {data}')
    
    self.ui.sideEditWidget1.setVisible(True)
    # Set the data 
    self.ui.sideEditWidget1.set_data(data)
    self.ui.sideEditWidget1.set_item(item)
            
    
def deleteTreeRowClicked(self, item):
    row_index = self.ui.inputDataTree.indexOfTopLevelItem(item)
    
    self.logger.debug(f"Delete clicked for row: {row_index}")
 
    jobName = item.text(0) +  '-' + item.text(1)
    result = deleteBox(self, f'Are you sure want to delete {jobName}?', "Once you've deleted this item, it cannot be undone")
    
    if(result): 
    
        # check if edit panel is visible and if the item delete 
        if(self.ui.sideEditWidget1.isVisible()):
            if(item is self.ui.sideEditWidget1.get_item()): 
                self.logger.info('SideEditWidget Item is the same as the delete tree Item')
                self.ui.sideEditWidget1.setVisible(False) 
                self.ui.sideEditWidget1.clear_data()

        # Remove the item from the tree
        self.ui.inputDataTree.takeTopLevelItem(row_index)
        
        # Delete Item from database 
    

# TODO: might have to move this into other functions so I can read it better lol 
class TreeActionWidget(QWidget): 

    edit_clicked = pyqtSignal(QTreeWidgetItem)  # Signal for edit button click
    delete_clicked = pyqtSignal(QTreeWidgetItem)  # Signal for delete button click
    
    def __init__(self, row_index, item, parent=None):
        super().__init__(parent)

        self.item = item; 
        self.row_index = row_index
        
        button_widget = QWidget()
        self.layout = QHBoxLayout(button_widget)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignLeft)

        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.on_edit_clicked)
        self.layout.addWidget(self.editBtn)

        self.deleteBtn = QPushButton("Delete")
        self.deleteBtn.clicked.connect(self.on_delete_clicked)
        self.layout.addWidget(self.deleteBtn)

        self.setLayout(self.layout)

    def on_edit_clicked(self):
        # Emit signal to trigger edit action in main window
        self.edit_clicked.emit(self.item)

    def on_delete_clicked(self):
        # Emit signal to trigger delete action in main window
        self.delete_clicked.emit(self.item)

    
#******************************************************************
#    Chemistry Input Data Classes 
#*****************************************************************

class parameterItem: 
    def __init__(self,testNum, testName): 
        self.testNum = testNum
        self.testName = testName 

        
def getParameterTypeNum(comboBox): 
    
    index = comboBox.currentIndex()
    if index >= 0:
        item = comboBox.itemData(index)
        if isinstance(item, parameterItem):
            return item.testNum
    return None