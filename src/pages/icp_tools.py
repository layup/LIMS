
import math 
import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QAbstractTableModel, QModelIndex


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


ICP_FILTER = {
    'Sample Number': 1, 
    
}


#******************************************************************
#    icp Setup 
#****************************************************************** 
#TODO: deal with the side panels 
#TODO: Lazy loading to make it better
def icpSetup(self): 
    
    # load the icp database inital setup 
    icp_history_setup(self)
    icp_elements_setup(self)

    self.ui.icpElementTreeWidget.setColumnWidth(1, 200);
    headers = self.ui.icpElementTreeWidget.header()
    headers.setDefaultAlignment(Qt.AlignCenter)

    self.ui.addReportBtn.clicked.connect(lambda: on_addReportBtn_clicked(self))

    # Reports Signals
    self.ui.reportsList.clicked.connect(lambda: on_reportsList_clicked(self))
    self.ui.saveFooterBtn.clicked.connect(lambda: on_saveFooterBtn_clicked(self))
    self.ui.deleteFooterBtn.clicked.connect(lambda: on_deleteFooterBtn_clicked(self))

    icpDatabaseSetup(self)

# TODO: don't even think I need to have a seperate reports section, can just combine it all into a single ICP page 

#******************************************************************
#    ICP General Functions
#****************************************************************** 

def loadReportList(self): 
    results = loadIcpReportList(self.db)
    self.ui.reportsList.clear()
    
    if(results): 
        for item in results: 
            self.ui.reportsList.addItem(item[0])    

#******************************************************************
#    ICP History 
#****************************************************************** 
def icp_history_setup(self): 
    print('[FUNCTION]: icp_history_setup(self)')
     
    # Format the icp History Table      
    columnNames = ['Sample Number', 'Job Number', 'Machine Type', 'File Location', 'Upload Date', 'Actions']

    smallCol = 140
    medCol = 240 
    bigCol = 340 
    
    self.ui.icpTable.setHorizontalHeaderLabels(columnNames)
    self.ui.icpTable.horizontalHeader().setStretchLastSection(True)

    self.ui.icpTable.verticalHeader().setVisible(True)

    # Set the width of the tables 
    self.ui.icpTable.setColumnWidth(0, smallCol)
    self.ui.icpTable.setColumnWidth(1, smallCol)
    self.ui.icpTable.setColumnWidth(2, smallCol)
    self.ui.icpTable.setColumnWidth(3, medCol)
    self.ui.icpTable.setColumnWidth(4, smallCol)
    self.ui.icpTable.setColumnWidth(5, medCol)
    
    # Search bar section 
    # TODO: add signals that will effect this 
    self.ui.filterComboBox.clear()
    self.ui.filterComboBox.addItems(FILTER_BY)

    #row_size = 100 
    #icpFooterSetup(self, row_size)
    
    # Connect the signals/buttons and change the database 
    self.ui.icpUploadBtn.clicked.connect(lambda: on_icpUploadBtn_clicked(self.tempDB))
    #self.ui.icpSearchBtn1.clicked.connect(lambda: on_icpSearchBtn_clicked(self))

    #loadIcpHistory(self) 
    
    
def icpFooterSetup(self, row_size: int): 
    """ Calculates how many the page size based on the row size filter

    Args:
        self (Object): contains all the information about the app 
        row_size (int): the row size of the data 
    """
    
    query = 'SELECT COUNT(*) FROM icpData' 

    totalPages = self.tempDB.query(query)[0][0]
    totalPages = int(math.ceil(totalPages/row_size)); 

    self.footer_widget = TableFooterWidget(totalPages)
    
    self.ui.icpHistoryLayout.addWidget(self.footer_widget)
    

@pyqtSlot()
def on_icpUploadBtn_clicked(database): 
    print('[SIGNAL]: on_icpUploadBtn_clicked(database)')
    
    fileLocation = openFile()
    print(fileLocation)
    icp_upload(fileLocation, database) 


