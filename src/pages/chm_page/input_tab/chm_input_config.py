

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (QHBoxLayout, QMessageBox, QPushButton, QTreeWidgetItem, QWidget, QComboBox)

from base_logger import logger

from modules.constants import CHM_REPORT, MED_COL, SMALL_COL

from modules.dialogs.basic_dialogs import save_or_cancel_dialog
from modules.utils.logic_utils import is_real_number
from modules.dialogs.basic_dialogs import yes_or_no_dialog, error_dialog
from modules.dialogs.duplicate_dialog import DuplicateDialog
from modules.widgets.SideEditWidget import SideEditWidget, hideSideEditWidget

#******************************************************************
#   Setup Functions
#******************************************************************

#TODO: takes in the values from the
#TODO: duplication error
#TODO: rename those old variable names

def chm_input_tab_setup(self):
    self.logger.info('Entering chm_input_tab_setup')

    side_edit_setup(self)
    input_tree_setup(self)
    new_entry_section_setup(self)

    clear_all_input_sections(self, True)
    format_line_edits(self)
    format_recently_added_tree(self.ui.inputDataTree)

    # Connect Signals
    self.ui.chmProceedBtn.clicked.connect(lambda: on_chmProceedBtn_clicked(self))
    self.ui.chmInputClearBtn.clicked.connect(lambda: clear_all_input_sections(self, False))
    self.ui.chmAddTestsBtn.clicked.connect(lambda: handle_add_chm_sample_btn_clicked(self))

def input_tree_setup(self):
    logger.info('Entering input_tree_setup')

    self.ui.inputDataTree.setHeaderLabels(["Job Number", "Sample #", 'Parameter Name', 'Value', 'Unit', '% Recovery', 'Action'])

    self.ui.inputDataTree.setColumnWidth(0, 120)
    self.ui.inputDataTree.setColumnWidth(1, 80)
    self.ui.inputDataTree.setColumnWidth(2, 200)
    self.ui.inputDataTree.setColumnWidth(4, 80)
    self.ui.inputDataTree.setColumnWidth(5, 80)

    header = self.ui.inputDataTree.header()
    header.setDefaultAlignment(Qt.AlignCenter)


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

    # Connect Side Edit Btn Signals
    self.ui.sideEditWidget1.cancelBtn.clicked.connect(lambda: hideSideEditWidget(self.ui.sideEditWidget1))
    self.ui.sideEditWidget1.save_clicked.connect(lambda tests_info, tree_item: handle_side_item_save_btn_clicked(self, tests_info, tree_item))

def new_entry_section_setup(self):
    self.logger.info('Entering populate_new_entry_section')

    # remove all existing tests from the database
    self.ui.gcmsTests.clear()
    self.ui.gcmsUnitVal.clear()

    # add empty front place holders
    self.ui.gcmsTests.addItem('')
    self.ui.gcmsUnitVal.addItem('')
    self.ui.chm_selected_units.addItem('')

    test_names = self.tests_manager.get_test_by_type('C')
    unit_names = self.units_manager.get_unit_names()

    # add the rest of the list items
    self.ui.gcmsUnitVal.addItems(unit_names)
    self.ui.chm_selected_units.addItems(unit_names)

    for item in test_names:
        self.ui.gcmsTests.addItem(item.test_name, userData=item.test_id)

###################################################################
#   Signal Functions
###################################################################

def handle_side_item_save_btn_clicked(self, save_data, item):
    self.logger.info(f'Entering handle_side_item_save_btn_clicked with parameters: save_data: {save_data}, row: {item}')

    new_data = save_data[:-1]
    param_id = save_data[-1]
    unit_id = None

    side_save_error_handling(self, new_data, param_id, item)


@pyqtSlot()
def on_chmProceedBtn_clicked(self):
    self.logger.info('Entering on_chmProceedBtn_clicked')
    recovery, units, testName = get_current_entry_values(self)

    errorCheckList = [0,0,0]

    errorCheckList[0] = 0 if (recovery != '' and is_real_number(recovery)) else 1
    errorCheckList[1] = 0 if units != '' else 1
    errorCheckList[2] = 0 if testName != '' else 1

    if(sum(errorCheckList) == 0):
        enable_enter_values_section(self, True)
        self.ui.gcmsStandardValShow.setText(recovery)
        self.ui.gcmsUnitValShow.setText(units)
        self.ui.gcmsTestsShow.setText(testName)

        self.ui.chm_error_widget.hide()

        if(int(recovery) < 70 or int(recovery) > 120):
            self.ui.chm_error_widget.show()
            self.ui.chm_error_msg.setText('WARNING: Recovery outside range')

        # set the unit combobox
        current_index = self.ui.gcmsUnitVal.currentIndex()
        self.ui.chm_selected_units.setCurrentIndex(current_index)

    else:
        NewEntryErrorDisplay(self, errorCheckList)


