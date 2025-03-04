import traceback

from base_logger import logger

from PyQt5.QtWidgets import QHeaderView, QDialog, QAbstractItemView

from modules.dialogs.open_job_dialog import OpenJobDialog
from modules.widgets.TableFooterWidget import TableFooterWidget
from modules.widgets.BasicSearchBar import BasicSearchBar

from pages.history_page.lab_section.lab_history_model import LabHistoryModel
from pages.history_page.lab_section.lab_history_view import LabHistoryView
from pages.history_page.lab_section.lab_history_controller import LabHistoryController

from pages.reports_page.reports_config import open_existing_report

def lab_section_setup(self):
    self.logger.info('Entering lab_section_setup ...')

    headers =  ['Job Number', 'Report Type', 'Parameter', 'Dilution Factor', 'Creation Date', 'Status', 'Action']

    lab_table_setup(self.ui.reportsTable, headers)
    lab_search_setup(self, headers)
    lab_footer_setup(self)

    # create lab Model-Controller-View
    self.chem_history_model = LabHistoryModel( self.parameters_manager, self.reports_manager)
    self.chem_history_view = LabHistoryView(self.ui.reportsTable, self.lab_history_footer, self.lab_history_search)
    self.chem_history_controller = LabHistoryController(self.chem_history_model, self.chem_history_view)

    # Connect Signals
    self.chem_history_controller.openReport.connect(lambda job_item :open_btn_pressed(self, job_item))
    self.ui.createReportBtn.clicked.connect(self.create_report.start)

def lab_table_setup(table, headers):
    logger.info('Entering lab_table_setup')

    # Disable editing for the entire table
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Set the column count
    table.setColumnCount(len(headers))

    # Set the column names and info
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setHorizontalHeaderLabels(headers)

    table.verticalHeader().setVisible(True)
    table.verticalHeader().setFixedWidth(30)

def lab_footer_setup(self):
    logger.info('Entering lab_footer_setup')

    self.lab_history_footer = TableFooterWidget()
    self.ui.historyLayout.addWidget(self.lab_history_footer)

def lab_search_setup(self, headers):
    logger.info('Entering lab_search_setup')

    # define and add widget
    self.lab_history_search = BasicSearchBar()
    self.ui.horizontalLayout_5.insertWidget(1, self.lab_history_search)

    # set filters
    self.lab_history_search.filters.addItems(headers)
    self.lab_history_search.filters.setCurrentIndex(0)

def open_btn_pressed(self, data):
    logger.info('Entering open_btn_pressed')
    logger.info(f'{data.__repr__}')

    try:
        popup = OpenJobDialog(data.jobNum)
        result = popup.exec_()

        if(result == QDialog.Accepted):
            self.logger.info('Opening Existing Report')
            open_existing_report(self, data)

        else:
            self.logger.info("Report doesn't exist in database'")

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Custom Error Message: {e}\nDetails:\n{error_details}")