@pyqtSlot()
def on_icpSearchBtn_clicked(self): 
    print('[SIGNAL]: on_icpSearchBtn_clicked(database)')

    jobNum = self.ui.icpSearchInput.text() 
    
    # Reload the inital table 
    if(jobNum == ''):
        loadIcpHistory(self)
    else: 
        inquery = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData WHERE sampleName LIKE ?' 
        machineData = list(self.tempDB.query(inquery,('%' + jobNum + '%',)))
        
        # FIXME: streamline the QMessageBox Process 
        if not machineData: 
            msgBox = QMessageBox()  
            msgBox.setText("No Search Results");
            msgBox.setInformativeText("No search results for given job number");
            msgBox.setStandardButtons(QMessageBox.Ok);
            x = msgBox.exec_()  # this will show our messagebox
        else: 
            populateIcpHistoryTable(self, machineData)

def loadIcpHistory(self):   
    print('[FUNCTION]: loadIcpHistory(self)')
    
    machineDataQuery = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData ORDER BY creationDate DESC'
    machineData = list(self.tempDB.query(machineDataQuery))
    totalItem = len(machineData) 
    #self.ui.headerDesc.setText(f'Total Items in Database: {totalItem}')
        
    populateIcpHistoryTable(self, machineData) 
            
def populateIcpHistoryTable(self, result): 
    print('[FUNCTION]: populateIcpHistoryTable(self, result)') 
    
    textLabelUpdate = 'Total Search Results: ' + str(len(result))
    
    TableHeader = ['Sample Number', 'Job Number', 'Machine Type', 'File Location', 'Upload Date', 'Actions']

    self.ui.headerDesc.setText(textLabelUpdate)    
    self.ui.icpTable.setRowCount(len(result)) 
    self.ui.icpTable.setColumnCount(len(TableHeader))
    self.ui.icpTable.setHorizontalHeaderLabels(TableHeader)

    for row , data in enumerate(result):
        #loops throught items in the order sql requested 
        self.ui.icpTable.setRowHeight(row, TABLE_ROW_HEIGHT)
        
        sampleNum = data[0] 
        machineType = data[2]
        
        for col in range(len(data)): 
            item = QtWidgets.QTableWidgetItem()
            item.setText(str(data[col]))
            item.setTextAlignment(Qt.AlignHCenter)
            self.ui.icpTable.setItem(row ,col ,item) 
            
        #FIXME: 
        button = QPushButton("Open") 
        button.setFixedSize(100, 10)  # Set the fixed size of the button (width, height)
       
        button.clicked.connect(lambda _, sampleNum=sampleNum, machineType=machineType: icpOpenbutton(self, sampleNum, machineType))
        actionRow = 5 
        self.ui.icpTable.setCellWidget(row, actionRow, button)

    
    self.ui.icpTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

def icpOpenbutton(database, sampleNum, machineType): 
    print(f'Sample: {sampleNum} Machine: {machineType}')
    
    dialog = viewIcpDataDialog(database, sampleNum, machineType) 
    dialog.exec()
    
    
    
    
# TODO: have a view, edit on the table 
# TODO: create a clone that holds data until user presses the save button (kind of a pain in the ass)
#******************************************************************
#    ICP Elements  
#******************************************************************   
    
    
#FIXME: has to load in the list each time, so create a function that app.py can access 
def icp_elements_setup(self): 

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
        
    #FIXME: I am loading in the data more times then I probably need to for this to work (have one master control)
    elements = getIcpElements2(self.tempDB)
    self.elementManager.loadElements(elements)
    
    #TODO: Trigger to change this when item is added or removed 
    totalElements = self.elementManager.getTotalElements()
    self.ui.headerDesc.setText("Total Elements: {}".format(totalElements))
    
    # Create a QDoubleValidator
    validator = QDoubleValidator()
    validator.setRange(-10000, 10000.0)  
    validator.setDecimals(10)  

    # Set the validator for the QLineEdit to only allow float values 
    self.ui.lowerLimit.setValidator(validator)
    self.ui.upperLimit.setValidator(validator)
    
    # Populate QList and QTree 
    loadElementsList(self)
    loadReportsTree(self)
    
    # Drop Down Widget 
    reportType = getAllParameters(self.tempDB)
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
    
    #TODO: can disable the buttons until something is selected 
    self.ui.deleteCompBtn.clicked.connect(lambda: print('Delete Element Button Clicked'))
    self.ui.addElementBtn.clicked.connect(lambda: addIcpElementBtnClicked(self))
    self.ui.saveCompBtn.clicked.connect(lambda: saveIcpBtnClicked(self))
    self.ui.icpCancelBtn.clicked.connect(lambda: cancelIcpBtnClicked(self))
        
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
    