@pyqtSlot()
def handle_add_chm_sample_btn_clicked(self):
    self.logger.info('Entering handle_add_chm_sample_btn_clicked ')


    standards, units, testName = get_current_entry_values(self)
    jobNum, sampleNum, selected_unit, sampleVal = get_current_entered_values(self)

    index = self.ui.gcmsTests.currentIndex()
    test_id = self.ui.gcmsTests.itemData(index, role=Qt.UserRole)

    edit_data = [jobNum, sampleNum, testName, sampleVal, selected_unit]

    errorCheckList = [0,0,0]

    errorCheckList[0] = 0 if (jobNum != '' and is_real_number(jobNum)) else 1;
    errorCheckList[1] = 0 if (sampleNum != '' and is_real_number(sampleNum)) else 1
    errorCheckList[2] = 0 if sampleVal != '' else 1

    self.logger.debug(f'Input Data Info: {jobNum}-{sampleNum}: {sampleVal}')

    #FIXME: problem arises if reading something to an existing list we can't then delete it afterwords
    if(sum(errorCheckList) == 0):


        # check if item exists in database
        existing_data_check = self.chm_test_data_manager.check_test_exists(jobNum, sampleNum, test_id)

        if(existing_data_check):
            #response = yes_or_no_dialog('Duplicate Sample', f"Would you like to overwrite existing sample {jobNum}-{sampleNum}")

            results = DuplicateDialog.show_dialog(f'{jobNum}-{sampleNum}')

            print(f'results: {results}')

            if(results == 'overwrite'):
                #TODO: remove this so it updates instead of adding to ite
                self.chm_test_data_manager.add_test(jobNum, sampleNum, test_id, sampleVal, standards, selected_unit)
                #updated_rows = self.chm_test_data_manager.update_test(jobNum, sampleNum, test_id, sampleVal, standards, selected_unit)

                # check if current sample is in the existing tree
                matching_item = check_matching_tree_items(self.ui.inputDataTree, jobNum, sampleNum)

                if matching_item:
                    logger.debug(f'Found a matching_item: {matching_item}')
                    set_input_tree_items(matching_item, jobNum, sampleNum, testName, sampleVal, units, standards)

                else:
                    add_input_tree_item(self, sampleNum, testName, sampleVal, selected_unit, standards, jobNum)

            if(results == 'duplicate'):
                #self.chm_test_data_manager.duplicate_test()
                return

            if(results == 'cancel'):
                return

            clear_samples_input(self)

        else:
            self.chm_test_data_manager.add_test(jobNum, sampleNum, test_id, sampleVal, standards, selected_unit)

            add_input_tree_item(self, sampleNum, testName, sampleVal, selected_unit, standards, jobNum)
            clear_samples_input(self)
    else:
        self.logger.error(f'errorCheckList: {errorCheckList}')
        addingSampleDataErrorDisplay(self, errorCheckList)

def check_matching_tree_items(tree_widget, job_num, sample_num):

    logger.info(f'Entering check_matching_tree_items with job_num: {job_num}, sample_num: {sample_num}')

    # Iterate through the top-level items
    for index in range(tree_widget.topLevelItemCount()):
        item = tree_widget.topLevelItem(index)

        logger.debug(f'item.text(0): {item.text(0)}, item.text(1): {item.text(1)}')

        if item.text(0) == job_num and item.text(1) == sample_num:  # Change 0 to the desired column index
            return item

    return None

