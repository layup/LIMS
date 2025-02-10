from base_logger import logger

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QSpacerItem, QSizePolicy


from modules.constants import REPORT_STATUS, REPORT_NAME
from modules.dialogs.basic_dialogs import error_dialog
from modules.widgets.SampleNameWidget import SampleNameWidget


#******************************************************************
#   General Functions
#******************************************************************

def populate_author_dropdown(self):
    logger.info('Entering populate_author_dropdown')

    # clear existing author info
    self.ui.authorOneDropDown.clear()
    self.ui.authorTwoDropDown.clear()

    # add blank nap place holders
    self.ui.authorOneDropDown.addItem('')
    self.ui.authorTwoDropDown.addItem('')

    for author_id, author_info in self.authors_manager.get_authors().items():
        full_name = author_info.full_name

        self.ui.authorOneDropDown.addItem(full_name, author_id)
        self.ui.authorTwoDropDown.addItem(full_name, author_id)

    # set the default to author number 1
    self.ui.authorOneDropDown.setCurrentIndex(1)

#TODO: error handle if they are both the same name
def get_selected_report_authors(self):
    logger.info('Entering get_selected_report_authors')

    authors = []

    # get the current index
    index_one = self.ui.authorOneDropDown.currentIndex()
    index_two = self.ui.authorTwoDropDown.currentIndex()

    if(index_one >= 1):
        author_id_one = self.ui.authorOneDropDown.itemData(index_one)
        author_info_one = self.authors_manager.get_author_info(author_id_one)

        if(author_info_one):
            authors.append(author_info_one)

    if(index_two >= 1):
        author_id_two = self.ui.authorTwoDropDown.itemData(index_two)
        author_info_two = self.authors_manager.get_author_info(author_id_two)

        if(author_info_two):
            authors.append(author_info_two)

    logger.info(f'authors: {authors}')

    return authors

def get_report_footer_comment(report_manager, param_id: int, report_type: int):
    logger.info('Entering get_report_footer_comment')

    footer_comment = report_manager.get_footer_message(param_id, report_type)

    if(footer_comment):
       return footer_comment.split('\n')

    return ''

def update_report_status(self, job_num: int, report_id: int):
    logger.info(f'Entering update_report_status with job_num: {job_num}, report_id: {report_id}')

    try:
        job_status = self.jobs_manager.get_status(job_num, report_id)

        if(job_status == 0 or job_status is None):
            complete_report_status_num = 1

            self.jobs_manager.update_status(job_num, report_id, complete_report_status_num)

            self.ui.statusHeaderLabel.setText(REPORT_STATUS[complete_report_status_num])

    except Exception as error:
        logger.error(f'Could not update Report Status for {(repr(job_num))}')





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
#   Custom Exceptions
#******************************************************************
class EmptyDataTableError(Exception):
    pass


