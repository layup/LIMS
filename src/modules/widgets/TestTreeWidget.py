

from base_logger import logger

from PyQt5.QtCore import Qt, pyqtSignal, QDir
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTreeWidget, QWidget, QDialog, QMessageBox, QTreeWidgetItem, QHBoxLayout, QPushButton
from PyQt5.uic import loadUi

from modules.dialogs.basic_dialogs import  yes_or_no_dialog
from modules.constants import EDIT_ICON ,DELETE_ICON

#from modules.dialogs.test_dialog import TestsEditDialog

class TestTreeWidget(QTreeWidget):

    def __init__(self, test_manager):
        super().__init__()
        self.test_manager = test_manager

        self.test_tree_items = {}

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            print("Enter key pressed")
        else:
            super().keyPressEvent(event)

    def clear_tree(self):
        # clear the table itself
        self.clear()

        self.test_tree_items = {}

    def add_tests_tree_item(self, test_id, test_item):

        test_name = test_item.test_name
        #test_type = TEST_TYPE[test_item.test_type]
        test_type = test_item.test_type
        show_status = 'True' if test_item.show_status == 1 else 'False'

        tree_item = QTreeWidgetItem()
        tree_item.setToolTip(0, "drag and drop the tests in into the Macro Tree")
        tree_item.setData(0, Qt.DisplayRole, test_id)
        tree_item.setText(1, test_name)
        tree_item.setText(2, test_type)
        tree_item.setText(3, show_status)


        self.addTopLevelItem(tree_item)

        action_widget = self.create_action_widget( tree_item, test_item)
        self.setItemWidget(tree_item, 4, action_widget);

        return tree_item

    def create_action_widget(self, tree_item, data_item):

        action_widget = QWidget()
        button_layout = QHBoxLayout(action_widget)
        button_layout.setContentsMargins(1, 1, 1, 1)

        edit_btn =  QPushButton('')
        delete_btn = QPushButton('')

        edit_btn.clicked.connect(lambda: self.handle_edit_tests_btn( tree_item, data_item))
        delete_btn.clicked.connect(lambda: self.handle_delete_tests_btn( tree_item))

        # define the icon
        edit_btn.setIcon(EDIT_ICON)
        delete_btn.setIcon(DELETE_ICON)

        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch(1)

        return  action_widget

    def handle_edit_tests_btn(self, tree_item, tests_item):

        return

        test_id = tests_item.test_id

        data_item = self.test_manager.get_test_info(test_id)

        dialog = TestsEditDialog(test_id,  'Edit Tests', data_item)
        dialog.update_tests.connect(lambda test_id, updated_items: self.handle_update_tests(test_id, updated_items, tree_item))
        dialog.exec()

    def handle_update_tests(self, test_id, updated_items, tree_item):
        print('handle_update_tests')

        test_name = updated_items.test_name
        test_type = updated_items.test_type
        show_status = 'True' if updated_items.show_status == 1 else 'False'

        tree_item.setData(0, Qt.DisplayRole, test_id)
        tree_item.setText(1, test_name)
        tree_item.setText(2, test_type)
        tree_item.setText(3, show_status)

        # TODO: update the manager item and the database
        self.test_manager.update_test(test_id, updated_items)


    def handle_delete_tests_btn(self, item):

        # delete the item from the tests tree
        self.delete_item(item)


        # TODO: remove item form the manager and database

    def delete_item(self, item):

        # Remove the top-level item from the QTreeWidget
        reply = yes_or_no_dialog('Delete Tests', 'Are you sure you wanna delete this item?')

        if(reply):
            print(f'Deleting {item.text(0)}')
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)

