#PYQT Imports 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QHeaderView, QLabel, QMainWindow, QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle, QStyledItemDelegate, QAbstractItemView
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
import string


from modules.createExcel import * 
from modules.utilities import * 
from modules.dbManager import *
from interface import *
    
class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        
        paths = load_pickle('data.pickle')
        print(paths)
        
        if(isValidDatabase(paths)): 
            self.db = Database(paths['databasePath'])
        else: 
            print('Database not valid')
            
            databasePathTemp = openFile()
            
            #paths['databasePath'] = setDatabase; 
            #save_pickle(paths)
            
            self.db = Database(databasePathTemp)
            


            
        #define other widget setups 
        self.setWindowTitle("Laboratory Information management System") 
        self.ui.LeftMenuContainerMini.hide()

        self.activeCreation = False; 
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.reportsBtn1.setChecked(True)
        

        fileLocationsDictonary = load_pickle('data.pickle')
        print(fileLocationsDictonary)
       
        #load the setup 
        self.loadCreatePage()
        
        self.ui.NextSection.clicked.connect(lambda: self.proceedPage())
        self.ui.clientInfoBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.dataEntryBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        
        
        self.ui.reportTypeDropdown.activated.connect(lambda: self.loadElementLimits())        
        self.showMaximized()



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
        #TODO: sort by date or somethingsetDatabase
        
        query = 'SELECT * FROM jobs' 
        try: 
            results = list(self.db.query(query)) 
            #print(results)
        except: 
            results = []

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
              
            button = QPushButton("Open")
            self.ui.reportsTable.setCellWidget(row,5, button)
            button.clicked.connect(lambda _, row=row: print(row));
            
         
        #button = QPushButton("Click me!")
        #self.ui.reportsTable.setCellWidget(1,1, button)
        
        self.ui.reportsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.reportsTable.doubleClicked.connect(self.on_table_double_clicked )

        #TODO: if sleected open this thing 

    def on_table_double_clicked(self, index):
    # Open the row data
        row = index.row()
        print(f"Double clicked on row {row}")
    
    #------------- Define Menu Button presses --------------
    
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
         
    #---------------- Stack Management -----------------------
             
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
        
        if(index == 0): 
            self.ui.icpPageTitle.setText("ICP Page")
            self.ui.icpLabel.setText("")
        
        if(index == 1): 
            columnNames = ['Sample Name', 'Job Number', 'Machine Type', 'File Location', 'Upload Date']
        
            #TODO: set the machine values for both of theses, create a single inqury that fetches based on date
            icpMachine1sql = 'SELECT sampleName, jobNumber, machine, fileLocation, createdDate data FROM icpMachineData1 ORDER BY createdDate DESC' 
            icpMachine2sql = 'SELECT sampleName, jobNumber, fileLocation, createdDate, machine data FROM icpMachineData2'
            
            machine1Data = list(self.db.query(icpMachine1sql))
            #machine2Data = list(self.db.query(icpMachine2sql))
            
            self.updateIcpTable(machine1Data) 
        
        if(index == 2): 
            total = self.getTotalElements()
            self.ui.icpPageTitle.setText("ICP Defined Elements")
            self.ui.icpLabel.setText("Total Elements: {}".format(total))
            self.loadDefinedElements()

        if(index == 3): 
            self.ui.icpPageTitle.setText("ICP Reports")
            self.ui.icpLabel.setText("Total Reports:") 
            self.loadReportList()

    def on_gcmsStack_currentChanged(self, index):
        
        if(index == 0): 
            self.ui.gcmsTitleLabel.setText('GCMS Page')
            self.ui.gcmsSubTitleLabel.setText('')
        
        if(index == 1): 
            self.ui.gcmsTitleLabel.setText('GCMS Defined Tests')
          
            
            totalTests = len(self.gcmsGetTotalTests())
            
            self.ui.gcmsSubTitleLabel.setText('Total Tests: ' + str(totalTests))

            self.gcmsLoadTestsNames()

        if(index == 2): 
            self.ui.gcmsTitleLabel.setText('GCMS Defined Reports')
            self.ui.gcmsSubTitleLabel.setText('Total Reports: ')
            
            
        if(index == 3): 
            self.ui.gcmsTitleLabel.setText('GCMS Tests Entry')
            self.ui.gcmsSubTitleLabel.setText('')
             
            self.gcmsClearEnteredTestsData()
            
            temp = self.getTestsAndUnits()
            
            self.ui.gcmsTests.addItems(temp[0])
            self.ui.gcmsUnitVal.addItems(temp[1])
        
        if(index == 4): 
            self.ui.gcmsTitleLabel.setText('GCMS Tests Database') 
            self.ui.gcmsSubTitleLabel.setText('')
            self.loadInputData(); 
            


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
            
        if(index == 4): 
            print('Settings baby')
            
        
        
        self.prev_index = (index - 1) % self.ui.stackedWidget.count()
        print('prev index: ', self.prev_index)
        prev_widget = self.ui.stackedWidget.widget(self.prev_index)
        current_widget = self.ui.stackedWidget.currentWidget()
        
        if(self.prev_index == 5): 
            print('Do you want to save?')
        # Access the previous and current widgets

        # Do something with the widgets
        #print(f"Previous widget: {prev_widget}")
        #print(f"Current widget: {current_widget}")

    #--------------------------------------------------------- 
        

    #---------------- Defined Elements -----------------------
    
    
    
    
    
    
    #---------------------------------------------------------
    
    @pyqtSlot()
    def on_addElementBtn_clicked(self): 

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
        
        
    
    def loadDefinedElements(self): 

        self.ui.reportTypeDropdown.clear()
        self.ui.gcmsDefinedtests.clear()
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
            #TODO: check to make sure not duplicate as well 
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
    
                
  
   # ----------------------- GCMS TEST PAGE -----------------------
   #TODO: if the txt name changes update the listName 
   #keep track of the currentIndex when first getting it 
   
    
    def gcmsLoadTestsData(self): 
        
        selectedTests = self.ui.gcmsDefinedtests.currentItem()
        
        print('selected Tests: ', selectedTests)
        
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
                
        
    def gcmsLoadTestsNames(self): 
        
        self.gcmsClearDefinedTestsValues(); 
        self.ui.gcmsDefinedtests.clear()
        self.ui.testsInputLabel.clear()
    
        getTestNamesQuery = 'SELECT testName FROM gcmsTests ORDER BY testName COLLATE NOCASE ASC'
        testNames = self.db.query(getTestNamesQuery)           
        
        print(testNames)
        
        for test in testNames: 
            self.ui.gcmsDefinedtests.addItem(test[0])

        
    
    def gcmsGetListValues(self): 
        
        values = []
        
        for index in range(self.ui.gcmsDefinedtests.count()):
            item = self.ui.gcmsDefinedtests.item(index)
            values.append(item.text())
            
        return values; 
    
    def gcmsGetTotalTests(self): 
        
        test = 'SELECT * FROM gcmsTests'
        
        return self.db.query(test)
        
    
    def gcmsClearDefinedTestsValues(self): 
        self.ui.gcmsDisplayName.clear()
        self.ui.gcmsTxtName.clear()
        self.ui.gcmsUnitType.clear()
        self.ui.gcmsRefValue.clear()
        self.ui.gcmsComment.clear()
     

    
    
    @pyqtSlot() 
    def on_gcmsAddTestsBtn_clicked(self): 
        
        existingTests = self.gcmsGetListValues()
        print(existingTests)
        
        currentText = self.ui.testsInputLabel.text()

        
        if(currentText != '' and currentText not in existingTests): 
            #clear values 
            self.gcmsClearDefinedTestsValues()
            self.ui.testsInputLabel.clear()
            #add to testse 
            self.ui.gcmsDefinedtests.addItem(currentText)
            
            totalItems = len(self.gcmsGetListValues())
            
            self.ui.gcmsDefinedtests.setCurrentRow(totalItems-1)
            self.ui.gcmsTxtName.setText(currentText)
            
        else: 
            print('Please enter a valid tests')

    
    
    @pyqtSlot()
    def on_gcmsSaveTestBtn_clicked(self):

        
        displayName = self.ui.gcmsDisplayName.text().strip()
        txtName = self.ui.gcmsTxtName.text().strip()
        unitType = self.ui.gcmsUnitType.text().strip()
        recoveryVal = self.ui.gcmsRefValue.text()        
        comment = self.ui.gcmsComment.toPlainText() 
        
        print(txtName, unitType, recoveryVal, displayName)
        
        if(txtName != ""):
            
            definedTestsValues = 'INSERT OR REPLACE INTO gcmsTests (testName, unitType, recoveryVal, displayName) VALUES (?,?,?, ?)' 
            
            try:
                self.db.execute(definedTestsValues, (txtName, unitType, recoveryVal, displayName) )
                self.db.commit()

            except sqlite3.IntegrityError as e:
                print(e)
    
    @pyqtSlot()    
    def on_gcmsDeleteTestBtn_clicked(self): 
        
        txtName = self.ui.gcmsTxtName.text().strip()
        selected_item = self.ui.gcmsDefinedtests.currentItem()

        print(txtName)
        print(selected_item)

        deleteQuery = 'DELETE FROM gcmstests WHERE testName = ?'
        
        try: 
            self.deleteBox("DELETE ELEMENT", "ARE YOU SURE YOU WANT TO DELETE THIS ITEM", lambda:print("hello World"))
            
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
        self.gcmsLoadTestsData()
            

    def on_gcmsDefinedtests_currentRowChanged(self):

        try:
            self.gcmsLoadTestsData()
        
        except: 
            print('error')
        
        
    #-------------------------------------------------------------
    
    def getTestsAndUnits(self): 
        
        inquery = 'SELECT testName, unitType FROM gcmsTests ORDER BY testName COLLATE NOCASE ASC'
        results = self.db.query(inquery)
        
        tests = ['']
        units = ['']
        
        for testName, unitType in results: 
            if(testName != '' ): 
                tests.append(testName)
            
            if(unitType != '' and unitType not in units):
                units.append(unitType)
        
        return (tests,units)
        


    # -------------------- GCMS Data Entering --------------------
    
    #TODO: have error handling for duplicates 
    #TODO: takes in the values from the 
    #TODO: connect from the defined values in gcms Defined Tests Page
    #TODO: make sure to add a date for the table so we can sort it by the most recent date
    #TODO: duplication error

    @pyqtSlot()    
    def on_gcmsProceedBtn_clicked(self):
        #check if the there is standard and entered unit
        
    
        errorCheck = [0,0,0]
        
        standards = self.ui.gcmsStandardVal.text().strip()
        units = self.ui.gcmsUnitVal.currentText()
        tests = self.ui.gcmsTests.currentText()
        
        if(standards != '' and is_real_number(standards)): 
            errorCheck[0] = 0 
        else: 
            errorCheck[0] = 1; 
            
        if(units != ''): 
            errorCheck[1] = 0
        else: 
            errorCheck[1] = 1; 
            
        if(tests != ''): 
            errorCheck[2] = 0 
        else: 
            errorCheck[2] = 1; 
        
        
        if(sum(errorCheck) == 0):
            self.ui.gcmsTestsValueWidget.setEnabled(True)
            self.ui.widget_28.setEnabled(False)
            
            self.ui.gcmsStandardVal_2.setText(standards)
            self.ui.gcmsUnitVal_2.setText(units)
            self.ui.gcmsTests_2.setText(tests)  
            
        else: 
            outputMessage = ''
            
            if(errorCheck[0] == 1): 
               
                outputMessage += 'Please Enter a Valid Standard Number\n'

            if(errorCheck[1] == 1): 
              
                outputMessage += 'Please Select a Unit\n'
                
            if(errorCheck[2] == 1): 
               
                outputMessage += 'Please Select a Tests\n'
            
                
            msg = QMessageBox() 
            msg.setWindowTitle("Error")
            msg.setText(outputMessage)
            x = msg.exec_()  # this will show our messagebox 
    
        pass; 
           

    @pyqtSlot()   
    def on_gcmsAddTestsBtn_2_clicked(self): 
        
        errorCheck = [0,0,0]
        
        standards = self.ui.gcmsStandardVal_2.text().strip()
        units = self.ui.gcmsUnitVal_2.text().strip()
        testName = self.ui.gcmsTests_2.text().strip()  
        
        
        errorCheck = [0,0,0]
        
        testNum = self.ui.gcmsTestsJobNum.text().strip()
        sampleNum = self.ui.gcmsTestsSample.text().strip()
        sampleVal = self.ui.gcmsTestsVal.text().strip()
        
        
        if(testNum != '' and is_real_number(testNum)): 
           errorCheck[0] = 0 
        else: 
            errorCheck[0] = 1; 
        
        if(sampleNum != '' and is_real_number(sampleNum)): 
           errorCheck[1] = 0 
        else: 
            errorCheck[1] = 1; 

        if(sampleVal != ''): 
            errorCheck[2] = 0
        else: 
            errorCheck[2] = 1; 
        
        
        if(sum(errorCheck) == 0): 
            
            sampleNum = testNum + '-' + sampleNum; 
            
            checkInquery = 'SELECT EXISTS(SELECT 1 FROM gcmsTestsData WHERE sampleNum = ? and testsName = ?)'
            self.db.execute(checkInquery, (sampleNum, testName))
            result = self.db.fetchone()[0]
            
            
            if(result == 1): 
                
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
            outputMessage = ''
            
            if(errorCheck[0] == 1): 
                outputMessage += 'Please Enter a Valid Job Number\n'

            if(errorCheck[1] == 1): 

                outputMessage += 'Please Enter a Valid Sample Number\n'
                
            if(errorCheck[2] == 1): 
            
                outputMessage += 'Please Enter a Valid Sample Value \n'
            
            msg = QMessageBox() 
            msg.setWindowTitle("Error")
            msg.setText(outputMessage)
            x = msg.exec_()  # this will show our messagebox 
    
            
            
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
        
        self.ui.gcmsStandardVal_2.clear()
        self.ui.gcmsUnitVal_2.clear()
        self.ui.gcmsTests_2.clear()
            
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
 
 
    def loadInputData(self): 
        print('Loading Existing Data'); 
        
        TableHeader = ['Sample Number', 'Tests', 'Test Values', 'Standard Value', 'Unit Value', 'Job Num', 'Delete']
        self.ui.gcmsInputTable.setColumnCount(len(TableHeader))
        self.ui.gcmsInputTable.setHorizontalHeaderLabels(TableHeader)
        
        
        query = 'SELECT * FROM gcmsTestsData ORDER BY jobNum ASC'
        results = self.db.query(query, [])
        print(results)
        self.ui.gcmsInputTable.setRowCount(len(results))
        
        for i, result in enumerate(results):
            for j in range(len(TableHeader)-1): 
                 self.ui.gcmsInputTable.setItem(i, j, QtWidgets.QTableWidgetItem(str(result[j])))     
            
            
            #button.setText("Delete")
            #button.clicked.connect(self.handleDeleteButtonClick)

            button = QPushButton("Delete")
            self.ui.gcmsInputTable.setCellWidget(i ,6, button)
            button.clicked.connect(lambda _, row=i: print('Delete Row: ', row));
            
            


    def replaceError(self,sampleName):
        msgBox = QMessageBox()  
        msgBox.setText("Duplicate Data?");
        message = 'There is sample named ' + str(sampleName) 
        
        msgBox.setInformativeText(message);
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save);
        msgBox.setDefaultButton(QMessageBox.Save);
        #msgBox.buttonClicked.connect(self.msgbtn)
        x = msgBox.exec_()  # this will show our messagebox
        
        if(x == QMessageBox.Save): 
            pass      


        if(x == QMessageBox.Cancel):
            pass 
        

        
    
    #-------------------------------------------------------------
    
    # ----------------------- Settings Page ------------------------

    
    @pyqtSlot()
    def on_reportsPathBtn_clicked(self): 
        paths = load_pickle('data.pickle')
        newLocation = getFileLocation()
        if(newLocation != ''): 
            paths['reportsPath'] = newLocation; 
            save_pickle(paths)
        
    
    @pyqtSlot()
    def on_txtPathBtn_clicked(self): 
        paths = load_pickle('data.pickle')
        newLocation = getFileLocation()
        if(newLocation != ''): 
            paths['TXTDirLocation'] = newLocation; 
            save_pickle(paths)
    
    
    @pyqtSlot() 
    def on_convertPathBtn_clicked(self): 
        paths = load_pickle('data.pickle')
        newLocation = openFile()
        if(newLocation != ''): 
            paths['ispDataUploadPath'] = newLocation; 
            save_pickle(paths) 
        
    @pyqtSlot()  
    def on_dbPathBtn_clicked(self):
        paths = load_pickle('data.pickle')
        newLocation = openFile()
        if(newLocation != ''): 
            paths['TXTDirLocation'] = newLocation; 
            save_pickle(paths)  
        
    
        
    
    
    
    
    # ----------------------- PROCESS PAGE ------------------------
  
    @pyqtSlot()
    def proceedPage(self):
        
        jobNum = self.ui.jobNumInput.text().strip()
        reportType = self.ui.reportType.currentText()
        parameter = self.ui.paramType.currentText()
        
        print('JobNumber: ', jobNum)
        print('ReportType: ', reportType)
        print('Parameter: ', parameter)
        
        #0 = name 
        #1 = reportType 
        #2 = parameter 
        #3 = TXT file exists
        errorCheck = [0, 0, 0, 0]     

        fileExist = scanForTXTFolders(jobNum)
        print(fileExist)
     
     
        if(re.match('^([0-9]{6})$', jobNum)): 
            errorCheck[0] = 0; 
        else: 
            errorCheck[0] = 1; 
            #self.ui.jobNumInput.setStyleSheet('border:1px solid red;')
         
        if(reportType == 'ISP' or reportType == 'GCMS'):
            errorCheck[1] = 0;
            
        else: 
            errorCheck[1] = 1; 
        
        if(parameter != ''): 
            errorCheck[2] = 0
        else: 
            errorCheck[2] = 1
            
        if(fileExist != None): 
            errorCheck[3] = 0;
        else: 
            errorCheck[3] = 1; 
        
            
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
                
                self.ui.createIcpReportBtn.setVisible(True)
                self.ui.createGcmsReportBtn.setVisible(False)
                
                self.ui.icpDataField.show()
                self.icpLoader()
            
            if(reportType == 'GCMS'):
                print('GCMS Loader')
                
                self.ui.createIcpReportBtn.setVisible(False)
                self.ui.createGcmsReportBtn.setVisible(True)
                
                self.ui.icpDataField.hide() 
                self.gcmsLoader()
            
        else: 
            #TODO: can combine into one function that print errors to the screen 
            # param(total errors, [error messages], add style) 
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
            
            if(errorCheck[3] == 1): 
                print("Error: TXT File doesn't exist")
                outputMessage += 'TXT File could not be located\n'
                
            msg = QMessageBox() 
            msg.setWindowTitle("Error")
            msg.setText(outputMessage)
            x = msg.exec_()  # this will show our messagebox

            
    # -------------------------------------------------------------
    
    def gcmsLoader(self): 
        print('GCMS LOADER')
        
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
    
    
        self.ui.createGcmsReportBtn.clicked.connect(lambda: self.GcmsReportHandler(GSMS_TESTS_LISTS)); 
        
    
    def GcmsReportHandler(self, tests):
        
        
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
                print('TestName: ', testsName)
                if(testsName): 
                    displayNames.append(testsName)
                    
        
            except: 
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

    def handle_item_changed(self, item, test): 
        row = item.row()
        column = item.column()
        value = item.text()
        
        #print(test)
        #print(f"Row {row}, Column {column} changed to {value}")
        
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


    #TODO: sidebar have a s
    def icpLoader(self): 
        print('LOADING ICP STUFF')
        
        self.loadClientInfo()
        
        #check if haas data to load into the file location 
        sql1 = 'SELECT sampleName, jobNumber, data FROM icpMachineData1 where jobNumber = ? ORDER BY sampleName ASC'
        sql2 = 'SELECT sampleName, jobNumber, data FROM icpMachineData2 where jobNumber = ? ORDER By sampleName ASC' 
        
        sampleData = list(self.db.query(sql1, (self.jobNum,)))
        sampleData2 = list(self.db.query(sql2, (self.jobNum,))); 
        
        
        selectedSampleNames = []
        
        for item in sampleData:
            selectedSampleNames.append(item[0])
        
        #TODO: can remove if you really think about it needs to combine both machines 
        for item in sampleData2: 
            if(item[0] not in selectedSampleNames): 
                selectedSampleNames.append(item[0]) 
        
        totalSamples = len(selectedSampleNames)     
        print('SelectedSampleItems: ', selectedSampleNames)    
        
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
            'REF Value', #TODO: remove ref value
            'distal factor'
        ]
        
        addtionalRows = [
            'pH', 
            'Hardness', 
        ]
        
        excludedElements = [
            'U', 'S'
        ]
        
        
        #setting up the table
        totalRows = len(periodic_table) + len(addtionalRows) - len(excludedElements)
        initalColumns = len(columnNames)
        
        self.ui.dataTable.setRowCount(totalRows)
        self.ui.dataTable.setColumnCount(initalColumns + len(selectedSampleNames))
        self.ui.dataTable.horizontalHeader().setVisible(True)
        self.ui.dataTable.verticalHeader().setVisible(True)

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
        
        queryDefinedElements = 'SELECT element, symbol FROM icpElements ORDER BY element ASC' 
        
        
        
        #print(elementNames)
        #print(len(elementNames))
        
        #self.ui.createReportBtn.clicked.connect(lambda: self.icpReportHander(elementNames, totalSamples)); 
        
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

        #adding hardness and Ph 
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
        #TODO: check if the sampleData's aren't empty 
        
        
        #TODO: combine both the datasets; 
        
        machine1 = {item[0]: json.loads(item[2]) for item in sampleData}
        machine2 = {item[0]: json.loads(item[2]) for item in sampleData2} 
        
        print(machine1)
        print(machine2)
        
        
        for i in range(len(elementNames)): 
            item = self.ui.dataTable.item(i, 1)
            
            if(item != None): 
                symbol = item.text()
                #print(symbol)
                
                for j, sample in enumerate(selectedSampleNames): 
                    item = QtWidgets.QTableWidgetItem(); 
                    #currentCell = self.ui.dataTable
                    #machine1Val = machine1[sample][symbol]
                    #machine2Val = machine2[sample][symbol]
                    
                    #currentCell.setText(i,j, item)
                    
                    if sample in machine1 and symbol in machine1[sample]: 
                        machine1Val = machine1[sample][symbol]
                        print(symbol, ' 1  ', machine1Val)      
                        
                        item.setText(machine1Val)
                        #currentCell.setText(i,j, item)
                        
                    
                    if sample in machine2 and symbol in machine2[sample]: 
                        machine2Val = machine2[sample][symbol]
                        machine2Val = round(machine2Val, 3 )
                        
                        print(symbol, ' 2  ', machine2Val) 
                        
                        item.setText(str(machine2Val))
                        #currentCell.setText(i,j, item)
                
                    self.ui.dataTable.setItem(i,j+5, item)


        for j, sample in enumerate(selectedSampleNames):   
            item = QtWidgets.QTableWidgetItem();  
            
            if sample in machine1 and ('Ca' in machine1[sample] and 'Mg' in machine1[sample]): 
                calcium = machine1[sample]['Ca']
                magnesium = machine1[sample]['Mg']
                
                print('cal: ', calcium)
                print('mag: ', magnesium)
                
                result = hardnessCalc(calcium, magnesium)
                print('result: ', result)
                item.setText(str(result))
                self.ui.dataTable.setItem(33, j+5, item)
                
                #item.setText(str(result))
                #self.ui.dataTable.setItem(34,j+5, item)
                
                    
        ''' 
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
                #print(cellValue2)
                hardnessVals[key] = cellValue2

            if not (['ND', 'uncal'] in hardnessValshardnessVals.items()): 
                result = hardnessCalc(hardnessVals['Ca'], hardnessVals['Mg'])
                item.setText(str(result))
                #print(result)
                
            else: 
                item.setText('ND')
            
            self.ui.dataTable.setItem(len(elementNames), col, item) 
        '''    
            #TODO: add text change items for when the values are changed
                
        
        
        column_width = self.ui.dataTable.columnWidth(2)
        padding = 10
        total_width = column_width + padding
        self.ui.dataTable.setColumnWidth(2, total_width)    

        self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
        self.ui.createIcpReportBtn.clicked.connect(lambda: self.icpReportHander(elementNames, totalSamples)); 
    
    def icpReportHander(self, tests, totalSamples): 
        #FIXME: adjust based on the sample information
        #FIXME: adjust the limits 
        #FIXME: adjust the unit amount  
        initalColumns = 5; 
        #totalSamples = len(self.sampleNames)
        totalTests = len(tests)
        sampleData = {}
        unitType = []
        
        #print(totalSamples)
        
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
        #print(elementsWithLimits)    

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
        print(limits)
        #print(self.reportType)
        #print(footerComment)
        print('--------')
   
        #load the footer comment 
        createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, tests, unitType, elementsWithLimits, limits, footerComments)
        
        
        

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
    
        newName = str(valueName).strip()
    
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
