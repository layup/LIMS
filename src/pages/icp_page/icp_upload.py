import csv
import os 
import re
import numpy
import json
import openpyxl
import string

from base_logger import logger
from copy import copy
from datetime import date

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFileDialog, QPushButton, QTableWidgetItem, 
    QTableWidget , QVBoxLayout, QDialog,  QSizePolicy, QSizeGrip, QGraphicsDropShadowEffect 
)

from modules.utils.pickle_utils import load_pickle

    
def icp_upload(filePath, db): 
    logger.info('Entering icp_upload with filePath: {filePath}')

    logger.info('Scanning File... ')
    if(filePath.endswith('.txt')):
        icpMethod1(filePath, db)
    elif(filePath.endswith('.xlsx')):
        icpMethod2(filePath, db)
    else: 
        print("Not valid file type")
    return; 
    
#TODO: sort by name  
#read line by line and just add the line instead 
#FIXME: tracking the icpData is wrong as well 
#TODO: insert try catch block 
def icpMethod1(filePath, db): 
    logger.info('Entering icpMethod1 txt filetype detected')

    file1 = open(filePath, 'r')
    baseName = os.path.basename(filePath)
    fname = baseName.split('.txt')[0]
    #remove extension 

    logger.debug('FileName: ', fname)
    
    Lines = file1.readlines()
    
    startingLine = 'Date Time Label Element Label (nm) Conc %RSD Unadjusted Conc Intensity %RSD' 
    headers = ['Sample', 'Analyze', 'Element', 'HT', ' ', 'units', 'rep', ' ', ' '] 
    
    startingPosition = []
    endPosition = []
    count = 0
    
    # Strips the newline character
    for line in Lines:
        
        #print("Line{}: {}".format(count, line.strip()))
        if(line.strip() == startingLine):
            startingPosition.append(count)
            
        if(re.search('([1-9]|[1-9][0-9]) of ([1-9]|[1-9][0-9])$', line)): 
            endPosition.append(count)

        count += 1

    #update headers 
    headerUpdate = Lines[startingPosition[0] + 1]; 
    headerUpdate = headerUpdate.split()
    headers[7] = headerUpdate[0]
    headers[8] = headerUpdate[1]

    newName = fname + '.csv'
    loadPath = load_pickle('data.pickle') 
    newPath = os.path.join(copy(loadPath['ispDataUploadPath']), newName) 
     
    logger.info('Writing CSV File: {}'.format(newPath))
    
    f = open(newPath, 'w')
    writer = csv.writer(f)
    writer.writerow(headers)
    
    spiltLengths = []
    
    jobNumbers = []
    jobData = {}
    
    elementData = {}
    currentJob = ''

    sampleNumbers = []
    
    #TODO: missing the last row 
    for start in startingPosition: 
        running = True; 
        counter = 1; 

        while(running): 

            currentLine = Lines[start + counter]
            
            if(re.search('([1-9]|[1-9][0-9]) of ([1-9]|[1-9][0-9])$', currentLine)): 
                break; 
            
            counter += 1; 

            splitLine = currentLine.split()
            spiltLengths.append(len(splitLine))

            if(re.search('\d{6}-\d{1,2}', splitLine[2])):
                temp = []
                temp.append(splitLine[2])
                temp.append(1)
                temp.append(splitLine[3])
                temp.append(1)
                temp.append(splitLine[6])
                temp.append('mg/L')
                temp.append(1)
                temp.append(splitLine[0])
                temp.append(splitLine[1])

                sampleNumbers.append([splitLine[2], start+counter, splitLine[3], splitLine[6]])

                if(currentJob == ''):
                    currentJob = splitLine[2]
  
                elif(currentJob != splitLine[2]): 
                    jobData[currentJob] = elementData   
                    elementData = {}
                    currentJob = splitLine[2]

                elementData[splitLine[3]] = splitLine[6]
    
                jobNumber = splitLine[2].split('-')[0]
                if(jobNumber not in jobNumbers):
                    jobNumbers.append(jobNumber)
                    
                if(temp): 
                    writer.writerow(temp)

        jobData[currentJob] = elementData   

    spiltLengths = numpy.array(spiltLengths)
    unique, counts = numpy.unique(spiltLengths, return_counts=True)

    f.close()
    file1.close()
    
    #TODO: factor in a way to show all the things and the lines where duplicates are 
    logger.debug(f'SampleNumbers: {sampleNumbers}')
    logger.debug(f'JobData: {jobData}')

    save = viewIcpTable(filePath, sampleNumbers, 1) 
    logger.info(f"Save Status: {repr(save)}")

    #save to database 
    if(save): 
        for (key, value) in jobData.items():             
            jobNum = key.split('-')[0]
            todayDate = date.today()
            
            tempData = json.dumps(value)
            if(key): 
                sql = 'INSERT OR REPLACE INTO icpData values(?, ?, ?, ?, ?, 1)'
                db.execute(sql, (key,jobNum,baseName, tempData, todayDate))
                db.commit()
                
        return jobNumber,jobData
    else: 
        return False; 

    
