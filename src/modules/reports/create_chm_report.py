
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)

from PyQt5.QtGui import QIntValidator, QDoubleValidator, QKeyEvent 

from modules.constants import REPORT_NUM 
from modules.dbFunctions import getTestsName, getTestsInfo, getTestsTextName, getJobStatus, updateJobStatus
from modules.dialogBoxes import createdReportDialog
from modules.excel.create_chm_excel import createChmReport
from modules.utilities import removeIllegalCharacters, is_float 
from modules.reports.report_utils import loadClientInfo,  formatReportTable, updateSampleNames
from widgets.widgets import SampleNameWidget 

#******************************************************************
#    CHM Report Loader
#******************************************************************

#TODO: scan in the TXT Tests, scan in from Defined Tests too 
#TODO: fix the error checking 
#TODO: make sure we set limits for the table items (limit text and to nums for some)
def chmReportLoader(self): 
    print('[FUNCTION]: chmLoader(self)')
    # Updating some basic information 
    self.ui.createIcpReportBtn.setVisible(False)
    self.ui.createGcmsReportBtn.setVisible(True)
    self.ui.icpDataField.hide() 
  
    loadClientInfo(self)
    
    #FIXME: this is the error, what happens when the data isn't added into the file, we have to just scan the text file 
    chmTestsLists, testResults = chmGetTestsList(self) 

    dataTable = self.ui.dataTable
    rowCount = len(chmTestsLists) 
    
    # Prepare the chm client Info and the table 
    chmInitialize(self, dataTable, rowCount)    
    
    # Prepare the objects 
    self.reportManager = chemReportManager(self.tempDB)
    self.reportView = chemReportView(dataTable)
    
    # Initiate the data 
    testsData = self.reportManager.init_test(chmTestsLists)
    sampleData = self.reportManager.init_samples(testResults)
    
    # Populate the table         
    self.reportView.populateTreeTests(testsData) 
    self.reportView.populateTreeSamples(sampleData)
    self.reportView.applyDistilFactor(self.dilution)

    # Signals
    self.ui.dataTable.itemChanged.connect(lambda item: handleTableChange(self, item))
    self.ui.createGcmsReportBtn.clicked.connect(lambda: chmReportHandler(self, 6, chmTestsLists)); 
    
    
def chmGetTestsList(self): 
    print('[FUNCTION]: chmGetTestsList(self)')
    print(self.sampleTests)
    CHM_TESTS_LISTS = []

    unitTypeRow = 4

    testsQuery = 'SELECT * FROM chemTestsData WHERE JobNum = ?' 
    testResults = self.tempDB.query(testsQuery, (self.jobNum,)) 

    # Checking CHM test lists  
    for (currentJob , testList) in self.sampleTests.items(): 
        for item in testList: 
            temp = removeIllegalCharacters(str(item)) 
            if(temp not in CHM_TESTS_LISTS and 'ICP' not in temp):          
                CHM_TESTS_LISTS.append(temp)
     
    # loop through the tests that users have manually added to the thing 
    if(testResults):
        for item in testResults:
            testTextName = getTestsTextName(self.tempDB, item[1])
            print(f'Test Name: {testTextName}')
            if testTextName not in CHM_TESTS_LISTS:
                CHM_TESTS_LISTS.append(testTextName)
                    
    
    #print('****UNSORTED CHM TESTS ')
    #print(CHM_TESTS_LISTS)  
    #CHM_TESTS_LISTS = sorted(CHM_TESTS_LISTS)
    print('***SORTED CHM TESTS')
    print(CHM_TESTS_LISTS) 
    
    return CHM_TESTS_LISTS, testResults 
   
def chmInitialize(self, table, rowCount): 
    print('[FUNCTION]: chmInitialize(self, table, rowCount, colCount, columnNames)')

    columnNames = [
        'Tests Name', 
        'Text Name',
        'Display Name',
        'Unit', 
        'Distal factor',
        'Standard Recovery',
    ]
    
    colCount = len(columnNames) + int(self.clientInfo['totalSamples'])
    
    # Load the sample names in client Info Section 
    for i, (key,value) in enumerate(self.sampleNames.items()):
        sampleItem = SampleNameWidget(key, value)
        self.ui.samplesContainerLayout.addWidget(sampleItem)
        sampleItem.edit.textChanged.connect(lambda textChange, key = key: updateSampleNames(self.sampleNames,textChange, key))

    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    self.ui.samplesContainerLayout.addItem(spacer)

    # Format Report Table 
    formatReportTable(table, rowCount, colCount) 
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    # Initialize the columns 
    for i, name in enumerate(columnNames):
        item = QtWidgets.QTableWidgetItem(name)
        table.setHorizontalHeaderItem(i, item)
        
    # Populate with sample names 
    for i , (key, value) in enumerate(self.sampleNames.items(), start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(key)
        table.setHorizontalHeaderItem(i, item)
        
    # Set all the sample items to be center
    for col in range(2, colCount):
        for row in range(rowCount): 
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, col, item)

                     
#******************************************************************
#    CHM Report Handler Function  
#******************************************************************
    
