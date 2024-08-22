import json
import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import ( QDialog, QTableWidgetItem, QTreeWidgetItem)
from PyQt5.QtGui import QDoubleValidator

from modules.dbFunctions import getIcpElements2, getAllParameters, getReportNum, getIcpElementLimits, updateIcpLimits, getIcpElements 
from modules.constants import TABLE_ROW_HEIGHT 

# TODO: create a clone that holds data until user presses the save button (kind of a pain in the ass)
#******************************************************************
#    ICP Elements  Setup
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
        
#******************************************************************
#    ICP Elements Helper Functions
#******************************************************************   

def icpElementsTableSetup(self): 
    
    self.ui.icpElementTreeWidget.setColumnWidth(1, 200);
    headers = self.ui.icpElementTreeWidget.header()
    headers.setDefaultAlignment(Qt.AlignCenter)

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

        #TODO: check if the element exists
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

#TODO: finish the implementation of this 
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
        
            #TODO: need to be able to convert the string back into int 
            self.ui.lowerLimit.setText(lowerLimit)
            self.ui.upperLimit.setText(upperLimit)
            self.ui.unitType.setText(unitType)  
            self.ui.RightSideComment.setPlainText(sideComment) 
        
    
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
        
    # load the initial data 
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


#******************************************************************
#    ICP Dialog  
#****************************************************************** 

class addElementDialog(QDialog):

    addedElement = pyqtSignal(str, Element)  
    
    def __init__(self, db, reportTypes):
        super().__init__()
                
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'elementDialog.ui')
        uic.loadUi(file_path, self)
        
        self.db = db 
        self.reportTypes = reportTypes 
        print(f'Reports Types: {self.reportTypes}')
        
        # Connect the buttons 
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
            
            #TODO: fix the error completion 
            # Save to the database 
            
            # Update the Element Manager 
            
            pass; 
        else: 
            self.errorMsg.show()
            self.errorMsg.setText('ERROR')
    
    def getTableValues(self): 
        pass; 
       
       


 
        
    

    
        

        