from base_logger import logger

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QSpacerItem, QSizePolicy


from modules.constants import REPORT_STATUS, REPORT_NAME
from modules.dialogs.basic_dialogs import error_dialog
from modules.dbFunctions import (
    getAllAuthorNames, getJobStatus, updateJobStatus, getAuthorInfo, getParameterNum,
    getChmReportFooter, getIcpReportFooter
)
from modules.widgets.SampleNameWidget import SampleNameWidget


#******************************************************************
#   General Functions
#******************************************************************




def populateReportAuthorDropdowns(self):
    #TODO: have some error checking and deal with the loading section
    authorsList = [item[0] for item in getAllAuthorNames(self.tempDB)]
    authorsList.insert(0, '')

    self.ui.authorOneDropDown.clear()
    self.ui.authorTwoDropDown.clear()

    self.ui.authorOneDropDown.addItems(authorsList)
    self.ui.authorTwoDropDown.addItems(authorsList)

def disconnect_all_slots(obj):
    logger.info('Entering disconnect_all_slots')
    while True:
        try:
            if(isinstance(obj, QPushButton)):
                obj.clicked.disconnect()
            if(isinstance(obj, QTableWidget)):
                obj.itemChanged.disconnect()
        except TypeError:
            break

def updateReport(statusWidget, database, jobNum, reportNum):
    logger.info(f'Entering updateReport')
    try:
        jobStatus = getJobStatus(database, jobNum, reportNum)
        logger.debug(f'Checking current job status: : {jobStatus}')

        if(jobStatus == 0):
            completeJobStatusNum = 1
            logger.info("Preparing to update job status")
            updateJobStatus(database, jobNum, reportNum, completeJobStatusNum)

            logger.info('Updating Header Status')
            statusWidget.setText(REPORT_STATUS[completeJobStatusNum])

    except Exception as error:
        logger.error(f'Could not update Report Status for {(repr(jobNum))}')
        print(error)

def retrieveAuthorInfo(self, authorName1, authorName2):
    authorsInfo = []

    if(authorName1 != ''):
        authorInfo1 = getAuthorInfo(self.tempDB, authorName1)
        self.logger.debug(f'authorInfo1: {authorInfo1}')
        authorsInfo.append(authorInfo1)

    if(authorName2 != ''):
        authorInfo2 = getAuthorInfo(self.tempDB, authorName2)
        self.logger.debug(f'authorInfo2: {authorInfo2}')
        authorsInfo.append(authorInfo2)

    return authorsInfo

def retrieveFooterComment(self, reportType, paramType):

    try:
        paramNum = getParameterNum(self.tempDB, paramType)
    except Exception as e:
        print(e)
        return ''

    if(paramNum):
        if(reportType == 'CHM'):
            try:
                footerComment = getChmReportFooter(self.tempDB, paramNum)

                return footerComment.split('\n')
            except Exception as e:
                return ''

        if(reportType == 'ICP'):
            try:
                footerComment = getIcpReportFooter(self.tempDB, paramNum)
                return footerComment.split('\n')
            except Exception as e:
                return ''

#******************************************************************
#   Error Handling
#******************************************************************
def createExcelErrorCheck(self):
    self.logger.info('Entering createExcelErrorCheck')


    #
    try:
        # Check if the data files are not empty
        if(self.ui.dataTable.rowCount() == 0):
            raise EmptyDataTableError("Data table is empty. Cannot create Excel file.")

    except EmptyDataTableError as error:
        print(error)
        self.logger.error('Data table is empty. Cannot create Excel file')
        error_dialog('Cannot create report', f'Data table is empty. Cannot create excel file for Job: {self.jobNum}')
        return

    except Exception as e:
        print("Unexpected error:", e)
        return


    errorCheck = [0,0,0]

    #TODO: make sure the names are both different for authors

    #check if at least one author is selected
    if(self.ui.authorOneDropDown.currentIndex() > 0 or self.ui.authorTwoDropDown.currentIndex() > 0):
        authorOne = self.ui.authorOneDropDown.currentText()
        authorTwo = self.ui.authorTwoDropDown.currentText()

        self.logger.debug('At least one combo box is selected')
        self.logger.info(f'AuthorOne: {authorOne}, authorTwo: {authorTwo}');
    else:
        self.logger.debug('No Combo Box is selected.')
        errorCheck[0] = 1
    if(self.ui.clientName_1.text() == ''):
        errorCheck[1] = 1

    if(sum(errorCheck) >= 1):
        self.logger.debug(f'ERROR CHECK: {errorCheck}')
        excelErrorHandler(self, errorCheck)

        return True
    else:
        return False

