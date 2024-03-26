
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot


from modules.dbFunctions import *
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *


#******************************************************************
#    icp Setup 
#****************************************************************** 
#TODO: deal with the side panels 
def icpSetup(self): 
    
    # load the icp database inital setup 
    # self.updateIcpTable(machine1Data) 
    loadIcpHistory(self)
    
    # Connect the signals/buttons 
    self.ui.icpUploadBtn.clicked.connect(lambda: on_icpUploadBtn_clicked(self.db))
    self.ui.icpSearchBtn.clicked.connect(lambda: on_icpSearchBtn_clicked(self))
    
    self.ui.addElementBtn.clicked.connect(lambda: on_addElementBtn_clicked(self))
    self.ui.saveCompBtn.clicked.connect(lambda: on_saveCompBtn_clicked(self)) 
    self.ui.deleteCompBtn.clicked.connect(lambda: on_deleteCompBtn_clicked(self))

    self.ui.addReportBtn.clicked.connect(lambda: on_addReportBtn_clicked(self))
    self.ui.definedElements.clicked.connect(lambda: on_definedElements_clicked(self))
    self.ui.definedElements.currentRowChanged.connect(lambda: on_definedElements_currentRowChanged(self))

    self.ui.reportsList.clicked.connect(lambda: on_reportsList_clicked(self))
    self.ui.saveFooterBtn.clicked.connect(lambda: on_saveFooterBtn_clicked(self))
    self.ui.deleteFooterBtn.clicked.connect(lambda: on_deleteFooterBtn_clicked(self))


    #on_reportlist_doubleClicked
    self.ui.reportsList.doubleClicked.connect(lambda: on_reportlist_doubleClicked())
    self.ui.reportTypeDropdown.activated.connect(lambda: loadElementLimits(self)) 

def loadReportList(self): 
    results = loadIcpReportList(self.db)
    self.ui.reportsList.clear()
    
    if(results): 
        for item in results: 
            self.ui.reportsList.addItem(item[0])    

            
def loadDefinedElements(self): 
    self.ui.reportTypeDropdown.clear()
    self.ui.gcmsDefinedtests.clear()
    self.ui.definedElements.clear()

    elements = getIcpElements(self.db)      
    
    reportType = getReportTypeList(self.db)
    self.ui.reportTypeDropdown.addItems(reportType)     
    
    for element in elements: 
        self.ui.definedElements.addItem(element[0])

    clearElementInfo(self)
    
#******************************************************************
#    ICP History 
#****************************************************************** 

@pyqtSlot()
def on_icpUploadBtn_clicked(database): 
    fileLocation = openFile()
    print(fileLocation)
    icp_upload(fileLocation, database) 


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
            updateIcpTable(self, machine1Data)


def loadIcpHistory(self):
        columnNames = ['Sample Name', 'Job Number', 'Machine Type', 'File Location', 'Upload Date']
    
        icpMachine1sql = 'SELECT sampleName, jobNumber, machine, fileLocation, createdDate data FROM icpMachineData1 ORDER BY createdDate DESC' 
        icpMachine2sql = 'SELECT sampleName, jobNumber, fileLocation, createdDate, machine data FROM icpMachineData2'
        
        machine1Data = list(self.db.query(icpMachine1sql))
        #machine2Data = list(self.db.query(icpMachine2sql))
        
        totalItems = len(machine1Data) 
        self.ui.icpLabel.setText(f'Total Items in Database: {totalItems}')
            
        updateIcpTable(self, machine1Data) 
            
def updateIcpTable(self, result): 
    textLabelUpdate = 'Total Search Results: ' + str(len(result))
    
    TableHeader = ['Sample Number', 'Job Number', 'Machine Type', 'File Location', 'Upload Date', 'Actions']

    self.ui.icpLabel.setText(textLabelUpdate)
    
    self.ui.icpTable.setRowCount(len(result)) 
    self.ui.icpTable.setColumnCount(len(TableHeader))
    self.ui.icpTable.setHorizontalHeaderLabels(TableHeader)

    smallCol = 140
    medCol = 300 
    bigCol = 750 
    
    self.ui.icpTable.setColumnWidth(0, smallCol)
    self.ui.icpTable.setColumnWidth(1, smallCol)
    self.ui.icpTable.setColumnWidth(2, smallCol)

    self.ui.icpTable.setColumnWidth(3, bigCol)
    self.ui.icpTable.setColumnWidth(4, smallCol)
    
    for i, data in enumerate(result):
        #loops throught items in the order sql requested 
        for j in range(len(data)): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(str(data[j]))
            item.setTextAlignment(Qt.AlignHCenter)
            self.ui.icpTable.setItem(i,j,item) 
    
    self.ui.icpTable.setEditTriggers(QAbstractItemView.NoEditTriggers)


#******************************************************************
#    ICP Defined Elements  
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


def icp_load_element_data(self): 
    print('[FUNCTION]: icp_load_element_data')
    selectedElement = self.ui.definedElements.currentItem()
    
    if selectedElement is not None:
        selectedElementText = selectedElement.text()
        #TODO: don't I have a global element that can do all of this stuff 
        reportType = self.ui.reportTypeDropdown.currentText()
        
        elementResult = loadIcpElement(self.db, selectedElementText)
        limitResults = loadIcpLimit(self.db, selectedElementText, reportType)
        
        print(f'Selected Element: {selectedElementText}');  
        print(f'Query Results: {elementResult}, {limitResults}'); 
        
        if elementResult: 
            self.ui.elementNameinput.setText(elementResult[0])
            self.ui.symbolInput.setText(elementResult[1])
            
            if(limitResults is None): 
                clearElementLimits(self)
            else: 
                self.ui.lowerLimit.setText(str(limitResults[2]))
                self.ui.upperLimit.setText(str(limitResults[3]))
                self.ui.unitType.setText(limitResults[5])
                self.ui.RightSideComment.setPlainText(limitResults[4]) 
        else: 
            clearElementInfo(self)
            self.ui.elementNameinput.setText(selectedElementText)
    else:
        print("No item selected.") 

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
    #FIXME: have proper save buttons
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
    
    #FIXME: move this all to the db function 
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
        clearElementInfo(self)
    
    except: 
        print('Error: could not delete item')
    

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

#******************************************************************
#    ICP Defined Reports   
#****************************************************************** 

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
            clearFooterReportContent(self); 

            item = self.ui.reportsList.currentRow(); 
            
            if(item != -1): 
                self.ui.reportsList.takeItem(item)
            
        except: 
            print("Error on_deleteFooterBtn_clicked: Deleting Report Type")

            
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

    
def clearFooterReportContent(self): 
    self.ui.icpReportNameLabel.setText("")
    self.ui.footerComments.clear()
    
#******************************************************************
#    ICP Classes  
#****************************************************************** 


    



def on_reportlist_doubleClicked(): 
    print('Something is being selected')
    #selected_item = self.ui.reportsList.currentItem()
