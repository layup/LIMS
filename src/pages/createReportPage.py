from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)

from PyQt5.QtGui import QIntValidator, QDoubleValidator

from modules.excel.chmExcel import createChmReport
from modules.excel.icpExcel import createIcpReport
from modules.dialogBoxes import createdReportDialog
from modules.dbFunctions import *
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *

#TODO: move a lot of these functions to the db fuinctions 
#FIXME: when file is sucessfully created it makes two copies of the dialog box 
#FIXME: when the use info is empty it will crash because it can't scan any of the existing files 
#******************************************************************
#   Create Report Page Setup 
#******************************************************************

def reportSetup(self): 
    #TODO: ERROR could not load TEXT_FILE please try again
 
    # Create a validator to accept only integer input
    validatorInt = QIntValidator(0, 999999) 
    validatorDec = QDoubleValidator(0.0, 999999.99, 3)

    # Set input limits and Validators
    self.ui.jobNumInput.setValidator(validatorInt)
    self.ui.dilutionInput.setValidator(validatorDec)
    
    self.ui.jobNumInput.setMaxLength(6)
    self.ui.dilutionInput.setMaxLength(6)
    
    apply_drop_shadow_effect(self.ui.createReportHeader)

    #load in the authors 
    #TODO: have some error checking and deal with the loadiong section 
    # FIXME: load in the other authors to the section
    authorsList = [item[0] for item in getAllAuthorNames(self.tempDB)]
    authorsList.insert(0, '')
    
    print(authorsList)
    
    self.ui.authorOneDropDown.clear()
    self.ui.authorTwoDropDown.clear()
    
    self.ui.authorOneDropDown.addItems(authorsList)
    self.ui.authorTwoDropDown.addItems(authorsList)
    
    # Connect signals  
    self.ui.NextSection.clicked.connect(lambda: createReportPage(self))

    # Connect create table info
    self.ui.dataTable.itemChanged.connect(lambda item: handleTableChange(self, item))

#******************************************************************
#   Creating Report 
#******************************************************************

@pyqtSlot()
def createReportPage(self, jobNum = None, reportType = None, parameter = None, dilution =None, method2= None):
    print('[FUNCTION]: createReportPage')
        
    # strip the basic informatioin 
    jobNum = jobNum or self.ui.jobNumInput.text().strip()
    reportType = reportType or self.ui.reportType.currentText()
    parameter = parameter or self.ui.paramType.currentText()
    dilution = dilution or self.ui.dilutionInput.text()
    
    print('*JobNumber: ', jobNum)
    print('*ReportType: ', reportType)
    print('*Parameter: ', parameter)
    print('*Dilution: ', dilution )

    dilution = 1 if (dilution == '' or dilution == None) else dilution       
    textFileExists = scanForTXTFolders(jobNum)
    
    errorCheck = [0, 0, 0, 0]     
    errorCheck[0] = 0 if re.match('^([0-9]{6})$', jobNum) else 1 
    errorCheck[1] = 0 if reportType in REPORTS_TYPE else 1
    errorCheck[2] = 0 if parameter != '' else 1
    errorCheck[3] = 0 if textFileExists != '' and textFileExists  else 1    
     
    if(sum(errorCheck) == 0): 
        # Clear existing data from previous jobs
        self.jobNum = jobNum
        self.reportType = reportType
        self.parameter = parameter
        self.dilution = dilution
        
        self.ui.reportsTab.setCurrentIndex(0)
        self.ui.stackedWidget.setCurrentIndex(5) 
        self.clearDataTable()
        self.ui.jobNum.setText(jobNum)
        
        reportNum = REPORT_NUM[self.reportType]
        paramNum = getReportNum(self.tempDB, parameter)[0][0] #TODO: fix this so just returns the num

        #TODO: load the information from database later (front house database)  
        clientInfo, sampleNames, sampleTests = processClientInfo(self.jobNum, textFileExists)

        checkTextFile(self, textFileExists)
        
        self.clientInfo = clientInfo 
        self.sampleNames = sampleNames
        self.sampleTests = sampleTests

        jobResult  = checkJobExists(self.tempDB, jobNum, reportNum)
        
        print(f'SAMPLE NAMES: {self.sampleNames}')
        
        if jobResult is None:  
            # Adding Job to the database
            currentDate = date.today()
            addNewJob(self.tempDB, jobNum, reportNum, paramNum, self.dilution, currentDate)
            self.ui.statusHeaderLabel.setText('NEW')

        else: 
            if(method2 is not True): 
                print('Report Exists')
                print(jobResult)
                
                #TODO: load the report if exists
                loadReportDialog(self)      

    
        try: 
            self.createState = REPORT_NUM[reportType]  
            
            if(reportType == 'ICP'):         
                icpReportLoader(self)
                
            if(reportType == 'CHM'):    
                chmReportLoader(self)
                
        except Exception as error: 
            print(error)
            showErrorDialog(self, 'Could not create report', 'ERROR')

    else: 
        reportErrorHandler(self, errorCheck)

        
