import sqlite3
from base_logger import logger
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

from modules.constants import REPORT_NUM, REPORT_STATUS
from modules.dbFunctions import getTestsName, getTestsInfo, getTestsTextName, getJobStatus, updateJobStatus
from modules.dialogBoxes import createdReportDialog, showErrorDialog
from modules.excel.create_chm_excel import createChmReport
from modules.utilities import removeIllegalCharacters, is_float 
from modules.reports.report_utils import (
    loadClientInfo,  formatReportTable, disconnect_all_slots, populateSamplesContainer, 
    populateReportAuthorDropdowns, EmptyDataTableError, updateReport
)
from widgets.widgets import SampleNameWidget 

#******************************************************************
#    CHM Report Loader
#******************************************************************

#TODO: scan in the TXT Tests, scan in from Defined Tests too 
#TODO: fix the error checking 
#TODO: make sure we set limits for the table items (limit text and to nums for some)
#TODO: we can have items with the same job num, report type but need to make sure the parameter is different 
#FIXME: if the row column doesn't have the data make it so we can't edit it in 
def chmReportLoader(self): 
    self.logger.info('Entering chmLoader...')
       
    self.logger.info('Preparing to load client information...') 
    loadClientInfo(self)
    
    #FIXME: this is the error, what happens when the data isn't added into the file, 
    # we have to just scan the text file 
    
    self.logger.info('Getting CHM Tests List and Results ...')  
    chmTestsLists, testResults = chmGetTestsList(self) 

    dataTable = self.ui.dataTable
    rowCount = len(chmTestsLists) 
    
    self.logger.info('Preparing the CHM client information and formatting table ...')  
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
    #FIXME: there seems to be a problem when the signals and connects when we call them keeps on adding connection signals 

    disconnect_all_slots(self.ui.dataTable)
    disconnect_all_slots(self.ui.createGcmsReportBtn)

    col_length: 6 
        
    self.ui.dataTable.itemChanged.connect(lambda item: handleTableChange(self, item))
    self.ui.createGcmsReportBtn.clicked.connect(lambda: chmReportHandler(self, 6, chmTestsLists)); 
    
 
def chmGetTestsList(self): 
    self.logger.info('Enter chmGetTestsList')
    
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
    
    else: 
        #FIXME: check this thing 
        pass; 
                    
    #CHM_TESTS_LISTS = sorted(CHM_TESTS_LISTS)
   
    self.logger.info('Returning Data') 
    self.logger.info(f'CHM_TESTS_LISTS:{CHM_TESTS_LISTS}')
    self.logger.info(f'testResults: {testResults}')

    return CHM_TESTS_LISTS, testResults 
   
def chmInitialize(self, table, rowCount): 
    self.logger.info(f'Entering chmInitialize with parameter: table: {table.objectName()} rowCount: {rowCount}')
    
    columnNames = [
        'Tests Name', 
        'Text Name',
        'Display Name',
        'Unit', 
        'Distal factor',
        'Standard Recovery',
    ]
    
    #colCount = len(columnNames) + int(self.clientInfo['totalSamples'])
    colCount = len(columnNames) + len(self.sampleNames)
    
    populateSamplesContainer(self.ui.samplesContainerLayout_2, self.sampleNames)

    # Format Report Table 
    formatReportTable(table, rowCount, colCount) 
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    # Initialize the columns 
    for i, name in enumerate(columnNames):
        item = QtWidgets.QTableWidgetItem(name)
        table.setHorizontalHeaderItem(i, item)
        
    # Populate with sample names in the table 
    for i , (key, value) in enumerate(self.sampleNames.items(), start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(key)
        table.setHorizontalHeaderItem(i, item)
        
    # Set all the sample items to be center
    for col in range(2, colCount):
        for row in range(rowCount): 
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, col, item)
        
    self.logger.debug(f'Total Column Size: {table.columnCount()}' )
                     
#******************************************************************
#    CHM Report Handler Function  
#******************************************************************
    