#scans thought all the text files and finds all the different sample types and the ISP and CHM files     
#TODO: insert try catch block 
def icpMethod2(filePath, db): 
    logger.info('Entering icpMethod1 xlsx filetype detected')
    wb = openpyxl.load_workbook(filePath)
    sheets = wb.sheetnames 
    
    baseName = os.path.basename(filePath)
    fname = baseName.split('.xlsx')[0]
    
    print('Method 2')
    print('FileName: ', fname)

    newName = fname + '_formatted'  + '.xlsx'
    loadPath = load_pickle('data.pickle') 
    newPath = os.path.join(copy(loadPath['ispDataUploadPath']), newName)  
    
    ws = wb[sheets[0]]

    sampleTypeColumn = ws['E']
    sampleNameColumn = ws['G']
    
    elementConversion = ['As', 'Se', 'Cd', 'Sb', 'Hg', 'Pb', 'U']
    elementColumns = ['I', 'J', 'M', "Q", 'U', 'AA', 'AC']
    selectedRows = []

    sampleInfo = {}

    for cell in sampleTypeColumn:     
        if(cell.value == 'Sample'):
             
            currentSampleName = ws.cell(row=cell.row, column=7).value
            pattern = r'^\d{6}-\d{3}'
            
            if(re.search(pattern, currentSampleName)): 
                selectedRows.append(cell.row)
                
                sampleName = formatJobSampleString(currentSampleName)
                jobNum = sampleName[:6]
                #print('---------------')
                #print(sampleName, '|' , jobNum)

                sampleData = {}
                
                for i, element in enumerate(elementColumns): 
        
                    col_index = openpyxl.utils.column_index_from_string(element)
                    elementVal = ws.cell(row=cell.row, column=col_index).value 

                    if(elementVal == '<0.000'):
                        sampleData[elementConversion[i]] = 0.00
                    else: 
                        sampleData[elementConversion[i]] = elementVal
                    
                sampleInfo[sampleName] = sampleData
                
    for key, value in sampleInfo.items(): 
        query  = 'INSERT OR REPLACE INTO icpData values(?, ?, ?, ?, ?, 2)'
        jobNum = key[:6]
        todayDate = date.today()
        tempData = json.dumps(value)
        if(jobNum): 
            db.execute(query, (key, jobNum, baseName, tempData, todayDate))
            db.commit()

    # Format the machine data 
    formatMachineData(ws, selectedRows, elementColumns, newPath)
    
    return; 

def formatMachineData(ws, selectedRows, elementColumns, newPath): 
    logger.info('Entering formatMachineData with parameters:')
    logger.info(f'selectedRows: {repr(selectedRows)}')
    logger.info(f'elementColumns: {repr(elementColumns)}')
    logger.info(f'newPath: {repr(newPath)}')

    newWb = openpyxl.Workbook()
    ws2 = newWb.active 
    
    ws2.cell(row=1, column=1).value = 'Sample'
    tableNames = ['', 'Rjct', 'Data File', 'Acq. Date-Time', 'Type', 'Level', 'Sample Name', 'Total Dil', 
                  '75  As  [ He ] ', '78  Se  [ H2 ] ', '111  Cd  [ No Gas ] ', '123 Sb [He]', '202 Hg [He]', '208 Pb [He]', '238 U[He]'
                  ]
    
    ws2.merge_cells('A1:H1')
    
    column_num = 1;
    for item in tableNames: 
        ws2.cell(row=2, column=column_num).value = item; 
        column_num += 1;  
   
    row_num = 3; 
    for row_value in selectedRows:

        for currentPos in range(1,8): 
            ws2.cell(row=row_num, column=currentPos).value = ws.cell(row=row_value, column=currentPos).value
        
        tempCol = 9
        for col in elementColumns: 
            col_index = openpyxl.utils.column_index_from_string(col)
            ws2.cell(row=row_num, column=tempCol).value = ws.cell(row=row_value, column=col_index).value
            tempCol+=1; 
            

        row_num+=1;      

    newWb.save(newPath)

def formatJobSampleString(inputString): 
    sample = inputString.strip()
    match = re.match(r'(\d+)-0+(\d+)', sample)
    
    if match: 
        first_part = match.group(1)
        second_part = match.group(2)
        formatted_string = f"{first_part}-{second_part}"
        
        return formatted_string; 

def formatStringArray(inputArray): 
    outputArray = []
    
    for sample in inputArray: 
        sample = sample.strip()
        
        # Use regular expressions to extract the desired pattern
        match = re.match(r'(\d+)-0+(\d+)', string)
        
        if match:
            # Get the captured groups from the regex match
            first_part = match.group(1)
            second_part = match.group(2)

            # Construct the desired format
            formatted_string = f"{first_part}-{second_part}"
            outputArray.append(formatted_string)
    
    return(outputArray)
    
def viewIcpTable(filePath, data, reportType): 
    logger.info(f'Entering viewIcpTable with parameters: filePath: {filePath}, data: {data}, reportType: {reportType}')

    dialog = icpTableView(filePath, data, reportType)
    
    if dialog.exec_() == QDialog.Accepted:
        return True; 
    else:
        return False; 

#******************************************************************
#    Classes 
#******************************************************************
class icpTableView(QDialog):
    def __init__(self, filePath, data, reportType):
        super().__init__()
        
        self.resize(600, 500)
        self.setWindowTitle(filePath)
    
        headers = ['Sample Number', 'Line', 'Element', 'Value', 'duplicate Line'] 

        layout = QVBoxLayout()
        
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
    
        seen = {}
        
        for row, rowData in enumerate(data):
            sampleNum = rowData[0]
            line = rowData[1]
            parameterName = rowData[2]
            
            if (sampleNum, parameterName) in seen: 
                previousRow = seen[(sampleNum, parameterName)] 
                item = QTableWidgetItem(str(previousRow))
                table_widget.setItem(row,4, item)
            else: 
                seen[(sampleNum, parameterName)] = line
            
            for column, columnData in enumerate(rowData):
                item = QTableWidgetItem(str(columnData))
                table_widget.setItem(row, column, item)
                
        layout.addWidget(table_widget)
        
        size_grip = QSizeGrip(self)
        layout.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.save_and_close)
        
        close_button = QPushButton('Close', self)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(close_button)
        layout.addWidget(save_button)

        self.setLayout(layout)

        
    def save_and_close(self):
        self.accept()

            