


from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal 
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
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
    

    # Connect Signal/Buttons 
    self.ui.gcmsAddTestsBtn.clicked.connect(lambda: on_chmAddTestsBtn_clicked(self))
    self.ui.gcmsSaveTestBtn.clicked.connect(lambda: on_chmSaveTestBtn_clicked(self))
    self.ui.gcmsDeleteTestBtn.clicked.connect(lambda: on_chmDeleteTestBtn_clicked(self))
    self.ui.gcmsDefinedtests.clicked.connect(lambda: on_chmDefinedtests_clicked(self))
        
    self.ui.gcmsDefinedtests.currentRowChanged.connect(lambda: on_chmDefinedtests_currentRowChanged(self)) 
    
    # CHM input data signals
    self.ui.gcmsTests.activated.connect(lambda index: on_gcmsTests_activated(self, index))
    self.ui.gcmsProceedBtn.clicked.connect(lambda: on_gcmsProceedBtn_clicked(self))
    self.ui.gcmsAddTestsBtn_2.clicked.connect(lambda: on_gcmsAddTestsBtn_2_clicked(self))
    


def chmLoader(self): 
    #TODO: scan in the TXT Tests, scan in from Defined Tests too 
    #TODO: fix the error checking 
    
    print('[FUNCTION]: chmLoader')
  
    columnNames = [
        'Tests', 
        'Display Name',
        'Unit', 
        'Standard Recovery', 
        'Distal factor'
    ]
    
    initalColumns = len(columnNames)
    GSMS_TESTS_LISTS = []
    
    self.loadClientInfo()

    #load sample names 
    for i, (key,value) in enumerate(self.sampleNames.items()):
        item = SampleNameWidget(key, value)
        self.ui.formLayout_5.addRow(item)
        item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
    
    self.ui.stackedWidget.currentChanged.connect(self.deleteAllSampleWidgets)
        
    for (currentJob ,testList) in self.sampleTests.items(): 
        for item in testList: 

            temp = removeIllegalCharacters(str(item)) 
            
            if(temp not in GSMS_TESTS_LISTS and 'ICP' not in temp):          
                GSMS_TESTS_LISTS.append(temp)

    
    testsQuery = 'SELECT * FROM gcmsTestsData WHERE jobNum = ?'
    testsResults = self.db.query(testsQuery, (self.jobNum,))
    
    #TODO: can create a list and combine unique values
    if(testsResults != None): 
        for item in testsResults: 
            if(item[1] not in GSMS_TESTS_LISTS):
                GSMS_TESTS_LISTS.append(item[1])
                    
    
    GSMS_TESTS_LISTS = sorted(GSMS_TESTS_LISTS)
    print('**FOUND CHM TESTS')
    print(GSMS_TESTS_LISTS) 

    self.ui.dataTable.setRowCount(len(GSMS_TESTS_LISTS))
    self.ui.dataTable.setColumnCount(initalColumns + int(self.clientInfo['totalSamples']))
    self.ui.dataTable.horizontalHeader().setVisible(True)
    self.ui.dataTable.verticalHeader().setVisible(True)
    self.ui.dataTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    #inital columns 
    for i in range(initalColumns): 
        item = QtWidgets.QTableWidgetItem()
        self.ui.dataTable.setHorizontalHeaderItem(i, item)
        item2 = self.ui.dataTable.horizontalHeaderItem(i)
        item2.setText(columnNames[i])
        
    #set the names of the columns 
    #self.ui.dataTable.setHorizontalHeaderLabels(columnNames)
    
    #populate with sample names 
    for i , (key,value ) in enumerate(self.sampleNames.items(), start=initalColumns):
        item = QtWidgets.QTableWidgetItem()
        self.ui.dataTable.setHorizontalHeaderItem(i, item)
        item2 = self.ui.dataTable.horizontalHeaderItem(i)
        item2.setText(key)
        
    #displayNamesQuery = 'SELECT * gcmsTests'
    #displayResults = self.db.query(displayNamesQuery) 
    #print(displayResults)
    
    #list tests 
    for i, value in enumerate(GSMS_TESTS_LISTS): 
        print('Current Test: ', value)
        item = QtWidgets.QTableWidgetItem()
        item.setText(value)
        self.ui.dataTable.setItem(i, 0, item)
        
        #TODO: search for the display name 
        displayQuery = 'SELECT * FROM gcmsTests WHERE testName = ?'
        
        self.db.execute(displayQuery, [value,])
        result = self.db.fetchone()
        print(f'Query Result: {result}')
        
        if(result): 
            displayNameItem  = QtWidgets.QTableWidgetItem() 
            displayNameItem.setText(result[0])
            self.ui.dataTable.setItem(i, 1, displayNameItem) 
        
        item2 = QtWidgets.QTableWidgetItem() 
        item2.setText(str(1))
        self.ui.dataTable.setItem(i, 4, item2) 
    
        #go down each column and determine if there is a match
        # print(i, value)
        for column in range(initalColumns, self.ui.dataTable.columnCount()):
            header_item = self.ui.dataTable.horizontalHeaderItem(column)
            if header_item is not None:
                column_name = header_item.text()

                result = search_list_of_lists(testsResults,[column_name, value] )
                
                if result is not None: 
                    #print(result)
                    
                    #value
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(str(result[2]))
                    self.ui.dataTable.setItem(i, column, item) 
                    
                    #So 
                    #item = QtWidgets.QTableWidgetItem()
                    #item.setText(str(result[3]))
                    #self.ui.dataTable.setItem(i, 3, item)
                    
                    #recovery  
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(str(result[3]))
                    self.ui.dataTable.setItem(i, 3, item)
                    
                    #unit 
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(result[4])
                    self.ui.dataTable.setItem(i, 2, item) 
                    
    
    #TODO: add the item changed thing 
    #self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test'))

    self.ui.createGcmsReportBtn.clicked.connect(lambda: chmReportHandler(self, GSMS_TESTS_LISTS)); 
    
