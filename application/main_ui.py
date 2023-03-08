#PYQT Imports 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle, QStyledItemDelegate
from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, pyqtSlot

#general Imports 
import sys 
import pandas as pd
import json
import sys 
import re 
import asyncio

from modules.utilities import * 
from modules.dbManager import *
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

        #print(self.ui.page_3.ui.__dir__())
        #first page options 
        
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
               
        #can have other keyboard modifiers as well 
        #self.ui.stackedWidget.currentChanged.connect(lambda: print("Stacked Widget Changed "))
        
        #connect the menu bar options 
        #self.ui.subHeaderText.setText("Hello World")
        
        self.showMaximized()
        #self.show()


    
    ## Change QPushButton Checkable status when stackedWidget index changed
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)
        
        #print(btn_list)
        #FIXME: issue that arises when the active creation setting is thing 
        for btn in btn_list:
            #if index in [5, 6]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            #else:
            btn.setAutoExclusive(True)



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
            
        
    #Define button presses
    def on_reportsBtn1_toggled(self):
        
        if(self.activeCreation == False):
            self.ui.stackedWidget.setCurrentIndex(0)
        else: 
            self.messageBox(); 
            #self.ui.reportsBtn1.setChecked(False)
    
    def on_reportsBtn2_toggled(self):
        if(self.activeCreation == False):
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
         
    
    def on_stackedWidget_currentChanged(self):
        print("Changed: ", self.ui.stackedWidget.currentIndex())
        print('Creation Active: ', self.activeCreation)
        
        if(self.ui.stackedWidget.currentIndex() == 5):
             self.activeCreation = True
             print('active is 5')
        

    
    #button activations  
    @pyqtSlot()
    def on_icpUploadBtn_clicked(self): 
        fileLocation = openFile()
        print(fileLocation)
        
        icp_upload(fileLocation, self.db) 
        
        #check if the file is .xlsx or txt document 
        
                
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.test_method()
        if event.key() == Qt.Key_Space: 
            self.test_method()
        
    def savePickle(self): 
        jsonLocation = getFileLocation()
        
        tempDictonary = {
            "JSONFileLocation":'/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/fileLocation.json', 
            "TXTDirLocation": jsonLocation 
        }
        
        save_pickle(tempDictonary)
        
    
    def proceedPage(self):
        #remove whitespaces 
        jobNum = self.ui.jobNumInput.text().strip()
        reportType = self.ui.reportType.currentText()
        
        #print(self.ui.jobNumInput.text())
        #print(reportType)
        
        #make sure they entered all the valid information
        
        errorCheck = {
            'jobNum': '', 
            'reportType': '', 
        }
        
        
        if(re.match('^([0-9]{6})$', jobNum)): 
            self.jobNum = jobNum; 
            self.ui.stackedWidget.setCurrentIndex(5)
            self.ui.stackedWidget_2.setCurrentIndex(0)

            tempLocation = scanForTXTFolders(self.jobNum)
            clientInfo, sampleNames, sampleTests = processClientInfo(self.jobNum, tempLocation)
            
            self.clientInfo = clientInfo 
            self.sampleNames = sampleNames
            self.sampleTests = sampleTests
  
            if(reportType == 'ISP-1'):
                print('isp loader')
                
                self.ispLoader()
            
            if(reportType == 'GSMS'):
                print('gsms loader')
            
                self.gsmsLoader()
            
        else:
            errorCheck['jobNum'] = 'Invalid Job Number'
            msg = QMessageBox() 
            msg.setWindowTitle("Error to procceed")
            msg.setText("Please enter a valid job number!")
            x = msg.exec_()  # this will show our messagebox
            
    #only define for the CHM file 
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
            'REF Value'
        ]
        initalColumns = len(columnNames)
        self.ui.dataTable.setRowCount(total_tests)
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
        for i, value in enumerate(tests): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(value)
            self.ui.dataTable.setItem(i, 0, item)

            item2 = QtWidgets.QTableWidgetItem()
            item2.setText('mg/L')
            self.ui.dataTable.setItem(i, 1, item2)
            #self.ui.dataTable.item(i, 0).setText(GSMS_TESTS_LISTS[i])
        
        
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
        
    def ispLoader(self): 
        
        self.loadClientInfo()
        
        #check if haas data to load into the file location 
        sql = 'SELECT sampleName, jobNumber, sampleData FROM machineData where jobNumber = ?'
        
        #need to get sample data from both machines 
        sampleData = list(self.db.query(sql, (self.jobNum,)))
        
        totalSamples = len(sampleData)
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
        
        elements = []
    
        #for sample in sampleData[0][2]: 
            
        #    for key,value in json.loads(sample).items():
        #        elements.append(key);
                
        for (key, value) in json.loads(sampleData[0][2]).items():
            elements.append(key)
        
        totalElements = len(elements)
        print(elements)
        print(totalElements)
        #load the given data information and column 

        columnNames = [
            'Element Name', 
            'Element symbol',
            'Unit Value', 
            'REF Value', 
            'distal factor'
            
        ]
        initalColumns = len(columnNames)
        self.ui.dataTable.setRowCount(totalElements)
        self.ui.dataTable.setColumnCount(initalColumns + len(selectedSampleNames))

        #inital columns 
        for i in range(initalColumns): 
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(columnNames[i])
        
        
        for i , (key) in enumerate(selectedSampleNames, start=initalColumns):
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(key)
        
        #reduce this 
        for i, value in enumerate(elements): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(periodic_table[value])
            self.ui.dataTable.setItem(i, 0, item)

            item2 = QtWidgets.QTableWidgetItem()
            item2.setText(value)
            self.ui.dataTable.setItem(i, 1, item2)
        
            item3 = QtWidgets.QTableWidgetItem()
            item3.setText('mg/L')
            self.ui.dataTable.setItem(i, 2, item3)
            
            #TODO: add ref values here 
            
            item4 = QtWidgets.QTableWidgetItem()
            item4.setText('1')
            self.ui.dataTable.setItem(i, 4, item4)
        
        #set the values for each sample 
        for col, currentSample in enumerate(sampleData, start=5): 
            
            #don't need to match column, did previous math to find out 
            tempName = currentSample[0]
            print(i,currentSample)
            
            for row, (key, value ) in enumerate(json.loads(currentSample[2]).items()): 
                item = QtWidgets.QTableWidgetItem()
                item.setText(value)
                self.ui.dataTable.setItem(row, col, item)
                
            #assume data is arranged in order? 
        
        # Calculate the required height of the table
        #row_height =  self.ui.dataTable.verticalHeader().defaultSectionSize()
        #total_height = row_height *  self.ui.dataTable.rowCount()
        #total_height = row_height +

        # Set the fixed size of the table to accommodate all the rows
        #self.ui.dataTable.setFixedSize( self.ui.dataTable.width(), total_height)
            
        column_width = self.ui.dataTable.columnWidth(2)
        padding = 10
        total_width = column_width + padding
        self.ui.dataTable.setColumnWidth(2, total_width)    
        
        pass 

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