def loadElementData(self): 
    print(f'loadElementData(self)')

    # Clear off the limit lineEdits
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
    reportTypes = getAllParameters(self.tempDB)
    
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
                    item.setData(4, Qt.TextAlignmentRole, Qt.AlignCenter)   
                    
#******************************************************************
#    ICP Elements Signals
#******************************************************************  

#TODO: finish the implmentation of this 
def elementManagerSignalHandler(self, value, element): 
    print(f'[SIGNAL FUNCTION]: elementManagerSignalHandler({value}, {element})')
    
    if(value == 'ADD'): 
        # Update QList, does the order really matter when we do this?
        pass; 
    
    if(value == 'REMOVE'): 
        pass; 
    
    if(value == 'UPDATE'):  
        loadElementReportTypeInfo(self, element)  


def addIcpElementBtnClicked(self): 
    print('[DIALOG]: addIcpElementBtnClicked(self)')
    # Get the report Types 

    # Save the ICP to database 
    
    # Update the QList and Element Manager
    
    reportType = getAllParameters(self.tempDB)
    reportType = [[report[0], report[1]] for report in reportType]
    
    dialog = addElementDialog(self.tempDB, reportType)

    dialog.exec()

def cancelIcpBtnClicked(self): 
    print('[SIGNAL]: cancelIcpBtnClicked(self)') 
    loadElementData(self)

def saveIcpBtnClicked(self): 
    print('[SIGNAL]: saveIcpElementClicked(self)')

    selectedElement = self.ui.definedElements.currentItem() 
    
    if(selectedElement): 
       
        elementName = selectedElement.text() 
 
        #TODO: allow for element info to be changed instead of just the limits and stuff
        updateElementName = self.ui.elementNameinput.text()
        updateElementSymbol = self.ui.symbolInput.text()
        
        # Save the report type ()
        updateLowerLimit = self.ui.lowerLimit.text()
        updateUpperLimit = self.ui.upperLimit.text()
        updateUnitType = self.ui.unitType.text()
        updateSideComment = self.ui.RightSideComment.toPlainText()
        
        reportName = self.ui.reportTypeDropdown.currentText()
        reportNum = getReportNum(self.tempDB, reportName)

        print(f'ReportNum: {reportNum}, reportName: {reportName}')    
    
        if(reportNum): 
            reportNum = reportNum[0][0]
            newLimitData = [updateUnitType, updateLowerLimit, updateUpperLimit, updateSideComment]
            self.elementManager.updateElementLimit(elementName, reportNum, newLimitData)

def onIcpListWidgetChange(self): 
    print(f'[SIGNAL]: onIcpListWidgetChange()')

    loadElementData(self)

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


#******************************************************************
#    ICP Reports   
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

class Element: 
    def __init__(self, elementNum, elementName, elementSymbol, limits): 
        self.num = elementNum
        self.name = elementName
        self.symbol = elementSymbol
        self.limits = limits    
        
class ElementsManager(QObject): 
    elementsChanged = pyqtSignal(str, Element)  # Custom signal to indicate changes in elements
    
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
        
        self.elementsChanged.emit('ADD', element) 
    
    def removeElement(self, elementNum): 
        self.elements.pop(elementNum, None) 
    
        #TODO: remove element from the database 
        self.elementsChanged.emit('REMOVE', None)
    
    
    def updateElementLimit(self, elementName, reportNum, newLimits): 
        element = self.getElementByName(elementName) 
        elementNum = element.num
        elementLimits = element.limits 
        
        print(f'Old Limits: {elementLimits}')
        
        elementLimits[reportNum] = newLimits
        print(f'New Limits: {elementLimits}')
        
        # Update the information to the database
        updateIcpLimits(self.db, reportNum, elementNum, newLimits)

        self.elementsChanged.emit('UPDATE', element)

    def updateElement(self, elementNum, element): 
        print(f'[CLASS]: UpdateElement(self, {elementNum}, element)')
        if(elementNum in self.elements): 
            self.elements[elementNum] = element
        
        self.elementsChanged.emit('UPDATE', element)


