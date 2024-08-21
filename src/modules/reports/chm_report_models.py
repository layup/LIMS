from base_logger import logger

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from modules.dbFunctions import getTestsName, getTestsInfo, getTestsTextName, getJobStatus, updateJobStatus

#******************************************************************
#    CHM Classes 
#******************************************************************

#TODO: is it easier to just scan all of the information in or just to pass the data lol 
class chemReportTestData: 
    def __init__(self, testNum, testName, textName, displayName, unitType):  
        self.testNum = testNum 
        self.testName = testName 
        self.textName = textName 
        self.displayName = displayName 
        self.unitType = unitType 

    def update_displayName(self, newName): 
        prevDisplayName = self.displayName
        self.displayName = newName
        logger.debug(f'Updating Display Name: {repr(self.textName)} from {repr(prevDisplayName)} to {repr(self.displayName)}')
         
         
#FIXME: this is too complicated, just need to have something that contains samples in a dict and their values
class chemReportSampleData: 
    def __init__(self, sampleNum, jobNum, sampleName): 
        self.sampleNum = sampleNum 
        self.jobNum = jobNum 
        self.sampleName = sampleName 
        
        # Data consists of data[testNum] = [value, recovery, unitType]
        self.data = {}
       
    def add_data(self, testNum, testValue, recovery, unitType): 
        self.data[testNum] = testValue
        logger.debug(f'{self.sampleName} ADDED {testNum}: {self.data[testNum]}')
        
        #self.data[testNum] = [testValue, recovery, unitType]
        #print(f'{self.sampleName} ADDED {testNum}: {self.data[testNum]}')
        
    #TODO: might be easier to just scan the data instead of loading it into the thing like this 
    #FIXME: Error occurs when we try to convert the data table to float when is a text 
    def update_data(self, testNum, newValue):
        
        if(testNum in self.data): 
            existing_data = self.data[testNum]
            self.data[testNum] = newValue
            logger.debug(f'{self.sampleName} UPDATED {testNum} FROM {existing_data} TO {self.data[testNum]}')
            
        else: 
            #TODO: fix this somehow so we can account for the recovery and unitType
            #self.data[testNum] = [newValue, None, None]
            self.data[testNum] = newValue
            logger.debug(f'{self.sampleName} ADDED {testNum} TO {newValue}')

    def get_data(self): 
        return self.data; 
        
class chemReportManager: 
    def __init__(self, db): 
        self.db = db 

        # chemReportSampleData Info 
        # Samples[sampleName] = chemReportSampleData.data[testNum] = [value, recovery, unitType] 
        # Samples[sampleName] = {
        #   testNum: value, 
        #}
        self.samples = {}

        # chemReportTestData Info 
        self.tests = {}
        
    def init_samples(self, sample_list):
        logger.info(f'Entering init_samples with parameters: sample_list: {sample_list}')

        testData = {}
        for test in sample_list: 
            sampleNum = test[0]
            testNum = test[1] #how to add the testNum for selection 
            testValue = test[2]
            recovery = test[3]
            unitType = test[4]
            jobNum = test[5]
            sampleName = f'{test[5]}-{test[0]}'
            
            '''  
            if(sampleName in self.samples): 
                self.samples[sampleName].add_data(testNum, testValue, recovery, unitType)
                
            else:  
                testData = chemReportSampleData(sampleNum, jobNum, sampleName)    
                testData.add_data(testNum, testValue, recovery, unitType)
                self.samples[sampleName] = testData

            '''

            # Check if sample exists. If not, create a new one.
            if sampleName not in self.samples:
                logger.debug(f'Current Sample: {sampleName} not in {self.samples}')
                self.samples[sampleName] = chemReportSampleData(sampleNum, jobNum, sampleName)

            # Add data to the existing sample
            self.samples[sampleName].add_data(testNum, testValue, recovery, unitType)
            
        #FIXME: add the other samples into this  
        
        logger.info(f'Returning self.samples: {self.samples}')

        return self.samples 

    def load_samples(self): 
        pass; 
    def load_tests(self): 
        pass; 

    def init_test(self, test_list):  
        logger.info(f'Entering init_test with parameters: test_list: {test_list}')
        
        testsInfo = {}
        testNums = []
        
        for textName in test_list: 
            logger.debug(f'Current textName: {textName}')
            testData = getTestsInfo(self.db, textName)
    
            if(testData): 
                testNum = testData[0]
                testsName = testData[1]
                textName = testData[2]
                displayName = testData[3]
                recovery = testData[4]
                unitType = testData[5]
                
                if(testNum not in testNums): 
                    testNums.append(testNum);
                
                testsInfo = chemReportTestData(testNum, testsName, textName, displayName, unitType) 
                self.tests[textName] = testsInfo 
                logger.debug(f'self.tests {textName} added the value {testsInfo}')
            else: 
                #TODO: if we cannot find the item 
                self.tests[textName] = textName
                logger.debug(f'self.tests {textName} added the value {textName}')
                
        #self.samples = testsInfo
        return self.tests 


    def getSamples(self): 
        return self.samples
    
    def getTests(self): 
        return self.tests 
    
    def print_samples(self): 
        for sampleName, sampleData in self.samples.items(): 
            print(sampleName)
            print(sampleData.data)
    
        