def excelErrorHandler(self, errorCheck):
    self.logger.info('ReportErrorHandler called with parameters: errorCheck {error}')

    errorTitle = 'Cannot Create Excel Document'
    errorMsg = ''

    if(errorCheck[0] == 1):
        self.logger.debug('Please select at least one author')
        errorMsg += 'Please Select a least one author in the Client Info Section\n'

    if(errorCheck[1] == 1):
        self.logger.debug('Please enter a client name')
        errorMsg += 'Please Enter a Client Name\n'

    error_dialog(errorTitle, errorMsg)



#******************************************************************
#   Table Functions
#******************************************************************

def clearDataTable(table):
    logger.info('Entering clearDataTable')
    table.clearContents()
    table.setRowCount(0)

def formatReportTable(table, rowCount, colCount):
    logger.info(f'Entering formatReportTable with parameters: rowCount: {repr(rowCount)}, colCount: {repr(colCount)}')
    table.setRowCount(rowCount)
    table.setColumnCount(colCount)
    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)


def populateTableRow(tableWidget, row, col, alignment, editable, value):
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
    tableWidget.setItem(row, col, item)

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

def clearLayout(layout):
    logger.info('Entering clearLayout')

    for i in reversed(range(layout.count())):
        item = layout.takeAt(i)
        if item:
            widget = item.widget()
            if widget:
                widget.setParent(None)  # Optional: Detach the widget from its parent


def populateSamplesContainer(layout, sampleNames):
    logger.info(f'Entering populateSamplesContainer with parameters: sampleNames: {sampleNames}')

    for i, (key,value) in enumerate(sampleNames.items()):

        logger.debug(f'Active Sample: {key}, Sample Name: {value}')
        sampleItem = SampleNameWidget(key, value)
        layout.addWidget(sampleItem)
        sampleItem.edit.textChanged.connect(lambda textChange, key = key: updateSampleNames(sampleNames, textChange, key))

    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)

    logger.info('Populated populateSamplesContainer')

def updateSampleNames(sampleNames, textChange, key):
    sampleNames[key] = textChange;
    print(f'Update Sample Name: {sampleNames}')

#******************************************************************
#   Client Info Functions
#******************************************************************

def loadClientInfo(self):
    logger.info('Entering loadClientInfo')

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

    logger.info('Populated loadClientInfo')


def load_client_info(self, client_info=None):
    logger.info("Entering load_client_info")

    # Set the header parameters
    self.ui.jobNum.setText(f"W{self.jobNum}")
    self.ui.clientNameHeader.setText(self.clientInfo.get('clientName', ''))
    self.ui.parameterHeader.setText(self.parameter)
    self.ui.reportTypeHeader.setText(self.reportType)
    self.ui.factorHeader.setText(str(self.dilution))

    # Define a mapping of UI elements to client info fields
    field_mapping = {
        self.ui.clientName_1: "clientName",
        self.ui.date_1: "date",
        self.ui.time_1: "time",
        self.ui.attention_1: "attn",
        self.ui.addy1_1: "addy1",
        self.ui.addy2_1: "addy2",
        self.ui.addy3_1: "addy3",
        self.ui.sampleType1_1: "sampleType1",
        self.ui.sampleType2_1: "sampleType2",
        self.ui.totalSamples_1: "totalSamples",
        self.ui.recvTemp_1: "recvTemp",
        self.ui.tel_1: "tel",
        self.ui.email_1: "email",
        self.ui.fax_1: "fax",
        self.ui.payment_1: "payment",
    }

    # Populate client info fields
    for widget, field in field_mapping.items():
        widget.setText(self.clientInfo.get(field, ""))

    logger.info("Populated Client")


#******************************************************************
#   Custom Exceptions
#******************************************************************
class EmptyDataTableError(Exception):
    pass


