#PYQT Imports 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle
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
        self.ui.setupUi(self) #self defined function that setups
        
        paths = load_pickle('data.pickle')
        self.db = Database(paths['databasePath'])
        
        #define other widget setups 
        self.setWindowTitle("Laboratory Information management System") 
        self.ui.LeftMenuContainerMini.hide()
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.reportsBtn1.setChecked(True)

        self.ui.jobNumInput.setText('171544')

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
        self.ui.matrixType.addItems(sorted(MATRIX_TYPE))

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
        for btn in btn_list:
            #if index in [5, 6]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            #else:
            btn.setAutoExclusive(True)

    #Define button presses
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
            

    def gsmsLoader(self): 
        
        self.loadClientInfo()
        #check if the samples are ISP or not 
        
        GSMS_TESTS_LISTS = []
        ICP_TESTS_LISTS = []
        
        for (currentJob ,testList) in self.sampleTests.items(): 
            for item in testList: 
                if(item not in GSMS_TESTS_LISTS and 'ICP' not in item):
                    GSMS_TESTS_LISTS.append(item)
                if(item not in ICP_TESTS_LISTS and 'ICP' in item):
                    ICP_TESTS_LISTS.append(item)
            
            
        print(GSMS_TESTS_LISTS) 
        print(ICP_TESTS_LISTS)       
        
        GSMS_TESTS_LISTS = sorted(GSMS_TESTS_LISTS)
        
        total_tests = len(GSMS_TESTS_LISTS)
        #newColumnCount = 5 + int(self.clientInfo['totalSamples'])    
        #TODO: fix the error checking 
        self.ui.dataTable.setRowCount(total_tests)
        

        self.ui.dataTable.setColumnCount(5 + int(self.clientInfo['totalSamples']))
        
        for i , (key,value ) in enumerate(self.sampleNames.items(), start=5):
            item = QtWidgets.QTableWidgetItem()
            self.ui.dataTable.setHorizontalHeaderItem(i, item)
            item2 = self.ui.dataTable.horizontalHeaderItem(i)
            item2.setText(key)
            
    
        
        for i, value in enumerate(GSMS_TESTS_LISTS): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(value)
            self.ui.dataTable.setItem(i, 0, item)

            item2 = QtWidgets.QTableWidgetItem()
            item2.setText('mg/L')
            self.ui.dataTable.setItem(i, 1, item2)
            #self.ui.dataTable.item(i, 0).setText(GSMS_TESTS_LISTS[i])
        
        #item = self.dataTable.horizontalHeaderItem(4)
        #item.setText(_translate("MainWindow", "STD += 2"))
        
    def loadClientInfo(self): 
        self.ui.jobNumInput.setText('')
        self.ui.reportType.setCurrentText('')
        
        #print(self.clientInfo)
        #sprint(self.sampleNames)

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
        for i, (key,value) in enumerate(self.sampleNames.items()):
            item = SampleNameWidget(key, value)
            self.ui.formLayout_5.addRow(item)
            item.edit.textChanged.connect(lambda textChange, key = key: self.updateSampleNames(textChange, key))
        
        self.ui.stackedWidget.currentChanged.connect(lambda: self.removeWidgets())
         
        
    def ispLoader(self): 
        
        self.loadClientInfo()
        
        #check if haas data to load into the file location 
        sql = 'SELECT sampleName, jobNumber, sampleData FROM machineData '
        
        temp = self.db.query(sql)
        print(temp)
        #print(temp)

        
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
    