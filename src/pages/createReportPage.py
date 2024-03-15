

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)


from modules.excel.chmExcel import createChmReport
from modules.excel.icpExcel import createIcpReport
from modules.dbFunctions import *
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *


#******************************************************************
#   Create Report Page Setup 
#******************************************************************

def reportSetup(self): 
    
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
    fileExist = scanForTXTFolders(jobNum)
    
    errorCheck = [0, 0, 0, 0]     
    errorCheck[0] = 0 if re.match('^([0-9]{6})$', jobNum) else 1 
    errorCheck[1] = 0 if reportType in REPORTS_TYPE else 1
    errorCheck[2] = 0 if parameter != '' else 1
    errorCheck[3] = 0 if fileExist != '' else 1    
    
    if(sum(errorCheck) == 0): 
        self.jobNum = jobNum; 
        self.parameter = parameter 
        self.reportType = reportType
        self.activeCreation = True; 

        #TODO: load the information from database later 
        tempLocation = scanForTXTFolders(self.jobNum)
        clientInfo, sampleNames, sampleTests = processClientInfo(self.jobNum, tempLocation)

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

        
#TODO: this should be in the preference section 
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
#   General Functions 
#******************************************************************

def formatReportTable(table, rowCount, colCount): 
    table.setRowCount(rowCount)
    table.setColumnCount(colCount)
    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    
