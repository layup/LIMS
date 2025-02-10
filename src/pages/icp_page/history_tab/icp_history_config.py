
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout)

from modules.widgets.TableFooterWidget import TableFooterWidget
from modules.widgets.BasicSearchBar import BasicSearchBar

from pages.icp_page.history_tab.icp_history_view import IcpHistoryView
from pages.icp_page.history_tab.icp_history_model import IcpHistoryModel
from pages.icp_page.history_tab.icp_history_controller import IcpHistoryController

from modules.dialogs.Icp_view_data_dialog import ViewIcpData

def icp_history_setup(self):
    logger.info('Entering icp_history_setup')
    headers = ['Sample Number', 'Job Number', 'Machine Type', 'File Name', 'Upload Date', 'Actions']

    icp_history_table_setup(self.ui.icpTable, headers)
    icp_history_footer_setup(self)
    icp_history_search_setup(self, headers)

    self.icp_history_model = IcpHistoryModel(self.db, self.icp_test_data_manager)
    self.icp_history_view = IcpHistoryView(self.ui.icpTable,  self.icp_history_footer, self.icp_history_search,  self.ui.icpUploadBtn)
    self.icp_history_controller = IcpHistoryController(self.icp_history_model, self.icp_history_view)

    # Connect signals
    self.icp_history_controller.openReport.connect(lambda current_item: handle_view_report(self, current_item))

def icp_history_table_setup(table, headers):

    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)

    table.verticalHeader().setVisible(True)

    small_col = 140
    med_col = 240
    big_col = 340

    # Set the width of the tables
    table.setColumnWidth(0, small_col)
    table.setColumnWidth(1, small_col)
    table.setColumnWidth(2, small_col)
    table.setColumnWidth(3, med_col)
    table.setColumnWidth(4, small_col)
    table.setColumnWidth(5, med_col)


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

def handle_view_report(self, current_item):

    dialog = ViewIcpData(self.icp_test_data_manager, current_item)
    dialog.delete_item.connect(lambda self=self:handle_delete_icp_item(self))
    dialog.exec()

def handle_delete_icp_item(self):
    logger.info(f'Entering handle_delete_icp_item')

    #TODO: manage when delete on other pages and etc

    self.icp_history_controller.update_view()



