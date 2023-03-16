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
        
        self.ui.jobNumInput.setText('171981')
        
        size = self.size()
        width = size.width() 
        
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

        #set first page paramenters         
        self.ui.reportType.addItems(REPORTS_TYPE)
        self.ui.paramType.addItems(sorted(MATRIX_TYPE))

        #connect buttons 
        self.ui.NextSection.clicked.connect(lambda: self.proceedPage())
        self.ui.clientInfoBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.dataEntryBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        
        #self.ui.stackedWidget.currentChanged.connect(lambda: print("Stacked Widget Changed "))
        
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
        #print(x);
        
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
        #remove whitespaces 
        jobNum = self.ui.jobNumInput.text().strip()
        reportType = self.ui.reportType.currentText()
        parameter = self.ui.paramType.currentText()
        recovery = self.ui.stdType.currentText()
        #make sure they entered all the valid information
        
        errorCheck = {
            'jobNum': '', 
            'reportType': '', 
            'parameter': '',
            'recovery': ''
        }
        
        
        
        #TODO: check if a report already exists, if so load that information instead 
        
        if(re.match('^([0-9]{6})$', jobNum)): 
            self.jobNum = jobNum; 
            self.ui.stackedWidget.setCurrentIndex(5)
            self.ui.stackedWidget_2.setCurrentIndex(0)
            self.activeCreation = True; 

            tempLocation = scanForTXTFolders(self.jobNum)
            clientInfo, sampleNames, sampleTests = processClientInfo(self.jobNum, tempLocation)
            
            self.clientInfo = clientInfo 
            self.sampleNames = sampleNames
            self.sampleTests = sampleTests
    
            createReport(self.db, jobNum, reportType)
  
            if('ISP' in reportType):
                print('isp loader')
                self.ui.icpDataField.show()
                self.icpLoader()
            
            if(reportType == 'GSMS'):
                print('gsms loader')
                self.ui.icpDataField.hide() 
                self.gsmsLoader()
            
        else:
            errorCheck['jobNum'] = 'Invalid Job Number'
            msg = QMessageBox() 
            msg.setWindowTitle("Error to procceed")
            msg.setText("Please enter a valid job number!")
            x = msg.exec_()  # this will show our messagebox
            
     
    def loadExistingInfo(self): 
        
        pass; 
    
    def overWriteExisting(self): 
        pass; 
    
    
    def gsmsLoader(self): 
        
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
        
        
        #TODO: remove the data when loading the information 
        #TODO: create the csv file we created 
        #TODO: add the side panel where user can add in more tests or remove the test 
        #TODO: have a popup when the user is trying to leave the page (save or not save)
        
        #item = self.dataTable.horizontalHeaderItem(4)
        #item.setText(_translate("MainWindow", "STD += 2"))
        
    def loadClientInfo(self): 
        #clear the first page 
        self.ui.jobNumInput.setText('')
        self.ui.reportType.setCurrentText('')
        
        #set the header parameter 
        self.ui.jobNum.setText(self.jobNum)
        
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
        
        self.loadClientInfo()
        
        #check if haas data to load into the file location 
        sql = 'SELECT sampleName, jobNumber, data FROM icpMachineData1 where jobNumber = ?'
        
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
                item2.setText("CaC0<sub>3</sub>")
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
        self.clientInfo['tel'] = self.ui.clientName_1.text()
    
    def on_email_1_textChanged(self):
        self.clientInfo['email'] = self.ui.email_1.text()
    
    def on_fax_1_textChanged(self): 
        self.clientInfo['fax'] = self.ui.fax_1.text()
    
    def on_payment_1_textChanged(self): 
        self.clientInfo['payment'] = self.ui.payment_1.text()
        #print(self.clientInfo)
        


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
