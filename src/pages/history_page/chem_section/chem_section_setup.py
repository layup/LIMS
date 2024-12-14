import sqlite3
import traceback

from base_logger import logger

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QHeaderView, QDialog, QPushButton, QAbstractItemView, QTableWidgetItem, QCompleter

from modules.constants import TABLE_ROW_HEIGHT, REPORT_NAME, REPORT_STATUS
from modules.dbFunctions import searchJobsList, getAllJobsList, getAllJobNumbersList, getFrontHistory, getParameterName
from modules.dialogs.open_job_dialog import OpenJobDialog
from modules.widgets.TableFooterWidget import TableFooterWidget
from modules.widgets.BasicSearchBar import BasicSearchBar

from pages.history_page.chem_section.ChemHistoryModel import ChemHistoryModel
from pages.history_page.chem_section.ChemHistoryView import ChemHistoryView
from pages.history_page.chem_section.ChemHistoryController import ChemHistoryController

from pages.reports_page.reports_config import open_existing_job

def chem_section_setup(self):
    self.logger.info(f'Entering chem_section_setup ...')

    headers =  ['Job Number', 'Report Type', 'Parameter', 'Dilution Factor', 'Creation Date', 'Status', 'Action']

    chem_table_setup(self.ui.reportsTable, headers)
    chem_search_setup(self, headers)
    chem_footer_setup(self)

    self.chem_history_model = ChemHistoryModel(self.tempDB)
    self.chem_history_view = ChemHistoryView(self.ui.reportsTable, self.chem_history_footer, self.chem_history_search)
    self.chem_history_controller = ChemHistoryController(self.chem_history_model, self.chem_history_view)

    # Connect Signals
    self.chem_history_controller.openReport.connect(lambda job_item :open_btn_pressed(self, job_item))


def chem_table_setup(table, headers):
    rowHeight = 25

    # Disable editing for the entire table
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Set the column count
    table.setColumnCount(len(headers))

    # Set the column names and info
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setHorizontalHeaderLabels(headers)

    ''' OPT: Setting the tool tips for the headers

    for col in range(table.columnCount()):
        header_item = QTableWidgetItem(headers[col])
        header_item.setToolTip('This is a test')
        table.setHorizontalHeaderItem(col, header_item)

    '''

    table.verticalHeader().setVisible(True)
    table.verticalHeader().setFixedWidth(30)

def chem_footer_setup(self):
    self.chem_history_footer = TableFooterWidget()
    self.ui.historyLayout.addWidget(self.chem_history_footer)

def chem_search_setup(self, headers):
    # define and add widget
    self.chem_history_search = BasicSearchBar()
    self.ui.horizontalLayout_5.insertWidget(1, self.chem_history_search)

    # set filters
    self.chem_history_search.filters.addItems(headers)
    self.chem_history_search.filters.setCurrentIndex(0);

def historySearchSetup(self):
    self.logger.info(f'Entering historyPageSetup')
    # Get the all of the jobNums for the completer
    jobList = getAllJobNumbersList(self.tempDB)
    jobList_as_strings = [str(item) for item in jobList]

    # Sets the completers
    completer = QCompleter(jobList_as_strings)
    completer.setCompletionMode(QCompleter.PopupCompletion)  # Set completion mode to popup
    completer.setMaxVisibleItems(10)

    self.ui.reportsSearchLine.setCompleter(completer)
    self.ui.reportsSearchLine.setPlaceholderText("Enter Job Number...")

def open_btn_pressed(self, data):
    logger.info('Entering open_existing_job')
    logger.info(f'{data.__repr__()}')

    try:
        popup = OpenJobDialog(data.jobNum)
        result = popup.exec_()

        if(result == QDialog.Accepted):
            self.logger.info('Opening Existing Report')
            open_existing_job(self, data)

        else:
            self.logger.info("Report doesn't exist in database'")

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Custom Error Message: {e}\nDetails:\n{error_details}")






