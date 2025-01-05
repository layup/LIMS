import json
import os

from base_logger import logger

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import ( QDialog, QTableWidgetItem, QTreeWidgetItem, QListWidgetItem, QMessageBox)
from PyQt5.QtGui import QDoubleValidator

from modules.dialogs.add_new_element import addNewElementDialog
from modules.dialogs.basic_dialogs import yes_or_no_dialog


###################################################################
#    Setup Functions
###################################################################
#FIXME: has to load in the list each time, so create a function that app.py can access
# TODO: create a clone that holds data until user presses the save button (kind of a pain in the ass)
#TODO: use a drop down well for unit type
#TODO: change the css style for the thing when look at the back color
def icp_elements_setup(self):
    logger.info("Entering icp_elements_setup")

    # basic setup for different sections within the icp elements tab
    validators_setup(self)
    elements_tree_setup(self)

    # clear all the elements information
    clear_all_element_info(self)

    # load in the initial
    populate_defined_elements_list(self)
    populate_icp_parameters(self)

    connect_icp_signals(self)

def connect_icp_signals(self):

    self.ui.reportTypeDropdown.activated.connect(lambda index: handle_parameter_change(self, index))
    self.ui.definedElements.currentRowChanged.connect(lambda: handle_selected_element_change(self))
    self.ui.icpElementTreeWidget.currentItemChanged.connect(lambda tree_item: handle_tree_change(self, tree_item))

    self.ui.deleteCompBtn.clicked.connect(lambda: handle_delete_btn_clicked(self))
    self.ui.addElementBtn.clicked.connect(lambda: handle_add_elements_btn_clicked(self))
    self.ui.saveCompBtn.clicked.connect(lambda: handle_save_btn_clicked(self))
    self.ui.icpCancelBtn.clicked.connect(lambda: handle_cancel_btn_clicked(self))

def populate_icp_parameters(self):
    logger.info('Entering populate_icp_parameters')
    # clear the QComboBox
    self.ui.reportTypeDropdown.clear()
    self.ui.reportTypeDropdown.addItem('')

    for param_id, param_info in self.parameters_manager.parameters.items():
        param_name = param_info.param_name

        # populate the report tree
        item = QTreeWidgetItem(self.ui.icpElementTreeWidget)
        item.setText(0, "{:03d}".format(param_id))
        item.setData(0, Qt.UserRole, param_id)
        item.setText(1, param_name)

        item.setTextAlignment(2, Qt.AlignCenter)
        item.setTextAlignment(3, Qt.AlignCenter)
        item.setTextAlignment(4, Qt.AlignCenter)

        # populate the QComboBox
        self.ui.reportTypeDropdown.addItem(param_name, userData=param_id)
        #current_data = self.ui.reportTypeDropdown.itemData(index, Qt.UserRole)

def clear_report_type_tree(treeWidget):
    logger.info('Entering clear_report_type_tree')

    columns_to_clear = (2, 3, 4)

    for item_index in range(treeWidget.topLevelItemCount()):
        item = treeWidget.topLevelItem(item_index)

        # unpack the tuple and clear the selected columns
        item.setData(*columns_to_clear, Qt.DisplayRole, None)

def populate_defined_elements_list(self):

    # clear the define elements tree to be safe
    self.ui.definedElements.clear()

    # load in the info
    for element_id, element_info in self.elements_manager.elements.items():
        element_name = element_info.name

        list_item = QListWidgetItem(element_name, self.ui.definedElements)
        list_item.setData(Qt.UserRole, element_id)

def validators_setup(self):

    # Create a QDoubleValidator
    validator = QDoubleValidator()
    validator.setRange(-10000, 10000.0)
    validator.setDecimals(10)

    # Set the validator for the QLineEdit to only allow float values
    self.ui.lowerLimit.setValidator(validator)
    self.ui.upperLimit.setValidator(validator)

