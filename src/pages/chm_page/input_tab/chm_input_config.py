
import math
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (QHBoxLayout, QMessageBox, QPushButton, QTreeWidgetItem, QWidget, QComboBox)

from base_logger import logger
from modules.constants import CHM_REPORT, MED_COL, SMALL_COL
from modules.dialogs.basic_dialogs import save_or_cancel_dialog
from modules.dbFunctions import (addChmTestData, checkChmTestsExist,deleteChmTestDataItem, getChmTestData, updateChmTestsData)
from modules.utils.logic_utils import is_real_number
from modules.dialogs.basic_dialogs import yes_or_no_dialog, error_dialog
from modules.widgets.SideEditWidget import SideEditWidget, hideSideEditWidget

#******************************************************************
#   Setup Functions
#******************************************************************

#TODO: takes in the values from the
#TODO: duplication error
#TODO: center all of the table items
def chm_input_tab_setup(self):
    self.logger.info(f'Entering chm_input_tab_setup')

    side_edit_setup(self)
    new_entry_section_setup(self)

    clear_all_input_sections(self, True)
    format_line_edits(self)
    format_recently_added_tree(self.ui.inputDataTree)

    # Signals
    self.ui.chmProceedBtn.clicked.connect(lambda: on_chmProceedBtn_clicked(self))
    self.ui.chmInputClearBtn.clicked.connect(lambda: clear_all_input_sections(self, False))
    self.ui.chmAddTestsBtn.clicked.connect(lambda:on_chmSampleDataAdd_clicked(self))

def side_edit_setup(self):
    logger.info('Entering side_edit_setup')

    # Get the list of parameters and allowed unit types
    self.ui.sideEditWidget1 = SideEditWidget()

    self.ui.sideEditLayout.addWidget(self.ui.sideEditWidget1) #only valid for layouts
    self.ui.sideEditWidget1.setVisible(False)

    test_names = self.tests_manager.get_test_by_type('C')
    unit_names = self.units_manager.get_unit_names()

    self.ui.sideEditWidget1.set_drop_down(test_names, unit_names)
    self.ui.sideEditWidget1.set_combo_disabled(True)

    # Signals
    self.ui.sideEditWidget1.cancelBtn.clicked.connect(lambda: hideSideEditWidget(self.ui.sideEditWidget1))
    self.ui.sideEditWidget1.save_clicked.connect(lambda tests_info, tree_item: sideEditSaveBtnClicked(self, tests_info, tree_item))

def new_entry_section_setup(self):
    self.logger.info('Entering populate_new_entry_section')

    # remove all existing tests from the database
    self.ui.gcmsTests.clear()
    self.ui.gcmsUnitVal.clear()

    # add empty front place holders
    self.ui.gcmsTests.addItem('')
    self.ui.gcmsUnitVal.addItem('')

    test_names = self.tests_manager.get_test_by_type('C')
    unit_names = self.units_manager.get_unit_names()

    # add the rest of the list items
    self.ui.gcmsUnitVal.addItems(unit_names)

    for item in test_names:
        self.ui.gcmsTests.addItem(item.test_name, userData=item.test_id)


###################################################################
#   Signal Functions
###################################################################

def sideEditSaveBtnClicked(self, new_data, item):
    self.logger.info(f'Entering sideEditSaveBtnClicked with parameters: data: {new_data}, row: {item}')

    save_error_handling(self, new_data, item)


@pyqtSlot()
def on_chmProceedBtn_clicked(self):
    self.logger.info('Entering on_chmProceedBtn_clicked')
    standards, units, testName = get_current_entry_values(self)

    errorCheckList = [0,0,0]

    errorCheckList[0] = 0 if (standards != '' and is_real_number(standards)) else 1
    errorCheckList[1] = 0 if units != '' else 1
    errorCheckList[2] = 0 if testName != '' else 1

    if(sum(errorCheckList) == 0):
        enable_enter_values_section(self, True)
        self.ui.gcmsStandardValShow.setText(standards)
        self.ui.gcmsUnitValShow.setText(units)
        self.ui.gcmsTestsShow.setText(testName)
    else:
        NewEntryErrorDisplay(self, errorCheckList)