#FIXME: adjust based on the sample information 
#TODO: move the message to the center of the screen and change the dimensions  self.portion
@pyqtSlot() 
def chmReportHandler(self, columnLength,  tests):
    self.logger.info(f'Entering chmReportHandler with parameters: columnLength: {columnLength}, tests: {tests}')
    
    totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    
    sampleData = {}
    unitType = []
    recovery = []
    displayNames = []

    try:  
        # Check if the data files are not empty 
        if(self.ui.dataTable.rowCount() == 0): 
            raise EmptyDataTableError("Data table is empty. Cannot create Excel file.") 
    
    except EmptyDataTableError as error:
        print(error)
        self.logger.error('Data table is empty. Cannot create Excel file') 
        showErrorDialog(self, 'Cannot create report', f'Data table is empty. Cannot create excel file for Job: {self.jobNum}')
        return 
    
    except Exception as e:
        print("Unexpected error:", e) 
        return 
    
    # Retrieve the Sample Input Data 
    self.logger.info('retrieving sample input data')
    for col in range(columnLength, totalSamples + columnLength): 
        currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
        
        self.logger.debug(f'Current Job Tests: {currentJob}')
        jobValues = []
        for row in range(totalTests): 
            try: 
                currentItem = self.ui.dataTable.item(row, col).text()
                jobValues.append(currentItem)
            except: 
                jobValues.append('ND')
                
        sampleData[currentJob] = jobValues
        self.logger.debug(f'Current Job: {currentJob}, Data: {sampleData[currentJob]}')
        
    # Retrieve the Tests Info 
    for row in range(totalTests): 
        try: 
            testsName = self.ui.dataTable.item(row, 1).text()
            self.logger.debug(f'Row: {row} TestName: {testsName}')
            displayNames.append(testsName if testsName else tests[row])
        except: 
            self.logger.error("problem when appending test name")
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
            
    self.logger.info('Preparing to create CHM Report')
    try: 
        filePath, fileName = createChmReport(self.clientInfo, self.jobNum, self.sampleNames, sampleData, displayNames, unitType, recovery) 
        createdReportDialog(self, fileName)
        
        jobCreatedNum = 1 
        self.logger.info(f'CHM Report Creation Successful: jobCreated: {jobCreatedNum}')  
            
    except: 
        #TODO: debating purring the error here so it's more clean 
        jobCreatedNum = 0; 
        self.logger.warning(f'CHM Report Creation Failed: jobCreated: {jobCreatedNum}')
        
    if(jobCreatedNum == 1): 
        updateReport(self.ui.statusHeaderLabel, self.tempDB, self.jobNum, self.reportNum)
        

    # TODO: Save the other client info 
    # TODO: Authors, client info, samples name. sample data 

#TODO: Move this into a report_utils.py so both functions can have access to this 
#TODO: need to move this can account for both ICP and CHM reports 
#FIXME: this is where it crashes when we try to edit that data
#FIXME: might be easier to connect and disconnect the handles based on what table is getting accessed   
@pyqtSlot() 
def handleTableChange(self, item):
    self.logger.info('Entering handleTableChange')
    
    table = self.ui.dataTable 
    row = item.row()
    column = item.column()
    #TODO: have an error for this thing 
    value = item.text()

    #self.logger.debug(f'Row: {repr(row)}, column: {repr(column)}, value: {repr(value)}')

    #updatedValue = table.item(row, column).text()
    #column_name = table.horizontalHeaderItem(column).text()
    self.logger.info(f'Report Status: {self.reportNum}')
    
    # ICP create state  
    if(self.reportNum == 1): 
        
        pass; 
    
    # CHM Create State
    if(self.reportNum == 2): 
        
        updatedValue = table.item(row, column).text()
        #column_name = table.horizontalHeaderItem(column).text()

        textNameCol = 1
        textName = table.item(row, textNameCol)

        #TODO: need to check if it is empty or not 
        if(textName and self.reportManager): 
            column_name = table.horizontalHeaderItem(column).text()
            textName = textName.text()

            self.logger.info(f'Col Name: {column_name}, TEXT: {textName}, NEW VAL: {updatedValue}')
            
            if(column == 2): # Update the display name  
                testType = self.reportManager.tests[textName]
                
                if(isinstance(testType, chemReportTestData)): 
                    self.reportManager.tests[textName].update_displayName(updatedValue)
                
            if(column == 3): # Update the unit value 
                pass; 
            
            if(column == 5): # Update the standard  
                pass; 
            
            if(column > 5): # Update the samples values
                #FIXME: if this doesn't exist we have to add it 
                testNum = self.reportManager.tests[textName].testNum
            
                if(column_name in self.reportManager.getSamples().keys()): 
                    self.reportManager.samples[column_name].update_data(testNum, updatedValue)
                else:
                    parts = column_name.split("-", 1)
                    self.reportManager.samples[column_name] = chemReportSampleData(parts[0], parts[1], column_name)
                    self.reportManager.samples[column_name].update_data(testNum, updatedValue)


#******************************************************************
#    CHM Classes 
#******************************************************************

#TODO: is it easier to just scan all of the information in or just to pass the data lol 
class chemReportTestData: 
    def __init__(self, testNum, testName, textName, displayName, unitType):  
        self.testNum = testNum 
        self.testName = testName 
        self.textName = textName 
        self.displayName = displayName 
        self.unitType = unitType 

    def update_displayName(self, newName): 
        prevDisplayName = self.displayName
        self.displayName = newName
        logger.debug(f'Updating Display Name: {repr(self.textName)} from {repr(prevDisplayName)} to {repr(self.displayName)}')
         
         