def elements_tree_setup(self):

    headers = self.ui.icpElementTreeWidget.header()
    headers.setDefaultAlignment(Qt.AlignCenter)

    # set the widths
    self.ui.icpElementTreeWidget.setColumnWidth(1, 250)

###################################################################
#    Helper Functions
###################################################################

def clear_all_element_info(self):

    # Clear the Tree Widget
    self.ui.icpElementTreeWidget.clear()

    clear_element_info(self)
    clear_element_limits(self)

def clear_element_info(self):
    self.ui.symbolInput.clear()
    self.ui.elementNameinput.clear()

def clear_element_limits(self):
    self.ui.lowerLimit.clear()
    self.ui.upperLimit.clear()
    self.ui.unitType.clear()
    self.ui.RightSideComment.clear()

def clear_report_tree_cols(tree_widget):
    logger.info('Entering clear_report_tree_cols')

    columns_to_clear = [2,3,4]

    for i in range(tree_widget.topLevelItemCount()):
        item = tree_widget.topLevelItem(i)

        for column in columns_to_clear:
            item.setData(column, Qt.DisplayRole, None)

def load_element_info(self):
    logger.info('Entering load_element_info')

    # clear off previous element info
    clear_element_limits(self)

    # get the current element_id
    current_row = self.ui.definedElements.currentRow()

    if(current_row >= 0):
        current_item = self.ui.definedElements.item(current_row)
        element_id = current_item.data(Qt.UserRole)
        element_name = current_item.text()

        # set the params combo box to ''
        self.ui.reportTypeDropdown.setCurrentIndex(0)

        self.ui.icpElementTreeWidget.clearSelection()

        # set the basic element info
        set_element_info(self, element_id)

        # set the limits for the table
        set_element_tree_limits(self, element_id)

        self.ui.elements_name_header.setText(f'[{element_id}] {element_name.capitalize()}')

def set_element_info(self, element_id):
    logger.info(f'Entering set_element_info with element_id: {element_id}')
    if(element_id in self.elements_manager.get_elements()):
        element_name = self.elements_manager.elements[element_id].name
        element_symbol = self.elements_manager.elements[element_id].symbol

        self.ui.elementNameinput.setText(element_name)
        self.ui.symbolInput.setText(element_symbol)

def set_element_tree_limits(self, element_id):
    logger.info("Entering set_element_tree_limits with element_id: {element_id} ")

    tree_widget = self.ui.icpElementTreeWidget

    # clear all of the info for columns > 2
    clear_report_tree_cols(tree_widget)

    for i in range(tree_widget.topLevelItemCount()):
        current_item = tree_widget.topLevelItem(i)

        if(current_item and element_id in self.elements_manager.get_elements()):
            param_id = current_item.data(0, Qt.UserRole)

            limits_info = self.elements_manager.elements[element_id].get_limits(param_id)

            if(limits_info):
                lower_limit = limits_info.lower_limit
                upper_limit = limits_info.upper_limit
                unit_type = limits_info.unit

                current_item.setData(2, Qt.DisplayRole, lower_limit)
                current_item.setData(3, Qt.DisplayRole, upper_limit)
                current_item.setData(4, Qt.DisplayRole, unit_type)

def save_defined_limits(self, param_id, element_id):
    logger.info(f'Entering save_defined_limits with param_id: {param_id}, element_id: {element_id} ')

    lower_limit, upper_limit, unit_type, side_comment = get_defined_limits_text(self)

    # check if any of the data is different before updating the database
    changed_status = check_limit_difference(self, param_id, element_id)

    logger.debug(f'changed_status: {changed_status}')

    if(changed_status):
        lower_limit, upper_limit, unit_type, side_comment = get_defined_limits_text(self)
        update_status = self.elements_manager.insert_or_update_limits( param_id, element_id, unit_type, lower_limit, upper_limit, side_comment)

        if(update_status):
            # update the element tree (reloading all the info again but is quick )
            set_element_tree_limits(self, element_id)

