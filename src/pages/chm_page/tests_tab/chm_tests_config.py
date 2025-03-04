from base_logger import logger


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QAbstractItemView, QTreeWidgetItem
from PyQt5.QtGui import QValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp

from modules.dialogs.basic_dialogs import okay_dialog, error_dialog

from pages.chm_page.tests_tab.chm_tests_view import TestsView
from pages.chm_page.tests_tab.chm_tests_controller import TestsController


class FloatIntValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.regex = QRegExp(r"^-?\d*(\.\d+)?$")  # Regex for floats and ints

    def validate(self, input_str, pos):
        if self.regex.exactMatch(input_str):
            return QValidator.Acceptable, input_str, pos
        elif input_str == "" or input_str == "-": # allow empty or just negative sign
            return QValidator.Intermediate, input_str, pos
        else:
            # Check if it's almost a valid float, handle cases like "12." or "12.3."
            if QRegExp(r"^-?\d*(\.\d*)?$").exactMatch(input_str): # Almost valid float
                return QValidator.Intermediate, input_str, pos
            return QValidator.Invalid, input_str, pos

    def fixup(self, input_str):
        # Remove any invalid characters to try and make it a valid number
        # This is very basic, you can customize it further
        cleaned_str = ""
        for char in input_str:
            if char.isdigit() or char == '.' or char == '-':
                cleaned_str += char
        return cleaned_str

#******************************************************************
#    Chemistry Tests Info
#*****************************************************************
def chm_tests_tab_setup(self):
    logger.info('Entering chm_tests_tab_setup')

    #tests_table_setup(self.ui.chm_tests_table)

    tests_tree_setup(self.ui.chm_test_tree)
    dropdown_setup(self)
    line_edit_setup(self)

    # load the initial tests data
    load_chm_tests(self)

    #self.tests_view = TestsView(self.ui.chm_test_tree ,self.ui.chm_tests_table, self.ui.chmAddNewTests, self.ui.chmSearchLine3, self.ui.chmSearchBtn3, self.ui.clear_tests_btn)
    #self.tests_controller = TestsController(self.tests_manager, self.tests_view)

    self.ui.chm_test_tree.currentItemChanged.connect(lambda item: handle_test_selected(self, item))

    self.ui.chm_save_btn.clicked.connect(lambda: handle_save_btn(self))
    self.ui.chm_test_btn.clicked.connect(lambda: handle_cancel_btn(self))
    self.ui.chmSearchBtn3.clicked.connect(lambda: handle_search(self))
    self.ui.chmSearchLine3.returnPressed.connect(lambda: handle_search(self))
    self.ui.clear_tests_btn.clicked.connect(lambda: load_chm_tests(self))

def line_edit_setup(self):

    float_validator = FloatIntValidator()

    self.ui.chm_lower.setValidator(float_validator)
    self.ui.chm_upper.setValidator(float_validator)
    self.ui.chm_so.setValidator(float_validator)

    max_string_length = 30
    max_value_length = 20

    self.ui.chm_tests_name.setMaxLength(max_string_length)
    self.ui.chm_text_name.setMaxLength(max_string_length)
    self.ui.chm_display_name.setMaxLength(max_string_length)
    self.ui.chm_side.setMaxLength(max_string_length)

    # restrict the values to 20 length
    self.ui.chm_upper.setMaxLength(max_value_length)
    self.ui.chm_lower.setMaxLength(max_value_length)
    self.ui.chm_so.setMaxLength(max_value_length)




def tests_tree_setup(tree):

    column_headers = ['Test ID', 'Test Name', 'Text Name']

    tree.setColumnCount(len(column_headers))
    tree.setHeaderLabels(column_headers)

    tree.setColumnWidth(0, 60)
    tree.setColumnWidth(1, 260)
    tree.setColumnWidth(2, 100)

def load_chm_tests(self):

    tests = self.tests_manager.get_tests_type('C')

    update_tree(self, tests)


