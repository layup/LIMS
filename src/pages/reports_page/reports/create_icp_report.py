import json 
from base_logger import logger
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot

from modules.dbFunctions import ( 
    getReportNum, getParameterNum,getIcpReportFooter, getJobStatus, updateJobStatus, 
    getIcpElementsList, getIcpLimitResults, getIcpMachineData
)
from modules.widgets.dialogs import createdReportDialog 
from modules.utils.logic_utils import is_float, hardnessCalc
from modules.widgets.dialogs import createdReportDialog 

from pages.reports_page.excel.create_icp_excel import createIcpReport
from pages.reports_page.reports.report_utils import (
    loadClientInfo,  formatReportTable, handleTableChange, populateTableRow, 
    disconnect_all_slots, populateSamplesContainer, updateReport, createExcelErrorCheck,
    retrieveFooterComment, retrieveAuthorInfo
) 


#TODO: disable editing for certain things in the table
#TODO: add the items to the table even if there are no loaded files for the ICP ones
#TODO: when there are not ICP file included I should so something that will edit the fuel
#******************************************************************
#    ICP Loader 
#******************************************************************

editable_row = 1; 
non_editable_row = 0; 
center_align = 1; 
left_align = 0 
        
#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: does this effect hardness and also what about the new values we enter in 
def icpReportLoader(self): 
    self.logger.info('Entering icpLoader')
       
    self.logger.info('Preparing to load client info')
    loadClientInfo(self)
 
    # FIXME: need to get redo this as well 
    elements = getIcpElementsList(self.tempDB)
    elementNames = [t[1] for t in elements]
    
    sampleData = getIcpMachineData(self.tempDB, self.jobNum)
    reportNum = getReportNum(self.tempDB, self.parameter)
    elementUnitValues = getIcpLimitResults(self.tempDB, reportNum)

    #TODO: demo what happens when have both machine types 
    databaseSampleNames = list({item[0] for item in sampleData})    
    machineData = {item[0]: json.loads(item[2]) for item in sampleData}

    selectedSampleNames = list(set(databaseSampleNames + icpSampleNameCheck(self.sampleTests)))

    self.logger.debug(f'ICP Report Loader Variables')
    self.logger.debug(f'*Elements: {elements}')
    self.logger.debug(f'*Parameter: {reportNum}')
    self.logger.debug(f'*sampleData: {sampleData}')
    self.logger.debug(f'*elementUnitValues: {elementUnitValues}')
    self.logger.debug(f'*SelectedSampleItems: {selectedSampleNames}' )    
    
    dataTable = self.ui.dataTable
    totalElements = len(elements)  
    totalSamples = len(selectedSampleNames)    
    
    # Disconnect Signals 
    disconnect_all_slots(self.ui.dataTable)
    disconnect_all_slots(self.ui.createIcpReportBtn)
    
    # Preparing to format and initialize the table
    icpInitTable(self, dataTable, totalElements, selectedSampleNames)
    
    # Preparing to populate the samples information
    populateSamplesContainer(self.ui.samplesContainerLayout_2, self.sampleNames)
    
    # Preparing to populate the table with column and sample info
    icpPopulateTableElements(self, elements, elementUnitValues)
    
    # Preparing to load the table with elemental machine information and do the hardness calculations
    icpLoadMachineData(self, elements, selectedSampleNames, machineData) 

    # Connect Signals 
    self.ui.dataTable.itemChanged.connect(lambda item: handleTableChange(self, item)) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHandler(self, elements, elementUnitValues, totalSamples, reportNum));     

            
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
        
        editable_row = 1; 
        non_editable_row = 0; 
        center_align = 1; 
        left_align = 0 
        
        if(self.dilution == ''):
            distalFactorDefault = 1        
        else:
            distalFactorDefault = self.dilution 
             
        populateTableRow(tableWidget, i, 0, left_align, non_editable_row, elementName)
        populateTableRow(tableWidget, i, 1, center_align, non_editable_row ,elementSymbol)
        populateTableRow(tableWidget, i, 5, center_align, non_editable_row, distalFactorDefault)

        # Set the limits
        if(elementNum in elementUnitValues): 
            unitType   = elementUnitValues[elementNum][0]
            lowerLimit = elementUnitValues[elementNum][1]
            upperLimit = elementUnitValues[elementNum][2]
            
            populateTableRow(tableWidget, i, 2, center_align, non_editable_row, unitType)
            populateTableRow(tableWidget, i, 3, center_align, non_editable_row, lowerLimit)
            populateTableRow(tableWidget, i, 4, center_align, non_editable_row, upperLimit)
           
   

