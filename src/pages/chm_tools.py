


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
from modules.dbFunctions import loadChmTestsData, deleteChmData, insertChmTests 
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *


#******************************************************************
#    Chemisty Setup 
#****************************************************************** 

def chemistySetup(self): 
    
    # Load in the inital Database 
    loadChmDatabase(self);   
    
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
    

    self.ui.inputDataTree.clear()
    
    # Set the column width for Input Tree 

    # Connect Signal/Buttons 
    self.ui.gcmsAddTestsBtn.clicked.connect(lambda: on_chmAddTestsBtn_clicked(self))
    self.ui.gcmsSaveTestBtn.clicked.connect(lambda: on_chmSaveTestBtn_clicked(self))
    self.ui.gcmsDeleteTestBtn.clicked.connect(lambda: on_chmDeleteTestBtn_clicked(self))        
    self.ui.gcmsDefinedtests.currentRowChanged.connect(lambda: on_chmDefinedtests_currentRowChanged(self)) 
    
    # CHM input data signals
    self.ui.gcmsTests.activated.connect(lambda index: on_gcmsTests_activated(self, index))
    self.ui.gcmsProceedBtn.clicked.connect(lambda: on_gcmsProceedBtn_clicked(self))
    
    self.ui.chmAddTestsBtn.clicked.connect(lambda: on_chmSampleDataAdd_clicked(self))
    


def chmLoadTestsData(self): 
    selectedTests = self.ui.gcmsDefinedtests.currentItem()
            
    if selectedTests is not None:
        try: 
            getTestsData = 'SELECT * FROM gcmsTests WHERE testName = ?'
            self.db.execute(getTestsData, (selectedTests.text(),))
            results = self.db.fetchone() 
            print('Results:') 
            print(results)
        
            self.ui.gcmsTxtName.setText(str(results[0]))
            self.ui.gcmsUnitType.setText(str(results[1]))
            self.ui.gcmsRefValue.setText(str(results[2]))
            self.ui.gcmsDisplayName.setText(str(results[3]))

            self.ui.chmTxtName.setText(str(results[0]))
            self.ui.chmUnitName.setText(str(results[1]))
            self.ui.chmRefValue.setText(str(results[2]))
            self.ui.chmDisplayName.setText(str(results[3])) 
            
        except: 
            #item is not in the database yet 
            print('Error: selected Text was None') 
            chmClearDefinedTestsValues(self)
            self.ui.gcmsTxtName.setText(selectedTests.text())
            
            
def chmLoadTestsNames(self): 
    print('[FUNCTION]: chmLoadTestsNames')
    chmClearDefinedTestsValues(self); 
    self.ui.gcmsDefinedtests.clear()
    self.ui.testsInputLabel.clear()

    getTestNamesQuery = 'SELECT testName FROM gcmsTests ORDER BY testName COLLATE NOCASE ASC'
    testNames = self.db.query(getTestNamesQuery)           
    
    print(testNames)
    
    for test in testNames: 
        self.ui.gcmsDefinedtests.addItem(test[0])


    # Clear the section (reloading)
    self.ui.chmTestTree.clear()

    # Query Results 
    query = 'SELECT * FROM gcmsTests gcmsTests ORDER BY testName COLLATE NOCASE ASC'
    testNames = self.db.query(query)        
    print(f'testsNames: {testNames}')
     
    for testInfo in testNames: 
        item = QTreeWidgetItem(self.ui.chmTestTree) 
        item.setData(0, 0, testInfo[0])
        item.setData(1, 0, testInfo[1])
        item.setData(2, 0, testInfo[2])
        item.setData(3, 0, testInfo[3])

    


def chmClearDefinedTestsValues(self): 
    self.ui.gcmsDisplayName.clear()
    self.ui.gcmsTxtName.clear()
    self.ui.gcmsUnitType.clear()
    self.ui.gcmsRefValue.clear()
    self.ui.gcmsComment.clear() 

  
    self.ui.chmTestsComment.clear()
    for child_widget in self.ui.temp1.findChildren(QWidget):
        # Check if the child widget is a QLineEdit
        if isinstance(child_widget, QLineEdit):
            # Clear the text of the QLineEdit
            child_widget.clear()
        
        
#******************************************************************
#    Chemisty Database Section 
#****************************************************************** 
#TODO: reload the data when we add new information 


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
def on_gcmsProceedBtn_clicked(self):            
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
            #self.ui.gcmsTestsLists.addItem(sampleNum)

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
    topItem = QTreeWidgetItem(inputTree)  
    
    topItem.setText(0, sampleNum)           
    topItem.setText(1, testName)
    topItem.setText(2, sampleVal)
    topItem.setText(3, units)
    topItem.setText(4, standards)
    
    deleteTreeBtn = QPushButton('Delete')

    # Create a widget container for the button
    widget_container = QWidget()
    layout = QVBoxLayout(widget_container)
    layout.addWidget(deleteTreeBtn)

    #inputTree.setItemWidget(topItem, 5, widget_container)

        
def chmClearSampleJob(self): 
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear() 
        
#FIXME: not used anywhere 
def gcmsClearSideData(self): 
    self.ui.gcmsStandardVal.clear()
    self.ui.gcmsUnitVal.clear()
    self.ui.gcmsTests.clear() 
        
