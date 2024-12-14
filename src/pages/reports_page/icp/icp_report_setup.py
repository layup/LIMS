import traceback

from base_logger import logger

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem
from modules.dialogs.basic_dialogs import okay_dialog, error_dialog
from modules.dbFunctions import getIcpElementsList, getChmReportFooter

from pages.reports_page.reports.report_utils import ( populateSamplesContainer, EmptyDataTableError, updateReport,
    createExcelErrorCheck, retrieveAuthorInfo, retrieveFooterComment )
from pages.reports_page.icp.icp_report_view import IcpReportView
from pages.reports_page.icp.icp_report_model import IcpReportModel
from pages.reports_page.icp.icp_report_controller import IcpReportController
from pages.reports_page.icp.icp_create_excel import icp_create_excel

def icp_report_setup(self):
    logger.info('Entering icp_report_setup');

    clean_up_previous_icp_report(self)

    column_names = ['Element Name', 'Element Symbol', 'Unit Type', 'Lower Limit', 'Upper Limit', 'Distal factor']
    icp_report_table_setup(self.ui.dataTable, column_names, self.sampleNames)
    icp_sample_widget_setup(self.ui.samplesContainerLayout_2, self.sampleNames)

    self.icp_report_model = IcpReportModel(self.tempDB, self.jobNum, self.parameter, self.dilution, self.sampleTests)
    self.icp_report_view = IcpReportView(self.ui.dataTable)
    self.icp_report_controller = IcpReportController(self.icp_report_model, self.icp_report_view)

    element_names, element_limits_info, element_units, samples_data = self.icp_report_controller.export_data()

    # Disconnect previous connections, if any
    try:
        self.ui.createIcpReportBtn.clicked.disconnect()
    except TypeError:
        # If no connection exists, just pass
        pass

    # Connect the button with the updated parameters
    self.ui.createIcpReportBtn.clicked.connect(
        lambda : handle_create_icp_btn(self, element_names, element_limits_info, element_units, samples_data )
    )

def clean_up_previous_icp_report(self):
    if hasattr(self, 'self.ui.dataTable'):
        self.self.ui.dataTable.clear_table()  # Clear the table to reset its state
    if hasattr(self, 'icp_report_model'):
        self.icp_report_model = None  # Dereference old model
    if hasattr(self, 'icp_report_view'):
        self.icp_report_view = None   # Dereference old view
    if hasattr(self, 'icp_report_controller'):
        self.icp_report_controller = None  # Dereference old controller


def icp_report_table_setup(table, column_names, sample_names):

    col_count = len(column_names) + len(sample_names)
    table.setColumnCount(col_count)

    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    # set the column width for tables
    table.setColumnWidth(0, 150)

    setup_column_headers(table, column_names)
    setup_sample_headers(table, sample_names, len(column_names))

def setup_column_headers(table, column_names):
    for i, name in enumerate(column_names):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(name))

def setup_sample_headers(table, sample_names, start_index):
    for i, (key, _) in enumerate(sample_names.items(), start=start_index):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(key))

def icp_sample_widget_setup(layout, sample_names):
    logger.info('Entering update_samples_widget')

    populateSamplesContainer(layout, sample_names)

def handle_create_icp_btn(self, element_names, element_limits, element_units, samples_data):
    logger.info('Entering handle_create_icp_btn')

    # Format and retrieve the necessary information to create excel reports
    authorsInfo = retrieveAuthorInfo(self, self.ui.authorOneDropDown.currentText(), self.ui.authorTwoDropDown.currentText())
    footerComment = get_footer_comment_temp(self.tempDB, self.parameter)
    client_info = self.client_manager.get_client_info()

    if(createExcelErrorCheck(self)):
        return

    try:
        self.logger.info(f'Preparing to create ICP Report {self.jobNum}')

        filePath, fileName = icp_create_excel(client_info, self.sampleNames, authorsInfo, self.jobNum, samples_data, element_names, element_units, element_names, element_limits, footerComment)

        title = f'Success Created ICP Report: {self.jobNum}'
        message= f'ICP Report Creation Successful File: {fileName}'

        okay_dialog(title, message)

        jobCreatedNum = 1
        self.logger.info(f'ICP Report Creation Successful: jobCreated: {jobCreatedNum}')
        self.status_bar_manager.update_status_bar(f'Successfully Created ICP Report: {self.jobNum}')

    except Exception as e:
        jobCreatedNum = 0;
        error_details = traceback.format_exc()
        logger.error(f"ICP Report Creation Error: {e}\nDetails:\n{error_details}")
        self.status_bar_manager.update_status_bar(f'Failed to create ICP Report: {self.jobNum}')

    if(jobCreatedNum == 1):
        updateReport(self.ui.statusHeaderLabel, self.tempDB, self.jobNum, self.reportNum)

def get_footer_comment_temp(database, paramNum):
    #footerComment = retrieveFooterComment(self, 'ICP', self.parameter)
    footerComment = getChmReportFooter(database, paramNum)

    if(footerComment is None):
        return ''

    return footerComment.split('\n')