#FIXME: this is too complicated, just need to have something that contains samples in a dict and their values
class chemReportSampleData: 
    def __init__(self, sampleNum, jobNum, sampleName): 
        self.sampleNum = sampleNum 
        self.jobNum = jobNum 
        self.sampleName = sampleName 
        
        # Data consists of data[testNum] = [value, recovery, unitType]
        self.data = {}
       
    def add_data(self, testNum, testValue, recovery, unitType): 
        self.data[testNum] = testValue
        logger.debug(f'{self.sampleName} ADDED {testNum}: {self.data[testNum]}')
        
        #self.data[testNum] = [testValue, recovery, unitType]
        #print(f'{self.sampleName} ADDED {testNum}: {self.data[testNum]}')
        
    #TODO: might be easier to just scan the data instead of loading it into the thing like this 
    def update_data(self, testNum, newValue):
        
        if(testNum in self.data): 
            existing_data = self.data[testNum]
            self.data[testNum] = float(newValue)
            logger.debug(f'{self.sampleName} UPDATED {testNum} FROM {existing_data} TO {self.data[testNum]}')
            
        else: 
            #TODO: fix this somehow so we can account for the recovery and unitType
            #self.data[testNum] = [newValue, None, None]
            self.data[testNum] = float(newValue)
            logger.debug(f'{self.sampleName} ADDED {testNum} TO {float(newValue)}')

    def get_data(self): 
        return self.data; 
        
class chemReportManager: 
    def __init__(self, db): 
        self.db = db 

        # chemReportSampleData Info 
        # Samples[sampleName] = chemReportSampleData.data[testNum] = [value, recovery, unitType] 
        # Samples[sampleName] = {
        #   testNum: value, 
        #}
        self.samples = {}

        # chemReportTestData Info 
        self.tests = {}
        
    def init_samples(self, sample_list):
        logger.info(f'Entering init_samples with parameters: sample_list: {sample_list}')

        testData = {}
        for test in sample_list: 
            sampleNum = test[0]
            testNum = test[1] #how to add the testNum for selection 
            testValue = test[2]
            recovery = test[3]
            unitType = test[4]
            jobNum = test[5]
            sampleName = f'{test[5]}-{test[0]}'
            
            '''  
            if(sampleName in self.samples): 
                self.samples[sampleName].add_data(testNum, testValue, recovery, unitType)
                
            else:  
                testData = chemReportSampleData(sampleNum, jobNum, sampleName)    
                testData.add_data(testNum, testValue, recovery, unitType)
                self.samples[sampleName] = testData

            '''

            # Check if sample exists. If not, create a new one.
            if sampleName not in self.samples:
                logger.debug(f'Current Sample: {sampleName} not in {self.samples}')
                self.samples[sampleName] = chemReportSampleData(sampleNum, jobNum, sampleName)

            # Add data to the existing sample
            self.samples[sampleName].add_data(testNum, testValue, recovery, unitType)
            
        #FIXME: add the other samples into this  
        
        logger.info(f'Returning self.samples: {self.samples}')

        return self.samples 

    def load_samples(self): 
        pass; 
    def load_tests(self): 
        pass; 

    def init_test(self, test_list):  
        logger.info(f'Entering init_test with parameters: test_list: {test_list}')
        
        testsInfo = {}
        testNums = []
        
        for textName in test_list: 
            logger.debug(f'Current textName: {textName}')
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
                logger.debug(f'self.tests {textName} added the value {testsInfo}')
            else: 
                #TODO: if we cannot find the item 
                self.tests[textName] = textName
                logger.debug(f'self.tests {textName} added the value {textName}')
                
        #self.samples = testsInfo
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
        logger.info(f'Entering populateTableRow in chemReportView with parameters: row: {row}, col: {col}, value: {value}')
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
        logger.info(f'Entering populateTreeTests in chemReportView class with parameters: testsLists: {testLists}')
        
        testNameCol = 0; 
        textNameCol = 1;
        displayNameCol = 2; 
        unitTypeCol = 3; 
        distilCol = 4; 
        recoveryValCol = 5; 
        
        self.rowNums = {}

        #TODO: should i sort this in alpha order? 
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
        logger.info(f'Entering populateTreeSamples in chemReportView class with parameters: samples_info: {samples_info}')

        unitTypeCol = 3; 
        recoveryCol  = 5; 

        # Determine which call we are in for the sample 
        logger.debug(f'Preparing to populate tree samples... ')
        for col_index in range(5, self.table.columnCount()): 
            logger.debug(f'Col Index: {col_index}')

            
            col_name_exist = self.table.horizontalHeaderItem(col_index)
            
            if(col_name_exist):
                col_name = self.table.horizontalHeaderItem(col_index).text()
            
                if(col_name in samples_info): 
              
                    sampleInfo = samples_info[col_name]
                    sampleData = sampleInfo.get_data()
                    
                    for key, value in sampleData.items(): 
                        logger.debug(f'Col: {col_index}, key: {key}, value: {value}') 
                        if(key in self.rowNums):
                            row_index = self.rowNums[key] 
                            testVal = value

                            #FIXME: refactor all of this bullshit
                            #testVal = value[0]
                            #recoveryVal = value[1]
                            #unitTypeVal = value[2]
                            
                            #self.populateTableRow(row_index, unitTypeCol, 1, 1,unitTypeVal) 
                            #self.populateTableRow(row_index, recoveryCol, 1, 1,recoveryVal)
                            self.populateTableRow(row_index, col_index, 1, 1,testVal)

    def applyDistilFactor(self, distilFactor): 
        distilCol = 4; 
            
        for row in range(self.table.rowCount()): 
            self.populateTableRow(row, distilCol, 1, 0, distilFactor)

        #TODO: apply this onto all of the items (do previous?)
   

