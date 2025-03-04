import traceback


from base_logger import logger
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem, QAbstractItemView

from modules.dialogs.basic_dialogs import okay_dialog, error_dialog
from modules.utils.excel_utils import validate_excel_creation_data
from modules.utils.report_utils import ( populate_samples_layout , update_report_status, get_selected_report_authors, get_report_footer_comment )

from pages.reports_page.chm.chm_report_controller import ChmReportController
from pages.reports_page.chm.chm_report_model import ChmReportModel
from pages.reports_page.chm.chm_report_view import ChmReportView
from pages.reports_page.excel.chm_excel_report import ChmExcelReport

def chm_report_setup(self, sample_names, sample_tests):
    logger.info('Entering chm_report_setup')

    report_column_names = ['Tests Name', 'Text Name', 'Display Name', 'Unit', '% Recovery', 'Distillation', 'So']
    comment_column_names = ['Tests Name', 'Lower Limits', 'Upper Limits', 'Side Comment', 'Display', 'Extra Comments']

    job_num = self.active_report.job_num
    param_id = self.active_report.param_id
    dilution = self.active_report.dilution
    sample_names = self.active_report.sample_names
    sample_tests = self.active_report.sample_tests

    logger.info(f'sample_tests: {sample_tests}')
    logger.info(f'sample_names: {sample_names}')

    #chm_report_table_setup(self.ui.dataTable, report_column_names, sample_names)
    chm_comments_table_setup(self.ui.comments_table, comment_column_names)
    #populate_samples_layout(self.ui.samplesContainerLayout_2, sample_names)

    # clear out the previous information and table before starting
    clean_up_previous_chm_report(self)

    self.chm_report_model = ChmReportModel(self.tests_manager, self.chm_test_data_manager, job_num, dilution, sample_tests, sample_names)
    self.chm_report_view = ChmReportView(self.ui.dataTable, self.ui.comments_table, self.ui.reportsTab, self.ui.samplesContainerLayout_2, self.ui.createChmReportBtn)
    self.chm_report_controller = ChmReportController(self.chm_report_model, self.chm_report_view)

    #TODO: ask the user if they would like to load in duplicate information

    # Connect the button with the updated parameters
    self.ui.createChmReportBtn.clicked.connect(lambda: handle_create_chem_btn(self))
    self.ui.save_report_btn.clicked.connect(lambda: handle_save_chm_report(self, True))

def clean_up_previous_chm_report(self):
    if hasattr(self, 'chm_report_view'):
        self.chm_report_view.clear_table()  # Clear the table to reset its state
        self.chm_report_view = None   # Dereference old view
    if hasattr(self, 'chem_report_model'):
        self.chm_report_model = None  # Dereference old model
    if hasattr(self, 'chm_report_controller'):
        self.chm_report_controller = None  # Dereference old controller

    # Disconnect previous connections, if any
    try:
        self.ui.save_report_btn.clicked.disconnect()
    except TypeError:
        pass

    try:
        self.ui.createChmReportBtn.clicked.disconnect()
    except TypeError:
        pass # If no connection exists, just pass

def chm_comments_table_setup(table, column_names):
    table.setColumnCount(len(column_names))

    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    # set the column width for tables
    table.setColumnWidth(0, 100)
    table.setColumnWidth(1, 100)
    table.setColumnWidth(2, 100)
    table.setColumnWidth(3, 200)
    table.setColumnWidth(4, 100)

    table.horizontalHeader().setStretchLastSection(True)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    setup_column_headers(table, column_names)

def chm_report_table_setup(table, column_names, sample_names):
    logger.info('Entering chm_report_table_setup')

    col_count = len(column_names) + len(sample_names) + 1
    table.setColumnCount(col_count)

    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(True)

    setup_column_headers(table, column_names)
    setup_sample_headers(table, sample_names, len(column_names))

    table.setHorizontalHeaderItem(col_count-1, QTableWidgetItem('Action'))

def setup_column_headers(table, column_names):
    for i, name in enumerate(column_names):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(name))

def setup_sample_headers(table, sample_names, start_index):
    for i, (key, _) in enumerate(sample_names.items(), start=start_index):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(key))


#TODO: move this into chm_controller
def handle_save_chm_report(self, enable_dialog=False):
    logger.info(f'Entering handle_save_chm_report with enable_dialog: {enable_dialog}')

    save_list = self.chm_report_controller.save_data()

    total_items = len(save_list)
    total_saved = 0

    for item in save_list:
        sample_num = item[0]
        test_id = item[1]
        test_val = item[2]
        recovery_val = item[3]
        unit_val = item[4]
        job_num = item[5]

        test_exists = self.chm_test_data_manager.check_test_exists(job_num, sample_num, test_id)

        logger.debug(f'test_exists: {test_exists} | sample_name: {job_num}-{sample_num}')

        if(test_exists):
            self.chm_test_data_manager.update_test(job_num, sample_num, test_id, test_val, recovery_val, unit_val)
            total_saved+=1;
            continue

        elif(test_id):
            add_test_status = self.chm_test_data_manager.add_test(job_num, sample_num, test_id, test_val, recovery_val, unit_val)

            if(not add_test_status):
                logger.warning(f'There was an error adding {job_num}-{sample_num}')
            else:
                total_saved+=1
        else:
            logger.debug(f"test_id:{test_id} doesn't exist ")

    if(enable_dialog):
        print('message display')
        okay_dialog(title='Successfully saved', message=f'Successfully saved {total_saved}/{total_items} tests')

    # TODO: save client information (test_names, )


# TODO: Save the other client info
# TODO: Authors, client info, samples name sample data
# TODO: can save the data through matching the rows

def handle_create_chem_btn(self):
    logger.info('Entering handle_create_chem_btn')

    param_id = self.active_report.param_id
    job_num = self.active_report.job_num
    report_id = self.active_report.report_id

    sample_names = self.chm_report_controller.export_sample_names()
    sample_data, display_name, recovery_vals, units, so_vals, hidden_rows = self.chm_report_controller.export_data()
    lower_limits, upper_limits, side_comments, extra_comments = self.chm_report_controller.export_comments()

    author_names = get_selected_report_authors(self)
    footer_comment = get_report_footer_comment(self.footers_manager, param_id, 2)
    client_info = self.client_manager.get_all_client_info()

    if(not validate_excel_creation_data(author_names, sample_names, client_info)):
        return

    try:
        # save the information
        handle_save_chm_report(self)

        logger.info(f'Preparing to create CHM Report {job_num}')

        #TODO: can condense into a single object or something like damn
        chm_excel_manager = ChmExcelReport(client_info, job_num, author_names, side_comments, extra_comments, footer_comment, sample_names, sample_data, display_name, units, recovery_vals, so_vals, lower_limits, upper_limits, hidden_rows)
        file_path, fileName = chm_excel_manager.create_report()

        okay_dialog(title = f'Success Created CHM Report: {job_num}', message= f'CHM Report Creation Successful File: {fileName}')

        self.logger.info(f'CHM Report Creation Successful: {job_num}')
        self.status_bar_manager.update_status_bar(f'Success Created CHM Report: {job_num}')

        update_report_status(self, job_num, report_id)

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"CHM Report Creation Error: {e}\nDetails:\n{error_details}")

        error_dialog(title = f'Failed to create CHM Report: {job_num}', message = 'Report generation failed due to an unexpected error.')
        self.status_bar_manager.update_status_bar(f'Failed to create CHM Report: {job_num}')

