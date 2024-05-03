
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QWidgetItem, QTreeWidgetItem,  
)
from PyQt5.QtGui import QDoubleValidator

from modules.dbFunctions import *
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *


#******************************************************************
#    icp Setup 
#****************************************************************** 
#TODO: deal with the side panels 
#TODO: Lazy loading to make it better
def icpSetup(self): 
    
    # load the icp database inital setup 
    # self.updateIcpTable(machine1Data) 
    icp_history_setup(self)
    elements_setup(self)

    # 
    self.ui.icpElementTreeWidget.setColumnWidth(1, 200);
    headers = self.ui.icpElementTreeWidget.header()
    headers.setDefaultAlignment(Qt.AlignCenter)

    
    # Connect the signals/buttons 
    self.ui.icpUploadBtn.clicked.connect(lambda: on_icpUploadBtn_clicked(self.db))
    self.ui.icpSearchBtn.clicked.connect(lambda: on_icpSearchBtn_clicked(self))
    
    #self.ui.addElementBtn.clicked.connect(lambda: on_addElementBtn_clicked(self))
    #self.ui.saveCompBtn.clicked.connect(lambda: on_saveCompBtn_clicked(self)) 
    #self.ui.deleteCompBtn.clicked.connect(lambda: on_deleteCompBtn_clicked(self))

    self.ui.addReportBtn.clicked.connect(lambda: on_addReportBtn_clicked(self))

    # When ICP elements list changes, we load up the new information 
    #self.ui.definedElements.currentRowChanged.connect(lambda: on_definedElements_currentRowChanged(self))

    self.ui.reportsList.clicked.connect(lambda: on_reportsList_clicked(self))
    self.ui.saveFooterBtn.clicked.connect(lambda: on_saveFooterBtn_clicked(self))
    self.ui.deleteFooterBtn.clicked.connect(lambda: on_deleteFooterBtn_clicked(self))

 
    #on_reportlist_doubleClicked
    self.ui.reportsList.doubleClicked.connect(lambda: on_reportlist_doubleClicked())
    
    #self.ui.reportTypeDropdown.activated.connect(lambda: loadElementLimits(self)) 

# TODO: don't even think I need to have a seperate reports section, can just combine it all into a single ICP page 
def loadReportList(self): 
    results = loadIcpReportList(self.db)
    self.ui.reportsList.clear()
    
    if(results): 
        for item in results: 
            self.ui.reportsList.addItem(item[0])    

            
def loadDefinedElements(self): 
    #self.ui.reportTypeDropdown.clear()
    self.ui.gcmsDefinedtests.clear()
    self.ui.definedElements.clear()

    elements = getIcpElements2(self.tempDB)
    
    reportType = getReportTypeList(self.db)
    #self.ui.reportTypeDropdown.addItems(reportType)     
    
    for element in elements: 
        elementNum = element[0]
        elementName = element[1]
        elementSymbol = element[2]
        
        self.ui.definedElements.addItem(elementName)
        

    clearElementInfo(self)
    
#******************************************************************
#    ICP History 
#****************************************************************** 

def icp_history_setup(self): 
    loadIcpHistory(self) 

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
    #reportType = self.ui.reportTypeDropdown.currentText()
    elementName = self.ui.elementNameinput.text().lower()
    
    try: 
        limitResults = loadIcpLimit(self.db, elementName, reportType)
        print(f'Query Results: {elementName}, {limitResults}'); 
        
        if(limitResults is None): 
            clearElementLimits(self)
        else: 
            #TODO: define what the limit values are equal to 
            self.ui.lowerLimit.setText(str(limitResults[2]))
            self.ui.upperLimit.setText(str(limitResults[3]))
            self.ui.unitType.setText(limitResults[5])
            self.ui.RightSideComment.setPlainText(limitResults[4]) 
    except: 
        print('Error on loadElementLimits: Could not load in limits')

