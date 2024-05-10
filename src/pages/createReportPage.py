

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIntValidator

from modules.excel.chmExcel import createChmReport
from modules.excel.icpExcel import createIcpReport
from modules.dialogBoxes import createdReportDialog
from modules.dbFunctions import *
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *


#TODO: move a lot of these functions to the db fuinctions 

#******************************************************************
#   Create Report Page Setup 
#******************************************************************

def reportSetup(self): 
    #TODO: ERROR could not load TEXT_FILE please try again
 
    # Create a validator to accept only integer input
    validator = QIntValidator()
    # Set the range of valid integer values
    validator.setBottom(0)  # Minimum value
    validator.setTop(999999)  # Maximum value

    # Set input limits and Validators
    self.ui.jobNumInput.setValidator(validator)
    self.ui.jobNumInput.setMaxLength(6)

    self.ui.dilutionInput.setValidator(validator)
    self.ui.dilutionInput.setMaxLength(6)

    #load in the authors 
    #TODO: have some error checking and deal with the loadiong section 
    authorsList = [item[0] for item in getAllAuthorNames(self.preferencesDB)]
    authorsList.insert(0, '')
    
    print(authorsList)
    
    self.ui.authorOneDropDown.clear()
    self.ui.authorTwoDropDown.clear()
    
    self.ui.authorOneDropDown.addItems(authorsList)
    self.ui.authorTwoDropDown.addItems(authorsList)
    
    # Connect signals  
    self.ui.NextSection.clicked.connect(lambda: createReportPage(self))


#******************************************************************
#   Creating Report 
#******************************************************************

def editReport(): 
    pass; 

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
    
        
    #TODO: check if it is a valid dilution value 
    #TODO: change the dilution thing into a number only slider lol, so the default would be 1 and otherwise 
    self.dilution = 1 if dilution == '' else dilution       
    textFileExists = scanForTXTFolders(jobNum)
    
    errorCheck = [0, 0, 0, 0]     
    errorCheck[0] = 0 if re.match('^([0-9]{6})$', jobNum) else 1 
    errorCheck[1] = 0 if reportType in REPORTS_TYPE else 1
    errorCheck[2] = 0 if parameter != '' else 1
    errorCheck[3] = 0 if textFileExists != '' else 1    
    
    if(sum(errorCheck) == 0): 
        #FIXME: I can adjust the client Info, so I don't need this (do I need global functions, bad pratice)

        self.ui.reportsTab.setCurrentIndex(0)
        
        self.jobNum = jobNum; 
        self.parameter = parameter 
        self.reportType = reportType
        self.activeCreation = True; 

        #TODO: load the information from database later (front house database) 
        tempLocation = scanForTXTFolders(self.jobNum) #FIXME: can remove this
        clientInfo, sampleNames, sampleTests = processClientInfo(self.jobNum, tempLocation)
        
        checkTextFile(self, tempLocation)
        
        self.clientInfo = clientInfo 
        self.sampleNames = sampleNames
        self.sampleTests = sampleTests

        reportResult = checkReportExists(self.db, jobNum, reportType)
        
        if reportResult is None:  
            print('No Exists, adding to the file')
            createReport(self.db, jobNum, reportType, parameter, self.dilution)
        else: 
            if(method2 is not True): 
                print('Report Exists')
                print(reportResult)
                #TODO: load the report if exists
                loadReportDialog(self)          

        self.ui.stackedWidget.setCurrentIndex(5) 
        self.clearDataTable()
        self.ui.jobNum.setText(jobNum)
        
        #TODO: populate the author section
        #self.populateAuthorNames() 

        if('ICP' in reportType):
            print('***ICP Loader')
            
            self.ui.createIcpReportBtn.setVisible(True)
            self.ui.createGcmsReportBtn.setVisible(False)
            self.ui.icpDataField.show()
            
            icpLoader(self)
            
        if(reportType == 'CHM'):
            print('***CHM Loader')
            
            self.ui.createIcpReportBtn.setVisible(False)
            self.ui.createGcmsReportBtn.setVisible(True)
            self.ui.icpDataField.hide() 
            
            chmLoader(self)
        
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
    
    #FIXME: do something to this
    #self.ui.factorHeader.setText(self.dilution);

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

#******************************************************************
#    Chemisty Loader  
#****************************************************************** 