class addElementDialog(QDialog):

    addedElement = pyqtSignal(str, Element)  
    
    def __init__(self, db, reportTypes):
        super().__init__()
                
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'elementDialog.ui')
        loadUi(file_path, self)
        
        self.db = db 
        self.reportTypes = reportTypes 
        print(f'Reports Types: {self.reportTypes}')
        
        # Conne the buttons 
        self.cancelBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.saveElement)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Add New Element')
        self.errorMsg.hide()

        # Setup up headers and columns 
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)

        self.table.verticalHeader().hide()
        
        # setting table column width 
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        
        # Set Row Count 
        self.table.setRowCount(len(self.reportTypes))

        if(self.reportTypes):         
            for row, item in enumerate(self.reportTypes): 
                
                self.table.setRowHeight(row, TABLE_ROW_HEIGHT)
                
                reportNumItem = QTableWidgetItem(str(item[0])) # Convert number into a string  
                reportNameItem = QTableWidgetItem(item[1])

                # disable editing for the first two tables 
                reportNumItem.setFlags(reportNumItem.flags() & ~Qt.ItemIsEditable) 
                reportNameItem.setFlags(reportNameItem.flags() & ~Qt.ItemIsEditable)
                
                self.table.setItem(row, 0, reportNumItem)
                self.table.setItem(row, 1, reportNameItem)
    
    #TODO: save the stuff 
    def saveElement(self): 
        self.errorMsg.hide()
        
        # Error Checking 
        existing_elements = getIcpElements(self.db)
        
        numbers, names, symbols = zip(*existing_elements)
    
        print(f'Elements: {existing_elements}')
        
        errorCheck = [0,0,0,0,0]
        
        if(self.elementNameLineEdit and self.symbolNameLineEdit): 
            elementName = self.elementNameLineEdit.text().lower()
            elementSymbol = self.symbolNameLineEdit.text().lower()
            
            if(elementName in names): 
                errorCheck[0] = 1 
                
            if(elementSymbol in symbols): 
                errorCheck[1] = 1
                
            
        print(sum(errorCheck)) 
        if(sum(errorCheck) == 0): 
            
            #TODO: fix the error completeionl 
            # Save to the database 
            
            # Update the Element Manager 
            
            pass; 
        else: 
            self.errorMsg.show()
            self.errorMsg.setText('ERROR')
    
    def getTableValues(self): 
        pass; 
       
       
class viewIcpDataDialog(QDialog): 
    
    def __init__(self, db, sampleNum,  machineType):
        super().__init__()
        
        self.db = db 
        self.sampleNum = sampleNum
        self.jobNum = sampleNum[0:6]
        self.machineType = machineType
        
        # load UI
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'icpViewDataDialog.ui')
        loadUi(file_path, self)

        # Connect Signals 
        self.saveBtn.clicked.connect(lambda: print('save button clicked'))
        self.cancelBtn.clicked.connect(self.close)

        self.init_data()
     
    def init_data(self): 
        # Get the data from the database 
        query = f"SELECT * FROM icpData WHERE jobNum = '{self.jobNum}' AND machineNum = '{int(self.machineType)}'"
        results = self.db.query(query)

        fileName = results[0][2]
        uploadDate = results[0][4]
        sampleNames = [item[0] for item in results]
        sampleNames.insert(0, 'Elements')
        elementNames = list(json.loads(results[0][3]).keys())
        
        # Lod the preset data 
        self.jobNumberLabel.setText(self.jobNum)
        self.textFileLabel.setText(fileName)
        self.uploadedDateLabel.setText(uploadDate)
        self.machineNumLabel.setText(str(self.machineType))
    
        # Prepare the table 
        self.tableWidget.setRowCount(len(elementNames))
        self.tableWidget.setColumnCount(len(sampleNames))
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)
    
        # Set the table heders 
        self.tableWidget.setHorizontalHeaderLabels(sampleNames)

        # Assign elements row and disable editing of them
        for row, element in enumerate(elementNames): 
            item = QTableWidgetItem(element)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 0, item) 

        for col, data in enumerate(results, start=1): 

            if isinstance(data[3], str):  # Check if it's a string
                try:
                    element_data = json.loads(data[3])  # Load JSON into a dictionary
                    
                    for row, (key, value) in enumerate(element_data.items()): 
                        #print(f'col: {col}, row: {row}, key: {key} data: {value}')
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, value)
                        self.tableWidget.setItem(row, col, item)
                        
                except json.JSONDecodeError:
                    print("Error: Invalid JSON data")  # Handle potential invalid JSON
                    
    def updateSampleData(): 
        pass; 
    
    
