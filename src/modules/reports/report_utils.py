

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot

from modules.dbFunctions import getAllAuthorNames 
from widgets.widgets import SampleNameWidget 

#from modules.reports.create_chm_report import chemReportTestData

#******************************************************************
#   General Functions 
#******************************************************************

#TODO: Move this into a report_utils.py so both functions can have access to this 
#TODO: need to move this can account for both ICP and CHM reports 
@pyqtSlot() 
def handleTableChange(self, item):
    
    table = self.ui.dataTable 
    row = item.row()
    column = item.column()
    value = item.text()

    updatedValue = table.item(row, column).text()
    column_name = table.horizontalHeaderItem(column).text()
   
    # ICP create state  
    if(self.createState == 1): 
        pass; 
    
    # CHM Create State
    if(self.createState == 2): 

        textNameCol = 1
        textName = table.item(row, textNameCol)

        #TODO: need to check if it is empty or not 
        if(textName and self.reportManager): 
            textName = textName.text()
            print(f'Col Name: {column_name}, TEXT: {textName}, NEW VAL: {updatedValue}')
            
            if(column == 2): 
                # Update the display name 
                testType = self.reportManager.tests[textName]
                
                if(isinstance(testType, chemReportTestData)): 
                    self.reportManager.tests[textName].update_displayName(updatedValue)
                
            if(column == 3): 
                # Update the unit value
                pass; 
            
            
            if(column == 5): 
                # Update the standard 
                pass; 
            
            if(column > 5):
                # Update the samples values
                testNum = self.reportManager.tests[textName].testNum
                self.reportManager.samples[column_name].update_data(testNum, updatedValue)

def populateReportAuthorDropdowns(self):
    #TODO: have some error checking and deal with the loading section 
    authorsList = [item[0] for item in getAllAuthorNames(self.tempDB)]
    authorsList.insert(0, '')
    
    self.ui.authorOneDropDown.clear()
    self.ui.authorTwoDropDown.clear()
    
    self.ui.authorOneDropDown.addItems(authorsList)
    self.ui.authorTwoDropDown.addItems(authorsList)


#******************************************************************
#   Table Functions 
#******************************************************************

def clearDataTable(table): 
    table.clearContents()
    table.setRowCount(0)

def formatReportTable(table, rowCount, colCount): 
    table.setRowCount(rowCount)
    table.setColumnCount(colCount)
    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

def populateTableRow(tableWidget, row, col, alignment, value): 
    item = QtWidgets.QTableWidgetItem()  
    if(alignment == 1):   
        item.setTextAlignment(Qt.AlignCenter)
    
        # Check data type and convert if necessary
    if isinstance(value, (int, float)):
        value = str(value)  # Prevent spinbox for numeric data
     
    item.setData(Qt.DisplayRole, value)
    tableWidget.setItem(row, col, item)
        
    return 

    
#******************************************************************
#   Sample Widget Functions 
#******************************************************************
    
def deleteAllSampleWidgets2(self): 
    for widget in self.ui.samplesContainer.children():
        if isinstance(widget, SampleNameWidget):
            widget.setParent(None)
            widget.deleteLater()
        else:
            spacer = widget.spacerItem()
            if spacer:
                self.layout.removeItem(spacer) 
            
def deleteAllSampleWidgets(self): 
    for i in reversed(range(self.ui.samplesContainer.layout().count())):
        item = self.ui.samplesContainer.layout().itemAt(i)
        if item.widget() is not None:
            if isinstance(item.widget(), SampleNameWidget):
                item.widget().deleteLater()
        elif item.spacerItem():
            self.ui.samplesContainer.layout().removeItem(item)
    
#******************************************************************
#   Client Info Functions 
#******************************************************************
    
def loadClientInfo(self): 
    print('[Function]: loadClientInfo(self)')
    
    # Set the header parameter 
    self.ui.jobNum.setText("W" + self.jobNum)
    self.ui.clientNameHeader.setText(self.clientInfo['clientName'])
    self.ui.parameterHeader.setText(self.parameter); 
    self.ui.reportTypeHeader.setText(self.reportType);
    
    self.ui.factorHeader.setText(str(self.dilution))

    # Set the client Info 
    self.ui.clientName_1.setText(self.clientInfo['clientName'])
    self.ui.date_1.setText(self.clientInfo['date'])
    self.ui.time_1.setText(self.clientInfo['time'])
    self.ui.attention_1.setText(self.clientInfo['attn'])
    self.ui.addy1_1.setText(self.clientInfo['addy1'])
    self.ui.addy2_1.setText(self.clientInfo['addy2'])
    self.ui.addy3_1.setText(self.clientInfo['addy3'])
    self.ui.sampleType1_1.setText(self.clientInfo['sampleType1'])
    self.ui.sampleType2_1.setText(self.clientInfo['sampleType2'])
    self.ui.totalSamples_1.setText(self.clientInfo['totalSamples'])
    self.ui.recvTemp_1.setText(self.clientInfo['recvTemp'])
    self.ui.tel_1.setText(self.clientInfo['tel'])
    self.ui.email_1.setText(self.clientInfo['email'])
    self.ui.fax_1.setText(self.clientInfo['fax'])
    self.ui.payment_1.setText(self.clientInfo['payment'])

def updateSampleNames(sampleNames, textChange, key):
    sampleNames[key] = textChange; 
    print(f'Update Sample Name: {sampleNames}')
    