def save_element_info(self, list_item, element_id):
    logger.info(f"Entering save_element_info with element_id: {element_id}")

    element_name = self.ui.elementNameinput.text()
    element_symbol = self.ui.symbolInput.text()

    errors = []

    if(not element_name):
        errors.append("Element name cannot be empty.")
    if(not element_symbol):
        errors.append("Element symbol cannot be empty.")

    if(errors):
        error_message = '\n'.join(errors)
        QMessageBox.critical(self, "Error", error_message)
        return  # Early return to prevent saving with errors

    changed_status = check_element_difference(self, element_id, element_name, element_symbol)

    logger.debug(f'changed_status: {changed_status}')

    if(changed_status):
        # update the database and elements handler
        update_status = self.elements_manager.update_element( element_id, element_name, element_symbol)

        if(update_status):
            list_item.setText(element_name)

def get_defined_limits_text(self):
    logger.info('Entering get_defined_limits_text')

    lower_limit = self.ui.lowerLimit.text()
    upper_limit = self.ui.upperLimit.text()
    unit_type = self.ui.unitType.text()
    side_comment = self.ui.RightSideComment.toPlainText()

    logger.debug(f'lower_limit: {lower_limit}, upper_limit: {upper_limit}, unit_type:{unit_type}, side_comment:{side_comment}')

    return lower_limit, upper_limit, unit_type, side_comment

def check_limit_difference(self, param_id, element_id):
    logger.info(f'Entering check_limit_difference param_id: {param_id}, element_id: {element_id}')

    limit_item = self.elements_manager.get_limits_item(element_id, param_id)

    if(limit_item):
        existing_lower_limit = limit_item.lower_limit
        existing_upper_limit = limit_item.upper_limit
        existing_unit_type = limit_item.unit
        existing_side_comment = limit_item.side_comment

        lower_limit, upper_limit, unit_type, side_comment = get_defined_limits_text(self)

        return existing_lower_limit != lower_limit or existing_upper_limit != upper_limit or existing_unit_type != unit_type or existing_side_comment != side_comment

    # means limit_item doesn't exist so not in the database yet
    return True

def check_element_difference(self, element_id, element_name, element_symbol):

    existing_name = self.elements_manager.elements[element_id].name
    existing_symbol = self.elements_manager.elements[element_id].symbol

    return existing_name != element_name or existing_symbol != element_symbol

###################################################################
#    Signal Functions
###################################################################

def handle_delete_btn_clicked(self):
    logger.info('Entering handle_delete_btn_clicked')

    current_row = self.ui.definedElements.currentRow()

    if(current_row >= 0):
        current_item = self.ui.definedElements.item(current_row)
        element_id = current_item.data(Qt.UserRole)
        element_name = current_item.text()

        response = yes_or_no_dialog('Delete Element', 'Are you sure you want to delete Element, cannot be undone once performed')

        if(response):

            delete_status = self.elements_manager.delete_element(element_id)

            if(delete_status):

                clear_element_limits(self)
                clear_element_info(self)
                clear_report_tree_cols(self.ui.icpElementTreeWidget)

                # set the current index
                self.ui.reportTypeDropdown.setCurrentIndex(0)

                # Deselect all items
                self.ui.icpElementTreeWidget.clearSelection()

                # reload the defined elements section
                populate_defined_elements_list(self)


def handle_add_elements_btn_clicked(self):
    logger.info('Entering handle_add_elements_btn_clicked')

    new_element_dialog = addNewElementDialog(self.elements_manager)
    new_element_dialog.status.connect(lambda status : handle_add_element_dialog(self, status))
    new_element_dialog.exec()

def handle_add_element_dialog(self, status):
    logger.info('Entering handle_add_element_dialog status: {status}')

    if(status):
        # clear all the basic info
        clear_element_limits(self)
        clear_element_info(self)
        clear_report_tree_cols(self.ui.icpElementTreeWidget)

        # set the current index
        self.ui.reportTypeDropdown.setCurrentIndex(0)

        # Deselect all items
        self.ui.icpElementTreeWidget.clearSelection()

        # reload the defined elements section
        populate_defined_elements_list(self)

        row_count = self.ui.definedElements.count()

        if row_count > 0:
            self.ui.definedElements.setCurrentRow(row_count - 1)



