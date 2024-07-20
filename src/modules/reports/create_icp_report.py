
import json 
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

from modules.dbFunctions import getReportNum, getParameterNum,getIcpReportFooter  
from modules.dialogBoxes import createdReportDialog 
from modules.excel.create_icp_excel import createIcpReport
from modules.reports.report_utils import loadClientInfo,  formatReportTable, updateSampleNames  
from modules.utilities import is_float, hardnessCalc
from widgets.widgets import SampleNameWidget 


#TODO: disable editing for certain things in the table

#******************************************************************
#    ICP Loader 
#******************************************************************
#TODO: move into dbFunctions
def getIcpMachineData(database, jobNumber): 
    query = 'SELECT sampleName, jobNum, data FROM icpData WHERE jobNum = ? ORDER BY sampleName ASC'
    
    return list(database.query(query, (jobNumber, )))
    
def getIcpLimitResults(database, parameters): 
    queryUnits = 'SELECT element, units, lowerLimit, maxLimit FROM icpLimits WHERE reportType = ?'

    limitResults = database.query(queryUnits, (parameters,))  
    elementUnitValues = {t[0]: t[1] for t in limitResults} 

    return elementUnitValues 

def getIcpElementsList2(db): 
    try: 
        query = 'SELECT * FROM icpElements ORDER BY elementName ASC'
        results = db.query(query)
        return results
    except Exception as error: 
        print(f'[ERROR]: {error}')
        return None

def getIcpLimitResults2(database, parameters):
    print('[FUNCTION]: getIcpLimitResults2(database, parameters)')
    print(parameters)
    
    try: 
        query = 'SELECT elementNum, unitType, lowerLimit, upperLimit, sideComment FROM icpLimits WHERE parameterNum = ?'
        result = database.query(query, (parameters, ))
        return {item[0]: [item[1], item[2], item[3], item[4]] for item in result}
        
    except Exception as e: 
        print(e)  
        return None 

#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: does this effect hardness and also what about the new values we enter in 
def icpReportLoader(self): 
    print('[FUNCTION]: icpLoader(self)')
   
    self.ui.createIcpReportBtn.setVisible(True)
    self.ui.createGcmsReportBtn.setVisible(False)
    self.ui.icpDataField.show()
   
    # FIXME: fix the machine getting username Information, can use a loop instead 
    loadClientInfo(self)
 
    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Type', 
        'Lower Limit', 
        'Upper Limit', 
        'distal factor'
    ]
    
    additionalRows = ['pH', 'Hardness']
     
    # FIXME: need to get redo this as well 
    #elements = getIcpElementsList(self.db) 
    elements = getIcpElementsList2(self.tempDB)
    elementNames = [t[1] for t in elements]
    
    print(f'Elements: {elements}')
    
    sampleData = getIcpMachineData(self.tempDB, self.jobNum)

    #TODO: change database later so we have just one database 
    reportNum = getReportNum(self.tempDB, self.parameter)[0][0]
    print(f'Parameter: {reportNum}')
    
    #TODO: add a try-except block here 
    
    #elementUnitValues = getIcpLimitResults(self.db, self.parameter); 
    elementUnitValues = getIcpLimitResults2(self.tempDB, reportNum)

    selectedSampleNames = []
    
    for item in sampleData:
        sampleName = item[0]
        if(sampleName not in selectedSampleNames): 
            selectedSampleNames.append(item[0])

    machineData = {item[0]: json.loads(item[2]) for item in sampleData}

    #print(f'Element Names: {elementNames}')
    print(f'Element Unit Values: {elementUnitValues}')
    print('SelectedSampleItems: ', selectedSampleNames)    
    
    dataTable = self.ui.dataTable
    colCount = len(columnNames) + len(selectedSampleNames)
    totalRows = len(elements) + len(additionalRows)
    totalSamples = len(selectedSampleNames)    
    
    # Connect Signals 
    
    #dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHander(self, elements, elementUnitValues, totalSamples, reportNum));     

    # Format and initialize the tables 
    icpInitTable(self, dataTable, colCount, totalRows, selectedSampleNames, columnNames)
    
    # Populate the sample table information 
    icpPopulateSamplesSection(self, selectedSampleNames)
    
    # Populate Hardness and pH 
    icpPopulateAdditonalRows(self, totalRows, additionalRows)
    
    # populate the table with column and smaple info 
    icpPopulateTable(self, elements, elementUnitValues)
    
    # load the tables elemental machine info and  hardness calculations 
    icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames)
            

def icpInitTable(self, table, colCount, totalRows, selectedSampleNames, columnNames): 
    print(f'[FUNCTION]: icpInitTable(self, table, colCount, totalRows, selectedSampleNames, columnNames)')

    formatReportTable(table, totalRows, colCount)

    column_width = self.ui.dataTable.columnWidth(2)
    padding = 10
    total_width = column_width + padding
    table.setColumnWidth(2, total_width)    
    
    # initialise the column names
    for i, name in enumerate(columnNames): 
        item = QtWidgets.QTableWidgetItem(name)
        table.setHorizontalHeaderItem(i, item)
    
    # Set the sample names in the column (after)
    for i , (key) in enumerate(selectedSampleNames, start=len(columnNames)):
        item = QtWidgets.QTableWidgetItem(key)
        table.setHorizontalHeaderItem(i, item)

