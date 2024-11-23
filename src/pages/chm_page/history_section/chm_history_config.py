
from base_logger import logger
import math

from PyQt5.QtCore import pyqtSlot, QDir, pyqtSignal, QObject, Qt, QAbstractTableModel,Qt, QModelIndex, QVariant, QEvent
from PyQt5.QtWidgets import (
    QHeaderView, QMessageBox, QPushButton, QWidget, QHBoxLayout, QAbstractItemView,
    QTableWidget, QTableWidgetItem,QLineEdit, QTableView, QStyledItemDelegate
)

from modules.dialogs.basic_dialogs import yes_or_no_dialog
from modules.dbFunctions import getTestsName, deleteChmTestDataItem, updateChmTestsData
from modules.constants import  TABLE_ROW_HEIGHT, TABLE_COL_SMALL, TABLE_COL_MED
from modules.utils.chm_utils import getParameterAndUnitTypes, getParameterTypeNum, parameterItem
from modules.widgets.dialogs import deleteBox, saveMessageDialog
from modules.widgets.SideEditWidget import SideEditWidget, hideSideEditWidget
from modules.widgets.TableFooterWidget import TableFooterWidget


from pages.chm_page.history_section.DatabaseTableModel import DatabaseTableModel
from pages.chm_page.history_section.DatabaseTableView import DatabaseTableView

##################################################################
#   Setup Section
##################################################################

def chm_database_setup(self):
    logger.info('Entering chm_database_setup')

    side_edit_setup(self)
    filters_setup(self)

    # Define the icp history model and table view
    self.chmHistoryDataModel  = DatabaseTableModel(self.tempDB)
    self.chmTableView = DatabaseTableView(self.tempDB, self.ui.chmInputTable, self.ui.chmDatabaseLayout, self.chmHistoryDataModel, self.ui.sideEditWidget2)

    #TODO: I wonder why this is being kind of fucky
    self.chmTableView.dialogAction.connect(lambda row, new_data: chmTestsSaveProcess(self, row, new_data));

    # update footer (buttons, page change, filter update) -> update data
    # update search -> update data and footer
    # update data -> update table
    self.chmHistoryDataModel.dataChanged.connect(lambda newData: self.chmTableView.update_table(newData))

    # Connect Signals
    self.ui.chmSearchBtn1.clicked.connect(lambda: self.chmTableView.handle_search_text(self.ui.chmSearchLine1.text()))
    self.ui.chmSearchLine1.returnPressed.connect(lambda: self.chmTableView.handle_search_text(self.ui.chmSearchLine1.text()))
    self.ui.chmAddItemBtn.clicked.connect(lambda: self.ui.chmTabWidget.setCurrentIndex(1))



##################################################################
#    SideEditWidget Functions
##################################################################


def filters_setup(self):
    filter_names = ['Job Number', 'Tests Name', 'Upload Date']
    creation_date = 2

    self.ui.chemHistoryFilter.addItem(filter_names)
    self.ui.chemHistoryFilter.setCurrentText(filter_names[2])

    #TODO: connect signal



#******************************************************************
#    SideEditWidget Functions
#******************************************************************

def side_edit_setup(self):
    logger.info('Entering side_edit_setup')

    # Get the list of parameters and allowed unit types
    self.ui.sideEditWidget2 = SideEditWidget()
    self.ui.sideEditWidget2.setVisible(False)

    # Add our widget to the correct layout
    self.ui.horizontalLayout_64.addWidget(self.ui.sideEditWidget2)

    # Set the QComboBox Items
    parameterType, unitType = getParameterAndUnitTypes(self.tempDB)
    self.ui.sideEditWidget2.set_drop_down(parameterType, unitType)
    self.ui.sideEditWidget2.set_combo_disabled(False)
    self.ui.sideEditWidget2.set_primary_key_editable(False)

    # Connect signals
    self.ui.sideEditWidget2.cancelBtn.clicked.connect(lambda: hideSideEditWidget(self.ui.sideEditWidget2))
    self.ui.sideEditWidget2.saveBtn.clicked.connect(lambda: sideEditWidgetSaveBtnClicked(self))

def sideEditWidgetSaveBtnClicked(self):
    logger.info(f'Entering sideEditWidgetSaveBtnClicked')
    row = self.ui.sideEditWidget2.get_item()
    new_data = self.ui.sideEditWidget2.get_data()

    logger.debug(f'New Data: {new_data}')

    jobNum = new_data[0]
    sampleNum = new_data[1]
    testName = new_data[2]
    testVal = new_data[3]
    unitType = new_data[4]
    standard = new_data[5]
    testNum = new_data[6]

    jobName = new_data[0] + '-' + new_data[1]

    result = saveMessageDialog(self, 'Overwrite Data?', f'Are you sure you want overwrite existing data for {jobName}?')

    if(result):
        # update table info
        updateTableRowValues(self.ui.chmInputTable, row, new_data)

        # Update the database
        updateChmTestsData(self.tempDB, sampleNum, testNum, jobNum, testVal, standard, unitType)


#******************************************************************
#    Table Functions
#******************************************************************
##################################################################
#    SideEditWidget Functions
##################################################################

def chmTestsSaveProcess(self, row, new_data):
    logger.info(f'Entering chmTestsSaveProcess with parameters: row: {row}, new_data: {new_data}')

    #TODO: check if the new data is valid
    title = 'Confirmation'
    message = 'Are you sure you want to save?'

    save_result = yes_or_no_dialog(title, message)

    if(save_result):
        # Update the table row
        updateRowValues(self.ui.chmInputTable, row, new_data)

        # Save update to database


def updateRowValues(table, row, new_data):
    for col in range(table.columnCount() -2):
        table.item(row, col).setText(new_data[col])

def updateTableRowValues(table, row, new_data):
    for col in range(table.columnCount() -2):
        if(col == 5):

            table.item(row, col).setText(str(float(new_data[col])))
        else:
            table.item(row, col).setText(new_data[col])


##################################################################
#   Helper Functions
##################################################################

def clearLineEdits(widget):
    lineEdits = widget.findChildren(QLineEdit)

    for line in lineEdits:
        line.clear()

    for child in widget.children():
        if(isinstance(child, QLineEdit)):
            clearLineEdits(child)

def getLineEditText(widget):
    lineEdits = widget.findChildren(QLineEdit)

    text_list = []
    for line in lineEdits:
        text_list.append(line.text())

    for child in widget.children():
        if(isinstance(child, QLineEdit)):
            text_list.extend(getLineEditText(child))

    return text_list



