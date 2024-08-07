import json 
from base_logger import logger
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)

from PyQt5.QtGui import QIntValidator, QDoubleValidator, QKeyEvent 

from modules.constants import REPORT_STATUS 
from modules.dbFunctions import ( 
            getReportNum, getParameterNum,getIcpReportFooter, getJobStatus, updateJobStatus, 
            getIcpElementsList, getIcpLimitResults, getIcpMachineData
)
from modules.dialogBoxes import createdReportDialog 
from modules.excel.create_icp_excel import createIcpReport
from modules.reports.report_utils import loadClientInfo,  formatReportTable, updateSampleNames, disconnect_all_slots, populateSamplesContainer, updateReport 
from modules.utilities import is_float, hardnessCalc
from widgets.widgets import SampleNameWidget 


#TODO: disable editing for certain things in the table
#TODO: add the items to the table even if there are no loaded files for the ICP ones
#TODO: when there are not ICP file included I should so something that will edit the fuel
#******************************************************************
#    ICP Loader 
#******************************************************************


#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: does this effect hardness and also what about the new values we enter in 
def icpReportLoader(self): 
    self.logger.info('Entering icpLoader')
       
    # FIXME: fix the machine getting username Information, can use a loop instead 
    self.logger.info('Preparing to load client info')
    loadClientInfo(self)
 
    # FIXME: need to get redo this as well 
    elements = getIcpElementsList(self.tempDB)
    elementNames = [t[1] for t in elements]
    
    sampleData = getIcpMachineData(self.tempDB, self.jobNum)
    reportNum = getReportNum(self.tempDB, self.parameter)
    elementUnitValues = getIcpLimitResults(self.tempDB, reportNum)

    self.logger.debug(f'Elements: {elements}')
    self.logger.debug(f'Parameter: {reportNum}')
    self.logger.debug(f'sampleData: {sampleData}')

    #TODO: demo what happens when have both machine types 
    databaseSampleNames = list({item[0] for item in sampleData})    
    machineData = {item[0]: json.loads(item[2]) for item in sampleData}

    selectedSampleNames = list(set(databaseSampleNames + icpSampleNameCheck(self.sampleTests)))

    self.logger.debug(f'Element Unit Values: {elementUnitValues}')
    self.logger.debug(f'SelectedSampleItems: {selectedSampleNames}' )    
    
    dataTable = self.ui.dataTable
    totalElements = len(elements)  
    totalSamples = len(selectedSampleNames)    
    
    # Connect Signals 
    #dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    disconnect_all_slots(self.ui.createIcpReportBtn)
    
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHandler(self, elements, elementUnitValues, totalSamples, reportNum));     

    self.logger.info('Preparing to format and initialize the table')
    icpInitTable(self, dataTable, totalElements, selectedSampleNames)
    
    self.logger.info('Preparing to populate the samples information')
    populateSamplesContainer(self.ui.samplesContainerLayout_2, self.sampleNames)
    
    self.logger.info('Preparing to populate the table with column and sample info')
    icpPopulateTableElements(self, elements, elementUnitValues)
    
    self.logger.info('Preparing to load the table with elemental machine information and do the hardness calculations')
    icpLoadMachineData(self, elements, selectedSampleNames, machineData) 
            
def icpSampleNameCheck(sampleTests): 
    logger.info(f'Entering icpSampleNameCheck with parameter: sampleData: {sampleTests}')
    
    sampleNames = []
    
    for sampleName, sampleTestsList in sampleTests.items(): 
        for sample in sampleTestsList:
            if('icp' in sample.lower()): 
                sampleNames.append(sampleName)
                break
             
        
    logger.debug(f'Returning sampleNames: {sampleNames}')
    return sampleNames 
 
def enableMachineChecks(self, machine1, machine2): 
    pass; 

