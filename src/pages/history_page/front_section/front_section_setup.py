import math

from base_logger import logger

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QHeaderView, QDialog, QPushButton, QAbstractItemView, QTableWidgetItem, QCompleter

from modules.widgets.TableFooterWidget import TableFooterWidget
from modules.widgets.BasicSearchBar import BasicSearchBar

from pages.history_page.front_section.FrontHistoryModel import FrontHistoryModel
from pages.history_page.front_section.FrontHistoryView import FrontHistoryView
from pages.history_page.front_section.FrontHistoryController import FrontHistoryController



def front_section_setup(self):
    logger.info('Entering front_section_setup')

    front_search_setup(self)
    front_footer_setup(self)
    front_table_setup(self.ui.frontHistoryTableWidget)

    self.front_history_model = FrontHistoryModel(self.officeDB)
    self.front_history_view = FrontHistoryView(self.ui.frontHistoryTableWidget, self.front_history_footer, self.front_history_search)
    self.front_history_controller = FrontHistoryController(self.front_history_model, self.front_history_view)


def front_table_setup(table):

    headers = ['Job Number', 'Client Name', 'Creation Date', 'Status']

    rowHeght = 25

    # Disable editing for the entire table
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Set the column count
    table.setColumnCount(len(headers))

    # Set the column names and info
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setHorizontalHeaderLabels(headers)

    table.verticalHeader().setVisible(True)
    table.verticalHeader().setFixedWidth(30)

def front_footer_setup(self):
    self.front_history_footer = TableFooterWidget()
    self.ui.frontHistoryVerticalLayout.insertWidget(2, self.front_history_footer)

def front_search_setup(self):

    filters = ['Job Number', 'Client Name', 'Creation Date', 'Status']

    # define and add widget
    self.front_history_search = BasicSearchBar()
    self.ui.frontHistoryVerticalLayout.insertWidget(0, self.front_history_search)

    # set filters
    self.front_history_search.filters.addItems(filters)
    self.front_history_search.filters.setCurrentIndex(0);
