
from base_logger import logger

from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt, QAbstractTableModel,Qt, QModelIndex, QVariant, QEvent
from PyQt5.QtWidgets import (
    QHeaderView, QMessageBox, QPushButton, QWidget, QHBoxLayout, QAbstractItemView,
    QTableWidget, QTableWidgetItem,QLineEdit, QTableView, QStyledItemDelegate
)

from modules.dialogs.basic_dialogs import yes_or_no_dialog, save_or_cancel_dialog
from modules.dbFunctions import getTestsName, deleteChmTestDataItem, updateChmTestsData
from modules.constants import  TABLE_ROW_HEIGHT, TABLE_COL_SMALL, TABLE_COL_MED
from modules.widgets.SideEditWidget import SideEditWidget2, hideSideEditWidget
from modules.widgets.TableFooterWidget import TableFooterWidget

from pages.chm_page.history_tab.HistoryController import HistoryController
from pages.chm_page.history_tab.HistoryModel import HistoryModel
from pages.chm_page.history_tab.HistoryView import HistoryView

#! should just have a global variable that saves the tests so I don't have to keep on loading it in and out again
#TODO: if on page 1 reload, but other pages and searches then it is fine

##################################################################
#   Setup Section
##################################################################

def chem_history_tab_setup(self):
    logger.info('Entering chem_history_section_setup')

    side_edit_setup(self)
    history_table_setup(self.ui.chmInputTable)
    history_filters_setup(self)
    history_footer_setup(self)

    self.history_model = HistoryModel(self.tempDB)
    self.history_view = HistoryView(self.ui.chmInputTable, self.ui.sideEditWidget2, self.ui.footerWidget, self.ui.chmSearchLine1, self.ui.chmSearchBtn1, self.ui.chemHistoryFilter)
    self.history_controller = HistoryController(self.history_model, self.history_view)

    # connect signal to switch page
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))


##################################################################
#   Filter functions
##################################################################

def history_filters_setup(self):
    logger.info('Entering history_filters_setup')

    filter_names = ['Job Num', 'Sample Num', 'Tests Name', 'Test Value', 'Unit Value', '% Recovery', 'Upload Date']

    self.ui.chemHistoryFilter.addItems(filter_names)
    self.ui.chemHistoryFilter.setCurrentIndex(6)

def history_footer_setup(self):
    logger.info('Entering history_footer_setup')
    self.ui.footerWidget = TableFooterWidget()
    self.ui.chmDatabaseLayout.addWidget(self.ui.footerWidget)

def history_table_setup(table):
    logger.info('Entering history_table_setup')

    # Define table columns
    column_headers = ['Job Num', 'Sample Num', 'Tests Name', 'Test Value', 'Unit Value', '% Recovery', 'Upload Date' , 'Actions']

    table.setColumnCount(len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)
    table.horizontalHeader().setStretchLastSection(True)

    # Show the vertical rows
    table.verticalHeader().setVisible(True)
    table.verticalHeader().setFixedWidth(30)

    # Disable Editing of the table
    table.setEditTriggers(QTableWidget.NoEditTriggers)

    # Set the width of the tables
    table.setColumnWidth(0, TABLE_COL_SMALL)
    table.setColumnWidth(1, TABLE_COL_SMALL)
    table.setColumnWidth(2, TABLE_COL_MED)
    table.setColumnWidth(3, TABLE_COL_SMALL)
    table.setColumnWidth(4, TABLE_COL_SMALL)
    table.setColumnWidth(5, TABLE_COL_SMALL)
    table.setColumnWidth(6, TABLE_COL_SMALL)

    # Set the last column to stretch
    table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)

##################################################################
#   Side edit popup functions
##################################################################

def side_edit_setup(self):
    logger.info('Entering side_edit_setup')

    # Get the list of parameters and allowed unit types
    self.ui.sideEditWidget2 = SideEditWidget2()
    self.ui.sideEditWidget2.setVisible(False)

    # Add our widget to the correct layout
    self.ui.horizontalLayout_64.addWidget(self.ui.sideEditWidget2)

    test_names = self.tests_manager.get_test_by_type('C')
    unit_names = self.units_manager.get_unit_names()

    self.ui.sideEditWidget2.loads_tests(test_names, unit_names)