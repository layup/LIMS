import traceback

from base_logger import logger
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem, QAbstractItemView

from modules.dialogs.basic_dialogs import okay_dialog, error_dialog
from modules.utils.excel_utils import validate_excel_creation_data

from modules.utils.report_utils import ( populate_samples_layout, update_report_status, get_selected_report_authors, get_report_footer_comment )
from pages.reports_page.icp.icp_report_view import IcpReportView
from pages.reports_page.icp.icp_report_model import IcpReportModel
from pages.reports_page.icp.icp_report_controller import IcpReportController
from pages.reports_page.excel.icp_excel_report import IcpExcelReport

def icp_report_setup(self, sample_names, sample_tests):
    logger.info('Entering icp_report_setup');

    clean_up_previous_icp_report(self)

    # column header information
    report_column_names = ['Element Name', 'Element Symbol', 'Unit Type', 'Lower Limit', 'Upper Limit', 'Distal factor']
    comment_column_names = ['Element Name', 'Display', 'Footer Comment']

    job_num = self.active_report.job_num
    param_id = self.active_report.param_id
    dilution = self.active_report.dilution

    icp_sample_tests, icp_sample_names = process_icp_tests_names(self, sample_tests, sample_names)


    icp_report_table_setup(self.ui.dataTable, report_column_names, icp_sample_names)
    icp_comments_table_setup(self.ui.comments_table, comment_column_names)
    populate_samples_layout(self.ui.samplesContainerLayout_2, icp_sample_names)

    self.icp_report_model = IcpReportModel(self.icp_test_data_manager, job_num, param_id, dilution, self.elements_manager, icp_sample_tests)
    self.icp_report_view = IcpReportView(self.ui.dataTable, self.ui.comments_table, self.ui.reportsTab, self.ui.reloadDataBtn, self.ui.calcHardnessBtn)
    self.icp_report_controller = IcpReportController(self.icp_report_model, self.icp_report_view)

    # problem is here the data isn't getting new data
    #element_names, element_symbols, element_limits_info, element_units, samples_data = self.icp_report_controller.export_data()

    # Connect the button with the updated parameters
    self.ui.createIcpReportBtn.clicked.connect(
        lambda : handle_create_icp_btn(self, icp_sample_names)
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

    # Disconnect previous connections, if any
    try:
        self.ui.createIcpReportBtn.clicked.disconnect()
    except TypeError:
        # If no connection exists, just pass
        pass

def icp_report_table_setup(table, column_names, sample_names):

    col_count = len(column_names) + len(sample_names)
    table.setColumnCount(col_count)

    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    # set the column width for tables
    table.setColumnWidth(0, 100)

    setup_column_headers(table, column_names)
    setup_sample_headers(table, sample_names, len(column_names))

def icp_comments_table_setup(table, column_names):
    table.setColumnCount(len(column_names))

    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    # set the column width for tables
    table.setColumnWidth(0, 100)
    table.setColumnWidth(1, 100)
    table.horizontalHeader().setStretchLastSection(True)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    setup_column_headers(table, column_names)

def setup_column_headers(table, column_names):
    for i, name in enumerate(column_names):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(name))

def setup_sample_headers(table, sample_names, start_index):
    for i, (key, _) in enumerate(sample_names.items(), start=start_index):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(key))

def process_icp_tests_names(self, sample_tests, sample_names):
    logger.info('Entering process_icp_tests_names')

    approved = {}

    element_symbols = self.elements_manager.get_element_symbols()

    for sample_name, tests in sample_tests.items():
        icp_tests = []

        for test in tests:
            # Check if item has icp or contained within element_symbols
            if('icp' in test.lower() or test.lower() in element_symbols):
                icp_tests.append(test)

        if(len(icp_tests) > 0):
            approved[sample_name] = icp_tests
            logger.info(f'{sample_name}, {icp_tests}')

    new_names_list = {key: sample_names[key] for key in sample_names if key in approved}

    for key, value in new_names_list.items():
        logger.info(f'{key}, {value}')

    return approved, new_names_list

def handle_create_icp_btn(self, sample_names):
    logger.info('Entering handle_create_icp_btn')

    sample_names = self.active_report.sample_names
    param_id = self.active_report.param_id
    job_num = self.active_report.job_num
    report_id = self.self.report_id.report_id

    element_names, element_symbols, element_limits, element_units, samples_data = self.icp_report_controller.export_data()
    author_names = get_selected_report_authors(self)
    footer_comment = get_report_footer_comment(self.footers_manager, param_id, 1)
    client_info = self.client_manager.get_all_client_info()

    if(not validate_excel_creation_data(author_names, sample_names, client_info)):
        return

    try:
        self.logger.info(f'Preparing to create ICP Report {job_num}')

        icp_excel_manager = IcpExcelReport(param_id, client_info, job_num, author_names, footer_comment, sample_names, samples_data, element_names, element_symbols, element_limits, element_units )
        filePath, fileName = icp_excel_manager.create_report()


        # Successful created report and let the user know
        okay_dialog(title = f'Success Created ICP Report: {job_num}', message= f'ICP Report Creation Successful File: {fileName}')
        self.logger.info(f'ICP Report Creation Successful: {job_num}')
        self.status_bar_manager.update_status_bar(f'Successfully Created ICP Report: {job_num}')

        # update the database with the status and info
        update_report_status(self, job_num, report_id)

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"ICP Report Creation Error: {e}\nDetails:\n{error_details}")

        error_dialog(title = f'Failed to create ICP Report:: {job_num}', message = 'ICP Report Creation Error')
        self.status_bar_manager.update_status_bar(f'Failed to create ICP Report: {job_num}')


