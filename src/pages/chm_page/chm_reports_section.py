

from PyQt5.QtCore import pyqtSlot

from modules.dbFunctions import (getAllParameters, getParameterNum, getChmReportFooter, addChmReportFooter )

#******************************************************************
#    Chemistry Report Info
#****************************************************************** 
def chm_report_setup(self): 
    # Load the init data on the setup
    loadChmReports(self); 
     
    # Connect Report signals 
    self.ui.chmReportList.itemSelectionChanged.connect(lambda: chmReportItemSelected(self))
    self.ui.chmReportCancelBtn.clicked.connect(lambda: on_chmReportCancelBtn_clicked(self))
    self.ui.chmReportSaveBtn.clicked.connect(lambda: on_chmSaveFooterBtn_clicked(self))
    
def loadChmReports(self): 
    parameters = getAllParameters(self.tempDB)    
    parameterNames = [item[1] for item in parameters]    
    self.ui.chmReportList.addItems(parameterNames); 

def chmReportItemSelected(self): 
    selectedReport = self.ui.chmReportList.currentItem() 
    
    if(selectedReport):
        reportName = selectedReport.text()
        reportNum = getParameterNum(self.tempDB, reportName)       
         
        # Set the report Name Label 
        self.ui.chmReportNameLabel.setText(f'[{reportNum}] {reportName.upper()}')

        chmReportLoadComment(self, reportNum)
        
def chmReportLoadComment(self, reportNum): 
    # Clear the Text Edit Widget 
    self.ui.chmFooterComment.clear()
    
    footerComment = getChmReportFooter(self.tempDB, reportNum)
    
    if(footerComment): 
        self.ui.chmFooterComment.setPlainText(footerComment) 

@pyqtSlot()
def on_chmReportCancelBtn_clicked(self): 
    selected_item = self.ui.chmReportList.currentItem() 
    
    if(selected_item): 
        reportName = selected_item.text()
        reportNum = getParameterNum(self.tempDB, reportName)     

        chmReportLoadComment(self, reportNum)
         
@pyqtSlot()
def on_chmSaveFooterBtn_clicked(self): 
    print('Save Footer button Clicked')
    footerComment = self.ui.chmFooterComment.toPlainText()
    selectedReport = self.ui.chmReportList.currentItem() 
    
    if(selectedReport and footerComment): 
        reportName = selectedReport.text()
        reportNum = getParameterNum(self.tempDB, reportName)  
           
        # Insert or Replace the current Footer into the thing 
        addChmReportFooter(self.tempDB, reportNum, footerComment)
        