def side_save_error_handling(self, new_data, test_id, tree_item):

    self.logger.info('Entering save_error_handling')

    prev_job_num = tree_item.text(0)
    prev_sample_num = tree_item.text(1)

    new_jobNum = new_data[0]
    new_sampleNum = new_data[1]
    new_sampleVal = new_data[3]
    new_unitType = new_data[4]
    new_standard = new_data[5]

    prev_job_name = f'{prev_job_num}-{prev_sample_num}'
    new_jobName = new_data[0] + '-' + new_data[1]

    logger.info(f'prev_job_name: {prev_job_name}, new_jobName: {new_jobName}')

    if(prev_job_num != new_jobNum or prev_sample_num != new_sampleNum):

        # check with the new info if in the database
        existing_data_check = self.chm_test_data_manager.check_test_exists(new_jobNum, new_sampleNum, test_id)

        if(existing_data_check):

            response = save_or_cancel_dialog('Overwrite Data?', f'Are you sure you want overwrite existing data for {new_jobName} and delete data for {prev_job_name} ')
            #TODO: should I check if there is other data existing that IW ill be saving into

            if(response):
                try:
                    # delete the old job
                    deleted_row = self.chm_test_data_manager.delete_test(prev_job_num, prev_sample_num, test_id)

                    # update the existing data with the new data
                    #TODO: if we are deleting maybe we are adding then
                    updated_rows = self.chm_test_data_manager.update_test(new_jobNum, new_sampleNum, test_id, new_sampleVal, new_standard, new_unitType)

                    # update table tree item info
                    for col, data in enumerate(new_data):
                        tree_item.setText(col, data)

                except Exception as e:
                    logger.warning(f'Error while trying to update_row, {e}')

    else:
        response = save_or_cancel_dialog('Overwrite Data?', f'Are you sure you want overwrite existing data for {new_jobName}?')

        if(response):
            # update the database
            updated_rows = self.chm_test_data_manager.update_test(new_jobNum, new_sampleNum, test_id, new_sampleVal, new_standard, new_unitType)

            for col, data in enumerate(new_data):
                tree_item.setText(col, data)


###################################################################
#   Error Messages
###################################################################


def NewEntryErrorDisplay(self, errorCheckList):

    errorTitle = 'Cannot Proceed with CHM Process'
    errorMsg = ''

    if(errorCheckList[0] == 1):
        errorMsg += 'Please Enter a Valid Percent Recovery\n'
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
    jobNum      = self.ui.gcmsTestsJobNum.text().strip()
    sampleNum   = self.ui.gcmsTestsSample.text().strip()
    sampleVal   = self.ui.gcmsTestsVal.text().strip()
    units       = self.ui.chm_selected_units.currentText()

    return jobNum, sampleNum, units, sampleVal

def enable_enter_values_section(self, status):
    logger.info(f'Entering enable_enter_values_section with parameter: status {repr(status)}')

    self.ui.newEntryWidget.setEnabled(not status)
    self.ui.chmActionWidget.setEnabled(status)
    self.ui.chmTestsValueWidget.setEnabled(status)

def clear_samples_input(self):
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear()

    # update and set the current index
    current_index = self.ui.gcmsUnitVal.currentIndex()
    self.ui.chm_selected_units.setCurrentIndex(current_index)

def clear_enter_values_section(self):
    self.ui.gcmsTestsJobNum.clear()
    self.ui.gcmsTestsSample.clear()
    self.ui.gcmsTestsVal.clear()

    self.ui.chm_selected_units.setCurrentIndex(0)

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

    self.ui.chm_error_widget.hide()

    if(clearTable):
        self.ui.inputDataTree.clear()

#******************************************************************
#  Action Function and Classes
#******************************************************************

def add_input_tree_item(self, sampleNum, testName, sampleVal, units, standards, jobNum):
    logger.info('Entering add_input_tree_item')

    tree_widget = self.ui.inputDataTree

    topItem = QTreeWidgetItem(tree_widget)

    set_input_tree_items(topItem, jobNum, sampleNum, testName, sampleVal, units, standards)

    row_index = tree_widget.indexOfTopLevelItem(topItem)

    actionWidget = TreeActionWidget(row_index, topItem)
    actionWidget.edit_clicked.connect(lambda tree_item: handle_edit_clicked(self, tree_item));
    actionWidget.delete_clicked.connect(lambda tree_item: handle_delete_clicked(self, tree_item))

    tree_widget.setItemWidget(topItem, 6, actionWidget)

def set_input_tree_items(item, job_num, sample_num, test_name, sample_val, units, standards):

    item.setText(0, job_num)
    item.setText(1, sample_num)
    item.setText(2, test_name)
    item.setText(3, sample_val)
    item.setText(4, units)
    item.setText(5, standards)

    item.setTextAlignment(1, Qt.AlignCenter)
    item.setTextAlignment(3, Qt.AlignCenter)
    item.setTextAlignment(4, Qt.AlignCenter)
    item.setTextAlignment(5, Qt.AlignCenter)


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