def icpPopulateSamplesSection(self, selectedSampleNames):
    print(f'[FUNCTION]: icpPopulateSamples(self, selectedSampleNames)')
        
    # Create the sample names in the client info section        
    for i, (key, value) in enumerate(self.sampleNames.items()):
        
        if(key in selectedSampleNames):
            print('active:', key)
            sampleItem = SampleNameWidget(key, value)
            self.ui.samplesContainerLayout.addWidget(sampleItem)
            sampleItem.edit.textChanged.connect(lambda textChange, key = key: updateSampleNames(self.sampleNames, textChange, key))

    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    self.ui.samplesContainerLayout.addItem(spacer) 

def icpPopulateTable(self, elements, elementUnitValues): 
    print('[FUNCTION]:icpPopulateTable(self, elements, elementUnitValues)')
    
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
    item = QtWidgets.QTableWidgetItem()  
    if(alignment == 1):   
        item.setTextAlignment(Qt.AlignCenter)
    
    if(value):
        item.setData(Qt.DisplayRole, value)
        tableWidget.setItem(row, col, item)
        
    return 

def icpPopulateAdditonalRows(self, totalRows, additionalRows ): 
    print('[FUNCTION]:icpPopulateAdditonalRows(self, totalRows, additionalRows)')
    
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

def icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames): 
    #print('[FUNCTION]: icpLoadMachineData(self, elements, selectedSampleNames, machineData, columnNames)')
    
    tableWidget = self.ui.dataTable 
    hardnessRow = 33
     
    #print('***Element Values')
    for i in range(len(elements)): 
        item = self.ui.dataTable.item(i, 1) 
        if(item != None): 
            symbol = item.text()
            for j, sample in enumerate(selectedSampleNames): 

                if sample in machineData and symbol in machineData[sample]: 
                    dilutionValue = dilutionConversion(machineData, sample, symbol, self.dilution)
                    
                    #print(f'Sample        : {sample} {symbol}')  
                    #print(f'Machine  Value: {machineData[sample][symbol]}')
                    #print(f'Dilution Value: {dilutionValue}');
                            
                    sampleCol = j + len(columnNames)
                    icpPopulateRow(tableWidget, i, sampleCol, 1, dilutionValue)
                else:
                    pass;  
                    #print(f'Sample        : {sample} {symbol}')  

    #print('***Hardness Calculations')
    for j, sample in enumerate(selectedSampleNames):   
        if sample in machineData and ('Ca' in machineData[sample] and 'Mg' in machineData[sample]): 
            calcium = machineData[sample]['Ca'] 
            magnesium = machineData[sample]['Mg'] 
            result = hardnessCalc(calcium, magnesium, self.dilution)

            sampleCol = j + len(columnNames)
            
            #print(f'*Sample: {sample}')
            #print('calcium: ', calcium)
            #print('magnesium: ', magnesium)
            #print('Result: ', result)

            icpPopulateRow(tableWidget, hardnessRow, sampleCol, 1, result)

def dilutionConversion(machineList, sample, symbol, dilution):
    print(f'[FUNCTION]: dilutionConversion(machineList, {sample}, {symbol}, {dilution})')
   
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
            print('[ERROR]: VALUE ERROR')
            return machineValue

#******************************************************************
#    ICP Report Handler Function  
#******************************************************************

@pyqtSlot()  
def icpReportHander(self, elements, limits, totalSamples, reportNum): 
    print('[FUNCTION]: icpReportHander(self, tests, totalSamples)')
    print(f'Total Samples: {totalSamples}') 
    
    elements = {item[0]: [item[1], item[2]]for item in elements}
    print('*Elements')
    for key, value in elements.items():
        print(key, value) 
        
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount  
    
    initalColumns = 6; 
    totalTests = len(elements)
    additonalRows = 2 
    sampleData = {}
    unitType = []
    elementNames =  [item[0] for item in elements.values()]
    
    #FIXME: have something determine the lower values of the things 
    for col in range(initalColumns, totalSamples + initalColumns): 
        #print(col)
        currentJob = self.ui.dataTable.horizontalHeaderItem(col).text()
        jobValues = []
        for row in range(totalTests + additonalRows): 
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
            print(f'[ERROR]: {e}') 
            unitType.append('')
        
    footerComments = icpGenerateFooter(self.tempDB, self.parameter)

    #print(f'Sample Data: {sampleData}')
    print('*Limits')
    for key, value in limits.items(): 
        print(key, value)
        
    print('*Sample Data')
    for key, value in sampleData.items(): 
        print(key, value)
    
    print(f'Unit Type: {unitType}')
    print(f'Footer: {footerComments}')
    print()
    print('------------------------------------------------------')

    
    #LAZY FIX 
    limitQuery2 = 'SELECT elementNum, lowerLimit, upperLimit, sideComment, unitType FROM icpLimits WHERE parameterNum = ?'
    limits = self.tempDB.query(limitQuery2, (reportNum,))  
    limits = [[elements[item[0]][0], item[1], item[2],item[3], item[4]] for item in limits]
    
    
    #elementNames = elementsWithLimits 
    
    #load the footer comment 
    #TODO: can just pass the self and remove some of the unessary info 
    createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, elementNames, unitType, elementNames, limits, footerComments)
    #createIcpReport2(self.clientInfo, self.samplenames, self.jobNum, sampleData, elements, limitsInfo, footer)

    #TODO: if successful update the database set the status = 1 

    createdReportDialog('test')

def icpGenerateFooter(database, paramenterName):
    print('[FUNCTION]: icpGenerateFooter()')
    paramNum = getParameterNum(database, paramenterName)
    footerComment = getIcpReportFooter(database, paramNum)
    print(footerComment)
    
    if(footerComment): 
        #footerList = '\n'.join(footerComment)
        footerComment = footerComment.split('\n')  
        print(footerComment)
    
        return footerComment
    else: 
        return ''


class icpManager: 
    pass; 