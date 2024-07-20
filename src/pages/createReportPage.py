import traceback
import sys
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

from modules.reports.report_utils import clearDataTable, populateReportAuthorDropdowns 
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
    #TODO: ERROR could not load TEXT_FILE please try again
    apply_drop_shadow_effect(self.ui.createReportHeader)
 
    # Create a validator to accept only integer input
    validatorInt = QIntValidator(0, 999999) 
    validatorDec = QDoubleValidator(0.0, 999999.99, 3)

    # Set input limits and Validators
    self.ui.jobNumInput.setValidator(validatorInt)
    self.ui.dilutionInput.setValidator(validatorDec)
    # Set the max length for both     
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
    print('[FUNCTION]: createReportPage')
    
    # strip the basic information 
    jobNum = jobNum or self.ui.jobNumInput.text().strip()
    reportType = reportType or self.ui.reportType.currentText()
    parameter = parameter or self.ui.paramType.currentText()
    dilution = dilution or self.ui.dilutionInput.text()
    
    print('*--------------------------')
    print('*JobNumber: ', jobNum)
    print('*ReportType: ', reportType)
    print('*Parameter: ', parameter)
    print('*Dilution: ', dilution )
    print('*--------------------------')

    dilution = 1 if (dilution == '' or dilution == None) else dilution       
    textFileExists = scanForTXTFolders(jobNum)
    
    # Error Checking Section
    errorCheck = [0, 0, 0, 0]     
    errorCheck[0] = 0 if re.match('^([0-9]{6})$', jobNum) else 1 
    errorCheck[1] = 0 if reportType in REPORTS_TYPE else 1
    errorCheck[2] = 0 if parameter != '' else 1
    errorCheck[3] = 0 if textFileExists != '' and textFileExists  else 1    
     
    if(sum(errorCheck) == 0): 
        self.jobNum = jobNum
        self.reportType = reportType
        self.parameter = parameter
        self.dilution = dilution

        self.reportNum = REPORT_NUM[self.reportType]  #TODO: does this need to be global 
        
        self.ui.reportsTab.setCurrentIndex(0)
        self.ui.stackedWidget.setCurrentIndex(5) 
        
        paramNum = getReportNum(self.tempDB, parameter)
        jobResult = checkJobExists(self.tempDB, self.jobNum, self.reportNum)

        #TODO: load the information from database later (front house database)  
        #FIXME: error when it is the 5th sample and not the first, the sample name gets it wrong ex. W172485.TXT  
        self.clientInfo, self.sampleNames, self.sampleTests = processClientInfo(self.jobNum, textFileExists)

        print(f'SAMPLE NAMES: {self.sampleNames}')
        print(f'SAMPLE TESTS: {self.sampleTests}')

        populateReportAuthorDropdowns(self)

        # Add the text file to the text file tab 
        checkTextFile(self, textFileExists)

        clearDataTable(self.ui.dataTable)
        
        # Check if the job exists in the database or not 
        if(jobResult is None):  
            currentDate = date.today()
            currentStatus = 0 
            
            # New Job so set the header status to 'Not Generated' 
            self.ui.statusHeaderLabel.setText(REPORT_STATUS[currentStatus])
            
            # Attempts to job to the database 
            addNewJob(self.tempDB, jobNum, self.reportNum, paramNum, self.dilution, currentStatus, currentDate)

        else: 
            if(method2 is not True): 
                print('Report Exists')
                print(f'Job Contents: {jobResult}')
                
                loadReportDialog(self)     
             
            # Check if has been generated or not before and assign to header status 
            status = getJobStatus(self.tempDB, self.jobNum, self.reportNum)
            print(f'Attempt Status: {status}')
            self.ui.statusHeaderLabel.setText(REPORT_STATUS[status])
             
        try: 
            if(reportType == 'ICP'):         
                icpReportLoader(self)
                
            if(reportType == 'CHM'):    
                chmReportLoader(self)
                
        except Exception as error: 
            print(f'[ERROR]: {error}') 
            traceback.print_exc(file=sys.stderr)  # Print detailed traceback
            
            if(method2 is not True): 
                showErrorDialog(self, 'Error Creating Report', f'Could not create report {self.jobNum}')
            else: 
                showErrorDialog(self, 'Error Loading Report', f'Could not load the report {self.jobNum}')

    else: 
        reportErrorHandler(self, errorCheck)

def reportErrorHandler(self, errorCheck): 
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
    print('[FUNCTION]: checkTextFile')
    
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
