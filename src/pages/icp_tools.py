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
    #FIXME: adjust based on the sample information
    #FIXME: adjust the limits 
    #FIXME: adjust the unit amount  
    initalColumns = 5; 
    #totalSamples = len(self.sampleNames)
    totalTests = len(tests)
    sampleData = {}
    unitType = []
    
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

    
#TODO: sidebar have a s
def icpLoader(self): 
    print('LOADING ICP STUFF')
    
    #load the given data information and column 
    columnNames = [
        'Element Name', 
        'Element symbol',
        'Unit Value', 
        'REF Value', #TODO: remove ref value
        'distal factor'
    ]
    
    addtionalRows = ['pH', 'Hardness']
    excludedElements = ['U', 'S']
    
    #setting up the table
    totalRows = len(periodic_table) + len(addtionalRows) - len(excludedElements)
    initalColumns = len(columnNames)
    
    
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
        if(self.dilution == ''):
            item4.setText('1')
        else: 
            item4.setText(str(self.dilution))
            
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
    #TODO: does this effect hardness and also what about the new values we enter in 
    
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
                    
                    if(is_float(machine1Val) and self.dilution != 1 ): 
                        print('is float bro')
                        temp = float(machine1Val)
                        temp = temp * float(self.dilution)
                        temp = round(temp, 3)
                        item.setText(str(temp))
                    else: 
                        item.setText(machine1Val)
                    #currentCell.setText(i,j, item)
                    
                
                if sample in machine2 and symbol in machine2[sample]: 
                    machine2Val = machine2[sample][symbol] 
                    
                    print(symbol, ' 2  ', machine2Val) 
                    
                    if(is_float(machine2Val) and self.dilution != 1): 
                        print('is float ')
                        temp = float(machine2Val)
                        temp = temp * float(self.dilution)
                        temp = round(temp, 3)
                        item.setText(str(temp))
                    else: 
                        machine2Val = round(machine2Val, 3 )
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
            
            result = hardnessCalc(calcium, magnesium, self.dilution)
            print('result: ', result)
            item.setText(str(result))
            self.ui.dataTable.setItem(33, j+5, item)
            
            #item.setText(str(result))
            #self.ui.dataTable.setItem(34,j+5, item)
    
    column_width = self.ui.dataTable.columnWidth(2)
    padding = 10
    total_width = column_width + padding
    self.ui.dataTable.setColumnWidth(2, total_width)    

    self.ui.dataTable.itemChanged.connect(lambda item: self.handle_item_changed(item, 'test')) 
    self.ui.createIcpReportBtn.clicked.connect(lambda: self.icpReportHander(elementNames, totalSamples)); 