def icpDatabaseSetup(self): 
 

    self.icpHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.icpTableView = DatabaseTableView(self.ui.icpTable, self.ui.icpHistoryLayout, self.icpHistoryDataModel) 


    # Connect the data change info martion 
    # 
    # update footer (buttons, page change, filter update) -> update data 
    # update search -> update data and footer 
    # update data -> update table 
    self.icpHistoryDataModel.dataChanged.connect(lambda newData: self.icpTableView.update_table(newData))
    self.ui.icpSearchBtn1.clicked.connect(lambda: self.icpTableView.handle_search_text(self.ui.icpSearchLine1.text()))

    # brute force approach
    # Load the data for the defaults 
    # when item change, reload the data as a whole,
    # keep track of everything ing the database Table Model and reload data as according to the information
    # model: data, footer info, 
    # Footer emits something when changed that the data model will deal with 
    
    
    pass; 

def process_data(int, list): 
    print('data changed')


def loadICPdatabase(self): 
    pass; 
    
    
# NOTE: this might not be quicker and might be better to load them in each time 
class icpHistoryData(): 
    def __init__(self, sampleName, jobNum, machineType, fileLocation, creationDate): 
        self.sampleName = sampleName
        self.jobNum = jobNum
        self.machineType = machineType
        self.fileLocation = fileLocation
    
class DatabaseTableModel(QObject): 
    # Update the table items 
    # Update the footer items 
    dataChanged = pyqtSignal(list)

    def __init__(self, database, current_page=1, total_rows=100):
        super().__init__()
        self.db = database 

        self.data = []
        self.filtered_data = self.data
          
        self.current_page = current_page
        self.total_rows = total_rows
        self.total_pages = self.get_total_rows()

        self.load_init_data()
        
    def get_data(self): 
        self.data = self.fetch_data()
    
    def get_total_rows(self): 
        query = 'SELECT COUNT(*) FROM icpData' 

        totalPages = self.db.query(query)[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));  
        
        return totalPages
    
    def get_total_rows_filter(self, text): 
        query = f'SELECT COUNT(*) FROM icpData WHERE sampleName LIKE %{text}%'

        totalPages = self.db.query(query)[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));  
        
        return totalPages
        
        
    def get_footer_info(self): 
        return {
            'current_page': self.current_page, 
            'total_rows': self.total_rows, 
            'total_pages': self.total_pages, 
        }
        
    def load_init_data(self): 
        print('load_init_data')
        self.data = self.fetch_data() 

    def fetch_data(self):
        machineDataQuery = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
        offSet = (self.current_page -1) * self.total_rows
        
        self.db.execute(machineDataQuery, (self.total_rows, offSet,))  # Pass offset as a single value
        self.data = list(self.db.fetchall())
        
        self.dataChanged.emit(self.data)
        return self.data
    

    def set_filter(self, jobNum):
        self.current_page = 1;     
        
        if(jobNum == ''): 
            # Reset the search to normal 
            self.total_pages = self.get_total_rows()
            self.fetch_data()
        else:  
            self.total_pages = self.get_total_rows_filter(jobNum)
            offSet = (self.current_page -1) * self.total_rows
            
            inquery = 'SELECT sampleName, jobNum, machineNum, batchName, creationDate FROM icpData WHERE sampleName LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?' 
            self.filtered_data = list(self.db.query(inquery,('%' + jobNum + '%', self.total_rows, offSet)))
            
            if(self.filtered_data): 
                self.dataChanged.emit(self.filtered_data)
                return self.filtered_data
            else: 
                return None; 
    
    def set_page(self, page_number): 
        self.current_page = page_number 
        print(f'Changed Page to {self.current_page} of {self.total_pages}')
        # offset will be updated
        self.fetch_data()
        
    def set_rows(self, index): 
        valid_rows = {0: 100, 1: 200, 2:300}

        if(index in valid_rows): 
            self.total_rows = valid_rows[index]
            self.fetch_data()
        