@pyqtSlot()
def icp_load_element_data(self): 
    print('[FUNCTION]: icp_load_element_data')
    selectedElement = self.ui.definedElements.currentItem()
    
    if selectedElement is not None:
        selectedElementText = selectedElement.text()
        elementResult = loadIcpElement(self.db, selectedElementText)
        
        print(f'Selected Element: {selectedElementText}');  
     
        if elementResult: 
            elementName = elementResult[0]
            elementSymbol = elementResult[1]
            
            # Set the element header name
            self.ui.icpElementNameHeader.setText(elementName.capitalize())
            
            # set the basic element info  
            #self.ui.elementNameinput.setText(elementName)
            #self.ui.symbolInput.setText(elementSymbol)

            # load the limits
            #loadElementLimits(self) 

            # Load the report type tree 
            #loadElementReportTree(self)
            #tests_one(self, elementName)

            
        else: 
            clearElementInfo(self)
            self.ui.elementNameinput.setText(selectedElementText)
    else:
        print("No item selected.") 

@pyqtSlot()
def loadElementReportTree(self): 
    print('[Function]: loadElementReportTree')
    
    # Clear the table before loading any data 
    self.ui.icpElementTreeWidget.clear()
    
    query = 'SELECT reportType, lowerLimit, maxLimit, units  FROM icpLimits WHERE element = ? ORDER BY reportType ASC'  
    
    elementName = self.ui.elementNameinput.text().lower()
    results = self.db.query(query, (elementName, ))

    # Populate the report table
    for currentReport in results: 
        item = QTreeWidgetItem(self.ui.icpElementTreeWidget) 
        item.setText(0, currentReport[0])  
        item.setData(1, 0, currentReport[1]) 
        item.setData(2, 0, currentReport[2])
        item.setText(3, currentReport[3])

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
    
    #reportType = self.ui.reportTypeDropdown.currentText()
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
    
@pyqtSlot()        
def on_definedElements_currentRowChanged(self):
    try:
        icp_load_element_data(self);
    except Exception as error: 
        print('Error: Could not loaded the defined element data')
        print(error)
    
        
def clearElementInfo(self): 
    # Clear element info 
    self.ui.symbolInput.clear()
    self.ui.elementNameinput.clear()

    # Clear the Tree Widget
    self.ui.icpElementTreeWidget.clear()
    
    # Clear the report type information 
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


class Element: 
    def __init__(self, elementNum, elementName, elementSymbol, limits): 
        self.num = elementNum
        self.name = elementName
        self.symbol = elementSymbol
        self.limits = limits         

class ElementsManager(QObject): 
    elementsChanged = pyqtSignal(int, Element)  # Custom signal to indicate changes in elements
    
    def __init__(self, db):
        super().__init__() 
        self.db = db   
        self.elements = {} 
        
    # load the inital data 
    def loadElements(self, elementsList ): 
        
        for element in elementsList: 
            elementNum = element[0]
            elementName = element[1]
            elementSymbol = element[2]
       
            elementLimits = self.loadElementLimits(elementNum)

            self.elements[elementNum] = Element(elementNum, elementName, elementSymbol, elementLimits)
        
    def loadElementLimits(self, elementNum): 
        try:
            # Limits = {
            #   reportType_1: [unitType, lowerLimit, upperLimit, sideComment]
            #   reportType_2: [unitType, lowerLimit, upperLimit, sideComment] 
           
            elementLimits = getIcpElementLimits(self.db, elementNum)
            return {report[0]: report[2:] for report in elementLimits}

        except Exception as error:
            print('[ERROR]:', error)
            return None
        

    def getElements(self): 
        return self.elements
    
    def getElementByNum(self, elementNum): 
        for element_key, element_value in self.elements.items(): 
            if element_key.num == elementNum:  
                return element_value
            
        return None 

    def getElementByName(self, elementName): 
        for element_key, element_value  in self.elements.items(): 
            if element_value.name == elementName:  
                return element_value 
            
            
        return None 
    
    def getTotalElements(self): 
        return len(self.elements)
    
    def addElement(self, elementNum, element): 
                
        self.elements[elementNum] = element
        
        #TODO: add element to the database 
        
        self.elementsChanged.emit(42, element) 
    
    def removeElement(self, elementNum): 
        self.elements.pop(elementNum, None) 
    
        #TODO: remove element from the database 
    
    def updateElement(self, elementNum, element): 
        print(f'[CLASS]: UpdateElement(self, {elementNum}, element)')
        if(elementNum in self.elements): 
            self.elements[elementNum] = element
        
        self.elementsChanged.emit(1, element)
    

