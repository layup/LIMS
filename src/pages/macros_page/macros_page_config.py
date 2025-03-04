from base_logger import logger

from PyQt5.QtCore import Qt

from modules.widgets.MacrosTreeWidget import MacrosTreeWidget
from modules.widgets.TestTreeWidget import TestTreeWidget


def macros_page_setup(self):

    trees_setup(self)

    # connect signals
    self.ui.create_macro_btn.clicked.connect(lambda: handle_create_macro_btn(self))
    self.ui.create_test_btn.clicked.connect(lambda: handle_create_test_btn(self))


def trees_setup(self):
    ''' Setup both the macros and test tree'''

    # create instance of both trees
    self.ui.macros_tree = MacrosTreeWidget(self.macros_manager, self.tests_manager)
    self.ui.tests_tree = TestTreeWidget(self.tests_manager)

    # format the tree
    format_macro_tree(self.ui.macros_tree)
    format_test_tree(self.ui.tests_tree)

    # add the tree containers
    layout = self.ui.macro_trees_container.layout()
    layout.addWidget(self.ui.tests_tree)
    layout.addWidget(self.ui.macros_tree)

    # load initial tree information
    load_test_tree_info(self)
    load_macro_tree_info(self)


def format_macro_tree(tree):

    # set the header labels
    tree.setHeaderLabels(['Macro ID', 'Macro Name', 'Show', 'Actions'])

    # column sizing
    small_col = 80
    med_col = 100
    big_col = 300

    # set the column widths
    tree.setColumnWidth(0, small_col)
    tree.setColumnWidth(1, big_col)
    tree.setColumnWidth(2, small_col)
    tree.setColumnWidth(3, med_col)

    # set the drag and drop options
    tree.setDragEnabled(False)
    tree.setAcceptDrops(True)
    tree.setAcceptDrops(True)
    tree.setDropIndicatorShown(True)

    tree.sortItems(0, Qt.AscendingOrder)


def format_test_tree(tree):

    # set the headers labels
    tree.setHeaderLabels(['Test ID', 'Test Name', 'Category', 'Show', 'Actions'])

    # column sizing
    small_col = 80
    med_col = 100
    big_col = 300

    # set the column widths for the tree
    tree.setColumnWidth(0, small_col)
    tree.setColumnWidth(1, big_col)
    tree.setColumnWidth(2, small_col)
    tree.setColumnWidth(3, small_col)
    tree.setColumnWidth(4, med_col)

    # Enable sorting
    tree.setSortingEnabled(True)
    tree.sortItems(0, Qt.AscendingOrder)

    # Enable drag and drop for both trees
    tree.setDragEnabled(True)


def load_test_tree_info(self):

    self.ui.tests_tree.clear()

    for test_id, test_values in self.tests_manager.tests.items():
        self.ui.tests_tree.add_tests_tree_item(test_id, test_values)

def load_macro_tree_info(self):

    # clear the tree and the database
    self.ui.macros_tree.clear_tree()

    for macro_id, macro_values in self.macros_manager.macros_list.items():
        self.ui.macros_tree.add_macro_item(macro_id, macro_values)


def handle_create_macro_btn(self):
    '''
        - dialog to insert new information
        - need to update the database
        - update the manager with new item
        - update the macro table
        - scroll to the newly added item in the table

    '''
    pass

def handle_create_test_btn(self):
    pass



def create_new_macro(self):
    pass


def create_new_test(self):
    pass
