import traceback
import sys
import logging
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, 
)

from PyQt5.QtGui import QIntValidator, QDoubleValidator, QKeyEvent, QValidator

from modules.reports.report_utils import clearDataTable, populateReportAuthorDropdowns, clearLayout, EmptyDataTableError
from modules.reports.create_chm_report import chmReportLoader  
from modules.reports.create_icp_report import icpReportLoader 

from modules.dbFunctions import *
from modules.constants import *
from modules.utilities import *
from widgets.widgets import *

#TODO: move a lot of these functions to the db functions 
#TODO: We can save the data, when closing the thing, such as if we are editing/adding new info. We want to save it for the future 
#FIXME: when file is successfully created it makes two copies of the dialog box 
#FIXME: when the use info is empty it will crash because it can't scan any of the existing files 
#******************************************************************
#   Report Setup 
#******************************************************************
def reportSetup(self): 
    self.logger.info(f'Entering reportSetup')
    #TODO: ERROR could not load TEXT_FILE please try again
    apply_drop_shadow_effect(self.ui.createReportHeader)

    self.logger.info(f'setting input limits and Validators')
    # Create a validator to accept only integer input
    validatorInt = QIntValidator(0, 999999) 
    validatorDec = QDoubleValidator(0.0, 999999.99, 3)

    self.logger.info(f'setting input limits, validators and max lengths')
    self.ui.jobNumInput.setValidator(validatorInt)
    self.ui.dilutionInput.setValidator(validatorDec)
  
    self.ui.jobNumInput.setMaxLength(6)
    self.ui.dilutionInput.setMaxLength(6)
    
    # Connect signals  
    self.ui.NextSection.clicked.connect(lambda: createReportPage(self))
    
    #FIXME: error on the setup because there isn't anything there yet    
    #self.ui.dataTable.itemChanged.connect(lambda item: handleTableChange(self, item))
    
    
#TODO: replace the create report with a custom thing that can paste strings and remove the ints 
class CustomIntLineEdit(QLineEdit): 
    
    attemptedPaste = pyqtSignal(str)  # Custom signal for attempted pastes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator()) 
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeyEvent.Paste):
            clipboard = QApplication.clipboard()
            attempted_text = clipboard.text()
            
            # Check if the pasted text would be fully accepted
            if not all(char.isdigit() for char in attempted_text):
                self.attemptedPaste.emit(attempted_text)
                return  # Don't process the paste event
        
        super().keyPressEvent(event)
    

#******************************************************************
#   Creating Report 
#******************************************************************

@pyqtSlot()
def createReportPage(self, jobNum = None, reportType = None, parameter = None, dilution =None, method2= None):
    self.logger.info(f"Entering createReportPage with arguments: jobNum={jobNum}, reportType={reportType}, parameter={parameter}, dilution={dilution}, method2={method2}")
    
    # strip the basic information, if is not none then load in 
    jobNum = jobNum or self.ui.jobNumInput.text().strip()
    reportType = reportType or self.ui.reportType.currentText()
    parameter = parameter or self.ui.paramType.currentText()
    dilution = dilution or self.ui.dilutionInput.text()
    
    dilution = 1 if (dilution == '' or dilution == None) else dilution       
    textFileExists = scanForTXTFolders(jobNum)
    
    # Error Checking Section
    errorCheck = [0, 0, 0, 0]     
    errorCheck[0] = 0 if re.match('^([0-9]{6})$', jobNum) else 1 
    errorCheck[1] = 0 if reportType in REPORTS_TYPE else 1
    errorCheck[2] = 0 if parameter != '' else 1
    errorCheck[3] = 0 if textFileExists != '' and textFileExists  else 1   
    #TODO: check if jobs even have the relevant tests that need to be done
     
    if(sum(errorCheck) == 0): 
        self.logger.info('All error checks passed')
         
        self.jobNum = jobNum
        self.reportType = reportType
        self.parameter = parameter
        self.dilution = dilution
        self.reportNum = REPORT_NUM[self.reportType]  #TODO: does this need to be global 
        
        self.logger.info('Getting Report Numbers...') 
        paramNum = getReportNum(self.tempDB, parameter)

        self.logger.info('Checking if the job exists...')
        jobResult = checkJobExists(self.tempDB, self.jobNum, self.reportNum)

        #TODO: load the information from database later (front house database)  
        #FIXME: error when it is the 5th sample and not the first, the sample name gets it wrong ex. W172485.TXT  
        self.logger.info('Processing client information...')
        self.clientInfo, self.sampleNames, self.sampleTests = processClientInfo(self.jobNum, textFileExists)
  
        populateReportAuthorDropdowns(self)

        # Add the text file to the text file tab 
        checkTextFile(self, textFileExists)

        self.logger.info('Clearing the data table and layout')
        clearDataTable(self.ui.dataTable)        
        clearLayout(self.ui.samplesContainerLayout_2)
    
        currentDate = date.today()
        currentStatus = 0 

        # Check if the job exists in the database or not 
        if(jobResult is None):  
            self.logger.info(f'Retrieved job data: {jobResult}')
            
            # New Job so set the header status to 'Not Generated' 
            self.ui.statusHeaderLabel.setText(REPORT_STATUS[currentStatus])
            
            # Attempts to job to the database 
            addNewJob(self.tempDB, jobNum, self.reportNum, paramNum, self.dilution, currentStatus, currentDate)

        else: 
            # Do you want to overwrite the existing file 
            #TODO: make it so we can save the data and load it in later
            if(method2 is not True): 
                self.logger.info('Report Exists')
                print(f'Job Contents: {jobResult}')
                
                overwrite = loadReportDialog(self)     
                self.logger.info(f'User overwrite choose: {overwrite}')
                
                if(overwrite == 'Cancel'): 
                    return;  
                if(overwrite == 'No'): 
                    # Does this just load the normal data and doesn't overwrite the database? 
                    pass; 
                if(overwrite == 'Yes'):   
                    updateJob(self.tempDB, jobNum, self.reportNum, paramNum, self.dilution, currentStatus, currentDate) 
            
            # Check if has been generated or not before and assign to header status 
            status = getJobStatus(self.tempDB, self.jobNum, self.reportNum)
            self.logger.info(f'Attempt Status: {status}')
            self.ui.statusHeaderLabel.setText(REPORT_STATUS[status])
    
        try: 
            layout_config(self, self.reportType) 


        except Exception as error: 
            self.logger.error(error)
            traceback.print_exc(file=sys.stderr)  # Print detailed traceback
            
            #TODO: give the reason why the report couldn't be created or opened
            if(method2 is not True): 
                showErrorDialog(self, 'Error Creating Report', f'Could not create report {self.jobNum}')
            else: 
                showErrorDialog(self, 'Error Loading Report', f'Could not load the report {self.jobNum}')
            return 

        # Switch the index of items
        self.ui.reportsTab.setCurrentIndex(0)
        self.ui.stackedWidget.setCurrentIndex(5) 

    else: 
        reportErrorHandler(self, errorCheck)