@pyqtSlot()
def on_chmSampleDataAdd_clicked(self):
    self.logger.info('Entering on_chmSampleDataAdd_clicked ')

    standards, units, testName = get_current_entry_values(self)
    jobNum, sampleNum, sampleVal = get_current_entered_values(self)

    index = self.ui.gcmsTests.currentIndex()
    testNum = self.ui.gcmsTests.itemData(index, role=Qt.UserRole)

    edit_data = [jobNum, sampleNum, testName, sampleVal, units];

    errorCheckList = [0,0,0]

    errorCheckList[0] = 0 if (jobNum != '' and is_real_number(jobNum)) else 1;
    errorCheckList[1] = 0 if (sampleNum != '' and is_real_number(sampleNum)) else 1;
    errorCheckList[2] = 0 if sampleVal != '' else 1;

    self.logger.debug(f'Input Data Info: {jobNum}-{sampleNum}: {sampleVal}')

    #FIXME: problem arises if reading something to an existing list we can't then delete it afterwords
    if(sum(errorCheckList) == 0):
        todaysDate = date.today()

        existingDataCheck = checkChmTestsExist(self.tempDB, sampleNum, testNum, jobNum)

        if(existingDataCheck):
            title = 'Duplicate Sample'
            duplicate_msg = f"Would you like to overwrite existing sample {jobNum}-{sampleNum}"
            response = yes_or_no_dialog(title, duplicate_msg)

            if(response):
                addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum, todaysDate)

                matchingItem = checkMatchingTreeItems(self.ui.inputDataTree, sampleNum)

                if not matchingItem:
                    add_input_tree_item(self, sampleNum, testName, sampleVal, units, standards, jobNum)

                clear_samples_input(self)
            else:
                clear_samples_input(self)

        else:
            addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum, todaysDate)
            add_input_tree_item(self, sampleNum, testName, sampleVal, units, standards, jobNum)
            clear_samples_input(self)
    else:
        self.logger.error(f'errorCheckList: {errorCheckList}')
        addingSampleDataErrorDisplay(self, errorCheckList)

def checkMatchingTreeItems(treeWidget, targetText):
    # Iterate through the top-level items
    for index in range(treeWidget.topLevelItemCount()):
        item = treeWidget.topLevelItem(index)
        if item.text(0) == targetText:  # Change 0 to the desired column index
            return item

    return None


#******************************************************************
# General Functions
#******************************************************************

def save_error_handling(self, new_data, item):

    self.logger.info('Entering save_error_handling')

    old_jobNum = item.text(0)
    old_sampleNum = item.text(1)

    new_jobNum = new_data[0]
    new_sampleNum = new_data[1]
    new_sampleVal = new_data[3]
    new_unitType = new_data[4]
    new_standard = new_data[5]

    testNum = new_data[6]
    #todaysDate = date.today()

    old_jobName = old_jobNum + '-' + old_sampleNum
    new_jobName = new_data[0] + '-' + new_data[1]

    logger.info(f'Old JobNum: {old_jobName}, new_jobName: {new_jobName}')

    #TODO: problem what if that data already exists in the table
    if(old_jobNum != new_jobNum or old_sampleNum != new_sampleNum):
        existing_data_check = checkChmTestsExist(self.tempDB, new_sampleNum, testNum, new_jobNum)

        if(existing_data_check):
            response = save_or_cancel_dialog('Overwrite Data?', f'Are you sure you want overwrite existing data for {new_jobName} and delete data for {old_jobName} ')

            if(response):
                try:
                    # delete the old job
                    deletedRows = deleteChmTestDataItem(self.tempDB, old_sampleNum, testNum, old_jobNum)

                    # update the existing data with the new data
                    updatedRows = updateChmTestsData(self.tempDB, new_sampleNum, testNum, new_jobNum, new_sampleVal, new_standard, new_unitType)

                    # update table info

                    for col in enumerate(new_data):
                        item.setText(col, new_data[col])

                except Exception as e:
                    print(e)

                    # upload old data back to database
                    # error message

        else:
            response = save_or_cancel_dialog('Overwrite Data?', f'Are you sure you want save {new_jobName} and delete {old_jobNum} ?')

            if(response):

                # delete old data
                deletedRows = deleteChmTestDataItem(self.tempDB, old_sampleNum, testNum, old_jobNum)

                # add new data
                #addChmTestData(self.tempDB, sampleNum, testNum, sampleVal, standards, units, jobNum, todaysDate)

                # update the table info
                for col in enumerate(new_data):
                    item.setText(col, new_data[col])

    else:
        response = save_or_cancel_dialog('Overwrite Data?', f'Are you sure you want overwrite existing data for {new_jobName}?')

        if(response):
            # update the database
            #updateChmTestsData()

            # update table info
            for col in enumerate(new_data):
                item.setText(col, new_data[col])