def chmClearEnteredTestsData(self): 
    self.ui.chmTestsValueWidget.setEnabled(False)
    self.ui.chmActionWidget.setEnabled(False)
    self.ui.widget_29.setEnabled(True)
        
    self.ui.gcmsStandardVal.clear()
    self.ui.gcmsUnitVal.clear()
    self.ui.gcmsTests.clear()
    
    self.ui.gcmsStandardValShow.clear()
    self.ui.gcmsUnitValShow.clear()
    self.ui.gcmsTestsShow.clear()
        
    self.ui.gcmsTestsJobNum.clear()
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear()
    #self.ui.gcmsTestsLists.clear()
    
    self.ui.inputDataTree.clear()


def addToChmTestsData(database, sampleNum, testName, sampleVal, standards, units, jobNum ): 
    addInquery = 'INSERT OR REPLACE INTO gcmsTestsData (sampleNum, testsName, testsValue, StandardValue, unitValue, jobNum) VALUES (?,?,?,?,?, ?)'
    
    try:
        database.execute(addInquery, (sampleNum, testName, sampleVal, standards, units, jobNum,) )
        database.commit()

    except sqlite3.IntegrityError as e:
        print(e) 

#******************************************************************
#    Chemisty Tests Info
#****************************************************************** 
#TODO: if the txt name changes update the listName 
#TODO: keep track of the currentIndex when first getting it 
    
def chmGetTestsValues(self): 
    values = []
    
    for index in range(self.ui.gcmsDefinedtests.count()):
        item = self.ui.gcmsDefinedtests.item(index)
        values.append(item.text())
        
    return values; 
    

@pyqtSlot() 
def on_chmAddTestsBtn_clicked(self): 
    existingTests = chmGetTestsValues(self)        
    currentText = self.ui.testsInputLabel.text()
 
    if(currentText != '' and currentText not in existingTests): 
        #clear values 
        chmClearDefinedTestsValues(self)
        self.ui.testsInputLabel.clear()
        self.ui.gcmsDefinedtests.addItem(currentText)

        totalItems = len(chmGetTestsValues(self))
        self.ui.gcmsDefinedtests.setCurrentRow(totalItems-1)
        self.ui.gcmsTxtName.setText(currentText)
        
    else: 
        errorTitle = 'Invald Tests'
        errorMsg = 'Please enter a valid test'
        showErrorDialog(self, errorTitle, errorMsg)


@pyqtSlot()
def on_chmSaveTestBtn_clicked(self):
    print('[SLOT]: on_gcmsSaveTestBtn_clicked')
    displayName = self.ui.gcmsDisplayName.text().strip()
    txtName = self.ui.gcmsTxtName.text().strip()
    unitType = self.ui.gcmsUnitType.text().strip()
    recoveryVal = self.ui.gcmsRefValue.text()        
    comment = self.ui.gcmsComment.toPlainText() 
    
    #print(txtName, unitType, recoveryVal, displayName)

    if(txtName != ""):
        insertChmTests(self.db, txtName, unitType, recoveryVal, displayName)
        

@pyqtSlot()    
def on_chmDeleteTestBtn_clicked(self): 
    txtName = self.ui.gcmsTxtName.text().strip()
    selected_item = self.ui.gcmsDefinedtests.currentItem()
    
    deleteQuery = 'DELETE FROM gcmstests WHERE testName = ?'
    
    print(f'[QUERY]: {deleteQuery}')
    print(f'TXT Name: {txtName}, Selected Item: {selected_item}')
    
    try: 
        #TODO: make sure it deletes 
        deleteBox(self, "DELETE ELEMENT", "ARE YOU SURE YOU WANT TO DELETE THIS ITEM", lambda:print("hello World"))
        self.db.execute(deleteQuery, (txtName,))
        self.db.commit()

        currentItem = self.ui.gcmsDefinedtests.currentRow()
        self.ui.gcmsDefinedtests.takeItem(currentItem)
        self.ui.gcmsDefinedtests.setCurrentItem(None)
        
        chmClearDefinedTestsValues(self)
    
    except: 
        print('Error: could not delete item')
    

        
def on_chmDefinedtests_currentRowChanged(self):
    try:
        chmLoadTestsData(self)
    except Exception as e:
        print("An error occurred:", e)

#TODO: move all the unitType and the basic assortment to the prefence item  
def getTestsAndUnits(self): 
    inquery = 'SELECT testName, unitType FROM gcmsTests ORDER BY testName COLLATE NOCASE ASC'
    results = self.db.query(inquery)
    
    self.chmParameters = {}
    
    tests = ['']
    units = ['']
    
    for testName, unitType in results: 
        
        if(testName != '' ): 
            tests.append(testName)
            
            self.chmParameters[testName] = unitType 
        
        if(unitType != '' and unitType not in units):
            units.append(unitType)
            
    print(self.chmParameters)
    
    return (tests,units)


#******************************************************************
#    Chemisty Report Info
#****************************************************************** 





#******************************************************************
#    Chemisty Class Definitions
#****************************************************************** 

class TestsInfoManager(): 

    def __init__(self, treeWidget, database):
        self.treeWidget = treeWidget
        self.db = database  
        
    def displayTreeData(self): 
        pass; 
    
    
    
    def displayWidgetData(self): 
        pass; 
    
        ##External functions maybe? 
    
    
    def updateDatabase(self): 
        pass; 
    
    
    

class ReportManager(): 
    pass; 


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
    
