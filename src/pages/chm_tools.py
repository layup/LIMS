from app import *
from modules.dbManager import * 
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *

from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)


def chmLoader(self): 
    print('CHM LOADER')
    
    self.loadClientInfo()

    #TODO: scan in the TXT Tests, scan in from Defined Tests too 
    #TODO: fix the error checking 
    
    
    #load sample names 
    for i, (key,value) in enumerate(self.sampleNames.items()):
        item = SampleNameWidget(key, value)
        self.ui.formLayout_5.addRow(item)
        item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
    
    self.ui.stackedWidget.currentChanged.connect(lambda: self.removeWidgets())
    
    GSMS_TESTS_LISTS = []
    #ICP_TESTS_LISTS = []
    #tests = []
    
    for (currentJob ,testList) in self.sampleTests.items(): 
        for item in testList: 
            
            temp = remove_escape_characters(str(item)) 
            
            if(temp not in GSMS_TESTS_LISTS and 'ICP' not in temp):
                                    
                GSMS_TESTS_LISTS.append(temp)

            #if(temp not in ICP_TESTS_LISTS and 'ICP' in temp):
            #    ICP_TESTS_LISTS.append(temp)
                
            #if(temp not in tests): 
            #    tests.append(temp)
    
    
    testsQuery = 'SELECT * FROM gcmsTestsData WHERE jobNum = ?'
    testsResults = self.db.query(testsQuery, (self.jobNum,))
    
    #TODO: can create a list and combine unique values
    if(testsResults != None): 
        for item in testsResults: 
            if(item[1] not in GSMS_TESTS_LISTS):
                GSMS_TESTS_LISTS.append(item[1])
                    
    
    GSMS_TESTS_LISTS = sorted(GSMS_TESTS_LISTS)
    print(GSMS_TESTS_LISTS) 


    #inital setup 
    columnNames = [
        'Tests', 
        'Display Name',
        'Unit', 
        'Standard Recovery', 
        'Distal factor'
    ]
    
    initalColumns = len(columnNames)
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
        item = QtWidgets.QTableWidgetItem()
        item.setText(value)
        self.ui.dataTable.setItem(i, 0, item)
        
        #TODO: search for the display name 
        displayQuery = 'SELECT displayName FROM gcmsTests WHERE testName = ?'
        self.db.execute(displayQuery, [value,])
        result = self.db.fetchone()
        print(result)
        
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


    self.ui.createGcmsReportBtn.clicked.connect(lambda: self.chmReportHandler(GSMS_TESTS_LISTS)); 
    
def chmReportHandler(self, tests):
    
    print('Tests: ', tests)
    #FIXME: adjust based on the sample information 
    #FIXME: crashes when doing gcms to icp without closing program 
    initalColumns = 5; 
    totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    sampleData = {}
    unitType = []
    recovery = []
    displayNames = []
    
    for col in range(initalColumns, totalSamples + initalColumns ): 
        
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
            

    #print("UNITS TESTING: ", unitType)
    
    createGcmsReport(self.clientInfo, self.jobNum, self.sampleNames, sampleData, displayNames, unitType, recovery)


def chmLoadTestsData(self): 
    
    selectedTests = self.ui.gcmsDefinedtests.currentItem()
            
    if selectedTests is not None:
        try: 
            getTestsData = 'SELECT * FROM gcmsTests WHERE testName = ?'
            self.db.execute(getTestsData, (selectedTests.text(),))
            results = self.db.fetchone() 
            
            print(results)
        
            self.ui.gcmsTxtName.setText(str(results[0]))
            self.ui.gcmsUnitType.setText(str(results[1]))
            self.ui.gcmsRefValue.setText(str(results[2]))
            self.ui.gcmsDisplayName.setText(str(results[3]))
        except: 
            #item is not in the database yet 
            print('Error: selected Text was None') 
            self.gcmsClearDefinedTestsValues()
            self.ui.gcmsTxtName.setText(selectedTests.text())
            
            
def chmLoadTestsNames(self): 
    
    self.gcmsClearDefinedTestsValues(); 
    self.ui.gcmsDefinedtests.clear()
    self.ui.testsInputLabel.clear()

    getTestNamesQuery = 'SELECT testName FROM gcmsTests ORDER BY testName COLLATE NOCASE ASC'
    testNames = self.db.query(getTestNamesQuery)           
    
    print(testNames)
    
    for test in testNames: 
        self.ui.gcmsDefinedtests.addItem(test[0])