def NewEntryErrorDisplay(self, errorCheckList):
    errorTitle = 'Cannot Proceed with CHM Process'
    errorMsg = ''

    if(errorCheckList[0] == 1):
        errorMsg += 'Please Enter a Valid Standard Number\n'
    if(errorCheckList[1] == 1):
        errorMsg += 'Please Select a Unit\n'
    if(errorCheckList[2] == 1):
        errorMsg += 'Please Select a Tests\n'

    error_dialog(errorTitle, errorMsg)

def addingSampleDataErrorDisplay(self, errorList):

    errorTitle = 'Cannot add Tests '
    errorMsg = ''

    if(errorList[0] == 1):
        errorMsg += 'Please Enter a Valid Job Number\n'

    if(errorList[1] == 1):
        errorMsg += 'Please Enter a Valid Sample Number\n'

    if(errorList[2] == 1):
        errorMsg += 'Please Enter a Valid Sample Value \n'

    error_dialog(errorTitle, errorMsg)


#******************************************************************
#  Formatting Functions
#******************************************************************

def format_recently_added_tree(tree):

    small_col = 90
    # Setting tree col size
    tree.setColumnWidth(0, small_col)
    tree.setColumnWidth(1, small_col)
    tree.setColumnWidth(2, MED_COL)
    tree.setColumnWidth(3, small_col)
    tree.setColumnWidth(4, small_col)
    tree.setColumnWidth(5, small_col)

def format_line_edits(self):
    logger.info('Entering format_line_edits')

    # allow only float values
    float_validator = QDoubleValidator()
    float_validator.setDecimals(10)

    # allow only int values
    int_validator = QIntValidator()

    # Set validators
    self.ui.gcmsStandardVal.setValidator(float_validator)
    self.ui.gcmsTestsJobNum.setValidator(int_validator)
    self.ui.gcmsTestsSample.setValidator(int_validator)
    self.ui.gcmsTestsVal.setValidator(float_validator)

    # set the limit to characters allowed in line edit
    self.ui.gcmsStandardVal.setMaxLength(20)
    self.ui.gcmsTestsJobNum.setMaxLength(6)
    self.ui.gcmsTestsSample.setMaxLength(6)

def get_current_entry_values(self):
    standards   = self.ui.gcmsStandardVal.text().strip()
    units       = self.ui.gcmsUnitVal.currentText()
    testName    = self.ui.gcmsTests.currentText()

    return standards, units, testName

def get_current_entered_values(self):
    jobNum     = self.ui.gcmsTestsJobNum.text().strip()
    sampleNum   = self.ui.gcmsTestsSample.text().strip()
    sampleVal   = self.ui.gcmsTestsVal.text().strip()

    return jobNum, sampleNum, sampleVal

def enable_enter_values_section(self, status):
    logger.info(f'Entering enable_enter_values_section with parameter: status {repr(status)}')

    self.ui.newEntryWidget.setEnabled(not status)
    self.ui.chmActionWidget.setEnabled(status)
    self.ui.chmTestsValueWidget.setEnabled(status)

def clear_samples_input(self):
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear()

def clear_enter_values_section(self):
    self.ui.gcmsTestsJobNum.clear()
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear()

def clear_active_values_section(self):
    self.ui.gcmsTestsShow.clear()
    self.ui.gcmsUnitValShow.clear()
    self.ui.gcmsStandardValShow.clear()