def dropdown_setup(self):

    show = {
        '':'',
        0:'False',
        1: 'True'
    }

    test_type = {
        '':'',
        'C':'Chemistry',
        'M': 'Micro',
        'G': 'General'
    }


    for key, value in show.items():
        self.ui.chm_print.addItem(str(value), userData=key)
        self.ui.chm_display.addItem(str(value), userData=key)

    for key, value in test_type.items():
        self.ui.chm_test_type.addItem(value, userData=key)


def handle_test_selected(self, item):

    if(item):

        # clear existing sample data before loading in existing info
        clear_tests_info(self)

        test_id = item.text(0)
        test_name = item.text(1)

        test_info = self.tests_manager.get_test_info(int(test_id))

        print(f'test_info: {test_info}')

        if(test_info):
            text_name = test_info.chem_name
            display_name = test_info.display_name
            test_type = test_info.test_type
            upper_limit = test_info.upper_limit
            lower_limit = test_info.lower_limit
            print_status = test_info.print_status
            show_status = test_info.show_status
            side_comment = test_info.comment
            footer_comment = test_info.footer
            so = test_info.so

            update_toggle_items(self, test_type, show_status, print_status)
            update_tests_info(self, test_id, test_name, text_name, display_name, lower_limit, upper_limit, so)
            update_tests_comment(self, side_comment, footer_comment)

            return

    #TODO: do prompt an error


def update_tree(self, data):

    # clear the tree of existing tests
    self.ui.chm_test_tree.clear()

    # clear the tests info
    clear_tests_info(self)

    # load the data
    for row, (test_id, test_info) in enumerate(data.items()):

        test_name = test_info.test_name
        text_name = test_info.chem_name

        parent_item = QTreeWidgetItem([str(test_id), str(test_name), str(text_name)])

        # add item to the tree
        self.ui.chm_test_tree.addTopLevelItem(parent_item)

def update_toggle_items(self, test_type, show_status, print_status):
    logger.info(f'Entering update_toggle_items test_type: {test_type}, show_status: {show_status}, print_status: {print_status}')

    show = {
        '':'',
        0:'False',
        1: 'True'
    }

    test_types = {
        '':'',
        'C':'Chemistry',
        'M': 'Micro',
        'G': 'General'
    }

    try:
        self.ui.chm_test_type.setCurrentText(test_types[test_type])
        self.ui.chm_print.setCurrentText(show[int(print_status)])
        self.ui.chm_display.setCurrentText(show[int(show_status)])

    except Exception as e:
        print(f'Cannot update_toggle_item {e}')

def update_tests_info(self, test_id, test_name, text_name, display_name, lower_limit, upper_limit, so):

    self.ui.chm_header.setText(f'[{test_id}] {test_name}')

    self.ui.chm_tests_name.setText(test_name)
    self.ui.chm_text_name.setText(text_name)
    self.ui.chm_display_name.setText(display_name)


    if(lower_limit):
        self.ui.chm_lower.setText(str(lower_limit))

    if(upper_limit):
        self.ui.chm_upper.setText(str(upper_limit))

    if(so):
        self.ui.chm_so.setText(str(so))


def update_tests_comment(self, side_comment, footer_comment):
    self.ui.chm_side.setText(side_comment)
    self.ui.chm_footer.setPlainText(footer_comment)

def clear_tests_info(self):

    # clear the QLineEdit
    self.ui.chm_header.clear()
    self.ui.chm_tests_name.clear()
    self.ui.chm_text_name.clear()
    self.ui.chm_display_name.clear()
    self.ui.chm_upper.clear()
    self.ui.chm_lower.clear()
    self.ui.chm_so.clear()

    # reset the QComboBox Item
    self.ui.chm_test_type.setCurrentIndex(0)
    self.ui.chm_print.setCurrentIndex(0)
    self.ui.chm_display.setCurrentIndex(0)

    # clear the comment section
    self.ui.chm_side.clear()
    self.ui.chm_footer.setPlainText("")