def handle_cancel_btn_clicked(self):
    logger.info('Entering handle_cancel_btn_clicked')

    # clear off previous element info
    clear_element_limits(self)

    # get the current element_id
    current_row = self.ui.definedElements.currentRow()
    current_index = self.ui.reportTypeDropdown.currentIndex()

    if(current_row >= 0 and current_index >= 0):
        current_item = self.ui.definedElements.item(current_row)
        element_id = current_item.data(Qt.UserRole)
        element_name = current_item.text()

        param_id = self.ui.reportTypeDropdown.itemData(current_index, Qt.UserRole)

        # set the basic element info
        set_element_info(self, element_id)

        if(element_id in self.elements_manager.get_elements()):

            limits_info = self.elements_manager.elements[element_id].get_limits(param_id)

            if(limits_info):
                lower_limit = limits_info.lower_limit
                upper_limit = limits_info.upper_limit
                unit_type = limits_info.unit
                side_comment = limits_info.side_comment

                self.ui.lowerLimit.setText(str(lower_limit))
                self.ui.upperLimit.setText(str(upper_limit))
                self.ui.unitType.setText(unit_type)
                self.ui.RightSideComment.setPlainText(side_comment)

        self.ui.elements_name_header.setText(f'[{element_id}] {element_name.capitalize()}')

def handle_save_btn_clicked(self):
    logger.info('Entering handle_save_btn_clicked')

    current_tree_item = self.ui.icpElementTreeWidget.currentItem()
    current_list_item = self.ui.definedElements.currentItem()

    if not current_list_item:
        # No list item selected, display error message
        QMessageBox.warning(self, "Error", "Please select an item from the Defined Elements list before you can save")
        return

    element_id = current_list_item.data(Qt.UserRole)

    # Save defined limits if both tree and list items are selected
    if current_tree_item:
        param_id = current_tree_item.data(0, Qt.UserRole)
        save_defined_limits(self, param_id, element_id)

    # Save basic information regardless of tree item selection
    save_element_info(self, current_list_item, element_id)

def handle_selected_element_change(self):
    logger.info('Entering handle_selected_element_change')

    load_element_info(self)

def handle_parameter_change(self, index):
    logger.info(f'Entering handle_parameter_change with index: {index}')

    param_name = self.ui.reportTypeDropdown.itemText(index)

    if(param_name == ''):
        self.ui.icpElementTreeWidget.clearSelection()
        return

    item = self.ui.icpElementTreeWidget.topLevelItem(index-1)
    self.ui.icpElementTreeWidget.setCurrentItem(item)

def handle_tree_change(self, tree_item):
    logger.info('Entering handle_tree_change')

    # clear existing limit QLineEdit
    clear_element_limits(self)

    tree_row = self.ui.icpElementTreeWidget.indexOfTopLevelItem(tree_item)
    list_row = self.ui.definedElements.currentRow()

    self.ui.reportTypeDropdown.setCurrentIndex(tree_row+1)

    if(list_row != -1):
        param_id = tree_item.data(0, Qt.UserRole)

        current_item = self.ui.definedElements.item(list_row)
        element_id = current_item.data(Qt.UserRole)

        logger.info(f'selected param_id: {param_id}, active element_id: {element_id}')

        if(element_id in self.elements_manager.get_elements()):

            limits_info = self.elements_manager.elements[element_id].get_limits(param_id)

            if(limits_info):
                lower_limit = limits_info.lower_limit
                upper_limit = limits_info.upper_limit
                unit_type = limits_info.unit
                side_comment = limits_info.side_comment

                self.ui.lowerLimit.setText(str(lower_limit))
                self.ui.upperLimit.setText(str(upper_limit))
                self.ui.unitType.setText(unit_type)
                self.ui.RightSideComment.setPlainText(side_comment)