def icpPopulateAdditionalRows(self, totalRows, additionalRows ): 
    self.logger.info(f'Entering icpPopulateAdditionalRows with parameters: totalRows: {repr(totalRows)}, additionalRows: {repr(additionalRows)}')
    
    unitCol = 2
    tableWidget = self.ui.dataTable
    
    for i, elementName in enumerate(additionalRows): 
        position = totalRows - i - 1; 
        populateTableRow(tableWidget, position, 0, left_align, editable_row, elementName)
        
        if(elementName == 'Hardness'): 
            symbolName = "CaC0₃"
            unitType = "ug/L"
            
            populateTableRow(tableWidget, position, 1, center_align, editable_row, symbolName) 
            populateTableRow(tableWidget, position, unitCol, center_align, editable_row, unitType) 
        else: 
            symbolName = ""
            unitType = "unit"
        
            populateTableRow(tableWidget, position, 1, center_align, editable_row, symbolName) 
            populateTableRow(tableWidget, position, unitCol, center_align, editable_row, unitType) 

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
                    populateTableRow(tableWidget, i, sampleCol, center_align, non_editable_row, dilutionValue)
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

            populateTableRow(tableWidget, hardnessRow, sampleCol, center_align, editable_row, result)

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
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount 
    
    self.logger.info('Entering icpReportHandler with parameters: ')
    self.logger.info(f'reportNum    : {reportNum}')
    self.logger.info(f'totalSamples : {totalSamples}') 
    self.logger.info(f'elements     : {elements}') 
    self.logger.info(f'limits       : {limits}') 

    totalTests = len(elements)

    elements = {item[0]: [item[1], item[2]]for item in elements}
    elementNames =  [item[0] for item in elements.values()]

    if(createExcelErrorCheck(self)): 
        return 
    
    # Format and retrieve the necessary information to create excel reports 
    authorsInfo = retrieveAuthorInfo(self, self.ui.authorOneDropDown.currentText(), self.ui.authorTwoDropDown.currentText())
    footerComment = retrieveFooterComment(self, 'ICP', self.parameter)
    sampleData = retrieveSampleData(self, totalTests, totalSamples)
    unitType = retrieveUnitType(self, totalTests)
    limits = retrieveLimits(self, elements, reportNum) 
    
    try: 
        self.logger.info('Preparing to create ICP Report')
        filePath, fileName = createIcpReport(self.clientInfo, self.sampleNames, authorsInfo, self.jobNum, sampleData, elementNames, unitType, elementNames, limits, footerComment)
        createdReportDialog(self, fileName)
        
        jobCreatedNum = 1 
        self.logger.info(f'ICP Report Creation Successful: jobCreated: {jobCreatedNum}')  
            
    except Exception as e: 
        print(e)
        
        jobCreatedNum = 0; 
        self.logger.warning(f'CHM Report Creation Failed: jobCreated: {jobCreatedNum}')
        

    if(jobCreatedNum == 1): 
        updateReport(self.ui.statusHeaderLabel, self.tempDB, self.jobNum, self.reportNum)


def retrieveLimits(self, elements, reportNum): 
    #LAZY FIX 
    limitQuery2 = 'SELECT elementNum, lowerLimit, upperLimit, sideComment, unitType FROM icpLimits WHERE parameterNum = ?'
    limits = self.tempDB.query(limitQuery2, (reportNum,))  
    limits = [[elements[item[0]][0], item[1], item[2],item[3], item[4]] for item in limits]

    return limits

def retrieveSampleData(self, totalTests, totalSamples):
    self.logger.info('Entering retrieveSampleData with parameters: totalTests: {totalTests}, totalSamples: {totalSamples}')
    
    initialColumns = 6; 
    totalAdditionalRows = 2 
    
    sampleData = {}
     
    #FIXME: have something determine the lower values of the things 
    
    for col in range(initialColumns, totalSamples + initialColumns): 
        currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
        jobValues = []
        for row in range(totalTests + totalAdditionalRows): 
            try: 
                currentItem = self.ui.dataTable.item(row, col).text()
                jobValues.append(currentItem)
            except: 
                jobValues.append('ND')
                
                
        sampleData[currentJob] = jobValues
        self.logger.debug(f'Current Job: {currentJob}, Data: {sampleData[currentJob]}')

    return sampleData

def retrieveUnitType(self, totalTests): 
    self.logger.info('Entering retrieveUnitType with parameters: totalTests: {totalTests}')

    unitType = []
    
    for i in range(totalTests): 
        try: 
            currentUnitType = self.ui.dataTable.item(i, 2)
            if(currentUnitType): 
                unitType.append(currentUnitType.text())
            
        except Exception as e: 
            self.logger.error(f'{e}')
            unitType.append('')

    self.logger.debug(f'Returning UnitType: {unitType}')
    return unitType