def reportErrorHandler(self, errorCheck): 
        errorTitle = 'Cannot Proceed to Report Creation Screen '
        errorMsg = ''
        
        if(errorCheck[0] == 1): 
            print('Error: Please Enter a valid job number')
            errorMsg += 'Please Enter a Valid Job Number\n'

        if(errorCheck[1] == 1): 
            print("Error: Please Select a reportType")
            errorMsg += 'Please Select a Report Type\n'
            
        if(errorCheck[2] == 1): 
            print('Error: Please Select a parameter')
            errorMsg += 'Please Select a Parmeter\n'
        
        if(errorCheck[3] == 1): 
            print("Error: TXT File doesn't exist")
            errorMsg += 'TXT File could not be located\n'

            
            
        showErrorDialog(self, errorTitle, errorMsg)
        
#TODO: this should be in the preference section, move this into other database  
def populateAuthorNames(self): 
    authorNamesQuery = 'SELECT * FROM authors'
    
    try: 
        results = self.db.query(authorNamesQuery); 
        
        self.authors = [{result[0]: result[1]} for result in results]
        print(self.authors)

        #TODO: clear a global author varliable 
        
    except: 
        print('Error: Could not load the authors for Create Report Page ')
        
        
#******************************************************************
#   reading text file  
#******************************************************************
def checkTextFile(self, fileLocation): 
    print('[FUNCTION]: checkTextFile')
    
    # Enable Text File Tab if the file is there
    if(fileLocation): 
        try: 
            self.ui.reportsTab.setTabEnabled(2, True)
            
            with open(fileLocation) as file: 
                content = file.read()
                 
            # Clear existing content in the QTextBrowser
            self.ui.textBrowser.clear()
            # Append the content of the text file to the QTextBrowser
            self.ui.textBrowser.append(content)
    
        except Exception as error: 
            print(error)
            self.ui.reportsTab.setTabEnabled(2, False) 
        
    else:
         self.ui.reportsTab.setTabEnabled(2, False)


#******************************************************************
#   General Functions 
#******************************************************************
def formatReportTable(table, rowCount, colCount): 
    table.setRowCount(rowCount)
    table.setColumnCount(colCount)
    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)
    
def deleteAllSampleWidgets2(self): 
    for widget in self.ui.samplesContainer.children():
        if isinstance(widget, SampleNameWidget):
            widget.setParent(None)
            widget.deleteLater()
        else:
            spacer = widget.spacerItem()
            if spacer:
                self.layout.removeItem(spacer) 
            
def deleteAllSampleWidgets(self): 
    for i in reversed(range(self.ui.samplesContainer.layout().count())):
        item = self.ui.samplesContainer.layout().itemAt(i)
        if item.widget() is not None:
            if isinstance(item.widget(), SampleNameWidget):
                item.widget().deleteLater()
        elif item.spacerItem():
            self.ui.samplesContainer.layout().removeItem(item)
    
