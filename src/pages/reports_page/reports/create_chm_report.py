import sqlite3
from base_logger import logger
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import  QHeaderView
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QKeyEvent 

from modules.constants import REPORT_NUM, REPORT_STATUS
from modules.dbFunctions import getTestsName, getTestsInfo, getTestsTextName, getJobStatus, updateJobStatus
from modules.utils.logic_utils import removeIllegalCharacters, is_float 
from modules.widgets.dialogs import createdReportDialog, showErrorDialog

from pages.reports_page.excel.create_chm_excel import createChmReport
from pages.reports_page.reports.chm_report_models import chemReportSampleData, chemReportTestData, chemReportManager, chemReportView
from pages.reports_page.reports.report_utils import (
    loadClientInfo,  formatReportTable, disconnect_all_slots, populateSamplesContainer, 
    populateReportAuthorDropdowns, EmptyDataTableError, updateReport, handleTableChange,
    createExcelErrorCheck, retrieveAuthorInfo, retrieveParamComment
)

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
       
    loadClientInfo(self)
    
    #FIXME: this is the error, what happens when the data isn't added into the file, 
    # we have to just scan the text file 
    
    self.logger.info('Getting CHM Tests List and Results ...')  
    chmTestsLists, testResults = chmGetTestsList(self) 

    dataTable = self.ui.dataTable
    rowCount = len(chmTestsLists) 
    
    self.logger.info('Preparing the CHM client information and formatting table ...')  
    chmInitialize(self, dataTable, rowCount)  
    
    # Signals
    disconnect_all_slots(self.ui.dataTable)
    disconnect_all_slots(self.ui.createChmReportBtn)  
    
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

    # Connect Signals         
    self.ui.dataTable.itemChanged.connect(lambda item: handleTableChange(self, item))
    self.ui.createChmReportBtn.clicked.connect(lambda: chmReportHandler(self, 6, chmTestsLists)); 
    
 
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

    
    # TODO: have a test list cleaner and tester that makes sure it works 
     
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

    
    # General Error Checking before creating excel document 
    if(createExcelErrorCheck(self)): 
        return 
    
    # Retrieve the authors info     
    authorsInfo = retrieveAuthorInfo(self, self.ui.authorOneDropDown.currentText(), self.ui.authorTwoDropDown.currentText())
    print(authorsInfo)
    
    # Retrieve the report bottom comment 
    reportComment = retrieveParamComment(self, 'CHM', self.parameter)
    print(reportComment)
    
    
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
        filePath, fileName = createChmReport(self.clientInfo, self.jobNum, authorsInfo, reportComment, self.sampleNames, sampleData, displayNames, unitType, recovery) 
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
    # TODO: can save the data through matching the rows 

