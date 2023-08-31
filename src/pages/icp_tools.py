from app import *
from modules.dbManager import * 
from modules.constants import *
from modules.utilities import *
from modules.excel.icpExcel import * 
from widgets.widgets import *

def icp_load_element_data(self): 
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
        
        

def icpReportHander(self, tests, totalSamples): 
    print('[FUNCTION]: icpReportHander(self, tests, totalSamples)')
    print(tests)
    print(totalSamples)
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount  
    
    initalColumns = 4; 
    totalTests = len(tests)
    additonalRows = 2 
    sampleData = {}
    unitType = []
    
    #FIXME: have something determine the lower values of the things 
    for col in range(initalColumns, totalSamples + initalColumns): 
        print(col)
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
    print(sampleData)
    print(limits)
    #print(self.reportType)
    #print(footerComment)
    print('--------')

    #load the footer comment 
    createIcpReport(self.clientInfo, self.sampleNames, self.jobNum, sampleData, tests, unitType, elementsWithLimits, limits, footerComments)

    
#TODO: have a helper change the hardness values when cal and mg values change 
#TODO: combine both the datasets;
#TODO: does this effect hardness and also what about the new values we enter in 
def icpLoader(self): 
    print('[FUNCTION]: icpLoader')
    print('***Loading ')
    
    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Value', 
        'distal factor'
    ]
    
    addtionalRows = ['pH', 'Hardness']
    initalColumns = len(columnNames)
     
    self.loadClientInfo()
    
    #check if haas data to load into the file location 
    sql1 = 'SELECT sampleName, jobNumber, data FROM icpMachineData1 where jobNumber = ? ORDER BY sampleName ASC'
    sql2 = 'SELECT sampleName, jobNumber, data FROM icpMachineData2 where jobNumber = ? ORDER By sampleName ASC' 
    
    sampleData = list(self.db.query(sql1, (self.jobNum,)))
    sampleData2 = list(self.db.query(sql2, (self.jobNum,))); 

    queryDefinedElements = 'SELECT element, symbol FROM icpElements ORDER BY element ASC' 
    queryUnits = 'SELECT element, units, lowerLimit, maxLimit FROM icpLimits WHERE reportType = ?'
    
    elements = list(self.db.query(queryDefinedElements))
    elementNames = [t[0] for t in elements]
    
    print(elementNames)
    limitResults = self.db.query(queryUnits, (self.parameter,)) 
    elementUnitValues = {t[0]: t[1] for t in limitResults} 
    
    totalRows = len(elements) + len(addtionalRows)
    
    selectedSampleNames = []
    
    for item in sampleData:
        selectedSampleNames.append(item[0])
    

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
    
    for i, element in enumerate(elements): 
        elementName = element[0]
        elementSymbol = element[1]
        
        elementNameCol = QtWidgets.QTableWidgetItem() 
        elementNameCol.setText(elementName.capitalize()) 
        self.ui.dataTable.setItem(i, 0, elementNameCol)
            
        elementSymbolCol = QtWidgets.QTableWidgetItem()
        elementSymbolCol.setText(elementSymbol.capitalize())
        self.ui.dataTable.setItem(i, 1, elementSymbolCol) 
        
        unitTypeCol = QtWidgets.QTableWidgetItem() 
        if(elementName in elementUnitValues):
            unitTypeCol.setText(elementUnitValues[elementName])
        else: 
            unitTypeCol.setText('')
            
        self.ui.dataTable.setItem(i, 2, unitTypeCol)
        
        item4 = QtWidgets.QTableWidgetItem()
        if(self.dilution == ''):
            distalFactorDefault = '1'           
            item4.setText(distalFactorDefault)
        else: 
            item4.setText(str(self.dilution))
            
        self.ui.dataTable.setItem(i, 3, item4) 
        

    for i, value in enumerate(addtionalRows): 
        postion = totalRows - i - 1; 
        elementName = QtWidgets.QTableWidgetItem()  
        elementName.setText(value)
        self.ui.dataTable.setItem(postion ,0 , elementName)

        symbolName = QtWidgets.QTableWidgetItem()
        unitValue = QtWidgets.QTableWidgetItem()
        
        if(value == 'Hardness'): 
            symbolName.setText("CaC0₃")
            unitValue.setText('ug/L')
            
            self.ui.dataTable.setItem(postion, 1, symbolName) 
            self.ui.dataTable.setItem(postion, 2, unitValue) 
        else: 
            symbolName.setText("")
            unitValue.setText('unit') 

            self.ui.dataTable.setItem(postion, 1, symbolName) 
            self.ui.dataTable.setItem(postion, 2, unitValue) 
            
    
    machine1 = {item[0]: json.loads(item[2]) for item in sampleData}
    machine2 = {item[0]: json.loads(item[2]) for item in sampleData2} 
    
    print('***Element Values')
    for i in range(len(elements)): 
        item = self.ui.dataTable.item(i, 1)
        
        if(item != None): 
            symbol = item.text()
            for j, sample in enumerate(selectedSampleNames): 
                print(f'*Sample: {sample}')
                item = QtWidgets.QTableWidgetItem(); 
                
                if sample in machine1 and symbol in machine1[sample]: 
                    machine1Val = machine1[sample][symbol] 
                    print(f'Machine 1: {symbol} {machine1Val}')
                    
                    if(is_float(machine1Val) and self.dilution != 1 ): 
                        temp = float(machine1Val)
                        temp = temp * float(self.dilution)
                        temp = round(temp, 3)
                        item.setText(str(temp))
                    else: 
                        item.setText(machine1Val)
            
                if sample in machine2 and symbol in machine2[sample]: 
                    machine2Val = machine2[sample][symbol] 
                    print(f'Machine 2: {symbol} {machine2Val}')
                    
                    if(is_float(machine2Val) and self.dilution != 1): 
                        temp = float(machine2Val)
                        temp = temp * float(self.dilution)
                        temp = round(temp, 3)
                        item.setText(str(temp))
                    else: 
                        machine2Val = round(machine2Val, 3 )
                        item.setText(str(machine2Val))
                
                sampleCol = j + len(columnNames)
                self.ui.dataTable.setItem(i,sampleCol, item)


    print('***Hardness Calculations')
    for j, sample in enumerate(selectedSampleNames):   
        print(f'*Sample: {sample}')
        item = QtWidgets.QTableWidgetItem();  
        
        if sample in machine1 and ('Ca' in machine1[sample] and 'Mg' in machine1[sample]): 
            calcium = machine1[sample]['Ca'] 
            magnesium = machine1[sample]['Mg'] 
            result = hardnessCalc(calcium, magnesium, self.dilution)

            item.setText(str(result))
            sampleCol = j + len(columnNames)
            
            self.ui.dataTable.setItem(33, sampleCol, item)

            print('calcium: ', calcium)
            print('magnesium: ', magnesium)
            print('Result: ', result)
            
    column_width = self.ui.dataTable.columnWidth(2)
    padding = 10
    total_width = column_width + padding
    self.ui.dataTable.setColumnWidth(2, total_width)    

    self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: icpReportHander(self, elementNames, totalSamples)); 