def elementManagerSignalHandler(self, value, element): 
    print(f'[SIGNAL FUNCTION]: elementManagerSignalHandler({value}, {element})')
    print("Received:", value)
    
    
    if(value == 1):  
        loadElementReportTypeInfo(self, element)  
    
    
    
#FIXME: has to load in the list each time, so create a function that app.py can access 
def elements_setup(self): 

    # Icp Element Tree Widget Formatting 
    self.ui.icpElementTreeWidget.setColumnWidth(1, 200);
    headers = self.ui.icpElementTreeWidget.header()
    headers.setDefaultAlignment(Qt.AlignCenter)
    
    # Clear the QList of the elements 
    self.ui.definedElements.clear()
    clearElementInfo(self) 
    
    self.elementManager = ElementsManager(self.tempDB)
    
    # Connect the element Manager slot 
    self.elementManager.elementsChanged.connect(lambda value, element: elementManagerSignalHandler(self, value, element))
        
    elements = getIcpElements2(self.tempDB)
    self.elementManager.loadElements(elements)
    
    #TODO: Trigger to change this when item is added or removed 
    totalElements = self.elementManager.getTotalElements()
    self.ui.icpLabel.setText("Total Elements: {}".format(totalElements))
    
    # Create a QDoubleValidator
    validator = QDoubleValidator()
    # Set the range of valid floating-point values
    validator.setRange(-10000, 10000.0)  
    # Set the number of decimal places allowed
    validator.setDecimals(10)  # Allow up to 5 decimal places
    
    # Set the validator for the QLineEdit to only allow float values 
    self.ui.lowerLimit.setValidator(validator)
    self.ui.upperLimit.setValidator(validator)
    
    # Populate QList 
    loadElementsList(self)
    
    # Populate QTree 
    loadReportsTree(self)
    
    # Drop Down Widget 
    reportType = getAllParameters(self.preferencesDB)
    reportType = [report[1] for report in reportType]
    reportType.insert(0,'')

    self.ui.reportTypeDropdown.clear()
    self.ui.reportTypeDropdown.addItems(reportType)   
    
    # Dropdown widget change Signal    
    self.ui.reportTypeDropdown.activated.connect(lambda index: onIcpDropDownMenuChange(self, index)) 
    
    # QList Signs 
    # When ICP elements list changes, we load up the new information 
    self.ui.definedElements.currentRowChanged.connect(lambda: onIcpListWidgetChange(self))
    
    # QTree Signs 
    # When selecting a item on the QTree Signal 
    self.ui.icpElementTreeWidget.currentItemChanged.connect(lambda current_report: onIcpTreeWidgetChange(self, current_report))


    # Need to create a clone element that get's delete when not in use 
    
    # When the limit changes we want to change the report type too 
    
    
    

    # Button Signs 
    #   Add Button 
    #   Delete Button  
    #   Saves Button 
    #   Cancel Button 
    
    
    #TODO: can disable the buttons until something is selected 
    # self.ui.deleteCompBtn()
    # self.ui.addElementBtn()
    # self.ui.icpCancelBtn()
    self.ui.saveCompBtn.clicked.connect(lambda: saveIcpBtnClicked(self))
    self.ui.icpCancelBtn.clicked.connect(lambda: cancelIcpBtnClicked(self))
    