#FIXME: adjust based on the sample information 
#TODO: move the message to the center of the screen and change the dimensions  self.portion
@pyqtSlot() 
def chmReportHandler(self, columnLength,  tests):
    print('[FUNCTION]: chmReportHandler(self, tests)')
    print('*Tests: ', tests)
    
    totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    
    sampleData = {}
    unitType = []
    recovery = []
    displayNames = []
    
    # Retrieve the Sample Input Data 
    for col in range(columnLength, totalSamples + columnLength): 
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
        
    # Retrieve the Tests Info 
    for row in range(totalTests): 
        try: 
            testsName = self.ui.dataTable.item(row, 1).text()
            print('Row: ',row, 'TestName: ', testsName)
            displayNames.append(testsName if testsName else tests[row])
        except: 
            print("Error: appending test name")
            displayNames.append(tests[row])
        
        try: 
            currentVal = self.ui.dataTable.item(row, 3).text()
            unitType.append(currentVal)
        except: 
            unitType.append('')
        
        try: 
            recoveryVal = self.ui.dataTable.item(row, 5).text()
            recovery.append(float(recoveryVal) if is_float(recoveryVal) else recoveryVal)
        except: 
            recovery.append('')       
        
    # Check and update the job status 
    try: 
        jobStatus = getJobStatus(self.tempDB, self.jobNum, self.reportNum)
        print(f'Current Job Status: : {jobStatus}')
        
        if(jobStatus == 0): 
            completeJobStatus = 1  
            updateJobStatus(self.tempDB, self.jobNum, self.reportNum, completeJobStatus) 
        
    except Exception as error: 
        print(error)
            
    createChmReport(self.clientInfo, self.jobNum, self.sampleNames, sampleData, displayNames, unitType, recovery)

    createdReportDialog('test.py')

    # Save the other client info 
    # Authors, client info, samples name. sample data

#TODO: Move this into a report_utils.py so both functions can have access to this 
#TODO: need to move this can account for both ICP and CHM reports 
@pyqtSlot() 
def handleTableChange(self, item):
    
    table = self.ui.dataTable 
    row = item.row()
    column = item.column()
    value = item.text()

    #updatedValue = table.item(row, column).text()
    #column_name = table.horizontalHeaderItem(column).text()
    
    # ICP create state  
    if(self.reportNum == 1): 
        pass; 
    
    # CHM Create State
    if(self.reportNum == 2): 

        updatedValue = table.item(row, column).text()
        column_name = table.horizontalHeaderItem(column).text()

        textNameCol = 1
        textName = table.item(row, textNameCol)

        #TODO: need to check if it is empty or not 
        if(textName and self.reportManager): 
            textName = textName.text()
            print(f'Col Name: {column_name}, TEXT: {textName}, NEW VAL: {updatedValue}')
            
            if(column == 2): 
                # Update the display name 
                testType = self.reportManager.tests[textName]
                
                if(isinstance(testType, chemReportTestData)): 
                    self.reportManager.tests[textName].update_displayName(updatedValue)
                
            if(column == 3): 
                # Update the unit value
                pass; 
            
            
            if(column == 5): 
                # Update the standard 
                pass; 
            
            if(column > 5):
                # Update the samples values
                testNum = self.reportManager.tests[textName].testNum
                self.reportManager.samples[column_name].update_data(testNum, updatedValue)


#******************************************************************
#    CHM Classes 
#******************************************************************

#TODO: need to convert the classes into dirct 
class chemReportTestData: 
    def __init__(self, testNum, testName, textName, displayName, unitType):  
        self.testNum = testNum 
        self.testName = testName 
        self.textName = textName 
        self.displayName = displayName 
        self.unitType = unitType 

    def update_displayName(self, newName): 
        print(f'{self.textName} BEFORE DISPLAY NAME: {self.displayName}')
        self.displayName = newName
        print(f'{self.textName} UPDATED DISPLAY NAME: {self.displayName}')

class chemReportSampleData: 
    def __init__(self, sampleNum, jobNum, sampleName): 
        self.sampleNum = sampleNum 
        self.jobNum = jobNum 
        self.sampleName = sampleName 
        
        self.data = {}
        
    def add_data(self, testNum, testValue, recovery, unitType): 
        self.data[testNum] = [testValue, recovery, unitType]
        print(f'{self.sampleName} ADDED {testNum}: {self.data[testNum]}')
        
    #TODO: might be easier to just scan the data instead of loading it into the thing like this 
    def update_data(self, testNum, newValue):
        
        if(testNum in self.data): 
            existing_data = self.data[testNum]
            print(f'{self.sampleName} BEFORE {testNum}: {existing_data}')
            
            existing_data[0] = newValue
            self.data[testNum] = existing_data
            
            print(f'{self.sampleName} UPDATED {testNum}: {self.data[testNum]}')
        else: 
            #TODO: fix this somehow so we can account for the recovery and unitType
            self.data[testNum] = [newValue, None, None]

    def get_data(self): 
        return self.data; 
        