def chmReportHandler(self, tests):
    #FIXME: adjust based on the sample information 
    #FIXME: crashes when doing gcms to icp without closing program 
    print('[FUNCTION]: chmReportHandler')
    print('*Tests: ', tests)
    
    initalColumns = 5; 
    totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    
    sampleData = {}
    unitType = []
    recovery = []
    displayNames = []
    
    for col in range(initalColumns, totalSamples + initalColumns): 
        currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
        print('currentJob Test: ', currentJob)
        jobValues = []
        for row in range(totalTests): 
            try: 
                currentItem = self.ui.dataTable.item(row, col).text()
                jobValues.append(currentItem)
            except: 
                jobValues.append('ND')
                
        sampleData[currentJob] = jobValues
        #print(currentJob, sampleData[currentJob])
        
    for row in range(totalTests): 
        try: 
            testsName = self.ui.dataTable.item(row, 1).text()
            print('Row: ',row, 'TestName: ', testsName)
            if(testsName): 
                displayNames.append(testsName)
            else: 
                displayNames.append(tests[row])
                
        except: 
            print("Error: appending test name")
            displayNames.append(tests[row])
        
        try: 
            currentVal = self.ui.dataTable.item(row, 2).text()
            unitType.append(currentVal)
        except: 
            unitType.append('')
        
        try: 
            recoveryVal = self.ui.dataTable.item(row, 3).text()
            
            if(is_float(recoveryVal)): 
                recovery.append(float(recoveryVal))
            else: 
                recovery.append(recoveryVal) 
        except: 
            recovery.append('')       
            
    createChmReport(self.clientInfo, self.jobNum, self.sampleNames, sampleData, displayNames, unitType, recovery)


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
        except: 
            #item is not in the database yet 
            print('Error: selected Text was None') 
            chmClearDefinedTestsValues(self)
            self.ui.gcmsTxtName.setText(selectedTests.text())
            
            
def chmLoadTestsNames(self): 
    
    chmClearDefinedTestsValues(self); 
    self.ui.gcmsDefinedtests.clear()
    self.ui.testsInputLabel.clear()

    getTestNamesQuery = 'SELECT testName FROM gcmsTests ORDER BY testName COLLATE NOCASE ASC'
    testNames = self.db.query(getTestNamesQuery)           
    
    print(testNames)
    
    for test in testNames: 
        self.ui.gcmsDefinedtests.addItem(test[0])

