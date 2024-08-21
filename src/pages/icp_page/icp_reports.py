from base_logger import logger

from PyQt5.QtCore import pyqtSlot 

from modules.dbFunctions import getAllParameters, getParameterNum, getIcpReportFooter, addIcpReportFooter

#******************************************************************
#    ICP Reports   
#****************************************************************** 

def icp_report_setup(self): 
    
    # Load the init data on the setup
    loadIcpReports(self); 
    
    # Connect Report signals 
    self.ui.reportsList.itemSelectionChanged.connect(lambda: icpReportItemSelected(self))
    self.ui.icpReportCancelBtn.clicked.connect(lambda: on_icpReportCancelBtn_clicked(self))
    self.ui.saveFooterBtn.clicked.connect(lambda: on_saveFooterBtn_clicked(self))
    
def loadIcpReports(self): 
    parameters = getAllParameters(self.tempDB)    
    parameterNames = [item[1] for item in parameters]    
    self.ui.reportsList.addItems(parameterNames); 

def icpReportItemSelected(self): 
    selectedReport = self.ui.reportsList.currentItem() 
    
    if(selectedReport):
        reportName = selectedReport.text()
        reportNum = getParameterNum(self.tempDB, reportName)       
         
        # Set the report Name Label 
        self.ui.icpReportNameLabel.setText(f'[{reportNum}] {reportName.upper()}')

        icpReportLoadComment(self, reportNum)
        
def icpReportLoadComment(self, reportNum): 
    # Clear the Text Edit Widget 
    self.ui.footerComments.clear()
    
    footerComment = getIcpReportFooter(self.tempDB, reportNum)
    
    if(footerComment): 
        self.ui.footerComments.setPlainText(footerComment) 

@pyqtSlot()
def on_icpReportCancelBtn_clicked(self): 
    selected_item = self.ui.reportsList.currentItem() 
    
    if(selected_item): 
        reportName = selected_item.text()
        reportNum = getParameterNum(self.tempDB, reportName)     

        icpReportLoadComment(self, reportNum)
         
@pyqtSlot()
def on_saveFooterBtn_clicked(self): 
    print('Save Footer button Clicked')
    footerComment = self.ui.footerComments.toPlainText()
    selectedReport = self.ui.reportsList.currentItem() 
    
    if(selectedReport and footerComment): 
        reportName = selectedReport.text()
        reportNum = getParameterNum(self.tempDB, reportName)  
           
        # Insert or Replace the current Footer into the thing 
        addIcpReportFooter(self.tempDB, reportNum, footerComment)
        