#TODO: scan in the TXT Tests, scan in from Defined Tests too 
#TODO: fix the error checking 
def chmLoader(self): 
    print('[FUNCTION]: chmLoader(self)')
  
    columnNames = [
        'Tests', 
        'Display Name',
        'Unit', 
        'Standard Recovery', 
        'Distal factor'
    ]
    
    GSMS_TESTS_LISTS = []
    
    loadClientInfo(self)
    
    # Checking CHM test lists  
    for (currentJob , testList) in self.sampleTests.items(): 
        for item in testList: 
            temp = removeIllegalCharacters(str(item)) 
            if(temp not in GSMS_TESTS_LISTS and 'ICP' not in temp):          
                GSMS_TESTS_LISTS.append(temp)

    testsQuery = 'SELECT * FROM gcmsTestsData WHERE jobNum = ?'
    testsResults = self.db.query(testsQuery, (self.jobNum,))
    
    #TODO: can create a list and combine unique values
    if(testsResults): 
        for item in testsResults: 
            if(item[1] not in GSMS_TESTS_LISTS):
                GSMS_TESTS_LISTS.append(item[1])
                    
    GSMS_TESTS_LISTS = sorted(GSMS_TESTS_LISTS)
    print('**FOUND CHM TESTS')
    print(GSMS_TESTS_LISTS) 

    dataTable = self.ui.dataTable
    rowCount = len(GSMS_TESTS_LISTS) 
    colCount = len(columnNames) + int(self.clientInfo['totalSamples'])

    # CHM Signals 
    #TODO: add the item changed thing 
    #self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test'))
    self.ui.createGcmsReportBtn.clicked.connect(lambda: chmReportHandler(self, len(columnNames), GSMS_TESTS_LISTS)); 

    chmIntalize(dataTable, rowCount, colCount, columnNames)

    chmPopulateTable(self, GSMS_TESTS_LISTS, columnNames, testsResults)
 
   
def chmIntalize(self, table, rowCount, colCount, columnNames): 

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


def chmPopulateTable(self, testLists, columnNames, testsResults): 
    
    # List the tests  
    for i, currentTest in enumerate(testLists): 
        print(f'Current Test {i}: {currentTest}') 
        testItem = QtWidgets.QTableWidgetItem(currentTest)
        self.ui.dataTable.setItem(i, 0, testItem)
        
        #TODO: Search for the display name 
        displayQuery = 'SELECT * FROM gcmsTests WHERE testName = ?'
        self.db.execute(displayQuery, [currentTest,])
        result = self.db.fetchone()
        print(f'Query Result: {result}')
        
        # Set the display Name if exists
        if(result): 
            displayNameItem = QtWidgets.QTableWidgetItem(result[0]) 
            self.ui.dataTable.setItem(i, 1, displayNameItem) 
        
        #TODO: Distral Factor 
        item2 = QtWidgets.QTableWidgetItem(str(1)) 
        self.ui.dataTable.setItem(i, 4, item2) 
    
        #go down each column and determine if there is a match
        for column in range(len(columnNames), self.ui.dataTable.columnCount()):
            header_item = self.ui.dataTable.horizontalHeaderItem(column)
            
            if header_item is not None:
                column_name = header_item.text()
                result = search_list_of_lists(testsResults,[column_name, currentTest] )
                
                if result is not None: 
                    print(f'CHM results: {result}')
                    valueText = str(result[2])
                    valueItem = QtWidgets.QTableWidgetItem(valueText) 
                    self.ui.dataTable.setItem(i, column, valueItem) 
                    
                    recoveryText = str(result[3])  
                    recoveryItem = QtWidgets.QTableWidgetItem(recoveryText) 
                    self.ui.dataTable.setItem(i, 3, recoveryItem) 
                    
                    unitText = result[4]
                    unitItem = QtWidgets.QTableWidgetItem(unitText) 
                    self.ui.dataTable.setItem(i, 2, unitItem)   

    
 
#******************************************************************
#    CHM Report Handler Function  
#******************************************************************
    
#FIXME: adjust based on the sample information 
#FIXME: crashes when doing gcms to icp without closing program 
def chmReportHandler(self, columnLength,  tests):
    print('[FUNCTION]: chmReportHandler(self, tests)')
    print('*Tests: ', tests)
    
    totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    
    sampleData = {}
    unitType = []
    recovery = []
    displayNames = []
    
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

    createdReportDialog('test')


#******************************************************************
#    ICP Loader 
#******************************************************************

def getIcpMachineData(database, jobNumber): 
    # Queries 
    #queryMachine1 = 'SELECT sampleName, jobNumber, data FROM icpMachineData1 where jobNumber = ? ORDER BY sampleName ASC'
    #queryMachine2 = 'SELECT sampleName, jobNumber, data FROM icpMachineData2 where jobNumber = ? ORDER By sampleName ASC' 
    
    
    # Query and convert into a list form 
    #sampleData = list(database.query(queryMachine1, (jobNumber,)))
    #sampleData2 = list(database.query(queryMachine2, (jobNumber,)))

    #return sampleData, sampleData2


    query = 'SELECT sampleName, jobNum, data FROM icpData WHERE jobNum = ? ORDER BY sampleName ASC'
    
    return list(database.query(query, (jobNumber, )))
    