def icpInitTable(self, table, totalElements, selectedSampleNames ): 
    self.logger.info('Entering icpInitTable with parameters:')
    self.logger.info(f'totalElements        : {repr(totalElements)}')
    self.logger.info(f'selectedSampleNames  : {repr(selectedSampleNames)}')

    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Type', 
        'Lower Limit', 
        'Upper Limit', 
        'distal factor'
    ]
    
    additionalRows = [
        'pH', 
        'Hardness'
    ]
    
    colCount = len(columnNames) + len(selectedSampleNames)
    totalRows = totalElements + len(additionalRows)
    
    self.logger.info('Preparing to format report table')
    formatReportTable(table, totalRows, colCount)

    column_width = table.columnWidth(2)
    padding = 10
    total_width = column_width + padding

    table.setColumnWidth(2, total_width)    
    
    self.logger.info('Preparing to initialise the column names')
    for i, name in enumerate(columnNames): 
        item = QtWidgets.QTableWidgetItem(name)
        table.setHorizontalHeaderItem(i, item)
        
    self.logger.info('Preparing to set the sample names in the column')
    for i , (key) in enumerate(selectedSampleNames, start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(key)
        table.setHorizontalHeaderItem(i, item)
        
    self.logger.info('Preparing to populate the hardness and pH section of the table')
    icpPopulateAdditionalRows(self, totalRows, additionalRows)
    

def icpPopulateTableElements(self, elements, elementUnitValues): 
    self.logger.info(f'Entering icpPopulateTableElements with parameters: elements: {elements}, elementUnitValues:{elementUnitValues}')
    
    tableWidget = self.ui.dataTable

    for i, element in enumerate(elements): 
        elementNum    = element[0]
        elementName   = element[1].capitalize()
        elementSymbol = element[2].capitalize()
        
        if(self.dilution == ''):
            distalFactorDefault = 1        
        else:
            distalFactorDefault = self.dilution 
           
        icpPopulateRow(tableWidget, i, 0, 0, elementName)
        icpPopulateRow(tableWidget, i, 1, 1, elementSymbol)
        icpPopulateRow(tableWidget, i, 5, 1, distalFactorDefault)

        # Set the limits
        if(elementNum in elementUnitValues): 
            unitType   = elementUnitValues[elementNum][0]
            lowerLimit = elementUnitValues[elementNum][1]
            upperLimit = elementUnitValues[elementNum][2]
            
            icpPopulateRow(tableWidget, i, 2, 1, unitType)
            icpPopulateRow(tableWidget, i, 3, 1,  lowerLimit)
            icpPopulateRow(tableWidget, i, 4, 1, upperLimit)
           
def icpPopulateRow(tableWidget, row, col, alignment, value): 
    logger.info('Entering icpPopulateRow with parameters: row: {row}, col: {col}, value: {value}')
    
    item = QtWidgets.QTableWidgetItem()  
    if(alignment == 1):   
        item.setTextAlignment(Qt.AlignCenter)
    
    if(value):
        item.setData(Qt.DisplayRole, value)
        tableWidget.setItem(row, col, item)
    return 

def icpPopulateAdditionalRows(self, totalRows, additionalRows ): 
    self.logger.info(f'Entering icpPopulateAdditionalRows with parameters: totalRows: {repr(totalRows)}, additionalRows: {repr(additionalRows)}')
    
    unitCol = 2
    tableWidget = self.ui.dataTable
    
    for i, elementName in enumerate(additionalRows): 
        position = totalRows - i - 1; 
        icpPopulateRow(tableWidget, position, 0, 0, elementName)
        
        if(elementName == 'Hardness'): 
            symbolName = "CaC0₃"
            unitType = "ug/L"
            
            icpPopulateRow(tableWidget, position, 1, 1, symbolName) 
            icpPopulateRow(tableWidget, position, unitCol, 1, unitType) 
        else: 
            symbolName = ""
            unitType = "unit"
        
            icpPopulateRow(tableWidget, position, 1, 1, symbolName) 
            icpPopulateRow(tableWidget, position, unitCol, 1, unitType) 

def icpLoadMachineData(self, elements, selectedSampleNames, machineData): 
    self.logger.info('Entering icpLoadMachineData with parameters')
    
    tableWidget = self.ui.dataTable 
    hardnessRow = 33
    initialColumnLength = 6
     
    self.logger.info('Beginning Element Value Calculations')
    for i in range(len(elements)): 
        item = self.ui.dataTable.item(i, 1) 
        if(item != None): 
            symbol = item.text()
            for j, sample in enumerate(selectedSampleNames): 
                if sample in machineData and symbol in machineData[sample]: 
                    dilutionValue = dilutionConversion(machineData, sample, symbol, self.dilution)
                    
                    self.logger.debug(f'Sample: {sample} {symbol} | Machine Value: {machineData[sample][symbol]} | Dilution: {dilutionValue}')
                             
                    sampleCol = j + initialColumnLength 
                    icpPopulateRow(tableWidget, i, sampleCol, 1, dilutionValue)
                else:
                    self.logger.debug(f'Sample: {sample} {symbol} Not in machine database ')
                    pass;  

    self.logger.info('Beginning Hardness Calculations')
    for j, sample in enumerate(selectedSampleNames):   
        if sample in machineData and ('Ca' in machineData[sample] and 'Mg' in machineData[sample]): 
            calcium = machineData[sample]['Ca'] 
            magnesium = machineData[sample]['Mg'] 
            result = hardnessCalc(calcium, magnesium, self.dilution)

            sampleCol = j + initialColumnLength 
            
            self.logger.debug(f'Sample: {sample}, calcium: {calcium}, magnesium: {magnesium}, result: {result}')

            icpPopulateRow(tableWidget, hardnessRow, sampleCol, 1, result)

def dilutionConversion(machineList, sample, symbol, dilution):
    logger.info(f'Entering dilutionConversion with parameters: sample: {sample}, symbol: {symbol}, dilution: {dilution}')
   
    machineValue = machineList[sample][symbol]
    
    if(is_float(machineValue) and dilution != 1): 
        newVal = float(machineValue)
        newVal = newVal * float(dilution)
        newVal = round(newVal, 3)
        return newVal
        
    else:         
        try:
            machineValue = float(machineValue)  # Convert to float first
            machineValue = round(machineValue, 3)
            return machineValue
        except ValueError:
            logger.warning('Could not convert to float with machine value: {machineValue}')
            return machineValue

#******************************************************************
#    ICP Report Handler Function  
#******************************************************************

@pyqtSlot()  
def icpReportHandler(self, elements, limits, totalSamples, reportNum): 
    self.logger.info('Entering icpReportHandler with parameters: ')
    self.logger.info(f'reportNum   : {reportNum}')
    self.logger.info(f'totalSamples: {totalSamples}') 
    
    elements = {item[0]: [item[1], item[2]]for item in elements}
    
    self.logger.info('*Elements') 
    for key, value in elements.items():
        self.logger.info(key, value) 
        
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount  
    
    initialColumns = 6; 
    totalTests = len(elements)
    totalAdditionalRows = 2 
    sampleData = {}
    unitType = []
    elementNames =  [item[0] for item in elements.values()]
    
    #FIXME: have something determine the lower values of the things 
    for col in range(initialColumns, totalSamples + initialColumns): 
        #print(col)
        currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
        jobValues = []
        for row in range(totalTests + totalAdditionalRows): 
            try: 
                currentItem = self.ui.dataTable.item(row, col).text()
                jobValues.append(currentItem)
            except: 
                jobValues.append('ND')
                
                
        sampleData[currentJob] = jobValues
        #print(currentJob, sampleData[currentJob])
        
    for i in range(totalTests): 
        try: 
            currentUnitType = self.ui.dataTable.item(i, 2)
            if(currentUnitType): 
                unitType.append(currentUnitType.text())
            
        except Exception as e: 
            self.logger.error(f'{e}')
            unitType.append('')
    
 
    self.logger.debug('*Limits')
    for key, value in limits.items(): 
        self.logger.debug(key, value)
        
    self.logger.debug('*Sample Data')
    for key, value in sampleData.items(): 
        self.logger.debug(key, value)
    
    self.logger.debug(f'Unit Type: {unitType}')

    #LAZY FIX 
    limitQuery2 = 'SELECT elementNum, lowerLimit, upperLimit, sideComment, unitType FROM icpLimits WHERE parameterNum = ?'
    limits = self.tempDB.query(limitQuery2, (reportNum,))  
    limits = [[elements[item[0]][0], item[1], item[2],item[3], item[4]] for item in limits]
    
    #elementNames = elementsWithLimits 
    
    #load the footer comment 
    footerComments = icpGenerateFooterComment(self.tempDB, self.parameter)
    
    self.logger.info('Preparing to create ICP Report')
    try: 
        filePath, fileName = createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, elementNames, unitType, elementNames, limits, footerComments)
        createdReportDialog(self, fileName)
        
        jobCreatedNum = 1 
        self.logger.info(f'ICP Report Creation Successful: jobCreated: {jobCreatedNum}')  
            
    except: 
        #TODO: debating purring the error here so it's more clean 
        jobCreatedNum = 0; 
        self.logger.warning(f'CHM Report Creation Failed: jobCreated: {jobCreatedNum}')
        
    if(jobCreatedNum == 1): 
        updateReport(self.ui.statusHeaderLabel, self.tempDB, self.jobNum, self.reportNum)

def icpGenerateFooterComment(database, parameterName):
    logger.info('Entering icpGenerateFooterComment with parameter: parameterName: {parameterName}')
    paramNum = getParameterNum(database, parameterName)
    footerComment = getIcpReportFooter(database, paramNum)
    
    logger.debug(f'paramNum: {paramNum} footerComment: {footerComment}') 
    
    if(footerComment): 
        #footerList = '\n'.join(footerComment)
        footerComment = footerComment.split('\n')  
    
        return footerComment
    else: 
        return ''

#******************************************************************
#    ICP Model-View-ViewModel  
#******************************************************************

# Manages all of the data 
class icpModel: 
    pass; 

# Control the data passed to Model and View
class icpViewModel: 
    pass; 

# Control the table view of the ICP data
class icpView: 
    pass; 

