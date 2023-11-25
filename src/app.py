import sys 
import re 
import pickle

from PyQt5 import QtWidgets
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QCompleter, QStyleFactory
)

from modules.constants import *
from modules.createExcel import * 
from modules.dbManager import *
from modules.dbFunctions import * 
from modules.dialogBoxes import *
from modules.utilities import * 

from interface import *
from pages.icp_tools import icp_load_element_data, icpLoader, icpReportHander
from pages.chm_tools import chmLoadTestsNames, chmLoadTestsData, chmLoader, chmReportHandler 
from widgets.widgets import * 
    
    
#TODO: need to have more class objects that deal with insertion, that way we can have lazy loading isntead of constant 
# need to get more info 
class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 

        
        #load the setup 
        self.loadDatabase()
        self.loadCreatePage()
        self.loadStartup()
        self.loadTabFunctionality()
        self.zeroIndexStacksSetup()

        #self.ui.pushButton_6.clicked.connect(self.open_new_window)
        self.ui.NextSection.clicked.connect(lambda: self.createReportPage())
        self.ui.reportTypeDropdown.activated.connect(lambda: self.loadElementLimits())   
        
        self.setTabOrder(self.ui.gcmsTestsJobNum, self.ui.gcmsTestsSample)
        self.setTabOrder(self.ui.gcmsTestsSample, self.ui.gcmsTestsVal)
      
        self.showMaximized()

   #******************************************************************
   #    inline Slot Function Calls 
   #****************************************************************** 
   
    def on_clientName_1_textChanged(self):
        self.clientInfo['clientName'] = self.ui.clientName_1.text()
     
    def on_date_1_textChanged(self): 
        self.clientInfo['date'] = self.ui.date_1.text()
    
    def on_time_1_textChanged(self):
        self.clientInfo['time'] = self.ui.time_1.text()
    
    def on_attention_1_textChanged(self):
        self.clientInfo['attn'] = self.ui.attention_1.text()
        
    def on_addy1_1_textChanged(self): 
        self.clientInfo['addy1'] = self.ui.addy1_1.text()
        
    def on_addy2_1_textChanged(self): 
        self.clientInfo['addy2'] = self.ui.addy2_1.text()
    
    def on_addy3_1_textChanged(self): 
        self.clientInfo['addy3'] = self.ui.addy3_1.text()
        
    def on_sampleType1_1_textChanged(self):
        self.clientInfo['sampleType1'] = self.ui.sampleType1_1.text()
        
    def on_sampleType_2_textChanged(self):
        self.clientInfo['sampleType2'] = self.ui.sampleType2_1.text()
    
    def on_totalSamples_1_textChanged(self): 
        self.clientInfo['totalSamples'] = self.ui.totalSamples_1.text() 
    
    def on_recvTemp_1_textChanged(self): 
        self.clientInfo['recvTemp'] = self.ui.recvTemp_1.text()
        
    def on_tel_1_textChanged(self):
        self.clientInfo['tel'] = self.ui.tel_1.text()
    
    def on_email_1_textChanged(self):
        self.clientInfo['email'] = self.ui.email_1.text()
    
    def on_fax_1_textChanged(self): 
        self.clientInfo['fax'] = self.ui.fax_1.text()
    
    def on_payment_1_textChanged(self): 
        self.clientInfo['payment'] = self.ui.payment_1.text()
        #print(self.clientInfo)
   
   #******************************************************************
   #   Reports/History Page 
   #****************************************************************** 
   #TODO: rename the whole section to history 
    
    def on_searchLine_clicked(self): 
        print('This is being clicked')
        self.ui.searchLine.clear()

    @pyqtSlot()
    def on_reportsSearchBtn_clicked(self): 
        print('Searching the report database')

        searchValueString = self.ui.reportsSearchLine.text()
        print(f'Searching for Job Number: {searchValueString}')
        
        #try to convert to an int 
        #TODO: if result don't work, don't clear the table 
        self.clearReportsTable()
        self.loadReportsPage(searchValueString)
            
    
   #******************************************************************
   #    Menu Buttons 
   #****************************************************************** 
    
    def on_reportsBtn1_toggled(self): 
        self.ui.stackedWidget.setCurrentIndex(0) 
    
    def on_reportsBtn2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_createReportBtn1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        
    def on_createReportBtn2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_icpBtn1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        
    def on_icpBtn2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        
    def on_gsmsBtn1_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(3)
    
    def on_gsmsBtn2_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(3)
     
    def on_settingBtn1_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(4)
    
    def on_settingBtn2_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(4)
         
   #******************************************************************
   #    Stack Mangament 
   #****************************************************************** 
             
    def on_gsmsBtn1_clicked(self): 
        self.ui.gcmsStack.setCurrentIndex(0)

    def on_gcmsDefineTestBtn_clicked(self): 
        self.ui.gcmsStack.setCurrentIndex(1)
     
    def on_gcmsReportTypeBtn_clicked(self): 
        self.ui.gcmsStack.setCurrentIndex(2)
        
    def on_gcmsEnterTestsBtn_clicked(self): 
        self.ui.gcmsStack.setCurrentIndex(3);     
    
    def on_gcmsViewDatabase_clicked(self): 
        self.ui.gcmsStack.setCurrentIndex(4)

    def on_icpBtn1_clicked(self): 
        self.ui.icpStack.setCurrentIndex(0)
    
    def on_icpBtn2_clicked(self): 
        self.ui.icpStack.setCurrentIndex(0)
    
    def on_icpDatabaseBtn_clicked(self): 
        self.ui.icpStack.setCurrentIndex(1)
        
    def on_icpElementsBtn_clicked(self): 
        self.ui.icpStack.setCurrentIndex(2)
       
    def on_icpReportBtn_clicked(self): 
        self.ui.icpStack.setCurrentIndex(3)
        
    def on_icpStack_currentChanged(self, index):
        #TODO: set the machine values for both of theses, create a single inqury that fetches based on date
        
        if(index == 0): 
            self.ui.icpPageTitle.setText("ICP Page")
            self.ui.icpLabel.setText("")
        
        #TODO: create a single function that loads this all to begin with isntead of having to reload this each time 
        #try lazy loading 
        if(index == 1): 
            columnNames = ['Sample Name', 'Job Number', 'Machine Type', 'File Location', 'Upload Date']
        
            icpMachine1sql = 'SELECT sampleName, jobNumber, machine, fileLocation, createdDate data FROM icpMachineData1 ORDER BY createdDate DESC' 
            icpMachine2sql = 'SELECT sampleName, jobNumber, fileLocation, createdDate, machine data FROM icpMachineData2'
            
            machine1Data = list(self.db.query(icpMachine1sql))
            #machine2Data = list(self.db.query(icpMachine2sql))
            
            self.updateIcpTable(machine1Data) 
        
        if(index == 2): 
            total = getTotalElements(self.db)
            self.ui.icpPageTitle.setText("ICP Defined Elements")
            self.ui.icpLabel.setText("Total Elements: {}".format(total))
            self.loadDefinedElements()

        if(index == 3): 
            self.ui.icpPageTitle.setText("ICP Reports")
            self.ui.icpLabel.setText("Total Reports:") 
            self.loadReportList()

    def on_gcmsStack_currentChanged(self, index):
        
        if(index == 0): 
            self.ui.chmTitleLabel.setText('CHM Page')
            self.ui.gcmsSubTitleLabel.setText('')
        
        if(index == 1): 
            self.ui.chmTitleLabel.setText('CHM Defined Parameters')
            totalTests = getChmTotalTests(self.db) 
            
            self.ui.gcmsSubTitleLabel.setText('Total Tests: ' + str(totalTests))
            chmLoadTestsNames(self)

        if(index == 2): 
            self.ui.chmTitleLabel.setText('CHM Defined Reports')
            self.ui.gcmsSubTitleLabel.setText('Total Reports: ')
            
        if(index == 3): 
            self.ui.chmTitleLabel.setText('CHM Tests Entry')
            self.ui.gcmsSubTitleLabel.setText('')
            self.gcmsClearEnteredTestsData()
            
            temp = self.getTestsAndUnits()
            print('*CHM Tests and Unit Values')
            print(temp)
            
            self.ui.gcmsTests.addItems(temp[0])
            self.ui.gcmsUnitVal.addItems(temp[1])
        
        if(index == 4): 
            self.ui.chmTitleLabel.setText('CHM Tests Database') 
            self.ui.gcmsSubTitleLabel.setText('')
            self.loadChmDatabase(); 
            
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)
        
        #print(btn_list)
        #FIXME: issue that arises when the active creation setting is thing 
        for btn in btn_list:
            #if index in [1,2,3,4]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            
            btn.setAutoExclusive(True)
                   
        if(index == 0): 
            self.loadReportsPage(); 
            
        if(index == 1): 
            #self.ui.jobNumInput.setText('171981')
            self.ui.reportType.setCurrentIndex(0)
            self.ui.paramType.setCurrentIndex(0)
            
        if(index == 4): 
            print('Settings baby')
            self.loadSettings()
            
        self.prev_index = (index - 1) % self.ui.stackedWidget.count()
        print('prev index: ', self.prev_index)
        #prev_widget = self.ui.stackedWidget.widget(self.prev_index)
        #current_widget = self.ui.stackedWidget.currentWidget()
        
        if(self.prev_index == 5): 
            pass; 
            #print('Do you want to save?')
            
        # Access the previous and current widgets
        # Do something with the widgets
        #print(f"Previous widget: {prev_widget}")
        #print(f"Current widget: {current_widget}")
        
   #******************************************************************
   #    Setup Loading
   #******************************************************************  
    
    def loadStartup(self): 
        self.setWindowTitle("Laboratory Information management System") 
        self.setStyle(QStyleFactory.create('Fusion'))
        self.ui.LeftMenuContainerMini.hide()

        self.activeCreation = False; 
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.settingsStack.setCurrentIndex(3)
        self.ui.reportsBtn1.setChecked(True)
         
        jobList = getAllJobNumbersList(self.db) 
        jobList_as_strings = [str(item) for item in jobList]
         
        completer = QCompleter(jobList_as_strings)
        completer.setCompletionMode(QCompleter.PopupCompletion)  # Set completion mode to popup
        completer.setMaxVisibleItems(10)
        
        self.ui.reportsSearchLine.setCompleter(completer)
        self.ui.searchLine.setCompleter(completer)
        
        self.ui.searchLine.setPlaceholderText("Enter Job Number...")
        self.ui.reportsSearchLine.setPlaceholderText("Enter Job Number...")
        
    def zeroIndexStacksSetup(self): 
        self.ui.stackedWidget.setCurrentIndex(0) 
        self.ui.gcmsStack.setCurrentIndex(0)
        self.ui.icpStack.setCurrentIndex(0)

       
    def loadDatabase(self): 
        paths = load_pickle('data.pickle')
        print('**Paths')
        for key, value in paths.items():
            print(key, value)
       
        if(isValidDatabase(paths['databasePath'])): 
            self.db = Database(paths['databasePath'])
        else: 
            #TODO: add popup 
            print('Database not valid')
            databasePathTemp = openFile()
            self.db = Database(databasePathTemp)
    
     
    def loadTabFunctionality(self): 
        #self.ui.gcmsTestsSample.editingFinished.connect(self.on_tab_pressed1)
        pass; 
        
    def on_tab_pressed1(self): 
        self.ui.gcmsTestsVal.setFocus()
    
    
    def loadClientInfo(self): 
        print('**Applying Client Infomation ')
        #clear the first page 
        self.ui.jobNumInput.setText('')
        
        #set the header parameter 
        self.ui.jobNum.setText("W" + self.jobNum)
        self.ui.clientNameHeader.setText(self.clientInfo['clientName'])
        self.ui.parameterHeader.setText(self.parameter); 
        self.ui.reportTypeHeader.setText(self.reportType)
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
               
    def loadCreatePage(self): 
        print('[FUNCTION]: loadCreatePage')
 
        #load the report Types
        self.ui.reportType.clear()
        self.ui.reportType.addItems(REPORTS_TYPE)
        
        paramResults = sorted(getReportTypeList(self.db))
        paramResults.insert(0, "")
        self.ui.paramType.addItems(paramResults)
            
    def loadReportsPage(self, searchValue=None): 
        print('[FUNCTION]: loadReportsPage')
        print(f'Search Value: {searchValue}')
        
        #TODO: could move this to the section when moving to the page 
        self.ui.reportsHeader.setText('Reports History'); 
        self.ui.totalReportsHeader.setText('Recently created reports')
        
        if(searchValue): 
            try: 
                results = searchJobsList(self.db, searchValue)
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
                results = []
        else: 
            try: 
                results = getAllJobsList(self.db);
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
                results = []

        historyTable = self.ui.reportsTable 
        
        
        historyTable.setRowCount(len(results))
        historyTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        historyTable.doubleClicked.connect(self.on_table_double_clicked )

        self.formatTable(historyTable)
        
        for row, current in enumerate(results): 
            jobNumber = str(current[1])
            reportType = str(current[2])
            parameterType = str(current[3])
            dilutionFactor = str(current[4])
            creationDate = str(current[5])
            
            self.setTableItem(row, 0, jobNumber) 
            self.setTableItem(row, 1, reportType)
            self.setTableItem(row, 2, parameterType)
            self.setTableItem(row, 3, dilutionFactor)
            self.setTableItem(row, 4, creationDate) 
             
            button = QPushButton("Open")
            button.clicked.connect(lambda _, row=row: self.openExistingReport(row));
            historyTable.setCellWidget(row, 5, button)
    

    def setTableItem(self, row, column, text, alignment=Qt.AlignCenter): 
        item = QTableWidgetItem()
        item.setTextAlignment(alignment)
        item.setText(text)
        self.ui.reportsTable.setItem(row, column, item)
        
    def formatTable(self, table): 

        rowHeight = 25; 
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        table.verticalHeader().setVisible(True)
        table.verticalHeader().setDefaultSectionSize(rowHeight)

        #Disable editing for the entire table 
        table.setEditTriggers(QTableWidget.NoEditTriggers)

    def addTableItem(self, table, item): 
        pass; 
        
    def clearReportsTable(self): 
        self.ui.reportsTable.clearContents()
        self.ui.reportsTable.setRowCount(0)

    def on_table_double_clicked(self, index):
    # Open the row data
        row = index.row()
        print(f"Double clicked on row {row}")
        
    #TODO: save the user data that they have entered? that might be a pain in the ass that will get done later
    def openExistingReport(self, row): 
        print('[FUNCTION]: openExistingReport')
        rowData = []
        
        for i in range(4): 
            item =self.ui.reportsTable.item(row, i) 
            if(item): 
                rowData.append(item.text()) 
                
        print(rowData) 
      
        popup = openJobDialog(rowData[0], self)
        result = popup.exec_()
        
        if result == QDialog.Accepted:
            print('Opening Existing Report')
            isExistingReport = True 
            self.createReportPage(rowData[0], rowData[1], rowData[2], rowData[3], isExistingReport) 
            
        else:
            print("Not Opening Existing Report'")
        
        
   #******************************************************************
   #    Define Elements? 
   #****************************************************************** 
    
    def loadElementLimits(self): 
        print('[Function]: loadElementLimits')
        reportType = self.ui.reportTypeDropdown.currentText()
        elementName = self.ui.elementNameinput.text().lower()
       
        try: 
            limitResults = loadIcpLimit(self.db, elementName, reportType)
            
            if(limitResults is None): 
                self.clearElementLimits()
            else: 
                #TODO: define what the limit values are equal to 
                self.ui.lowerLimit.setText(str(limitResults[2]))
                self.ui.upperLimit.setText(str(limitResults[3]))
                self.ui.unitType.setText(limitResults[5])
                self.ui.RightSideComment.setPlainText(limitResults[4]) 
        except: 
            print('Error on loadElementLimits: Could not load in limits ')
       
   #******************************************************************
   #    ICP Page 
   #****************************************************************** 
    #TODO: deal with the side panel page 
    
    @pyqtSlot()
    def on_addElementBtn_clicked(self): 
        print(f'[EVENT]: on_addElementBtn_clicked')
        #TODO: makeing sure not inserting duplicates 
        currentText = self.ui.elementInput.text()
        if(currentText != ''): 
            print(currentText)
            self.ui.definedElements.addItem(currentText)
            self.ui.elementInput.clear()
        else: 
            print('User entered a blank value, please enter a valid value')
         
    @pyqtSlot()
    def on_saveCompBtn_clicked(self): 
        #TODO: remove white spaces just in case 
        #TODO: check if they are valid limits
        symbolName = self.ui.symbolInput.text().lower().strip()
        elementName = self.ui.elementNameinput.text().lower().strip()
        
        reportType = self.ui.reportTypeDropdown.currentText()
        lowerLimit = self.ui.lowerLimit.text()
        upperLimit = self.ui.upperLimit.text()
        unitType = self.ui.unitType.text().strip()
        
        comment = self.ui.RightSideComment.toPlainText() 
        
        print(symbolName, elementName)
        
        #TODO: cannot save without a something
        #TODO: make the thing lowercase 

        
        errorCheck = [0,0,0]

        #errorCheck[0] = 0 if (standards != '' and is_real_number(standards)) else 1; 
        #errorCheck[1] = 0 if units != '' else 1; 
        #errorCheck[2] = 0 if tests != '' else 1; 
        
        if(sum(errorCheck) == 0):
            pass; 
            #self.ui.gcmsTestsValueWidget.setEnabled(True)
            #self.ui.widget_28.setEnabled(False)
            #self.ui.gcmsStandardValShow.setText(standards)
            #self.ui.gcmsUnitValShow.setText(units)
            #self.ui.gcmsTestsShow.setText(tests)  
        else: 
            errorTitle = 'Cannot Proceed with CHM Process'
            errorMsg = ''
            
            if(errorCheck[0] == 1): 
                errorMsg += 'Please Enter a Valid Standard Number\n'
            if(errorCheck[1] == 1): 
                errorMsg += 'Please Select a Unit\n'
            if(errorCheck[2] == 1): 
                errorMsg += 'Please Select a Tests\n'
        
        
        if(symbolName != "" and elementName != ""):
            
            defineElementQuery = 'INSERT OR REPLACE INTO icpElements (element, symbol) VALUES (?,?)'
            #definedLimitsQuery = 'INSERT OR REPLACE INTO icpLimits (reportType, element, lowerLimit, maxLimit, comments, units) VALUES (?,?,?,?,?,?)'
            
            loadLimits = 'SELECT * FROM icpLimits WHERE element = ? and ReportType = ?'  
            self.db.execute(loadLimits, (elementName, reportType))
            limitResults = self.db.fetchone()
            
            insertLimit = 'INSERT INTO icpLimits (reportType, element, lowerLimit, maxLimit, comments, units) VALUES (?,?,?,?,?,?)' 
            updateLimit = 'UPDATE icpLimits SET lowerLimit = ?, maxLimit = ?, comments =?, units =? WHERE reportType=? AND element=?' 

            try:
                self.db.execute(defineElementQuery, (elementName, symbolName) )
                
                if(limitResults): 
                    self.db.execute(updateLimit, (lowerLimit, upperLimit, comment, unitType, reportType, elementName))
                else: 
                    self.db.execute(insertLimit, (reportType, elementName, lowerLimit, upperLimit, comment, unitType))
                
                self.db.commit()

            except sqlite3.IntegrityError as e:
                print(e)

    @pyqtSlot()
    def on_deleteCompBtn_clicked(self):
        #TODO: are you sure you wanted to delete this time popup
        #TODO: error when deleting nothing
        print("Deleting the componenet")

        elementName = self.ui.elementNameinput.text().lower()
        print(f'Element Name: {elementName}')
        
        deleteQuery = 'DELETE FROM icpElements WHERE element = ?'
        
        try: 
            deleteBox(self, "DELETE ELEMENT", "ARE YOU SURE YOU WANT TO DELETE THIS ITEM", lambda:print("hello World"))
            self.db.execute(deleteQuery, (elementName,))
            self.db.commit()

            currentItem = self.ui.definedElements.currentRow()
            self.ui.definedElements.takeItem(currentItem)
            self.ui.definedElements.setCurrentItem(None)
            self.clearElementInfo()
        
        except: 
            print('Error: could not delete item')
        
                
    @pyqtSlot()
    def on_addReportBtn_clicked(self): 
        reportText = self.ui.reportNameInput.text()
        
        if(reportText != ''): 
            createReportquerry = 'INSERT INTO icpReportType (reportType) values (?)'
            try:
                self.db.execute(createReportquerry, (reportText,) )
                self.db.commit()
                self.ui.reportsList.addItem(reportText)
                self.ui.reportNameInput.setText("")
            except sqlite3.IntegrityError as e:
                print(e)

        else: 
            print("Error No Report Name")

    def loadReportList(self): 
        results = loadIcpReportList(self.db)
        self.ui.reportsList.clear()
        
        if(results): 
            for item in results: 
                self.ui.reportsList.addItem(item[0])    
        
   
    def on_definedElements_clicked(self):
        try:
            icp_load_element_data(self);
        except: 
            print('Error: Could not loaded the defined element data')

          
    def on_definedElements_currentRowChanged(self):
        try:
            icp_load_element_data(self);
        except: 
            print('Error: Could not loaded the defined element data')
            
    
    def on_reportsList_clicked(self): 
        reportType = self.ui.reportsList.currentItem().text()
        self.ui.footerComments.setText(None)
        self.ui.icpReportNameLabel.setText(reportType) 
        
        try:
            result = loadIcpFooterComment(self.db, reportType)
            list_binary = result[0]
            
            #TODO: what the hell is this function even doing? 
            if(list_binary): 
                commentList = pickle.loads(list_binary)
                text = '\n'.join(commentList)
                self.ui.footerComments.insertPlainText(text)
                
        except:
            print("Error: Couldn't load comment") 
        

    @pyqtSlot() 
    def on_saveFooterBtn_clicked(self):        
        saveComment = self.ui.footerComments.toPlainText()
        reportType = self.ui.reportsList.currentItem()
                
        if(saveComment != ''):            
            commentLists = saveComment.split('\n')
            list_binary = pickle.dumps(commentLists)
                        
            try: 
                updateFooterCommentQuery = 'UPDATE icpReportType SET footerComment = ? WHERE reportType = ?'
                self.db.execute(updateFooterCommentQuery, (list_binary, reportType.text()))
                self.db.commit()
            except: 
                print("Error: updating footer not working")            
        else: 
            print('Nothing is the same')

    @pyqtSlot() 
    def on_deleteFooterBtn_clicked(self): 
        reportType = self.ui.icpReportNameLabel.text()
        print(reportType)
        
        deleteQuery = 'DELETE FROM icpReportType WHERE reportType = ?'
        
        if(reportType != ""): 
            try: 
                self.db.execute(deleteQuery, (reportType, ))
                self.db.commit()
                self.clearFooterReportContent(); 

                item = self.ui.reportsList.currentRow(); 
                
                if(item != -1): 
                    self.ui.reportsList.takeItem(item)
                
            except: 
                print("Error on_deleteFooterBtn_clicked: Deleting Report Type")
        
    
    def clearFooterReportContent(self): 
        self.ui.icpReportNameLabel.setText("")
        self.ui.footerComments.clear()
        
    def loadDefinedElements(self): 
        self.ui.reportTypeDropdown.clear()
        self.ui.gcmsDefinedtests.clear()
        self.ui.definedElements.clear()
    
        elements = getIcpElements(self.db)      
     
        reportType = getReportTypeList(self.db)
        self.ui.reportTypeDropdown.addItems(reportType)     
        
        for element in elements: 
            self.ui.definedElements.addItem(element[0])

        self.clearElementInfo()
            
    def clearElementInfo(self): 
        self.ui.symbolInput.clear()
        self.ui.elementNameinput.clear()
        
        self.ui.lowerLimit.clear()
        self.ui.upperLimit.clear()
        self.ui.unitType.clear()
        self.ui.RightSideComment.clear()
        
    def clearElementLimits(self): 
        self.ui.lowerLimit.clear()
        self.ui.upperLimit.clear()
        self.ui.unitType.clear()
        self.ui.RightSideComment.clear()
        
    def clearDataTable(self): 
        self.ui.dataTable.clearContents()
        self.ui.dataTable.setRowCount(0)
    
    def updateIcpTable(self, result): 
        textLabelUpdate = 'Total Search Results: ' + str(len(result))

        self.ui.icpLabel.setText(textLabelUpdate)
        self.ui.icpTable.setRowCount(len(result)) 
        self.ui.icpTable.setColumnWidth(3, 600)
        
        for i, data in enumerate(result):
            #loops throught items in the order sql requested 
            for j in range(len(data)): 
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(data[j]))
                item.setTextAlignment(Qt.AlignHCenter)
                self.ui.icpTable.setItem(i,j,item) 
        
        self.ui.icpTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    @pyqtSlot()
    def on_icpSearchBtn_clicked(self): 
        jobNum = self.ui.icpSearchInput.text() 
        inquery = 'SELECT sampleName, jobNumber, machine, fileLocation, createdDate data FROM icpMachineData1 WHERE sampleName LIKE ?'
        
        if(jobNum == ''):
            pass; 
        else: 
            machine1Data = list(self.db.query(inquery, ('%' + jobNum + '%',)))
            
            #TODO: create a message button, streamline the process 
            #TODO: check to make sure not duplicate as well 
            if not machine1Data: 
                msgBox = QMessageBox()  
                msgBox.setText("No Search Results");
                msgBox.setInformativeText("No search results for given job number");
                msgBox.setStandardButtons(QMessageBox.Ok);
                x = msgBox.exec_()  # this will show our messagebox
                
            else: 
                self.updateIcpTable(machine1Data)

    @pyqtSlot()
    def on_icpUploadBtn_clicked(self): 
        fileLocation = openFile()
        print(fileLocation)
        icp_upload(fileLocation, self.db) 
    
    def on_reportlist_doubleClicked(self): 
        print('Something is being selected')
        selected_item = self.ui.reportsList.currentItem()
    
  
   #******************************************************************
   #    CHM TEST PAGE 
   #****************************************************************** 
   #TODO: if the txt name changes update the listName 
   #TODO: keep track of the currentIndex when first getting it 
   
    def gcmsGetListValues(self): 
        values = []
        
        for index in range(self.ui.gcmsDefinedtests.count()):
            item = self.ui.gcmsDefinedtests.item(index)
            values.append(item.text())
            
        return values; 
    
    
    def gcmsClearDefinedTestsValues(self): 
        self.ui.gcmsDisplayName.clear()
        self.ui.gcmsTxtName.clear()
        self.ui.gcmsUnitType.clear()
        self.ui.gcmsRefValue.clear()
        self.ui.gcmsComment.clear()
     
    
    @pyqtSlot() 
    def on_gcmsAddTestsBtn_clicked(self): 
        existingTests = self.gcmsGetListValues()        
        currentText = self.ui.testsInputLabel.text()
        
        if(currentText != '' and currentText not in existingTests): 
            #clear values 
            self.gcmsClearDefinedTestsValues()
            self.ui.testsInputLabel.clear()
            self.ui.gcmsDefinedtests.addItem(currentText)
    
            totalItems = len(self.gcmsGetListValues())
            self.ui.gcmsDefinedtests.setCurrentRow(totalItems-1)
            self.ui.gcmsTxtName.setText(currentText)
            
        else: 
            errorTitle = 'Invald Tests'
            errorMsg = 'Please enter a valid test'
            showErrorDialog(self, errorTitle, errorMsg)


    @pyqtSlot()
    def on_gcmsSaveTestBtn_clicked(self):
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
    def on_gcmsDeleteTestBtn_clicked(self): 
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
            
            self.gcmsClearDefinedTestsValues()
        
        except: 
            print('Error: could not delete item')
        
    
    @pyqtSlot()
    def on_gcmsDefinedtests_clicked(self): 
        chmLoadTestsData(self)
            
    def on_gcmsDefinedtests_currentRowChanged(self):
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
   #    CHM data Entry  
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
            self.ui.widget_28.setEnabled(False)
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
                    self.addToGcmsTestsData(sampleNum, testName, sampleVal, standards, units, testNum)
                    
                    matching_items = self.ui.gcmsTestsLists.findItems(sampleNum, Qt.MatchExactly) 
                    if not matching_items: 
                        self.ui.gcmsTestsLists.addItem(sampleNum)
                    
                    self.gcmsClearSampleJob() 
                    
                if(x == QMessageBox.No):
                    self.gcmsClearSampleJob() 
                    
                if(x == QMessageBox.Cancel):
                    pass 
                
            else: 
                self.addToGcmsTestsData(sampleNum, testName, sampleVal, standards, units, testNum)
                self.ui.gcmsTestsLists.addItem(sampleNum)
                self.gcmsClearSampleJob() 
                
                
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
    
            
    def gcmsClearSampleJob(self): 
        self.ui.gcmsTestsSample.clear()
        self.ui.gcmsTestsVal.clear() 
             
    def gcmsClearSideData(self): 
        self.ui.gcmsStandardVal.clear()
        self.ui.gcmsUnitVal.clear()
        self.ui.gcmsTests.clear() 
           
    def gcmsClearEnteredTestsData(self): 
        self.ui.gcmsTestsValueWidget.setEnabled(False)
        self.ui.widget_28.setEnabled(True)
            
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


    def addToGcmsTestsData(self, sampleNum, testName, sampleVal, standards, units, jobNum ): 
        addInquery = 'INSERT OR REPLACE INTO gcmsTestsData (sampleNum, testsName, testsValue, StandardValue, unitValue, jobNum) VALUES (?,?,?,?,?, ?)'
        
        try:
            self.db.execute(addInquery, (sampleNum, testName, sampleVal, standards, units, jobNum,) )
            self.db.commit()

        except sqlite3.IntegrityError as e:
            print(e) 
 
 
    def loadChmDatabase(self): 
        print('[FUNCTION]: loadChmDatabase, Loading Existing Data'); 
        
        TableHeader = ['Sample Number', 'Tests', 'Test Values', 'Standard Value', 'Unit Value', 'Job Num', 'Delete']
        chmTable = self.ui.gcmsInputTable 

        self.formatTable(chmTable) ;

        results = loadChmTestsData(self.db) 
        #print(results)
        
        self.ui.gcmsInputTable.setRowCount(len(results))
        self.ui.gcmsInputTable.setColumnCount(len(TableHeader))
        self.ui.gcmsInputTable.setHorizontalHeaderLabels(TableHeader)
        
        for i, result in enumerate(results):
            for j in range(len(TableHeader)-1):
                data = str(result[j]) 
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                
                self.ui.gcmsInputTable.setItem(i, j, item)     

            button = QPushButton("Delete")
            self.ui.gcmsInputTable.setCellWidget(i ,6, button)
            button.clicked.connect(lambda _, row=i: self.chmTableDeleteRow(row));
            
    def chmTableDeleteRow(self, row): 
        print(f'[FUNCTION]: chmTableDeleteRow, row to delete {row}')
        
        sampleNum = self.ui.gcmsInputTable.item(row, 0).text()
        testsName = self.ui.gcmsInputTable.item(row, 1).text()
        self.ui.gcmsInputTable.removeRow(row)
        deleteChmData(self.db, sampleNum, testsName)
   
    
   #******************************************************************
   #    Settings Page Options 
   #****************************************************************** 
    def on_settingsStack_currentChanged(self, index): 
        if(index == 2): 
            self.ui.authorList.clear()
            self.clearAuthorData()
            self.loadAuthors()
        
    @pyqtSlot()
    def on_setPathsBtn_clicked(self): 
        self.ui.settingsStack.setCurrentIndex(0)
    
    @pyqtSlot() 
    def on_setUnitsBtn_clicked(self): 
        pass;  

    @pyqtSlot()
    def on_setAuthorsBtn_clicked(self): 
        self.ui.settingsStack.setCurrentIndex(2)   
         
    @pyqtSlot()
    def on_reportsPathBtn_clicked(self): 
        paths = load_pickle('data.pickle')
        newLocation = getFileLocation()
        if(newLocation != ''): 
            paths['reportsPath'] = newLocation; 
            save_pickle(paths)
            self.ui.reportPath.setText(paths['reportsPath'])
        
    @pyqtSlot()
    def on_txtPathBtn_clicked(self): 
        paths = load_pickle('data.pickle')
        newLocation = getFileLocation()
        if(newLocation != ''): 
            paths['TXTDirLocation'] = newLocation; 
            save_pickle(paths)
            self.ui.txtPath.setText(paths['TXTDirLocation'])
    
    @pyqtSlot() 
    def on_convertedPathBtn_clicked(self): 
        paths = load_pickle('data.pickle')
        newLocation = getFileLocation() 
        if(newLocation != ''): 
            paths['ispDataUploadPath'] = newLocation; 
            save_pickle(paths) 
            self.ui.convertPath.setText(paths['ispDataUploadPath'])
        
    @pyqtSlot()  
    def on_dbPathBtn_clicked(self):
        paths = load_pickle('data.pickle')
        newLocation = openFile()
        if(newLocation != ''): 
            paths['databasePath'] = newLocation; 
            save_pickle(paths)  
            self.ui.dbPath.setText(paths['databasePath'])
        
    #TODO: have a path object that will deal with all of the other bs that I have writen here 
    def loadSettings(self): 
        paths = load_pickle('data.pickle')
        self.ui.reportPath.setText(paths['reportsPath'])
        self.ui.txtPath.setText(paths['TXTDirLocation'])
        self.ui.convertPath.setText(paths['ispDataUploadPath'])
        self.ui.dbPath.setText(paths['databasePath'])



    #******************************************************************
    #    Settings Page Options 
    #       - Author Settings 
    #****************************************************************** 
    def loadAuthors(self): 
        authorsQuery = 'SELECT * FROM authors ORDER BY authorName ASC'

        try: 
            results = self.db.query(authorsQuery)
            print('Loading Authors')
            print(results)
            for author in results: 
                self.ui.authorList.addItem(author[0])
            
        except: 
            print('Error: could not load authors')
        
    def clearAuthorData(self): 
        self.ui.authorNameLine.clear()
        self.ui.authorPostionLine.clear()
        
    @pyqtSlot()  
    def on_saveAuthorBtn_clicked(self): 
        authorName = self.ui.authorNameLine.text()
        authorPosition = self.ui.authorPostionLine.text()
        
        if((authorName != None or '') and (authorPosition != None or "")): 
            sql = 'INSERT OR REPLACE INTO authors (authorName, authorPosition) VALUES (?,?)'
            try:
                self.db.execute(sql, (authorName, authorPosition,) )
                self.db.commit()

            except sqlite3.IntegrityError as e:
                print(e) 
         
        
    @pyqtSlot()  
    def on_deleteAuthorBtn_clicked(self): 
        deleteQuery = 'DELETE FROM authors WHERE authorName = ?' 
        authorName = self.ui.authorList.currentItem().text() 
        
        try: 
            self.db.execute(deleteQuery, (authorName,))
            self.db.commit()
            self.removeAuthorFromAuthorList(authorName)
        except:
            print("Error: Could not delete author: ", authorName)


    def on_authorList_currentItemChanged(self, authorName):   
        if(authorName != None):  
            self.loadAuthorInfo(authorName.text())
    
    def removeAuthorFromAuthorList(self, authorName): 
        for row in range(self.ui.authorList.count()): 
            item = self.ui.authorList.item(row)
            if item.text() == authorName: 
                self.ui.authorList.takeItem(row)
                break;         

    
    def loadAuthorInfo(self, authorName):             
        result = getAuthorInfo(self.db, authorName) 
        
        if(result): 
            self.ui.authorNameLine.setText(result[0])
            self.ui.authorPostionLine.setText(result[1])
        else: 
            print("Error loading author info")
            self.clearAuthorData()
            self.ui.enterAuthorName.clear()
            self.ui.authorNameLine.setText(authorName)
            
    
    #add authors 
    @pyqtSlot()  
    def on_addAuthor_clicked(self): 

        authorName = self.ui.enterAuthorName.text()

        sql = "SELECT authorName FROM authors"
        result = self.db.query(sql)
        
        print(result)
        
        if(authorName != ''): 
            self.ui.authorList.addItem(authorName)
            self.ui.authorNameLine.setText(authorName)
         
            new_item_index = self.ui.authorList.count() - 1
            self.ui.authorList.setCurrentRow(new_item_index)

    
   #******************************************************************
   #    Create Report Process 
   #****************************************************************** 
  
    @pyqtSlot()
    def createReportPage(self, jobNum = None, reportType = None, parameter = None, dilution =None, method2= None):
        print('[FUNCTION]: createReportPage')
         
        jobNum = jobNum or self.ui.jobNumInput.text().strip()
        reportType = reportType or self.ui.reportType.currentText()
        parameter = parameter or self.ui.paramType.currentText()
        dilution = dilution or self.ui.dilutionInput.text()
            
        #TODO: check if it is a valid dilution value 
        #TODO: change the dilution thing into a number only slider lol, so the default would be 1 and otherwise 
        self.dilution = 1 if dilution == '' else dilution 

        print('*JobNumber: ', jobNum)
        print('*ReportType: ', reportType)
        print('*Parameter: ', parameter)
        print('*Dilution: ', dilution )
        
        errorCheck = [0, 0, 0, 0]     
        fileExist = scanForTXTFolders(jobNum)
     
        errorCheck[0] = 0 if re.match('^([0-9]{6})$', jobNum) else 1 
        errorCheck[1] = 0 if reportType in REPORTS_TYPE else 1
        errorCheck[2] = 0 if parameter != '' else 1
        errorCheck[3] = 0 if fileExist != '' else 1    
        
        if(sum(errorCheck) == 0): 
            self.jobNum = jobNum; 
            self.parameter = parameter 
            self.reportType = reportType
            self.activeCreation = True; 

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
            #TODO: have one button instead these two that get switched around lol
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

    def deleteAllSampleWidgets(self): 
        for widget in self.ui.samplesContainer.children():
            if isinstance(widget, SampleNameWidget):
                widget.setParent(None)
                widget.deleteLater()
            
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
   #   Global Functions 
   #******************************************************************         
    #TODO: could be moved to the utiles.py 

    def handle_item_changed(self, item, test): 
        row = item.row()
        column = item.column()
        value = item.text()
        
        if(column >= 5):
            print(self.ui.dataTable.item(row,column).text())
            
    def updateSampleNames(self, textChange, key):
        self.sampleNames[key] = textChange; 
        print(f'Update Sample Name: {self.sampleNames}')
 
  
   #******************************************************************
   #   Other/Testing Area 
   #****************************************************************** 

    def getElementLimits(self): 
        elementsQuery = 'SELECT element FROM icpLimits WHERE reportType = ? ORDER BY element ASC'
        elementWithLimits = self.db.query(elementsQuery, ('Water',))    
        
        temp = []

        for item in elementWithLimits: 
            #print(item)
            temp.append(item[0]) 
        
        return temp; 
    
    def open_new_window(self):
        #data = 'Hello from Main Window!'
        #new_window = NewWindow(data)
        #new_window.show()
        
        data = [
            [1, 'John', 'Doe'],
            [2, 'Jane', 'Smith'],
            [3, 'Bob', 'Johnson']
        ]

        dialog = CustomDialog(data, 1)
        #dialog.exec_()
        
        if dialog.exec_() == QDialog.accept:
            print('Dialog closed with Accept')
        else:
            print('Dialog closed with Reject')

    @pyqtSlot()
    def on_testBtn_clicked(self): 
        print('Test Button Pressed')

        dialog = ChmTestsDialog()
        user_input = dialog.get_user_input()

        if user_input is not None:
            print(f"User entered: {user_input}")
        else:
            print("User canceled.")



    
