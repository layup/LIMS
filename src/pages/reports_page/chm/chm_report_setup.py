import traceback


from base_logger import logger
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem

from modules.dialogs.basic_dialogs import okay_dialog, error_dialog

#TODO: maybe improve the SampleWidget
from pages.reports_page.reports.report_utils import ( populateSamplesContainer, EmptyDataTableError, updateReport,
    createExcelErrorCheck, get_selected_report_authors, get_report_footer_comment )
from pages.reports_page.chm.chm_report_controller import ChmReportController
from pages.reports_page.chm.chm_report_model import ChmReportModel
from pages.reports_page.chm.chm_report_view import ChmReportView
from pages.reports_page.reports.ExcelReports import ChmExcelReport

def chm_report_setup(self):
    # prepare the report page for data
    column_names = ['Tests Name', 'Text Name', 'Display Name', 'Unit', 'Distillation Factor', 'Standard Recovery']
    chem_report_table_setup(self.ui.dataTable, column_names, self.sampleNames)
    chem_sample_widget_setup(self.ui.samplesContainerLayout_2, self.sampleNames)

    # clear out the previous information and table before starting
    clean_up_previous_chm_report(self)

    self.chem_report_model = ChmReportModel(self.tempDB, self.jobNum, self.dilution, self.sampleTests)
    self.chem_report_view = ChmReportView(self.ui.dataTable, self.ui.createChmReportBtn)
    self.chem_report_controller = ChmReportController(self.chem_report_model, self.chem_report_view, self.sampleNames)

    # Connect the button with the updated parameters
    self.ui.createChmReportBtn.clicked.connect(
        lambda: handle_create_chem_btn(self)
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

    # Disconnect previous connections, if any
    try:
        self.ui.createChmReportBtn.clicked.disconnect()
    except TypeError:
        # If no connection exists, just pass
        pass

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

def handle_create_chem_btn(self):
    logger.info('Entering handle_create_chem_btn')

    sample_data, display_name, recovery_vals, units = self.chem_report_controller.export_data()
    author_names = get_selected_report_authors(self)
    footerComment = get_report_footer_comment(self.footers_manager, self.parameter, 2)
    client_info = self.client_manager.get_client_info()

    # TODO: error check if valid to create report
    if(createExcelErrorCheck(self)):
        return

    try:
        logger.info(f'Preparing to create CHM Report {self.jobNum}')

        chm_excel_manager = ChmExcelReport(client_info, self.jobNum, author_names, footerComment, self.sampleNames, sample_data, display_name, units, recovery_vals)
        filePath, fileName = chm_excel_manager.create_report()

        okay_dialog(title = f'Success Created CHM Report: {self.jobNum}', message= f'CHM Report Creation Successful File: {fileName}')

        self.logger.info(f'CHM Report Creation Successful: {self.jobNum}')
        self.status_bar_manager.update_status_bar(f'Success Created CHM Report: {self.jobNum}')

        # TODO: Save the other client info
        # TODO: Authors, client info, samples name. sample data
        # TODO: can save the data through matching the rows

        updateReport(self.ui.statusHeaderLabel, self.tempDB, self.jobNum, self.reportNum)

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"CHM Report Creation Error: {e}\nDetails:\n{error_details}")

        error_dialog(title = f'Failed to create CHM Report: {self.jobNum}', message = 'CHM Report Creation Error')
        self.status_bar_manager.update_status_bar(f'Failed to create CHM Report: {self.jobNum}')