def loadClientInfo(self): 
    print('[Function]: loadClientInfo(self)')
    
    # Set the header parameter 
    self.ui.jobNum.setText("W" + self.jobNum)
    self.ui.clientNameHeader.setText(self.clientInfo['clientName'])
    self.ui.parameterHeader.setText(self.parameter); 
    self.ui.reportTypeHeader.setText(self.reportType);
    
    self.ui.factorHeader.setText(str(self.dilution))

    # Set the client Info 
    self.ui.clientName_1.setText(self.clientInfo['clientName'])
    self.ui.date_1.setText(self.clientInfo['date'])
    self.ui.time_1.setText(self.clientInfo['time'])
    self.ui.attention_1.setText(self.clientInfo['attn'])
    self.ui.addy1_1.setText(self.clientInfo['addy1'])
    self.ui.addy2_1.setText(self.clientInfo['addy2'])
    self.ui.addy3_1.setText(self.clientInfo['addy3'])
    self.ui.sampleType1_1.setText(self.clientInfo['sampleType1'])
    self.ui.sampleType2_1.setText(self.clientInfo['sampleType2'])
    self.ui.totalSamples_1.setText(self.clientInfo['totalSamples'])
    self.ui.recvTemp_1.setText(self.clientInfo['recvTemp'])
    self.ui.tel_1.setText(self.clientInfo['tel'])
    self.ui.email_1.setText(self.clientInfo['email'])
    self.ui.fax_1.setText(self.clientInfo['fax'])
    self.ui.payment_1.setText(self.clientInfo['payment'])

def updateSampleNames(sampleNames, textChange, key):
    sampleNames[key] = textChange; 
    print(f'Update Sample Name: {sampleNames}')
    
def populateTableRow(tableWidget, row, col, alignment, value): 
    item = QtWidgets.QTableWidgetItem()  
    if(alignment == 1):   
        item.setTextAlignment(Qt.AlignCenter)
    
        # Check data type and convert if necessary
    if isinstance(value, (int, float)):
        value = str(value)  # Prevent spinbox for numeric data
     
    item.setData(Qt.DisplayRole, value)
    tableWidget.setItem(row, col, item)
        
    return 

#******************************************************************
#    Chemisty Loader  
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
   
@pyqtSlot() 
def handleTableChange(self, item):
    
    table = self.ui.dataTable 
    row = item.row()
    column = item.column()
    value = item.text()

    updatedValue = table.item(row, column).text()
    column_name = table.horizontalHeaderItem(column).text()
    
    if(self.createState == 1): 
        pass; 
    if(self.createState == 2): 

        textNameCol = 1
        textName = table.item(row, textNameCol)

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
    
    chmTestsLists, testResults = chmGetTestsList(self) 

    dataTable = self.ui.dataTable
    rowCount = len(chmTestsLists) 
    
    # Prepare the chm cliennt Info and the table 
    chmIntalize(self, dataTable, rowCount)    
    
    # Prepare the objects 
    self.reportManager = chemReportManager(self.tempDB)
    self.reportView = chemReportView(self.ui.dataTable)
    
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
     
    # loop through the tests that ussers have manually added to the thing 
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
   
def chmIntalize(self, table, rowCount): 
    print('[FUNCTION]: chmIntalize(self, table, rowCount, colCount, columnNames)')

    #TODO: maybe make this into a global variable? 

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
    
    # Initalize the columns 
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
#FIXME: crashes when doing gcms to icp without closing program 
#TODO: move the message to the center of the screen and change the dimensions 
def chmReportHandler(self, columnLength,  tests):
    print('[FUNCTION]: chmReportHandler(self, tests)')
    print('*Tests: ', tests)
    
    totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    
    sampleData = {}
    unitType = []
    recovery = []
    displayNames = []
    
    # Retreive the Sample Input Data 
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
        
    # Retreive the Tests Info 
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
            currentVal = self.ui.dataTable.item(row, 3).text()
            unitType.append(currentVal)
        except: 
            unitType.append('')
        
        try: 
            recoveryVal = self.ui.dataTable.item(row, 5).text()
            
            if(is_float(recoveryVal)): 
                recovery.append(float(recoveryVal))
            else: 
                recovery.append(recoveryVal) 
        except: 
            recovery.append('')       
            
    createChmReport(self.clientInfo, self.jobNum, self.sampleNames, sampleData, displayNames, unitType, recovery)

    createdReportDialog('test')

    # Save the other client info 
    # Authors, client ifno, samples name. sample data
    


#******************************************************************
#    ICP Loader 
#******************************************************************

def getIcpMachineData(database, jobNumber): 
    query = 'SELECT sampleName, jobNum, data FROM icpData WHERE jobNum = ? ORDER BY sampleName ASC'
    
    return list(database.query(query, (jobNumber, )))
    