class chemReportView: 
    def __init__(self, table): 
        self.table = table
   
    def populateTableRow(self, row, col, alignment, editable, value): 
        logger.info(f'Entering populateTableRow in chemReportView with parameters: row: {row}, col: {col}, value: {value}')
        item = QtWidgets.QTableWidgetItem()  
        if(alignment == 1):   
            item.setTextAlignment(Qt.AlignCenter)
        
        if(editable == 0):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
          
        else: 
            item.setFlags(item.flags() | Qt.ItemIsEditable) 
            
        # Check data type and convert if necessary
        if isinstance(value, (int, float)):
            value = str(value)  # Prevent spinbox for numeric data
        
        item.setData(Qt.DisplayRole, value)
        self.table.setItem(row, col, item)     
   
    def populateTreeTests(self, testLists): 
        logger.info(f'Entering populateTreeTests in chemReportView class with parameters: testsLists: {testLists}')
        
        testNameCol = 0; 
        textNameCol = 1;
        displayNameCol = 2; 
        unitTypeCol = 3; 
        distilCol = 4; 
        recoveryValCol = 5; 
        
        self.rowNums = {}

        #TODO: should i sort this in alpha order? 
        for row, (key, value) in enumerate(testLists.items()): 
            if(isinstance(value, chemReportTestData)): 
                self.populateTableRow(row, testNameCol, 0, 0, value.testName)
                self.populateTableRow(row, textNameCol, 0, 0, value.textName)
                self.populateTableRow(row, displayNameCol, 0, 1,value.displayName)

                if(row not in self.rowNums): 
                    self.rowNums[value.testNum ] = row;  
                
            else: 
                self.populateTableRow(row, testNameCol, 0, 0, '')
                self.populateTableRow(row, textNameCol, 0, 0, value)

                self.rowNums[row] = None; 

    #FIXME: Error when loading in existing data 
    def populateTreeSamples(self, samples_info): 
        logger.info(f'Entering populateTreeSamples in chemReportView class with parameters: samples_info: {samples_info}')

        unitTypeCol = 3; 
        recoveryCol  = 5; 

        # Determine which call we are in for the sample 
        logger.debug(f'Preparing to populate tree samples... ')
        for col_index in range(5, self.table.columnCount()): 
            logger.debug(f'Col Index: {col_index}')

            
            col_name_exist = self.table.horizontalHeaderItem(col_index)
            
            if(col_name_exist):
                col_name = self.table.horizontalHeaderItem(col_index).text()
            
                if(col_name in samples_info): 
              
                    sampleInfo = samples_info[col_name]
                    sampleData = sampleInfo.get_data()
                    
                    for key, value in sampleData.items(): 
                        logger.debug(f'Col: {col_index}, key: {key}, value: {value}') 
                        if(key in self.rowNums):
                            row_index = self.rowNums[key] 
                            testVal = value

                            #FIXME: refactor all of this bullshit
                            #testVal = value[0]
                            #recoveryVal = value[1]
                            #unitTypeVal = value[2]
                            
                            #self.populateTableRow(row_index, unitTypeCol, 1, 1,unitTypeVal) 
                            #self.populateTableRow(row_index, recoveryCol, 1, 1,recoveryVal)
                            self.populateTableRow(row_index, col_index, 1, 1,testVal)

    def applyDistilFactor(self, distilFactor): 
        distilCol = 4; 
            
        for row in range(self.table.rowCount()): 
            self.populateTableRow(row, distilCol, 1, 0, distilFactor)

        #TODO: apply this onto all of the items (do previous?)
   

