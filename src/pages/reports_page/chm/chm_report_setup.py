import traceback


from base_logger import logger
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem

from modules.dialogs.basic_dialogs import okay_dialog, error_dialog
from modules.dbFunctions import (getIcpReportFooter, getParameterNum, getChmReportFooter, addChmReportFooter )
from modules.utils.logic_utils import is_float

#TODO: maybe improve the SampleWidget
from pages.reports_page.reports.report_utils import ( populateSamplesContainer, EmptyDataTableError, updateReport,
    createExcelErrorCheck, retrieveAuthorInfo, retrieveFooterComment )
from pages.reports_page.chm.chm_report_controller import ChemReportController
from pages.reports_page.chm.chm_report_model import ChemReportModel
from pages.reports_page.chm.chm_report_view import ChemReportView
from pages.reports_page.chm.chm_create_excel import chm_create_excel

from pages.reports_page.ExcelReports import ChmExcelReport


def chm_report_setup(self):
    # prepare the report page for data
    column_names = ['Tests Name', 'Text Name', 'Display Name', 'Unit', 'Distillation Factor', 'Standard Recovery']
    chem_report_table_setup(self.ui.dataTable, column_names, self.sampleNames)
    chem_sample_widget_setup(self.ui.samplesContainerLayout_2, self.sampleNames)

    # clear out the previous information and table before starting
    clean_up_previous_chm_report(self)

    #TODO: rename them to chm
    self.chem_report_model = ChemReportModel(self.tempDB, self.jobNum, self.dilution, self.sampleTests)
    self.chem_report_view = ChemReportView(self.ui.dataTable, self.ui.createChmReportBtn)
    self.chem_report_controller = ChemReportController(self.chem_report_model, self.chem_report_view, self.sampleNames)

    #TODO: check if this data is up to date when changed
    sample_data, display_name, recovery_vals, units = self.chem_report_controller.export_data()

    # Disconnect previous connections, if any
    try:
        self.ui.createChmReportBtn.clicked.disconnect()
    except TypeError:
        # If no connection exists, just pass
        pass

    # Connect the button with the updated parameters
    self.ui.createChmReportBtn.clicked.connect(
        lambda: handle_create_chem_btn(self, sample_data, display_name, recovery_vals, units)
    )


def clean_up_previous_chm_report(self):
    if hasattr(self, 'chem_report_view'):
        self.chem_report_view.clear_table()  # Clear the table to reset its state
    if hasattr(self, 'chem_report_model'):
        self.chem_report_model = None  # Dereference old model
    if hasattr(self, 'chem_report_view'):
        self.chem_report_view = None   # Dereference old view
    if hasattr(self, 'chem_report_controller'):
        self.chem_report_controller = None  # Dereference old controller

def chem_sample_widget_setup(layout, sample_names):
    logger.info('Entering update_samples_widget')

    populateSamplesContainer(layout, sample_names)

def chem_report_table_setup(table, column_names, sample_names):
    logger.info('Entering chem_report_table_setup')

    col_count = len(column_names) + len(sample_names)
    table.setColumnCount(col_count)

    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    setup_column_headers(table, column_names)
    setup_sample_headers(table, sample_names, len(column_names))

def setup_column_headers(table, column_names):
    for i, name in enumerate(column_names):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(name))

def setup_sample_headers(table, sample_names, start_index):
    for i, (key, _) in enumerate(sample_names.items(), start=start_index):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(key))

def handle_create_chem_btn(self, sampleData, displayNames, recovery, unitType):
    logger.info('Entering handle_create_chem_btn')

    # retrieve other information
    authorsInfo = retrieveAuthorInfo(self, self.ui.authorOneDropDown.currentText(), self.ui.authorTwoDropDown.currentText())
    footerComment = get_footer_comment(self, 'CHM', self.parameter)

    client_info = self.client_manager.get_client_info()

    if(footerComment is None):
        footerComment = ''

    # TODO: error check if valid to create report
    if(createExcelErrorCheck(self)):
        return

    try:
        logger.info(f'Preparing to create CHM Report {self.jobNum}')

        #filePath, fileName = chm_create_excel(client_info, self.jobNum, authorsInfo, footerComment, self.sampleNames, sampleData, displayNames, unitType, recovery)
        chm_excel_manager = ChmExcelReport(client_info, self.jobNum, authorsInfo, footerComment, self.sampleNames, sampleData, displayNames, unitType, recovery)
        filePath, fileName = chm_excel_manager.create_report()

        title = f'Success Created CHM Report: {self.jobNum}'
        message= f'CHM Report Creation Successful File: {fileName}'

        okay_dialog(title, message)

        jobCreatedNum = 1
        self.logger.info(f'CHM Report Creation Successful: jobCreated: {jobCreatedNum}')
        self.status_bar_manager.update_status_bar(title)

    except Exception as e:
        jobCreatedNum = 0;
        error_details = traceback.format_exc()

        title = f'Failed to create CHM Report:: {self.jobNum}'
        message = 'CHM Report Creation Error'

        error_dialog(title, message)

        logger.error(f"CHM Report Creation Error: {e}\nDetails:\n{error_details}")
        self.status_bar_manager.update_status_bar(title)

    #TODO: can move into on excel file
    if(jobCreatedNum == 1):
        updateReport(self.ui.statusHeaderLabel, self.tempDB, self.jobNum, self.reportNum)

    # TODO: Save the other client info
    # TODO: Authors, client info, samples name. sample data
    # TODO: can save the data through matching the rows


def get_footer_comment(self, reportType, paramNum ):
    print(f'Entering get_footer_comment with reportType:{reportType}, paramNum:{paramNum}')

    try:
        if(paramNum):
            if(reportType == 'CHM'):
                footerComment = getChmReportFooter(self.tempDB, paramNum)
                return footerComment.split('\n')

            if(reportType == 'ICP'):
                footerComment = getIcpReportFooter(self.tempDB, paramNum)
                return footerComment.split('\n')

    except Exception as e:
        return ''