def getIcpLimitResults(database, parameters): 
    queryUnits = 'SELECT element, units, lowerLimit, maxLimit FROM icpLimits WHERE reportType = ?'

    limitResults = database.query(queryUnits, (parameters,))  
    elementUnitValues = {t[0]: t[1] for t in limitResults} 

    return elementUnitValues 

def getIcpElementsList2(db): 
    try: 
        query = 'SELECT * FROM icpElements ORDER BY elementName ASC'
        results = db.query(query)
        return results
    except Exception as error: 
        print(f'[ERROR]: {error}')
        return None

def getIcpLimitResults2(database, parameters):
    print('[FUNCTION]: getIcpLimitResults2(database, parameters)')
    print(parameters)
    
    try: 
        query = 'SELECT elementNum, unitType, lowerLimit, upperLimit, sideComment FROM icpLimits WHERE parameterNum = ?'
        result = database.query(query, (parameters, ))
        return {item[0]: [item[1], item[2], item[3], item[4]] for item in result}
        
    except Exception as e: 
        print(e)  
        return None 

#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: does this effect hardness and also what about the new values we enter in 
def icpReportLoader(self): 
    print('[FUNCTION]: icpLoader(self)')
   
    self.ui.createIcpReportBtn.setVisible(True)
    self.ui.createGcmsReportBtn.setVisible(False)
    self.ui.icpDataField.show()
   
    # FIXME: fix the machine getting username Information, can use a loop instead 
    loadClientInfo(self)
 
    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Type', 
        'Lower Limit', 
        'Upper Limit', 
        'distal factor'
    ]
    
    addtionalRows = ['pH', 'Hardness']
     
    # FIXME: need to get redo this as well 
    #elements = getIcpElementsList(self.db) 
    elements = getIcpElementsList2(self.tempDB)
    elementNames = [t[1] for t in elements]
    
    print(f'Elements: {elements}')
    
    sampleData = getIcpMachineData(self.tempDB, self.jobNum)

    #TODO: change database later so we have just one database 
    reportNum = getReportNum(self.tempDB, self.parameter)[0][0]
    print(f'Parameter: {reportNum}')
    
    #TODO: add a try-except block here 
    
    #elementUnitValues = getIcpLimitResults(self.db, self.parameter); 
    elementUnitValues = getIcpLimitResults2(self.tempDB, reportNum)

    selectedSampleNames = []
    
    for item in sampleData:
        sampleName = item[0]
        if(sampleName not in selectedSampleNames): 
            selectedSampleNames.append(item[0])

    machineData = {item[0]: json.loads(item[2]) for item in sampleData}

    #print(f'Elment Names: {elementNames}')
    print(f'Element Unit Values: {elementUnitValues}')
    print('SelectedSampleItems: ', selectedSampleNames)    
    
    dataTable = self.ui.dataTable
    colCount = len(columnNames) + len(selectedSampleNames)
    totalRows = len(elements) + len(addtionalRows)
    totalSamples = len(selectedSampleNames)    
    
    # Connect Signals 
    
    #dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHander(self, elements, elementUnitValues, totalSamples, reportNum));     

    # Format and intalize the tables 
    icpIntalizeTable(self, dataTable, colCount, totalRows, selectedSampleNames, columnNames)
    
    # Populate the sample table information 
    icpPopulateSamplesSection(self, selectedSampleNames)
    
    # Populate Hardness and pH 
    icpPopulateAdditonalRows(self, totalRows, addtionalRows)
    
    # populate the table with column and smaple info 
    icpPopulateTable(self, elements, elementUnitValues)
    
    # load the tables elemental machine info and  hardness calculations 
    icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames)
            