def cancelIcpBtnClicked(self): 
    print('[SIGNAL]: cancelIcpBtnClicked(self)') 

    clearElementLimits(self)

    # Load the previous stuff 
    selectedElement = self.ui.definedElements.currentItem() 
    
    if(selectedElement): 
        elementName = selectedElement.text()
        
        # De-active tree selection and drop down menu 
        self.ui.icpElementTreeWidget.clearSelection()
        self.ui.reportTypeDropdown.setCurrentText('')

        #TODO: check if the elemenet exists
        element = self.elementManager.getElementByName(elementName)
        

    
        # Load the basic Element Info 
        loadElementsInfo(self, element)
        
        # Load the element Report Types 
        loadElementReportTypeInfo(self, element)
    
    
    
    

def saveIcpBtnClicked(self): 
    print('[SIGNAL]: saveIcpElementClicked(self)')

    selectedElement = self.ui.definedElements.currentItem() 
    
    if(selectedElement): 
       
        elementName = selectedElement.text() 

        
        # Save the element Info (name, symbol)
        element = self.elementManager.getElementByName(elementName) 
        elementNum = element.num
        elementLimits = element.limits
        
        updateElementName = self.ui.elementNameinput.text()
        updateElementSymbol = self.ui.symbolInput.text()
        
        # Save the report type ()
        updateLowerLimit = self.ui.lowerLimit.text()
        updateUpperLimit = self.ui.upperLimit.text()
        updateUnitType = self.ui.unitType.text()
        updateSideComment = self.ui.RightSideComment.toPlainText()
        
        reportName = self.ui.reportTypeDropdown.currentText()
        reportNum = getReportNum(self.preferencesDB, reportName) #TODO: make this better somehow? 
        
        
        # TODO: Update the element and QList element and QTree report info  
        # TODO: Error checking if we allowed to make those changes
        print(f'ReportNum: {reportNum}, reportName: {reportName}')

        newLimitData = [updateUnitType, updateLowerLimit, updateUpperLimit, updateSideComment]
        element.limits[reportNum] = newLimitData
        self.elementManager.updateElement(elementNum, element)
    


#TODO: when items are delete and add?, does it matter thought I have an item that keeps track of it all 
def loadElementsList(self): 
    print('[FUNCTION]: loadElementsList(self)')
    elements = getIcpElements2(self.tempDB) 
    
    for element in elements: 
        elementNum = element[0]
        elementName = element[1]
        elementSymbol = element[2]
        
        self.ui.definedElements.addItem(elementName) 
        
def loadReportsTree(self): 
    print(f'[FUNCTION]: loadReportsTree(self))') 
    reportTypes = getAllParameters(self.preferencesDB)
    
    # set the tree widget 
    for currentReport in reportTypes: 
        reportNum = currentReport[0]
        reportName = currentReport[1]
        
        item = QTreeWidgetItem(self.ui.icpElementTreeWidget) 
        item.setText(0, "{:03d}".format(reportNum))   
        item.setText(1, reportName)
    
def clearReportsTree(treeWidget):
    print(f'[FUNCTION]: clearReportsTree(treeWidget)') 
    columns = [2,3,4]
    
    for item_index in range(treeWidget.topLevelItemCount()):
        item = treeWidget.topLevelItem(item_index)

        # Only clear these columns
        for column in columns:
            item.setData(column, Qt.DisplayRole, None)

def loadElementReportTypeInfo(self, element):
    print(f'[FUNCTION]: loadElementReportTypeInfo(self, element)')
    treeWidget = self.ui.icpElementTreeWidget 
    
    clearReportsTree(treeWidget)
    limits = element.limits 

    for item_index in range(treeWidget.topLevelItemCount()):
        item = treeWidget.topLevelItem(item_index)
        
        if(item): 
            reportNum = int(item.text(0))
            
            if(reportNum in limits):
                lowerLimit = str(limits[reportNum][1])
                upperLimit = str(limits[reportNum][2])
                unitType = limits[reportNum][0]

                # Set the Tree Widget 
                if(lowerLimit): 
                    item.setData(2, Qt.DisplayRole, lowerLimit)
                    item.setData(2, Qt.TextAlignmentRole, Qt.AlignCenter)
                    
                if(upperLimit): 
                    item.setData(3, Qt.DisplayRole, upperLimit)
                    item.setData(3, Qt.TextAlignmentRole, Qt.AlignCenter)         

                if(unitType): 
                    item.setText(4, unitType)
    
   