def deleteAllSampleWidgets(self): 
    for widget in self.ui.samplesContainer.children():
        if isinstance(widget, SampleNameWidget):
            widget.setParent(None)
            widget.deleteLater()
        


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
    
    self.loadClientInfo()

    # Load the sample names 
    for i, (key,value) in enumerate(self.sampleNames.items()):
        item = SampleNameWidget(key, value)
        self.ui.formLayout_5.addRow(item)
        item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
    
    # checking CHM test lists  
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

    formatReportTable(dataTable, rowCount, colCount) 
    self.ui.dataTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    # Initalize the columns 
    for i, name in enumerate(columnNames):
        item = QtWidgets.QTableWidgetItem(name)
        self.ui.dataTable.setHorizontalHeaderItem(i, item)
        
    # Populate with sample names 
    for i , (key, value) in enumerate(self.sampleNames.items(), start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(key)
        self.ui.dataTable.setHorizontalHeaderItem(i, item)
        
    #displayNamesQuery = 'SELECT * gcmsTests'
    #displayResults = self.db.query(displayNamesQuery) 
    #print(displayResults)
    
    # List the tests  
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
        for column in range(len(columnNames), self.ui.dataTable.columnCount()):
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
    self.ui.createGcmsReportBtn.clicked.connect(lambda: chmReportHandler(self, len(columnNames), GSMS_TESTS_LISTS)); 
    
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


#******************************************************************
#    ICP Loader 
#******************************************************************
#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: combine both the datasets;
#TODO: does this effect hardness and also what about the new values we enter in 
def icpLoader(self): 
    print('[FUNCTION]: icpLoader')
    
    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Value', 
        'distal factor'
    ]
    
    addtionalRows = ['pH', 'Hardness']
     
    self.loadClientInfo()
    
    #check if haas data to load into the file location 
    sql1 = 'SELECT sampleName, jobNumber, data FROM icpMachineData1 where jobNumber = ? ORDER BY sampleName ASC'
    sql2 = 'SELECT sampleName, jobNumber, data FROM icpMachineData2 where jobNumber = ? ORDER By sampleName ASC' 
    
    sampleData = list(self.db.query(sql1, (self.jobNum,)))
    sampleData2 = list(self.db.query(sql2, (self.jobNum,))); 
    
    queryUnits = 'SELECT element, units, lowerLimit, maxLimit FROM icpLimits WHERE reportType = ?'
    
    elements = getIcpElementsList(self.db) 
    elementNames = [t[0] for t in elements]
    print(f'ElmentNames: {elementNames}')
    
    limitResults = self.db.query(queryUnits, (self.parameter,)) 
    elementUnitValues = {t[0]: t[1] for t in limitResults} 
    
    selectedSampleNames = []
    
    for item in sampleData:
        selectedSampleNames.append(item[0])

    for item in sampleData2: 
        if(item[0] not in selectedSampleNames): 
            selectedSampleNames.append(item[0]) 
    
    print('SelectedSampleItems: ', selectedSampleNames)    
    
    #create the sample names based on that         
    for i, (key, value) in enumerate(self.sampleNames.items()):
        
        if(key in selectedSampleNames):
            print('active:', key)
            item = SampleNameWidget(key, value)
            self.ui.formLayout_5.addRow(item)
            item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
    
    # Format table
    dataTable = self.ui.dataTable
    colCount = len(columnNames) + len(selectedSampleNames)
    totalRows = len(elements) + len(addtionalRows)
    totalSamples = len(selectedSampleNames)    
    
    formatReportTable(dataTable, totalRows, colCount)

    # inital column names
    for i, name in enumerate(columnNames): 
        item = QtWidgets.QTableWidgetItem(name)
        self.ui.dataTable.setHorizontalHeaderItem(i, item)
    
    # Set the sample names after 
    for i , (key) in enumerate(selectedSampleNames, start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(name)
        self.ui.dataTable.setHorizontalHeaderItem(i, item)
    
    for i, element in enumerate(elements): 
        elementName = element[0]
        elementSymbol = element[1]
        
        elementNameCol = QtWidgets.QTableWidgetItem() 
        elementNameCol.setText(elementName.capitalize()) 
        self.ui.dataTable.setItem(i, 0, elementNameCol)
            
        elementSymbolCol = QtWidgets.QTableWidgetItem()
        elementSymbolCol.setText(elementSymbol.capitalize())
        self.ui.dataTable.setItem(i, 1, elementSymbolCol) 
        
        unitTypeCol = QtWidgets.QTableWidgetItem() 
        if(elementName in elementUnitValues):
            unitTypeCol.setText(elementUnitValues[elementName])
        else: 
            unitTypeCol.setText('')
            
        self.ui.dataTable.setItem(i, 2, unitTypeCol)
        
        item4 = QtWidgets.QTableWidgetItem()
        if(self.dilution == ''):
            distalFactorDefault = '1'           
            item4.setText(distalFactorDefault)
        else: 
            item4.setText(str(self.dilution))
            
        self.ui.dataTable.setItem(i, 3, item4) 
    
    # Add additional Row Information
    for i, value in enumerate(addtionalRows): 
        postion = totalRows - i - 1; 
        elementName = QtWidgets.QTableWidgetItem()  
        elementName.setText(value)
        self.ui.dataTable.setItem(postion ,0 , elementName)

        symbolName = QtWidgets.QTableWidgetItem()
        unitValue = QtWidgets.QTableWidgetItem()
        
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
            
    
    machine1 = {item[0]: json.loads(item[2]) for item in sampleData}
    machine2 = {item[0]: json.loads(item[2]) for item in sampleData2} 
    
    print('***Element Values')
    for i in range(len(elements)): 
        item = self.ui.dataTable.item(i, 1)
        
        if(item != None): 
            symbol = item.text()
            for j, sample in enumerate(selectedSampleNames): 
                print(f'*Sample: {sample}')
                item = QtWidgets.QTableWidgetItem(); 
                
                if sample in machine1 and symbol in machine1[sample]: 
                    machine1Val = machine1[sample][symbol] 
                    print(f'Machine 1: {symbol} {machine1Val}')
                    
                    if(is_float(machine1Val) and self.dilution != 1 ): 
                        temp = float(machine1Val)
                        temp = temp * float(self.dilution)
                        temp = round(temp, 3)
                        item.setText(str(temp))
                    else: 
                        item.setText(machine1Val)
            
                if sample in machine2 and symbol in machine2[sample]: 
                    machine2Val = machine2[sample][symbol] 
                    print(f'Machine 2: {symbol} {machine2Val}')
                    
                    if(is_float(machine2Val) and self.dilution != 1): 
                        temp = float(machine2Val)
                        temp = temp * float(self.dilution)
                        temp = round(temp, 3)
                        item.setText(str(temp))
                    else: 
                        machine2Val = round(machine2Val, 3 )
                        item.setText(str(machine2Val))
                
                sampleCol = j + len(columnNames)
                self.ui.dataTable.setItem(i,sampleCol, item)


    print('***Hardness Calculations')
    for j, sample in enumerate(selectedSampleNames):   
        print(f'*Sample: {sample}')
        item = QtWidgets.QTableWidgetItem();  
        
        if sample in machine1 and ('Ca' in machine1[sample] and 'Mg' in machine1[sample]): 
            calcium = machine1[sample]['Ca'] 
            magnesium = machine1[sample]['Mg'] 
            result = hardnessCalc(calcium, magnesium, self.dilution)

            item.setText(str(result))
            sampleCol = j + len(columnNames)
            
            self.ui.dataTable.setItem(33, sampleCol, item)

            print('calcium: ', calcium)
            print('magnesium: ', magnesium)
            print('Result: ', result)
            
    
    column_width = self.ui.dataTable.columnWidth(2)
    padding = 10
    total_width = column_width + padding
    self.ui.dataTable.setColumnWidth(2, total_width)    

    self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHander(self, elementNames, totalSamples)); 


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
        except: 
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
    
    if(commentResults[0]):
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

    