def icpIntalizeTable(self, table, colCount, totalRows, selectedSampleNames, columnNames): 
    print(f'[FUNCTION]: icpIntalizeTable(self, table, colCount, totalRows, selectedSampleNames, columnNames)')

    formatReportTable(table, totalRows, colCount)

    column_width = self.ui.dataTable.columnWidth(2)
    padding = 10
    total_width = column_width + padding
    table.setColumnWidth(2, total_width)    
    
    # inital column names
    for i, name in enumerate(columnNames): 
        item = QtWidgets.QTableWidgetItem(name)
        table.setHorizontalHeaderItem(i, item)
    
    # Set the sample names in the column (after)
    for i , (key) in enumerate(selectedSampleNames, start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(key)
        table.setHorizontalHeaderItem(i, item)

def icpPopulateSamplesSection(self, selectedSampleNames):
    print(f'[FUNCTION]: icpPopulateSamples(self, selectedSampleNames)')
        
    # Create the sample names in the client info section        
    for i, (key, value) in enumerate(self.sampleNames.items()):
        
        if(key in selectedSampleNames):
            print('active:', key)
            sampleItem = SampleNameWidget(key, value)
            self.ui.samplesContainerLayout.addWidget(sampleItem)
            sampleItem.edit.textChanged.connect(lambda textChange, key = key: updateSampleNames(self.sampleNames, textChange, key))

    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    self.ui.samplesContainerLayout.addItem(spacer) 

def icpPopulateTable(self, elements, elementUnitValues): 
    print('[FUNCTION]:icpPopulateTable(self, elements, elementUnitValues)')
    
    tableWidget = self.ui.dataTable

    for i, element in enumerate(elements): 
        elementNum    = element[0]
        elementName   = element[1].capitalize()
        elementSymbol = element[2].capitalize()
        
        if(self.dilution == ''):
            distalFactorDefault = 1        
        else:
            distalFactorDefault = self.dilution 
           
        icpPopulateRow(tableWidget, i, 0, 0, elementName)
        icpPopulateRow(tableWidget, i, 1, 1, elementSymbol)
        icpPopulateRow(tableWidget, i, 5, 1, distalFactorDefault)

        # Set the limits
        if(elementNum in elementUnitValues): 
            unitType   = elementUnitValues[elementNum][0]
            lowerLimit = elementUnitValues[elementNum][1]
            upperlimit = elementUnitValues[elementNum][2]
            
            icpPopulateRow(tableWidget, i, 2, 1, unitType)
            icpPopulateRow(tableWidget, i, 3, 1,  lowerLimit)
            icpPopulateRow(tableWidget, i, 4, 1, upperlimit)
           
def icpPopulateRow(tableWidget, row, col, alignment, value): 
    item = QtWidgets.QTableWidgetItem()  
    if(alignment == 1):   
        item.setTextAlignment(Qt.AlignCenter)
    
    if(value):
        item.setData(Qt.DisplayRole, value)
        tableWidget.setItem(row, col, item)
        
    return 

def icpPopulateAdditonalRows(self, totalRows, addtionalRows ): 
    print('[FUNCTION]:icpPopulateAdditonalRows(self, totalRows, addtionalRows)')
    
    unitCol = 2
    tableWidget = self.ui.dataTable
    
    for i, elementName in enumerate(addtionalRows): 
        postion = totalRows - i - 1; 
        icpPopulateRow(tableWidget, postion, 0, 0, elementName)
        
        if(elementName == 'Hardness'): 
            symbolName = "CaC0₃"
            unitType = "ug/L"
            
            icpPopulateRow(tableWidget, postion, 1, 1, symbolName) 
            icpPopulateRow(tableWidget, postion, unitCol, 1, unitType) 
        else: 
            symbolName = ""
            unitType = "unit"
        
            icpPopulateRow(tableWidget, postion, 1, 1, symbolName) 
            icpPopulateRow(tableWidget, postion, unitCol, 1, unitType) 

def icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames): 
    #print('[FUNCTION]: icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames)')
    
    tableWidget = self.ui.dataTable 
    hardnessRow = 33
     
    #print('***Element Values')
    for i in range(len(elements)): 
        item = self.ui.dataTable.item(i, 1) 
        if(item != None): 
            symbol = item.text()
            for j, sample in enumerate(selectedSampleNames): 

                if sample in machineData and symbol in machineData[sample]: 
                    dilutionValue = dilutionConversion(machineData, sample, symbol, self.dilution)
                    
                    #print(f'Sample        : {sample} {symbol}')  
                    #print(f'Machine  Value: {machineData[sample][symbol]}')
                    #print(f'Dilution Value: {dilutionValue}');
                            
                    sampleCol = j + len(columnNames)
                    icpPopulateRow(tableWidget, i, sampleCol, 1, dilutionValue)
                else:
                    pass;  
                    #print(f'Sample        : {sample} {symbol}')  

    #print('***Hardness Calculations')
    for j, sample in enumerate(selectedSampleNames):   
        if sample in machineData and ('Ca' in machineData[sample] and 'Mg' in machineData[sample]): 
            calcium = machineData[sample]['Ca'] 
            magnesium = machineData[sample]['Mg'] 
            result = hardnessCalc(calcium, magnesium, self.dilution)

            sampleCol = j + len(columnNames)
            
            #print(f'*Sample: {sample}')
            #print('calcium: ', calcium)
            #print('magnesium: ', magnesium)
            #print('Result: ', result)

            icpPopulateRow(tableWidget, hardnessRow, sampleCol, 1, result)