def onIcpListWidgetChange(self): 
    print(f'[SIGNAL]: onIcpListWidgetChange()')

    clearElementLimits(self)

    # Get the Element Name from the QList 
    selectedElement = self.ui.definedElements.currentItem() 

    
    #TODO: create a temp element that is the same or we only update it when we change it
    if selectedElement is not None: 
        elementName = selectedElement.text()
        
        # De-active tree selection and drop down menu 
        self.ui.icpElementTreeWidget.clearSelection()
        self.ui.reportTypeDropdown.setCurrentText('')

        #TODO: check if the elemenet exists
        element = self.elementManager.getElementByName(elementName)


    
        # Load the basic Element Info 
        loadElementsInfo(self, element)
        
        # Load the element Report Types 
        loadElementReportTypeInfo(self, element)



def onIcpDropDownMenuChange(self, index): 
    print(f'[SIGNAL]: onIcpDropDownMenuChange()')
    treeWidget = self.ui.icpElementTreeWidget

    current_text = self.ui.reportTypeDropdown.itemText(index)

    print('Current Index: ', index)
    if(index): 
        
        reportName = self.ui.reportTypeDropdown.itemText(index)
        
        # Setting the Report Type Tree to match active selection 
        if(reportName != ''): 
            for i in range(treeWidget.topLevelItemCount()):
                item = treeWidget.topLevelItem(i)
                
                if(item): 
                    treeReportName = item.text(1)
                    
                    if(reportName == treeReportName): 
                        treeWidget.setCurrentItem(item)   
                        

def onIcpTreeWidgetChange(self, current_widget):
    print(f'[SIGNAL]: onIcpTreeWidgetChange()')
    clearElementLimits(self)    
 
    # Get the Element Name from the QList  
    elementName = self.ui.definedElements.currentItem()
    
    if current_widget and elementName:  
        elementName = self.ui.definedElements.currentItem().text()
        
        reportNum = int(current_widget.text(0))
        reportName = current_widget.text(1)

        element = self.elementManager.getElementByName(elementName)
        
        # Check if the text is in the list of items
        if reportName in [self.ui.reportTypeDropdown.itemText(i) for i in range(self.ui.reportTypeDropdown.count())]:
            # Setting the drop down menu to match active selection 
            self.ui.reportTypeDropdown.setCurrentText(reportName)
        else:
            print("The text is not in the list of items.")
        
        # Check if the limits exists 
        if reportNum in element.limits: 
            limits = element.limits[reportNum]
            #print(f'Element: {elementName} | Report: {reportNum} | Limits: {limits}')
            
            lowerLimit = str(limits[1])
            upperLimit = str(limits[2])
            unitType = limits[0]
            sideComment = limits[3]
        
            #TODO: need to be able to conver the string back into int 
            self.ui.lowerLimit.setText(lowerLimit)
            self.ui.upperLimit.setText(upperLimit)
            self.ui.unitType.setText(unitType)  
            self.ui.RightSideComment.setPlainText(sideComment) 
        
def loadElementsInfo(self, element): 
    print(f'[FUNCTION]: loadElementsInfo(self, {element})')
    
    self.ui.elementNameinput.clear()
    self.ui.symbolInput.clear()
   
    if(element): 
    
        elementNum = element.num
        elementName = element.name
        elementSymbol = element.symbol 
        elementLimits = element.limits 

        # Load the basic information into UI 
        self.ui.elementNameinput.setText(elementName)
        self.ui.symbolInput.setText(elementSymbol) 