def getIcpLimitResults(database, parameters): 
    queryUnits = 'SELECT element, units, lowerLimit, maxLimit FROM icpLimits WHERE reportType = ?'

    limitResults = database.query(queryUnits, (parameters,))  
    elementUnitValues = {t[0]: t[1] for t in limitResults} 

    return elementUnitValues 

#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: combine both the datasets;
#TODO: does this effect hardness and also what about the new values we enter in 
def icpLoader(self): 
    print('[FUNCTION]: icpLoader(self)')
   
    # FIXME: fix the machine getting username Information, can use a loop instead 
    loadClientInfo(self)
 
    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Value', 
        'distal factor'
    ]
    
    addtionalRows = ['pH', 'Hardness']
     
    elements = getIcpElementsList(self.db) 
    elementNames = [t[0] for t in elements]
    
    #sampleData, sampleData2 =  getIcpMachineData(self.db, self.jobNum)
    sampleData = getIcpMachineData(self.tempDB, self.jobNum)
    elementUnitValues = getIcpLimitResults(self.db, self.parameter)

    selectedSampleNames = []
    
    for item in sampleData:
        sampleName = item[0]
        if(sampleName not in selectedSampleNames): 
            selectedSampleNames.append(item[0])

    machineData = {item[0]: json.loads(item[2]) for item in sampleData}

    print(f'Elment Names: {elementNames}')
    print(f'Element Unit Values: {elementUnitValues}')
    print('SelectedSampleItems: ', selectedSampleNames)    
    
    dataTable = self.ui.dataTable
    colCount = len(columnNames) + len(selectedSampleNames)
    totalRows = len(elements) + len(addtionalRows)
    totalSamples = len(selectedSampleNames)    
    
    # Connect Signals 
    self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHander(self, elementNames, totalSamples));     

    # Format and intalize the tables 
    icpIntalizeTable(self, dataTable, colCount, totalRows, selectedSampleNames, columnNames)
    
    # Populate the sample table information 
    icpPopulateSamplesSection(self, selectedSampleNames)
    
    # populate the table with column and smaple info 
    icpPopulateTable(self, elements, elementUnitValues, addtionalRows, totalRows)
    
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

def icpPopulateTable(self, elements, elementUnitValues, addtionalRows, totalRows): 
    print(f'[FUNCTION]: icpPopulateTable(self, elements, elementUnitValues, addtionalRows, totalRows)')

    # Set the elemental Information (columns)
    for i, element in enumerate(elements): 
        elementName = element[0]
        elementSymbol = element[1]
        
        # Set the element Name 
        elementNameCol = QtWidgets.QTableWidgetItem() 
        elementNameCol.setText(elementName.capitalize()) 
        
        # Set the Elment Symbol Name 
        elementSymbolCol = QtWidgets.QTableWidgetItem()
        elementSymbolCol.setTextAlignment(Qt.AlignCenter)
        elementSymbolCol.setText(elementSymbol.capitalize())
        
        unitTypeItem = QtWidgets.QTableWidgetItem() 
        unitTypeItem.setTextAlignment(Qt.AlignCenter)
        
        distilFactorItem = QtWidgets.QTableWidgetItem()
        distilFactorItem.setTextAlignment(Qt.AlignCenter)
        
        if(elementName in elementUnitValues):
            unitTypeItem.setText(elementUnitValues[elementName])
        else: 
            unitTypeItem.setText('')
            
        if(self.dilution == ''):
            distalFactorDefault = '1'           
            distilFactorItem.setText(distalFactorDefault)
        else: 
            distilFactorItem.setText(str(self.dilution))

        self.ui.dataTable.setItem(i, 0, elementNameCol)
        self.ui.dataTable.setItem(i, 1, elementSymbolCol) 
        self.ui.dataTable.setItem(i, 2, unitTypeItem)
        self.ui.dataTable.setItem(i, 3, distilFactorItem) 
    
    # Add additional Row Information
    for i, value in enumerate(addtionalRows): 
        postion = totalRows - i - 1; 
        
        # Assign Table Items 
        elementName = QtWidgets.QTableWidgetItem()  
        symbolName = QtWidgets.QTableWidgetItem()
        unitValue = QtWidgets.QTableWidgetItem()
        
        # Center Alignment 
        symbolName.setTextAlignment(Qt.AlignCenter)
        unitValue.setTextAlignment(Qt.AlignCenter)
         
        elementName.setText(value)

        self.ui.dataTable.setItem(postion, 0, elementName)
        
        if(value == 'Hardness'): 
            symbolName.setText("CaC0₃")
            unitValue.setText('ug/L')
            
            self.ui.dataTable.setItem(postion, 1, symbolName) 
            self.ui.dataTable.setItem(postion, 2, unitValue) 
        else: 
            symbolName.setText("")
            unitValue.setText('unit') 

            self.ui.dataTable.setItem(postion, 1, symbolName) 
            self.ui.dataTable.setItem(postion, 2, unitValue)
              
def icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames): 
    print('[FUNCTION]: icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames)')
    
    print('***Element Values')
    for i in range(len(elements)): 
        item = self.ui.dataTable.item(i, 1)
        
        if(item != None): 
            symbol = item.text()
            for j, sample in enumerate(selectedSampleNames): 
                print(f'*Sample: {sample}')
                item = QtWidgets.QTableWidgetItem(); 
                item.setTextAlignment(Qt.AlignCenter)
                
                # TODO: fix the logic here somehow 
                if sample in machineData and symbol in machineData[sample]: 
                    print(f'Machine 1: {symbol} {machineData[sample][symbol]}')
                    item = dilutionConversion(machineData, sample, symbol, self.dilution)
                            
                sampleCol = j + len(columnNames)
                
                self.ui.dataTable.setItem(i, sampleCol, item)

    print('***Hardness Calculations')
    for j, sample in enumerate(selectedSampleNames):   
        print(f'*Sample: {sample}')
        item = QtWidgets.QTableWidgetItem();  
        item.setTextAlignment(Qt.AlignCenter)
        
        if sample in machineData and ('Ca' in machineData[sample] and 'Mg' in machineData[sample]): 
            calcium = machineData[sample]['Ca'] 
            magnesium = machineData[sample]['Mg'] 
            result = hardnessCalc(calcium, magnesium, self.dilution)

            item.setText(str(result))
            sampleCol = j + len(columnNames)
            
            self.ui.dataTable.setItem(33, sampleCol, item)

            print('calcium: ', calcium)
            print('magnesium: ', magnesium)
            print('Result: ', result)
    
    
def dilutionConversion(machineList, sample, symbol, dilutuion):
    item = QtWidgets.QTableWidgetItem(); 
    item.setTextAlignment(Qt.AlignCenter)

    machineValue = machineList[sample][symbol]
    
    if(is_float(machineValue) and dilutuion != 1): 
        newVal = float(machineValue)
        newVal = newVal * float(dilutuion)
        newVal = round(newVal, 3)
        item.setText(str(newVal))
        
    else:         
        try:
            machineValue = float(machineValue)  # Convert to float first
            machineValue = round(machineValue, 3)
            item.setText(str(machineValue))
        except ValueError:
            item.setText(machineValue)

    return item 


#******************************************************************
#    ICP Report Handler Function  
#******************************************************************

def icpReportHander(self, tests, totalSamples): 
    print('[FUNCTION]: icpReportHander(self, tests, totalSamples)')
    print(f'Tests: {tests}')
    print(f'Total Samples: {totalSamples}')
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount  
    
    initalColumns = 4; 
    totalTests = len(tests)
    additonalRows = 2 
    sampleData = {}
    unitType = []
    
    #FIXME: have something determine the lower values of the things 
    for col in range(initalColumns, totalSamples + initalColumns): 
        print(col)
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
            currentItem = self.ui.dataTable.item(i, 2).text()
            unitType.append(currentItem)
        except Exception as e: 
            print(f'[ERROR]: {e}') 
            unitType.append('')
    
    elementsWithLimits = getElementLimits(self.db); 
    #print(elementsWithLimits)    

    #TODO: have in own function 
    limitQuery = 'SELECT element, lowerLimit, maxLimit, comments, units FROM icpLimits WHERE reportType = ? ORDER BY element ASC' 
    commentQuery = 'SELECT footerComment FROM icpReportType WHERE reportType = ?'
    limits = self.db.query(limitQuery, (self.parameter,))
    
    self.db.execute(commentQuery, (self.parameter,))
    commentResults = self.db.fetchone()

    footerComments = ''
    
    if(commentResults):
        footerComments = pickle.loads(commentResults[0])
        footerList = '\n'.join(footerComments)
        footerComments = footerList.split('\n')


    print('ICP HANDLER')
    print(sampleData)
    print(limits)
    #print(self.reportType)
    #print(footerComment)
    print('--------')

    #load the footer comment 
    #TODO: can just pass the self and remove some of the unessary info 
    createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, tests, unitType, elementsWithLimits, limits, footerComments)
    

    createdReportDialog('test')