def get_tests_info(self):

    test_name = self.ui.chm_tests_name.text()
    text_name = self.ui.chm_text_name.text()
    display_name = self.ui.chm_display_name.text()
    upper_limit = self.ui.chm_upper.text()
    lower_limit = self.ui.chm_lower.text()
    so = self.ui.chm_so.text()

    test_type = self.ui.chm_test_type.itemData(self.ui.chm_test_type.currentIndex(), Qt.UserRole)
    print_item = self.ui.chm_print.itemData(self.ui.chm_print.currentIndex(), Qt.UserRole)
    show_item = self.ui.chm_display.itemData(self.ui.chm_display.currentIndex(), Qt.UserRole)

    side_comment = self.ui.chm_side.text()
    footer_comment = self.ui.chm_footer.toPlainText()

    logger.debug(f'test_name: {test_name}, text_name: {text_name}, display_name: {display_name}')
    logger.debug(f'lower_limit: {lower_limit}, upper_limit: {upper_limit}, so: {so}')
    logger.debug(f'test_type: {test_type}, print_item: {print_item}, show_item: {show_item}')
    logger.debug(f'side_comment: {side_comment}, footer:{footer_comment}')

    return [test_name, text_name, display_name, lower_limit, upper_limit, so, test_type, print_item, show_item, side_comment, footer_comment]

def get_test_id(self):

    tree_item = self.ui.chm_test_tree.currentItem()

    if(tree_item):
        return int(tree_item.text(0))

    return None

def handle_search(self):
    logger.info('Entering handle_search')

    search_query = self.ui.chmSearchLine3.text()

    print(f'search_query: {search_query}')

    if(search_query != ''):

        search_tests = self.tests_manager.get_search_tests(search_query)

        update_tree(self, search_tests)

        return

    load_chm_tests(self)


def handle_add_btn(self):
    pass

def handle_delete_btn(self):
    pass

def handle_save_btn(self):
    logger.info('Entering handle_save_btn')

    test_id = get_test_id(self)

    if(test_id):
        print(f'test_id: {test_id}')

        current_test_info = get_tests_info(self)

        test_name = current_test_info[0]
        text_name = current_test_info[1]
        display_name = current_test_info[2]
        lower_limit = current_test_info[3]
        upper_limit = current_test_info[4]
        so = current_test_info[5]
        test_type = current_test_info[6]
        print_item = current_test_info[7]
        show_item = current_test_info[8]
        side_comment = current_test_info[9]
        footer = current_test_info[10]

        status = self.tests_manager.update_chm_test(test_id, test_name, text_name, display_name, lower_limit, upper_limit, so,  print_item, show_item, side_comment, footer)

        if(status):
            okay_dialog('Tests Saved', f'{test_name} was saved successfully')
            return

        error_dialog('Error Saving Tests', f'Could not save {test_name}, error occurred')

    else:
        error_dialog('Error Saving Tests', 'Please select a tests to save')


def handle_cancel_btn(self):

    # clear and reload the data
    clear_tests_info(self)

    # reload the initial data
    tree_item = self.ui.chm_test_tree.currentItem()

    if(tree_item):
        handle_test_selected(self, tree_item)


def tests_table_setup(table):

    column_headers = ['Test ID', 'Test Name', 'Text Name', 'Report Name', 'Side Comment', 'Action']

    table.setColumnCount(len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)

    # Hide the left-side row numbers
    table.verticalHeader().setVisible(False)

    small_col = 80
    med_col = 150
    big_col = 220
    extra_big_col = 320

    table.setColumnWidth(0, small_col)
    table.setColumnWidth(1, big_col)
    table.setColumnWidth(2, med_col)
    table.setColumnWidth(3, big_col)
    table.setColumnWidth(4, extra_big_col)

    # Optionally, stretch the last column to fill the remaining space
    table.horizontalHeader().setStretchLastSection(True)

    # Disable editing
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Disable sorting
    table.setSortingEnabled(True)

def chm_tests_helper(self):
    self.ui.chmTestsReportNameLabel.setToolTip('This is what will show up on the excel report')