def dilutionConversion(machineList, sample, symbol, dilutuion):
    print(f'[FUNCTION]: dilutionConversion(machineList, {sample}, {symbol}, {dilutuion})')
   
    machineValue = machineList[sample][symbol]
    
    if(is_float(machineValue) and dilutuion != 1): 
        newVal = float(machineValue)
        newVal = newVal * float(dilutuion)
        newVal = round(newVal, 3)
        return newVal
        
    else:         
        try:
            machineValue = float(machineValue)  # Convert to float first
            machineValue = round(machineValue, 3)
            return machineValue
        except ValueError:
            print('[ERROR]: VALUE ERROR')
            return machineValue

#******************************************************************
#    ICP Report Handler Function  
#******************************************************************

    
def icpReportHander(self, elements, limits, totalSamples, reportNum): 
    print('[FUNCTION]: icpReportHander(self, tests, totalSamples)')
    print(f'Total Samples: {totalSamples}') 
    
    elements = {item[0]: [item[1], item[2]]for item in elements}
    print('*Elements')
    for key, value in elements.items():
        print(key, value) 
        
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount  
    
    initalColumns = 6; 
    totalTests = len(elements)
    additonalRows = 2 
    sampleData = {}
    unitType = []
    elementNames =  [item[0] for item in elements.values()]
    
    #FIXME: have something determine the lower values of the things 
    for col in range(initalColumns, totalSamples + initalColumns): 
        #print(col)
        currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
        jobValues = []
        for row in range(totalTests + additonalRows): 
            try: 
                currentItem = self.ui.dataTable.item(row, col).text()
                jobValues.append(currentItem)
            except: 
                jobValues.append('ND')
                
                
        sampleData[currentJob] = jobValues
        #print(currentJob, sampleData[currentJob])
        
    for i in range(totalTests): 
        try: 
            currentUnitType = self.ui.dataTable.item(i, 2)
            if(currentUnitType): 
                unitType.append(currentUnitType.text())
            
        except Exception as e: 
            print(f'[ERROR]: {e}') 
            unitType.append('')
        
    footerComments = icpGenerateFooter(self)

    #print(f'Sample Data: {sampleData}')
    print('*Limits')
    for key, value in limits.items(): 
        print(key, value)
        
    print('*Sample Data')
    for key, value in sampleData.items(): 
        print(key, value)
    
    print(f'Unit Type: {unitType}')
    print(f'Footer: {footerComments}')
    print()
    print('------------------------------------------------------')

    
    #LAZY FIX 
    limitQuery2 = 'SELECT elementNum, lowerLimit, upperLimit, sideComment, unitType FROM icpLimits WHERE parameterNum = ?'
    limits = self.tempDB.query(limitQuery2, (reportNum,))  
    limits = [[elements[item[0]][0], item[1], item[2],item[3], item[4]] for item in limits]
    
    
    #elementNames = elementsWithLimits 
    
    #load the footer comment 
    #TODO: can just pass the self and remove some of the unessary info 
    createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, elementNames, unitType, elementNames, limits, footerComments)
    #createIcpReport2(self.clientInfo, self.samplenames, self.jobNum, sampleData, elements, limitsInfo, footer)

    createdReportDialog('test')
    
def icpGenerateFooter(self): 
    try: 
        commentQuery = 'SELECT footerComment FROM icpReportType WHERE reportType = ?'
        self.db.execute(commentQuery, (self.parameter,))
        commentResults = self.db.fetchone()
    except Exception as error: 
        print(f'[ERROR]: {error}')

    footerComments = ''
    
    if(commentResults):
        footerComments = pickle.loads(commentResults[0])
        footerList = '\n'.join(footerComments)
        footerComments = footerList.split('\n') 
        
    return footerComments


class icpManager: 
    pass; 