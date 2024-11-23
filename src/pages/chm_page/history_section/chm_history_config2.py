
from base_logger import logger
import math

from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt, QAbstractTableModel,Qt, QModelIndex, QVariant, QEvent
from PyQt5.QtWidgets import (
    QHeaderView, QMessageBox, QPushButton, QWidget, QHBoxLayout, QAbstractItemView,
    QTableWidget, QTableWidgetItem,QLineEdit, QTableView, QStyledItemDelegate
)

from modules.dialogs.basic_dialogs import yes_or_no_dialog, save_or_cancel_dialog
from modules.dbFunctions import getTestsName, deleteChmTestDataItem, updateChmTestsData
from modules.constants import  TABLE_ROW_HEIGHT, TABLE_COL_SMALL, TABLE_COL_MED
from modules.utils.chm_utils import getParameterAndUnitTypes, getParameterTypeNum, parameterItem
from modules.widgets.dialogs import deleteBox, saveMessageDialog
from modules.widgets.SideEditWidget import SideEditWidget2, hideSideEditWidget
from modules.widgets.TableFooterWidget import TableFooterWidget


from pages.chm_page.history_section.HistoryManager import HistoryController, HistoryModel, HistoryView



#! should just have a global variable that saves the tests so I don't have to keep on loading it in and out again
#TODO: if on page 1 reload, but other pages and searches then it is fine

##################################################################
#   Setup Section
##################################################################

def chem_history_section_setup(self):
    logger.info('Entering chem_history_section_setup')


    side_edit_setup(self)
    history_table_setup(self.ui.chmInputTable)
    history_filters_setup(self)

    self.ui.footerWidget = TableFooterWidget()
    self.ui.chmDatabaseLayout.addWidget(self.ui.footerWidget)
    self.history_model = HistoryModel(self.tempDB)
    self.history_view = HistoryView(self.ui.chmInputTable, self.ui.sideEditWidget2, self.ui.footerWidget, self.ui.chmSearchLine1, self.ui.chmSearchBtn1, self.ui.chemHistoryFilter)

    self.history_controller = HistoryController(self.history_model, self.history_view)



    '''
        1. state manager (manages the data that is displayed and save)
            - control footer states
            - control table view items
            - control side_view status
            - data
        2. table view  (manages what the tables show)
            2.1 action widget -> trigger side_view
        3. footer view
        4. side view
            - receive data
            - update table
            - update database
        5. search feature


        i have the history itemed passed into the side_edit so when that data gets saved it will save the item itself

        table view <-> data
        footer view <-> state
        filter <-> state
        search <-> data, table view, footer view





    '''

##################################################################
#   Filter functions
##################################################################

def history_filters_setup(self):
    logger.info('Entering history_filters_setup')

    filter_names = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Unit Value', 'Standard', 'Upload Date']



    self.ui.chemHistoryFilter.addItems(filter_names)
    self.ui.chemHistoryFilter.setCurrentIndex(6)

    #self.ui.chemHistoryFilter.currentIndexChanged.connect(lambda new_index: history_filter_changed(self, new_index))

def history_filter_changed(self, new_index):

    filter_col = {
        'Job Number': 0,
        'Tests Name': 2,
        'Upload Date': 6
    }

    selected_text = self.ui.chemHistoryFilter.currentText()
    table_col = filter_col[selected_text]


    #TODO: update the table view section
    #self.history_table_view.filter_table_by(filter_column)


def history_table_setup(table):

    # Define table columns
    column_headers = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Unit Value', 'Standard Value', 'Upload Date' , 'Actions']

    table.setColumnCount(len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)
    table.horizontalHeader().setStretchLastSection(True)

    #table.setSortingEnabled(True)
    table.setSortingEnabled(False)

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

    # Set the QComboBox Items
    parameterType, unitType = getParameterAndUnitTypes2(self.tempDB)


    self.ui.sideEditWidget2.loads_tests(parameterType, unitType)

    # load in the

    #self.ui.sideEditWidget2.set_drop_down(parameterType, unitType)
    #self.ui.sideEditWidget2.set_combo_disabled(False)
    #self.ui.sideEditWidget2.set_primary_key_editable(False)

    # Connect signals
    #self.ui.sideEditWidget2.cancelBtn.clicked.connect(lambda: hideSideEditWidget(self.ui.sideEditWidget2))
    #self.ui.sideEditWidget2.saveBtn.clicked.connect(lambda: sideEditWidgetSaveBtnClicked(self))

def getParameterAndUnitTypes2(database):
    query = 'SELECT testNum, testName FROM Tests WHERE testName NOT LIKE "%ICP%" AND type = "C" ORDER BY testName ASC'
    results = database.query(query)

    unitTypes =  ['TCU', 'ug/L', 'mg/g']

    # Convert results into readable
    parameterTypes = [(item[0], item[1]) for item in results]

    return parameterTypes, unitTypes