class DatabaseTableView(): 
    
    footerAction = pyqtSignal(int)
    
    def __init__(self, table, layout, dataModel): 
        self.table = table
        self.data_model = dataModel
        self.layout = layout 
    
        # Footer Widget setup 
        self.footerWidget = MyFooterWidget() 
        self.layout.addWidget(self.footerWidget)   
        
        # Populate the table and footer 
        self.init_table()
        self.init_footer()

        self.footerWidget.nextBtn.clicked.connect(self.handle_next_page)
        self.footerWidget.prevBtn.clicked.connect(self.handle_prev_page)
        self.footerWidget.QSpinBox.valueChanged.connect(lambda newValue: self.handle_spinBox_change(newValue))
        self.footerWidget.QComboBox.currentIndexChanged.connect(lambda newIndex: self.handle_row_filter_change(newIndex))
                
    def init_table(self): 
        # Define table columns 
        column_headers = ['Sample Number', 'Job Number', 'Machine Type', 'File Location', 'Upload Date', 'Actions'] 
        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        
        # Get the init data to populate table 
        init_data = self.data_model.fetch_data()
        self.update_table(init_data)
        
    def init_footer(self): 
        self.update_footer() 
                
    def update_table(self, results): 
        print('update_table')
        # Clear existing data 
        self.clear_table()
        
        # Bring the vertical scroll bar back to the top 
        self.table.verticalScrollBar().setValue(0)
        
        # Define table rows 
        total_results = len(results) 
        self.table.setRowCount(total_results)  
        
        for row , data in enumerate(results):
            #loops throught items in the order sql requested 
            self.table.setRowHeight(row, TABLE_ROW_HEIGHT)
            
            sampleNum = data[0] 
            machineType = data[2]
            
            for col in range(len(data)): 
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(data[col]))
                item.setTextAlignment(Qt.AlignHCenter)
                self.table.setItem(row ,col ,item) 
                
            #FIXME: open button for within this class 
            button = QPushButton("Open") 
            button.setFixedSize(100, 10)  # Set the fixed size of the button (width, height)

            button.clicked.connect(lambda _, sampleNum=sampleNum, machineType=machineType: icpOpenbutton(self, sampleNum, machineType))
            actionRow = 5 
            self.table.setCellWidget(row, actionRow, button)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.update_footer()
    
    def clear_table(self): 
        # Get the number of rows
        num_rows = self.table.rowCount()

        # Iterate through all rows (in reverse order to avoid index shifting)
        for i in range(num_rows - 1, -1, -1):
            self.table.removeRow(i)
                
    def update_footer(self): 
        footer_info = self.data_model.get_footer_info()
        print(f'Footer Info: {footer_info}')
        self.footerWidget.load_data(footer_info['current_page'], footer_info['total_rows'], footer_info['total_pages'])
        #self.layoutChanged.emit()
    
    def handle_search_text(self, text): 
        result = self.data_model.set_filter(text)
        
        if(result == None): 
            # Throw an error if result is none 
            msgBox = QMessageBox()  
            msgBox.setText("No Search Results");
            msgBox.setInformativeText("No search results for given job number");
            msgBox.setStandardButtons(QMessageBox.Ok);
            x = msgBox.exec_()  # this will show our messagebox
        
            # Returns just regular data if doesn't work 
            regular_data = self.data_model.get_data()
            self.update_table(regular_data)
    
    def handle_row_filter_change(self, index): 
        self.data_model.set_rows(index)
        
    def handle_spinBox_change(self, newValue): 
        self.data_model.set_page(newValue)
    
    def handle_next_page(self): 
        footer_info = self.data_model.get_footer_info()
        
        if((footer_info['current_page']) != footer_info['total_pages']): 
            self.data_model.set_page(footer_info['current_page']+1)
        
    def handle_prev_page(self): 
        footer_info = self.data_model.get_footer_info()
        
        if((footer_info['current_page']) != 0): 
            self.data_model.set_page(footer_info['current_page']-1)
    
    
class MyFooterWidget(QWidget): 
    def __init__(self, parent=None):
        super().__init__(parent)
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'tableFooterWidget.ui')
            
        self.ui = loadUi(file_path, self)  # Pass 'self' as parent
        
    def load_data(self, current_page, total_rows, total_pages): 
        self.current_page = current_page
        self.total_rows = total_rows
        self.total_pages = total_pages
        
        # Update the pages 
        self.QSpinBox.setValue(current_page)
        self.QSpinBox.setMaximum(total_pages)
        self.pageLabel.setText(f'of {total_pages}')
    
        valid_rows = {100: 0, 200:1, 300:2}
        
        if(total_rows in valid_rows): 
            self.QComboBox.setCurrentIndex(valid_rows[total_rows])
    
    
 
        
    

    
        

        