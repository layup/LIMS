#PYQT Imports 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle, QStyledItemDelegate, QAbstractItemView
from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, pyqtSlot, QDateTime

#general Imports 
import sys 
import pandas as pd
import json
import sys 
import re 
import asyncio
import pickle

from modules.createExcel import * 
from modules.utilities import * 
from modules.dbManager import *
from modules.excelCreation import *
from interface import *
    
class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        
        paths = load_pickle('data.pickle')
        self.db = Database(paths['databasePath'])
       
        #define other widget setups 
        self.setWindowTitle("Laboratory Information management System") 
        self.ui.LeftMenuContainerMini.hide()

        self.activeCreation = False; 
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.reportsBtn1.setChecked(True)
        

        
        size = self.size()
        width = size.width() 
        
        #TODO: move this into a different function 
        columnWidth = width / 7
        
        for column in range(7): 
            self.ui.reportsTable.setColumnWidth(column, columnWidth)

        #self.ui.jobNumInput.textChanged.connect(lambda: print(self.ui.jobNumInput.text()))
        #load initial database 
        
        #temp = {'ispDataUploadPath': '/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/data/uploadData', 
        #        'databasePath':'/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/ISP.db',
        #        'TXTDirLocation':'/Users/layup/Downloads/MB_LABS/TXT files/'}
        #temp['TXTDirLocation'] = getFileLocation()
        #save_pickle(temp)

        self.loadCreatePage()
        
        #connect buttons 
        self.ui.NextSection.clicked.connect(lambda: self.proceedPage())
        self.ui.clientInfoBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.dataEntryBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        
        
        self.ui.reportTypeDropdown.activated.connect(lambda: self.loadElementLimits())        
        self.showMaximized()
        #self.show()

    
    ## Change QPushButton Checkable status when stackedWidget index changed
    def messageBox(self):
        msgBox = QMessageBox()  
        msgBox.setText("The document has been modified.");
        msgBox.setInformativeText("Do you want to save your changes?");
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel);
        msgBox.setDefaultButton(QMessageBox.Save);
        #msgBox.buttonClicked.connect(self.msgbtn)
        x = msgBox.exec_()  # this will show our messagebox
        
        if(x == QMessageBox.Save): 
            self.ui.stackedWidget.setCurrentIndex(0)  
            self.activeCreation = False; 
        if(x == QMessageBox.Discard):
            self.ui.stackedWidget.setCurrentIndex(0) 
            self.activeCreation = False; 
        if(x == QMessageBox.Cancel):
            pass 
        
        
    def loadReport(self): 
        msgBox = QMessageBox()  
        msgBox.setText("Report Already Exists");
        msgBox.setInformativeText("Would you like to load existing report or overwrite report?");
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);
        msgBox.setDefaultButton(QMessageBox.Yes);
        
        x = msgBox.exec_()

        if(x == QMessageBox.Yes): 
            pass
            #FIXME: load in the values as well 
        if(x == QMessageBox.No):
            pass 
        if(x == QMessageBox.Cancel):
            pass 
        
    def deleteBox(self, title, message, action):
        msgBox = QMessageBox()  
        msgBox.setText(title);
        msgBox.setInformativeText(message);
        msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        x = msgBox.exec_() 
        
        if(x == QMessageBox.Yes): 
            pass
        if(x == QMessageBox.No):
            pass 
        

   
    def on_stackedWidget_currentChanged(self, index):
        #print('Running')
        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)
        
        #print(btn_list)
        #FIXME: issue that arises when the active creation setting is thing 
        for btn in btn_list:
            #if index in [1,2,3,4]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            #else:s
            btn.setAutoExclusive(True)
                   
        if(index == 0): 
            self.loadReportsPage(); 
            
        if(index == 1): 
            self.ui.jobNumInput.setText('171981')
            self.ui.reportType.setCurrentIndex(0)
            self.ui.paramType.setCurrentIndex(0)
            

            

    def loadCreatePage(self): 
        print('Loading user information')
        
        #load the report Types
        
        
        self.ui.reportType.addItems(REPORTS_TYPE)

        paramResults = sorted(self.getReportTypeList())
        paramResults.insert(0, "")
       
        self.ui.paramType.addItems(paramResults)
        
        #based on what the reportType is should load the appropriate parameters Type 
        
    
    def loadReportsPage(self): 
    
        print('Loading Report Page')
       
        #FIXME: include the other table and also some how to open up this table again  
        #TODO: sort by date or something
        query = 'SELECT * FROM jobs' 
        results = list(self.db.query(query)) 
        print(results)

        self.ui.reportsTable.setRowCount(len(results))
    
        #inital columns 
        for row, current in enumerate(results): 
            item = QtWidgets.QTableWidgetItem() 
            item.setTextAlignment(Qt.AlignCenter)
            item.setText(str(current[1])) 
            self.ui.reportsTable.setItem(row, 0, item)  

            item2 = QtWidgets.QTableWidgetItem()
            item2.setTextAlignment(Qt.AlignCenter)
            item2.setText(str(current[2]))
            self.ui.reportsTable.setItem(row, 1, item2)  
            
            item2 = QtWidgets.QTableWidgetItem()
            item2.setTextAlignment(Qt.AlignCenter)
            item2.setText(str(current[3]))
            self.ui.reportsTable.setItem(row, 2, item2)
            
            item2 = QtWidgets.QTableWidgetItem()
            item2.setTextAlignment(Qt.AlignCenter)
            item2.setText(str(current[5]))
            self.ui.reportsTable.setItem(row, 3, item2)  
             
           
            item2 = QtWidgets.QTableWidgetItem()
            item2.setTextAlignment(Qt.AlignCenter)
            
            if(current[4] == 1): 
                item2.setText('COMPLETE')
            else: 
                item2.setText("INCOMPLETE")
            
            self.ui.reportsTable.setItem(row,4, item2)   
            
        button = QPushButton("Click me!")
        self.ui.reportsTable.setCellWidget(1,1, button)
        
        self.ui.reportsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.reportsTable.doubleClicked.connect(self.on_table_double_clicked )

        #TODO: if sleected open this thing 

    def on_table_double_clicked(self, index):
    # Open the row data
        row = index.row()
        print(f"Double clicked on row {row}")
    
    #Define Menu Button presses 
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
        
    def on_gsmsBtn1_clicked(self): 
        self.ui.gcmsStack.setCurrentIndex(0)
     
    #Define ICP Page Menu Buttons 
    def on_icpBtn1_clicked(self): 
        self.ui.icpStack.setCurrentIndex(0)
    
    def on_icpBtn2_clicked(self): 
        self.ui.icpStack.setCurrentIndex(0)
    
    def on_icpDatabaseBtn_clicked(self): 
        self.ui.icpStack.setCurrentIndex(1)
        
        columnNames = ['Sample Name', 'Job Number', 'Machine Type', 'File Location', 'Upload Date']
        
        #load both databases 
        #TODO: set the machine values for both of theses, create a single inqury that fetches based on date
        icpMachine1sql = 'SELECT sampleName, jobNumber, machine, fileLocation, createdDate data FROM icpMachineData1 ORDER BY createdDate DESC' 
        icpMachine2sql = 'SELECT sampleName, jobNumber, fileLocation, createdDate, machine data FROM icpMachineData2'
        
        machine1Data = list(self.db.query(icpMachine1sql))
        #machine2Data = list(self.db.query(icpMachine2sql))
        
        self.updateIcpTable(machine1Data)

    def on_icpElementsBtn_clicked(self): 
        self.ui.icpStack.setCurrentIndex(2)
        #TODO: load in the total elements 
        #TODO: add something when activated 
        
        total = self.getTotalElements()
        self.ui.icpLabel.setText("Total Elements: {}".format(total))
        
        
        
        #self.ui.addElementBtn.clicked.connect(lambda: self.add_element())
    
    @pyqtSlot()
    def on_icpReportBtn_clicked(self): 
        self.ui.icpStack.setCurrentIndex(3)
        self.loadReportList()
        
        
    #ICP Buttons 
    @pyqtSlot()
    def on_addElementBtn_clicked(self): 
        #TODO: add a message box about adding blanks 
        currentText = self.ui.elementInput.text()
        
        if(currentText != ''): 
            print(currentText)
            self.ui.definedElements.addItem(currentText)
            self.ui.elementInput.clear()
            
        else: 
            print("Please enter not blank")
         
         
    @pyqtSlot()
    def on_saveCompBtn_clicked(self): 
        #TODO: remove white spaces just in case 
        #TODO: check if they are valid limits
        symbolName = self.ui.symbolInput.text().lower().strip()
        elementName = self.ui.elementNameinput.text().lower().strip()
        
        lowVal = self.ui.lowValueInput.text()
        standVal = self.ui.standardValueInput.text()
        highVal = self.ui.HighValueInput.text()
        
        reportType = self.ui.reportTypeDropdown.currentText()
        lowerLimit = self.ui.lowerLimit.text()
        upperLimit = self.ui.upperLimit.text()
        unitType = self.ui.unitType.text().strip()
        
        comment = self.ui.RightSideComment.toPlainText() 
        
        print(symbolName, elementName)
        
        if(symbolName != "" and elementName != ""):
            
            defineElementQuery = 'INSERT OR REPLACE INTO icpElements (element, symbol, lowValue, standValue, highValue) VALUES (?,?,?,?,?)'
            #definedLimitsQuery = 'INSERT OR REPLACE INTO icpLimits (reportType, element, lowerLimit, maxLimit, comments, units) VALUES (?,?,?,?,?,?)'
            
            loadLimits = 'SELECT * FROM icpLimits WHERE element = ? and ReportType = ?'  
            self.db.execute(loadLimits, (elementName, reportType))
            limitResults = self.db.fetchone()
            
            insertLimit = 'INSERT INTO icpLimits (reportType, element, lowerLimit, maxLimit, comments, units) VALUES (?,?,?,?,?,?)' 
            updateLimit = 'UPDATE icpLimits SET lowerLimit = ?, maxLimit = ?, comments =?, units =? WHERE reportType=? AND element=?' 

            try:
                self.db.execute(defineElementQuery, (elementName, symbolName, lowVal, standVal, highVal) )
                
                if(limitResults): 
                    self.db.execute(updateLimit, (lowerLimit, upperLimit, comment, unitType, reportType, elementName))
                else: 
                    self.db.execute(insertLimit, (reportType, elementName, lowerLimit, upperLimit, comment, unitType))
                
                self.db.commit()

            except sqlite3.IntegrityError as e:
                print(e)

    @pyqtSlot()
    def on_deleteCompBtn_clicked(self):
        print("Deleting the componenet")

        elementName = self.ui.elementNameinput.text().lower()
        print(elementName)
        #TODO: are you sure you wanted to delete this time popup
        #TODO: error when deleting nothing
        
        deleteQuery = 'DELETE FROM icpElements WHERE element = ?'
        
        try: 
            self.deleteBox("DELETE ELEMENT", "ARE YOU SURE YOU WANT TO DELETE THIS ITEM", lambda:print("hello World"))
            
            self.db.execute(deleteQuery, (elementName,))
            self.db.commit()

            currentItem = self.ui.definedElements.currentRow()
            self.ui.definedElements.takeItem(currentItem)
            self.ui.definedElements.setCurrentItem(None)
            self.clearElementInfo()
        
        except: 
            print('Error: could not delete item')
            
    
    def loadElementLimits(self): 
        print('CHANGE')
        reportType = self.ui.reportTypeDropdown.currentText()
        elementName = self.ui.elementNameinput.text().lower()

        limitsQuery = 'SELECT * from icpLimits WHERE reportType = ? and element = ?'
        
        try: 
            self.db.execute(limitsQuery, (reportType, elementName))
            limitResults = self.db.fetchone()
            print('results: ', limitResults)
            if(limitResults is None): 
                self.clearElementLimits()
            else: 
                self.ui.lowerLimit.setText(str(limitResults[2]))
                self.ui.upperLimit.setText(str(limitResults[3]))
                self.ui.unitType.setText(limitResults[5])
                self.ui.RightSideComment.setPlainText(limitResults[4]) 
            
        except: 
            print('Error: Could not load in limits ')
       
        
                
    @pyqtSlot()
    def on_addReportBtn_clicked(self): 
        reportText = self.ui.reportNameInput.text()
        
        if(reportText != ''): 
           
            createReportquerry = 'INSERT INTO icpReportType values (?)'
            
            try:
                self.db.execute(createReportquerry, (reportText,) )
                self.db.commit()
                self.ui.reportsList.addItem(reportText)
            except sqlite3.IntegrityError as e:
                print(e)

        else: 
            print("Error No Report Name")

    def loadReportList(self): 
        
        loadquerry = 'SELECT * FROM icpReportType' 
        results = self.db.query(loadquerry)
        
        self.ui.reportsList.clear()
        
        for item in results: 
            #print(item)
            self.ui.reportsList.addItem(item[0])    
        
   
    def on_definedElements_clicked(self):
        print('Defined Elements')
         
        selected_item = self.ui.definedElements.currentItem()
        
        if selected_item is not None:
            selected_item_text = selected_item.text()
            print(selected_item_text); 
            
            loadElement = 'SELECT * FROM icpElements WHERE element = ?'
            loadLimits = 'SELECT * FROM icpLimits WHERE element = ? and ReportType = ?'
            
            self.db.execute(loadElement, (selected_item_text,))
            elementResult = self.db.fetchone()
           
            reportType = self.ui.reportTypeDropdown.currentText()
            
            self.db.execute(loadLimits, (selected_item_text, reportType))
            limitResults = self.db.fetchone()
            
            print(elementResult); 
            if elementResult: 
                
                self.ui.elementNameinput.setText(elementResult[0])
                self.ui.symbolInput.setText(elementResult[1])
                self.ui.lowValueInput.setText(elementResult[2])
                self.ui.HighValueInput.setText(elementResult[3])
                self.ui.standardValueInput.setText(elementResult[4])
                
                if(limitResults is None): 
                    self.clearElementLimits()
                else: 
                    self.ui.lowerLimit.setText(str(limitResults[2]))
                    self.ui.upperLimit.setText(str(limitResults[3]))
                    self.ui.unitType.setText(limitResults[5])
                    self.ui.RightSideComment.setPlainText(limitResults[4])
                
            else: 
                self.clearElementInfo()
                self.ui.elementNameinput.setText(selected_item_text)
            
        else:
            print("No item selected.")

    def on_reportsList_clicked(self): 
        reportType = self.ui.reportsList.currentItem().text()
        self.ui.footerComments.setText(None)
        
        try:
            loadFooterComment = 'SELECT footerComment from icpReportType WHERE reportType = ?'
            self.db.execute(loadFooterComment, (reportType,))
            result = self.db.fetchone()
            list_binary = result[0]
            
            if(list_binary): 
                commentList = pickle.loads(list_binary)
                text = '\n'.join(commentList)
                self.ui.footerComments.insertPlainText(text)
                
        except:
            print("Error: Couldn't load comment") 
        

    @pyqtSlot() 
    def on_saveFooter_clicked(self):        
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
        
        
    def on_icpStack_currentChanged(self, index):
        
        if(index == 2): 
            self.loadDefinedElements()        
            
    
    def loadDefinedElements(self): 
        print("Loading Defined Elements Friends")
            
        self.ui.reportTypeDropdown.clear()
        self.ui.definedElements.clear()
    
        getElementsQuery = 'SELECT * FROM icpElements ORDER BY element ASC'
        definedElements = self.db.query(getElementsQuery)        
     
        reportType = self.getReportTypeList()
        self.ui.reportTypeDropdown.addItems(reportType)     
        
         
        for element in definedElements: 
            self.ui.definedElements.addItem(element[0])

        self.clearElementInfo()
            
    def clearElementInfo(self): 
        self.ui.symbolInput.clear()
        self.ui.elementNameinput.clear()
        self.ui.lowValueInput.clear()
        self.ui.HighValueInput.clear()
        self.ui.standardValueInput.clear()
        
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
            if not machine1Data: 
                msgBox = QMessageBox()  
                msgBox.setText("No Search Results");
                msgBox.setInformativeText("No search results for given job number");
                msgBox.setStandardButtons(QMessageBox.Ok);
                x = msgBox.exec_()  # this will show our messagebox
                
            else: 
                self.updateIcpTable(machine1Data)

    #button activations  
    @pyqtSlot()
    def on_icpUploadBtn_clicked(self): 
        fileLocation = openFile()
        print(fileLocation)
        icp_upload(fileLocation, self.db) 
        
        #check if the file is .xlsx or txt document 
    
    def on_reportlist_doubleClicked(self): 
        print('Something is being selected')
        
        selected_item = self.ui.reportsList.currentItem()
    
                
    def keyPressEvent(self, event):
        #print(event)

        if event.key() == Qt.Key_Enter:
            #self.test_method()
            pass 
        if event.key() == Qt.Key_Space: 
            #elf.test_method()
            pass
        
    def savePickle(self): 
        jsonLocation = getFileLocation()
        
        tempDictonary = {
            "JSONFileLocation":'/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/fileLocation.json', 
            "TXTDirLocation": jsonLocation 
        }
        
        save_pickle(tempDictonary)
        
    
    #PROCESS PAGE 
    def proceedPage(self):
        
        jobNum = self.ui.jobNumInput.text().strip()
        reportType = self.ui.reportType.currentText()
        parameter = self.ui.paramType.currentText()
        
    
        #0 = name 
        #1 = reportType 
        #2 = parameter 
        errorCheck = [0, 0, 0]       
     
        if(re.match('^([0-9]{6})$', jobNum)): 
            errorCheck[0] = 0; 
        else: 
            errorCheck[0] = 1; 
            #self.ui.jobNumInput.setStyleSheet('border:1px solid red;')
         
        if(reportType != ''):
            errorCheck[1] = 0;
            
        else: 
            errorCheck[1] = 1; 
        
        if(parameter != ''): 
            errorCheck[2] = 0
        else: 
            errorCheck[2] = 1
            
        print("ErrorCheck: ", errorCheck)
        
        
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

            checkReports = 'SELECT * FROM jobs WHERE jobNum = ? and reportType = ?'
            self.db.execute(checkReports, (jobNum, reportType)) 
            reportResult = self.db.fetchone()
            
            if reportResult is None:  
                print('No Exists, adding to the file')
                createReport(self.db, jobNum, reportType, parameter)
            else: 
                print('Report Exists')
                print(reportResult)
                #TODO: load the report if exists
                self.loadReport()            
  
            self.ui.stackedWidget.setCurrentIndex(5)
            self.ui.stackedWidget_2.setCurrentIndex(0) 
            self.clearDataTable()
            
            self.ui.jobNum.setText(jobNum)
            

            if('ISP' in reportType):
                print('ISP Loader')
                self.ui.icpDataField.show()
                self.icpLoader()
            
            if(reportType == 'GCMS'):
                print('GCMS Loader')
                self.ui.icpDataField.hide() 
                self.gcmsLoader()
            
        else: 
            outputMessage = ''
            
            if(errorCheck[0] == 1): 
                print('Error: Please Enter a valid job number')
                outputMessage += 'Please Enter a Valid Job Number\n'

            if(errorCheck[1] == 1): 
                print("Error: Please Select a reportType")
                outputMessage += 'Please Select a Report Type\n'
                
            if(errorCheck[2] == 1): 
                print('Error: Please Select a parameter')
                outputMessage += 'Please Select a Parmeter\n'
                
            msg = QMessageBox() 
            msg.setWindowTitle("Error")
            msg.setText(outputMessage)
            x = msg.exec_()  # this will show our messagebox

            
     
    def loadExistingInfo(self): 
        
        pass; 
    
    def overWriteExisting(self): 
        pass; 
    
    
    def gcmsLoader(self): 
        
        self.loadClientInfo()
    
        #check if the samples are ISP or not 
        
        #load sample names 
        for i, (key,value) in enumerate(self.sampleNames.items()):
            item = SampleNameWidget(key, value)
            self.ui.formLayout_5.addRow(item)
            item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
        
        self.ui.stackedWidget.currentChanged.connect(lambda: self.removeWidgets())
        
        GSMS_TESTS_LISTS = []
        ICP_TESTS_LISTS = []
        tests = []
        
        for (currentJob ,testList) in self.sampleTests.items(): 
            for item in testList: 
                if(item not in GSMS_TESTS_LISTS and 'ICP' not in item):
                    GSMS_TESTS_LISTS.append(item)
                if(item not in ICP_TESTS_LISTS and 'ICP' in item):
                    ICP_TESTS_LISTS.append(item)
                if(item not in tests): 
                    tests.append(item)
        
        GSMS_TESTS_LISTS = sorted(GSMS_TESTS_LISTS)
        
        tests = sorted(tests)
        total_tests = len(tests)
        #newColumnCount = 5 + int(self.clientInfo['totalSamples'])    
        #TODO: fix the error checking 
        #define the CHM information 
    
        #inital setup 
        columnNames = [
            'Tests', 
            'Tests Name',
            'Unit Value', 
            'REF Value', 
            'Distal factor'
        ]
        initalColumns = len(columnNames)
        self.ui.dataTable.setRowCount(len(GSMS_TESTS_LISTS))
        self.ui.dataTable.setColumnCount(initalColumns + int(self.clientInfo['totalSamples']))
        
        #inital columns 
        for i in range(initalColumns): 
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(columnNames[i])
    
        
        #populate with sample names 
        for i , (key,value ) in enumerate(self.sampleNames.items(), start=initalColumns):
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(key)
            
        #list the tests 
        for i, value in enumerate(GSMS_TESTS_LISTS): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(value)
            self.ui.dataTable.setItem(i, 0, item)

            item2 = QtWidgets.QTableWidgetItem()
            item2.setText('mg/L')
            self.ui.dataTable.setItem(i, 2, item2)
            #self.ui.dataTable.item(i, 0).setText(GSMS_TESTS_LISTS[i])
            
            item2 = QtWidgets.QTableWidgetItem() 
            item2.setText(str(1))
            self.ui.dataTable.setItem(i, 4, item2) 
        
        self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test'))
        
        
        #TODO: remove the data when loading the information 
        #TODO: create the csv file we created 
        #TODO: add the side panel where user can add in more tests or remove the test 
        #TODO: have a popup when the user is trying to leave the page (save or not save)
        #TODO: save the data as we switch pages 
        
        #item = self.dataTable.horizontalHeaderItem(4)
        #item.setText(_translate("MainWindow", "STD += 2"))
       


        self.ui.createReportBtn.clicked.connect(lambda: self.GcmsReportHandler(GSMS_TESTS_LISTS)); 
        
    def GcmsReportHandler(self, tests):
        #FIXME: adjust based on the sample information 
        #FIXME: crashes when doing gcms to icp without closing program 
        initalColumns = 5; 
        totalSamples = len(self.sampleNames)
        totalTests = len(tests)
        sampleData = {}
        unitType = []
        
        
        #FIXME: have something determine the lower values of the things 
        #FIXME: 804 error occurs when Nonetype, can't get .text()
        for col in range(initalColumns, totalSamples + initalColumns ): 
            currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
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
                currentVal = self.ui.dataTable.item(row, 2).text()
                unitType.append(currentVal)
            except: 
                unitType.append('')
            
        print("UNITS TESTING: ", unitType)
        
        createGcmsReport(self.clientInfo, self.sampleNames, sampleData, tests, unitType)

    def handle_item_changed(self, item, test): 
        row = item.row()
        column = item.column()
        value = item.text()
        
        print(test)
        
        print(f"Row {row}, Column {column} changed to {value}")
        
        if(column >= 5):
            print(self.ui.dataTable.item(row,column).text())
            
        
        
    def loadClientInfo(self): 
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

        #load sample names 
        ''' 
        for i, (key,value) in enumerate(self.sampleNames.items()):
            item = SampleNameWidget(key, value)
            self.ui.formLayout_5.addRow(item)
            item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
        
        self.ui.stackedWidget.currentChanged.connect(lambda: self.removeWidgets())
        '''
        
    #TODO: sidebar have a s
    def icpLoader(self): 
        #FIXME: error 
        self.loadClientInfo()
        
        #check if haas data to load into the file location 
        sql = 'SELECT sampleName, jobNumber, data FROM icpMachineData1 where jobNumber = ? ORDER BY sampleName ASC'
        
        #need to get sample data from both machines 
        #FIXME: add a try catch and get second sample amount 
        sampleData = list(self.db.query(sql, (self.jobNum,)))
        
     
        totalSamples = len(sampleData)
        #FIXME: have check if sample names is empty 
        selectedSampleNames = []
        
        for item in sampleData:
            selectedSampleNames.append(item[0])
            
        print(self.sampleNames)   
        print('currentNames: ', selectedSampleNames)
        print('current2: ', selectedSampleNames[0])
       
        #create the sample names based on that         
        for i, (key, value) in enumerate(self.sampleNames.items()):
            
            if(key in selectedSampleNames):
                print('active:', key)
                item = SampleNameWidget(key, value)
                self.ui.formLayout_5.addRow(item)
                item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
        
        self.ui.stackedWidget.currentChanged.connect(lambda: self.removeWidgets()) 
        
        #load the given data information and column 
        columnNames = [
            'Element Name', 
            'Element symbol',
            'Unit Value', 
            'REF Value', 
            'distal factor'
        ]
        
        addtionalRows = [
            'pH', 
            'Hardness', 
        ]
        
        excludedElements = [
            'U', 'S'
        ]
        
        totalRows = len(periodic_table) + len(addtionalRows) - len(excludedElements)
        
        initalColumns = len(columnNames)
        self.ui.dataTable.setRowCount(totalRows)
        self.ui.dataTable.setColumnCount(initalColumns + len(selectedSampleNames))

        #inital columns 
        for i in range(initalColumns): 
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(columnNames[i])
        
        #set the sampleNames 
        for i , (key) in enumerate(selectedSampleNames, start=initalColumns):
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(key)
        
       
        #Get all the names of the elments then sort them
        elementNames = []
         
        for (key,value) in periodic_table.items(): 
            if(key not in excludedElements): 
                elementNames.append(value)
            
        elementNames.sort()
        
        print(elementNames)
        print(len(elementNames))
        
        hardnessLocation = {}
        #TODO: load in the right Elements and the unit values 
        for i, value in enumerate(elementNames): 
            
            currentSymbol = elementSymbols[value]
            
            if(currentSymbol in ['Mg', 'Ca']): 
                hardnessLocation[currentSymbol] = int(i); 
            
            item = QtWidgets.QTableWidgetItem() 
            item.setText(value) 
            self.ui.dataTable.setItem(i, 0, item)

            item2 = QtWidgets.QTableWidgetItem()
            item2.setText(currentSymbol)
            self.ui.dataTable.setItem(i, 1, item2)
            
            item3 = QtWidgets.QTableWidgetItem()
            if(currentSymbol in icpMachine2Symbols): 
                item3.setText('ug/L')
            else: 
                item3.setText('mg/L')
            self.ui.dataTable.setItem(i, 2, item3)
            
            #set distal factor to default of 1 
            item4 = QtWidgets.QTableWidgetItem()
            item4.setText('1')
            self.ui.dataTable.setItem(i, 4, item4)

        for i, value in enumerate(addtionalRows): 
            postion = totalRows - i - 1; 
            item = QtWidgets.QTableWidgetItem()  
            item.setText(value)
            self.ui.dataTable.setItem(postion ,0 , item)
            
            if(value == 'Hardness'): 
                item2 = QtWidgets.QTableWidgetItem()
                item2.setText("CaC0₃")
                self.ui.dataTable.setItem(postion, 1, item2) 
                
                item3 = QtWidgets.QTableWidgetItem()
                item3.setText('ug/L')
                self.ui.dataTable.setItem(postion, 2, item3) 
       
        

        #print(hardnessLocation)
        
        #TODO: combine the two tables so can easily iterate through them lol 
        for col, currentSample in enumerate(sampleData, start=5): 
            #tempName = currentSample[0]
            #print(i,currentSample) 
            
            currentSampleVal = json.loads(currentSample[2])
            for row in range(len(elementNames)): 
                item = QtWidgets.QTableWidgetItem(); 
                
                cellValue = self.ui.dataTable.item(row, 1).text()

                #determine if both things have been loaded yet
                #TODO: add a side reload button 
                if(cellValue in currentSampleVal): 
                    item.setText(currentSampleVal[cellValue])
                else: 
                    item.setText('ND')
                    
                self.ui.dataTable.setItem(row, col, item)
                
            #determine the hardness postion 
            hardnessVals = {}
            item = QtWidgets.QTableWidgetItem() 
            
            for (key, value) in hardnessLocation.items(): 
                #get the row location
                cellValue2 = self.ui.dataTable.item(value, col).text()
                print(cellValue2)
                hardnessVals[key] = cellValue2

            if not (['ND', 'uncal'] in hardnessVals.items()): 
                result = hardnessCalc(hardnessVals['Ca'], hardnessVals['Mg'])
                item.setText(str(result))
                print(result)
                
            else: 
                item.setText('ND')
            
            self.ui.dataTable.setItem(len(elementNames), col, item) 
            
            #TODO: add text change items for when the values are changed
                
        
        column_width = self.ui.dataTable.columnWidth(2)
        padding = 10
        total_width = column_width + padding
        self.ui.dataTable.setColumnWidth(2, total_width)    

        self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 

        self.ui.createReportBtn.clicked.connect(lambda: self.icpReportHander(elementNames, totalSamples)); 
    
    def icpReportHander(self, tests, totalSamples): 
        #FIXME: adjust based on the sample information 
        initalColumns = 5; 
        #totalSamples = len(self.sampleNames)
        totalTests = len(tests)
        sampleData = {}
        unitType = []
        
        print(totalSamples)
        
        
        #FIXME: have something determine the lower values of the things 
        for col in range(initalColumns, totalSamples + initalColumns ): 
            currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
            jobValues = []
            for row in range(totalTests + 2): 
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
        
        elementsWithLimits = self.getElementLimits(); 
        print(elementsWithLimits)    

        limitQuery = 'SELECT element, lowerLimit, maxLimit, comments, units FROM icpLimits WHERE reportType = ? ORDER BY element ASC' 
        limits = self.db.query(limitQuery, ('Water',))

        print(limits)
        
        #load the footer comment 
        
                         
        createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, tests, unitType, elementsWithLimits, limits)
        
        
        

    def updateSampleNames(self, textChange, key):
        self.sampleNames[key] = textChange; 
        print(self.sampleNames)

    
    def removeWidgets(self): 
        count = self.ui.formLayout_5.count(); 

        for index in range(count): 
            item = self.ui.formLayout_5.itemAt(index)
            
            if(item != None): 
                widget = item.widget()
                self.ui.formLayout.removeWidget(widget)
            
    
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
    
    
    def getReportTypeList(self): 
        getReportsQuery = 'SELECT * FROM icpReportType' 
        reportTypes = self.db.query(getReportsQuery)
        
        temp = []

        for item in reportTypes: 
            #print(item)
            temp.append(item[0])
            
        return temp; 


    #SQL Query Functions 
    def getElementLimits(self): 
        elementsQuery = 'SELECT element FROM icpLimits WHERE reportType = ? ORDER BY element ASC'
        elementWithLimits = self.db.query(elementsQuery, ('Water',))    
        
        temp = []

        for item in elementWithLimits: 
            #print(item)
            temp.append(item[0]) 
        
        return temp; 
    
    def getTotalElements(self): 
        amountQuery = 'SELECT count(*) FROM icpElements'
        
        self.db.execute(amountQuery)
        total = self.db.fetchone()[0]
        
        return total; 
    


class SampleNameWidget(QWidget): 
    def __init__(self, labelName, valueName, parent=None): 
        super(SampleNameWidget ,self).__init__(parent)
    
        self.label = QLabel(labelName)
        self.edit = QLineEdit(valueName)
        self.button = QPushButton()
        
        pixmapi = getattr(QStyle, 'SP_TitleBarCloseButton')
        icon = self.style().standardIcon(pixmapi)
        self.button.setIcon(icon)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        
        self.setLayout(layout)

class SaveMessageBoxWidget(QWidget): 
    
    def __init__(self):
        super().__init__()
        
        self.error_popup()

    def removeDuplicate(self):
        print('def removeDuplicate(self): ...')
#        curItem = self.listWidget_2.currentItem()
#        self.listWidget_2.takeItem(curItem)

    def error_popup(self):
        msg = QMessageBox.critical(
            self, 
            'Title', 
            "You can't select more than one wicket-keeper", 
            QMessageBox.Yes | QMessageBox.Cancel
        )
        if msg == QMessageBox.Yes:
#            msg.buttonClicked.connect(self.removeDuplicate)
            print('Ok')
            self.removeDuplicate()