def layout_config(self, reportType):
    self.logger.info(f'Entering layout_config with parameter: reportType: {repr(reportType)}')
    
    reportNum = REPORT_NUM[reportType]
    
    if(reportNum == 1):  
        self.logger.info('Preparing ICP report Configuration')
        self.ui.reloadDataBtn.setVisible(True)
        self.ui.calcHardnessBtn.setVisible(True)
        
        self.ui.createIcpReportBtn.setVisible(True)
        self.ui.createGcmsReportBtn.setVisible(False)
        self.ui.icpDataField.show()

        icpReportLoader(self)
        
    if(reportNum == 2): 
        self.logger.info('Preparing CHM report Configuration')
        self.ui.reloadDataBtn.setVisible(False)
        self.ui.calcHardnessBtn.setVisible(False)
        
        self.ui.createIcpReportBtn.setVisible(False)
        self.ui.createGcmsReportBtn.setVisible(True)
        self.ui.icpDataField.hide()  
       
        chmReportLoader(self) 
        
def reportErrorHandler(self, errorCheck): 
    self.logger.info('ReportErrorHandler called with parameters: errorCheck {error}')
    
    errorTitle = 'Cannot Proceed to Report Creation Screen '
    errorMsg = ''
    
    if(errorCheck[0] == 1): 
        print('Error: Please Enter a valid job number')
        errorMsg += 'Please Enter a Valid Job Number\n'

    if(errorCheck[1] == 1): 
        print("Error: Please Select a reportType")
        errorMsg += 'Please Select a Report Type\n'
        
    if(errorCheck[2] == 1): 
        print('Error: Please Select a parameter')
        errorMsg += 'Please Select a Parameter\n'
    
    if(errorCheck[3] == 1): 
        print("Error: TXT File doesn't exist")
        errorMsg += 'TXT File could not be located\n'

    showErrorDialog(self, errorTitle, errorMsg)
        
def checkTextFile(self, fileLocation): 
    self.logger.info('Entering checkTextFile')
    
    # Enable Text File Tab if the file is there
    if(fileLocation): 
        try: 
            self.ui.reportsTab.setTabEnabled(2, True)
            
            with open(fileLocation) as file: 
                content = file.read()
                 
            # Clear existing content in the QTextBrowser
            self.ui.textBrowser.clear()
            # Append the content of the text file to the QTextBrowser
            self.ui.textBrowser.append(content)
    
        except Exception as error: 
            print(error)
            self.ui.reportsTab.setTabEnabled(2, False) 
        
    else:
         self.ui.reportsTab.setTabEnabled(2, False)