def chmClearDefinedTestsValues(self): 
    self.ui.gcmsDisplayName.clear()
    self.ui.gcmsTxtName.clear()
    self.ui.gcmsUnitType.clear()
    self.ui.gcmsRefValue.clear()
    self.ui.gcmsComment.clear() 
        
        
        
#******************************************************************
#    Chemisty Database Section 
#****************************************************************** 

def loadChmDatabase(self): 
    print('[FUNCTION]: loadChmDatabase, Loading Existing Data'); 
    
    TableHeader = ['Sample Number', 'Tests', 'Test Values', 'Standard Value', 'Unit Value', 'Job Num', 'Delete']
    chmTable = self.ui.chmInputTable 

    #TODO: maybe move this somewhere else 
    self.formatTable(chmTable) ;

    results = loadChmTestsData(self.db) 
    #print(results)
    
    chmTable.setRowCount(len(results))
    chmTable.setColumnCount(len(TableHeader))
    chmTable.setHorizontalHeaderLabels(TableHeader)
    
    # hide the vertical rows 
    chmTable.verticalHeader().setVisible(False)
    
    
    for i, result in enumerate(results):
        for j in range(len(TableHeader)-1):
            data = str(result[j]) 
            item = QTableWidgetItem(data)
            item.setTextAlignment(Qt.AlignCenter)
            
            chmTable.setItem(i, j, item)     

        #TODO: add the edit button 
        deleteBtn = QPushButton("Delete")
        editbtn = QPushButton('Edit')
        chmTable.setCellWidget(i ,6, deleteBtn)
        deleteBtn.clicked.connect(lambda _, row=i: chmTableDeleteRow(self, row));
        
def chmTableDeleteRow(self, row): 
    print(f'[FUNCTION]: chmTableDeleteRow, row to delete {row}')
    
    sampleNum = self.ui.chmInputTable.item(row, 0).text()
    testsName = self.ui.chmInputTable.item(row, 1).text()
    print(f'Sample Num: {sampleNum}, Tests Name: {testsName}')
    
    self.ui.chmInputTable.removeRow(row)
    #deleteChmData(self.db, sampleNum, testsName)


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
    
        self.ui.gcmsTestsValueWidget.setEnabled(True)
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
def on_gcmsAddTestsBtn_2_clicked(self): 
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
            
    if(sum(errorCheck) == 0): 
        sampleNum = testNum + '-' + sampleNum; 
        
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
                
                matching_items = self.ui.gcmsTestsLists.findItems(sampleNum, Qt.MatchExactly) 
                if not matching_items: 
                    self.ui.gcmsTestsLists.addItem(sampleNum)
                
                chmClearSampleJob(self) 
                
            if(x == QMessageBox.No):
                chmClearSampleJob(self) 
                
            if(x == QMessageBox.Cancel):
                pass 
            
        else: 
            addToChmTestsData(self.db, sampleNum, testName, sampleVal, standards, units, testNum)
            self.ui.gcmsTestsLists.addItem(sampleNum)
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

        
def chmClearSampleJob(self): 
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear() 
        
#FIXME: not used anywhere 
def gcmsClearSideData(self): 
    self.ui.gcmsStandardVal.clear()
    self.ui.gcmsUnitVal.clear()
    self.ui.gcmsTests.clear() 
        
def chmClearEnteredTestsData(self): 
    self.ui.gcmsTestsValueWidget.setEnabled(False)
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
    self.ui.gcmsTestsLists.clear()


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
    existingTests = self.chmGetTestsValues()        
    currentText = self.ui.testsInputLabel.text()


 
    if(currentText != '' and currentText not in existingTests): 
        #clear values 
        chmClearDefinedTestsValues(self)
        self.ui.testsInputLabel.clear()
        self.ui.gcmsDefinedtests.addItem(currentText)

        totalItems = len(self.chmGetTestsValues())
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
    

@pyqtSlot()
def on_chmDefinedtests_clicked(self): 
    chmLoadTestsData(self)
        
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
    
