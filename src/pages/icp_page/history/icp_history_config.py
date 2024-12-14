
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from PyQt5.QtWidgets import (
    QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget,
    QHBoxLayout
)

from modules.widgets.TableFooterWidget import TableFooterWidget
from modules.widgets.BasicSearchBar import BasicSearchBar

from pages.icp_page.history.icp_history_view import IcpHistoryView
from pages.icp_page.history.icp_history_model import IcpHistoryModel
from pages.icp_page.history.icp_history_controller import IcpHistoryController

from modules.dialogs.Icp_view_data_dialog import ViewIcpData

def icp_history_setup2(self):
    logger.info('Entering icp_history_setup2')
    headers = ['Sample Number', 'Job Number', 'Machine Type', 'File Name', 'Upload Date', 'Actions']

    icp_history_table_setup(self.ui.icpTable, headers)
    icp_history_footer_setup(self)
    icp_history_search_setup(self, headers)

    self.icp_history_model = IcpHistoryModel(self.tempDB)
    self.icp_history_view = IcpHistoryView(self.ui.icpTable,  self.icp_history_footer, self.icp_history_search,  self.ui.icpUploadBtn)
    self.icp_history_controller = IcpHistoryController(self.icp_history_model, self.icp_history_view)

    # Connect signals
    self.icp_history_controller.openReport.connect(lambda current_item: handle_view_report(self.tempDB, current_item))

def icp_history_table_setup(table, headers):

    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)

    table.verticalHeader().setVisible(True)

    smallCol = 140
    medCol = 240
    bigCol = 340

    # Set the width of the tables
    table.setColumnWidth(0, smallCol)
    table.setColumnWidth(1, smallCol)
    table.setColumnWidth(2, smallCol)
    table.setColumnWidth(3, medCol)
    table.setColumnWidth(4, smallCol)
    table.setColumnWidth(5, medCol)


def icp_history_footer_setup(self):
    self.icp_history_footer = TableFooterWidget()
    self.ui.icpHistoryLayout.addWidget(self.icp_history_footer)

def icp_history_search_setup(self, headers):
    # define and add widget
    self.icp_history_search = BasicSearchBar()
    self.ui.horizontalLayout_24.insertWidget(1, self.icp_history_search)

    # set filters
    self.icp_history_search.filters.addItems(headers)
    self.icp_history_search.filters.setCurrentIndex(0)

def handle_view_report(db, current_item):

    dialog = ViewIcpData(db, current_item)
    dialog.exec()