def reset_new_entry_section(self):
    self.ui.gcmsTests.setCurrentIndex(0)
    self.ui.gcmsUnitVal.setCurrentIndex(0)
    self.ui.gcmsStandardVal.clear()

def clear_all_input_sections(self, clearTable=False):
    self.logger.info(f'Entering clear_all_input_sections with parameter: clearTable: {clearTable}')

    enable_enter_values_section(self, False)
    clear_active_values_section(self)
    clear_enter_values_section(self)
    reset_new_entry_section(self)

    if(clearTable):
        self.ui.inputDataTree.clear()

#******************************************************************
#  Action Function and Classes
#******************************************************************

def add_input_tree_item(self, sampleNum, testName, sampleVal, units, standards, jobNum):
    logger.info('Entering add_input_tree_item')

    tree_widget = self.ui.inputDataTree

    topItem = QTreeWidgetItem(tree_widget)

    topItem.setText(0, jobNum)
    topItem.setText(1, sampleNum)
    topItem.setText(2, testName)
    topItem.setText(3, sampleVal)
    topItem.setText(4, units)
    topItem.setText(5, standards)

    topItem.setTextAlignment(1, Qt.AlignCenter)
    topItem.setTextAlignment(3, Qt.AlignCenter)
    topItem.setTextAlignment(4, Qt.AlignCenter)
    topItem.setTextAlignment(5, Qt.AlignCenter)

    row_index = tree_widget.indexOfTopLevelItem(topItem)

    actionWidget = TreeActionWidget(row_index, topItem)
    actionWidget.edit_clicked.connect(lambda tree_item: handle_edit_clicked(self, tree_item));
    actionWidget.delete_clicked.connect(lambda tree_item: handle_delete_clicked(self, tree_item))

    tree_widget.setItemWidget(topItem, 6, actionWidget)

def handle_edit_clicked(self, item):

    row_index = self.ui.inputDataTree.indexOfTopLevelItem(item)
    data = [item.text(i) for i in range(6)]

    self.logger.debug(f"Edit clicked for row: {row_index}")
    self.logger.debug(f'Current Tree Item: {data}')

    self.ui.sideEditWidget1.setVisible(True)
    self.ui.sideEditWidget1.set_data(data)
    self.ui.sideEditWidget1.set_item(item)


def handle_delete_clicked(self, item):
    row_index = self.ui.inputDataTree.indexOfTopLevelItem(item)

    self.logger.debug(f"Delete clicked for row: {row_index}")

    jobName = item.text(0) +  '-' + item.text(1)
    result = yes_or_no_dialog( f'Are you sure want to delete {jobName}?', "Once you've deleted this item, it cannot be undone")

    if(result):

        # check if edit panel is visible and if the item delete
        if(self.ui.sideEditWidget1.isVisible()):
            if(item is self.ui.sideEditWidget1.get_item()):
                self.logger.info('SideEditWidget Item is the same as the delete tree Item')
                self.ui.sideEditWidget1.setVisible(False)
                self.ui.sideEditWidget1.clear_data()

        # Remove the item from the tree
        self.ui.inputDataTree.takeTopLevelItem(row_index)

        # Delete Item from database

# TODO: might have to move this into other functions so I can read it better lol
class TreeActionWidget(QWidget):

    edit_clicked = pyqtSignal(QTreeWidgetItem)  # Signal for edit button click
    delete_clicked = pyqtSignal(QTreeWidgetItem)  # Signal for delete button click

    def __init__(self, row_index, item, parent=None):
        super().__init__(parent)

        self.item = item
        self.row_index = row_index

        button_widget = QWidget()
        self.layout = QHBoxLayout(button_widget)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignLeft)

        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.on_edit_clicked)
        self.layout.addWidget(self.editBtn)

        self.deleteBtn = QPushButton("Delete")
        self.deleteBtn.clicked.connect(self.on_delete_clicked)
        self.layout.addWidget(self.deleteBtn)

        self.setLayout(self.layout)

    def on_edit_clicked(self):
        # Emit signal to trigger edit action in main window
        self.edit_clicked.emit(self.item)

    def on_delete_clicked(self):
        # Emit signal to trigger delete action in main window
        self.delete_clicked.emit(self.item)