class chemReportManager: 
    def __init__(self, db): 
        self.db = db 

        # chemReportSampleData Info
        self.samples = {}

        # chemReportTestData Info 
        self.tests = {}
        
    def init_samples(self, sample_list):
        print(f'init_test: {sample_list}')

        testData = {}
        for test in sample_list: 
            sampleNum = test[0]
            testNum = test[1] #how to add the testNum for selection 
            testValue = test[2]
            recovery = test[3]
            unitType = test[4]
            jobNum = test[5]
            sampleName = f'{test[5]}-{test[0]}'
            
            if(sampleName in self.samples): 

                self.samples[sampleName].add_data(testNum, testValue, recovery, unitType)
                
            else:  
                testData = chemReportSampleData(sampleNum, jobNum, sampleName)    
                testData.add_data(testNum, testValue, recovery, unitType)
                self.samples[sampleName] = testData
             
        print(f'self.samples: {self.samples}')

        return self.samples 

    def load_samples(self): 
        pass; 
    def load_tests(self): 
        pass; 

    def init_test(self, test_list): 
        print(f'init_samples: {test_list}') 
        
        testsInfo = {}
        testNums = []
        
        for textName in test_list: 
            print(textName)
            testData = getTestsInfo(self.db, textName)
    
            if(testData): 
                testNum = testData[0]
                testsName = testData[1]
                textName = testData[2]
                displayName = testData[3]
                recovery = testData[4]
                unitType = testData[5]
                
                if(testNum not in testNums): 
                    testNums.append(testNum);
                
                testsInfo = chemReportTestData(testNum, testsName, textName, displayName, unitType) 
                self.tests[textName] = testsInfo 
            else: 
                #TODO: if we cannot find the item 
                self.tests[textName] = textName
                
        #self.samples = testsInfo
        print(f'self.tests: {self.tests}')
        
        return self.tests 
    
    def getSamples(self): 
        return self.samples
    
    def getTests(self): 
        return self.tests 
    
    def print_samples(self): 
        for sampleName, sampleData in self.samples.items(): 
            print(sampleName)
            print(sampleData.data)
    
        
class chemReportView: 
    def __init__(self, table): 
        self.table = table
   
    def populateTableRow(self, row, col, alignment, editable, value): 
        item = QtWidgets.QTableWidgetItem()  
        if(alignment == 1):   
            item.setTextAlignment(Qt.AlignCenter)
        
        if(editable == 0):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
          
        else: 
            item.setFlags(item.flags() | Qt.ItemIsEditable) 
            
        # Check data type and convert if necessary
        if isinstance(value, (int, float)):
            value = str(value)  # Prevent spinbox for numeric data
        
        item.setData(Qt.DisplayRole, value)
        self.table.setItem(row, col, item)     
   
    def populateTreeTests(self, testLists): 
        testNameCol = 0; 
        textNameCol = 1;
        displayNameCol = 2; 
        unitTypeCol = 3; 
        distilCol = 4; 
        recoveryValCol = 5; 
        
        self.rowNums = {}

        #TODO: should i sort this in alph order? 
        for row, (key, value) in enumerate(testLists.items()): 
            if(isinstance(value, chemReportTestData)): 
                self.populateTableRow(row, testNameCol, 0, 0, value.testName)
                self.populateTableRow(row, textNameCol, 0, 0, value.textName)
                self.populateTableRow(row, displayNameCol, 0, 1,value.displayName)

                if(row not in self.rowNums): 
                    self.rowNums[value.testNum ] = row;  
                
            else: 
                self.populateTableRow(row, testNameCol, 0, 0, '')
                self.populateTableRow(row, textNameCol, 0, 0, value)

                self.rowNums[row] = None; 

    #FIXME: Error when loading in existing data 
    def populateTreeSamples(self, samples_info): 
        print('[FUNCTION]: populateTreeSamples(self, samples_info)')
        print(samples_info)

        unitTypeCol = 3; 
        recoveryCol  = 5; 

        # Determine which call we are in for the sample 
        for col_index in range(5, self.table.columnCount()): 
            col_name = self.table.horizontalHeaderItem(col_index).text()

            if(col_name in samples_info): 
                print(f'Col Name: {col_name}')
            
                sampleInfo = samples_info[col_name]
                sampleData = sampleInfo.get_data()
                
                for key, value in sampleData.items(): 
                    print(f'Col: {col_index}, key: {key}, value: {value}') 
                    if(key in self.rowNums):
                        row_index = self.rowNums[key] 
                        testVal = value[0]
                        recoveryVal = value[1]
                        unitTypeVal = value[2]
                        
                        self.populateTableRow(row_index, unitTypeCol, 1, 1,unitTypeVal) 
                        self.populateTableRow(row_index, recoveryCol, 1, 1,recoveryVal)
                        self.populateTableRow(row_index, col_index, 1, 1,testVal)

    def applyDistilFactor(self, distilFactor): 
        distilCol = 4; 
            
        for row in range(self.table.rowCount()): 
            self.populateTableRow(row, distilCol, 1, 0, distilFactor)

        #TODO: apply this onto all of the items (do previous?)
   

