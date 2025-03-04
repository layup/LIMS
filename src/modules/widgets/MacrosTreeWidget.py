from base_logger import logger

from PyQt5.QtCore import Qt, pyqtSignal, QDir
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import QTreeWidget, QWidget, QDialog, QMessageBox, QTreeWidgetItem, QHBoxLayout, QPushButton
from PyQt5.uic import loadUi


from modules.constants import EDIT_ICON, DELETE_ICON
from modules.dialogs.basic_dialogs import error_dialog, yes_or_no_dialog
#from modules.dialogs.macro_dialog import MacroEditDialog

class MacrosTreeWidget(QTreeWidget):

    delete_macro = pyqtSignal(int)
    edit_macro =  pyqtSignal(int)
    delete_test = pyqtSignal(int)
    add_test = pyqtSignal(int)

    def __init__(self, macro_manager, test_manager):
        super().__init__()
        self.macro_manager = macro_manager
        self.test_manager = test_manager

        self.macro_tree_items = {}

    def clear_tree(self):

        # clear the tree itself
        self.clear()

        # clear the tree item container
        self.macro_tree_items = {}


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            print("Delete key pressed")
        else:
            super().keyPressEvent(event)

    def dragMoveEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        if event.source() == self:
            # Prevent dragging from the same tree widget
            event.ignore()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        source = event.source()
        source_tree_name = source.objectName()
        source_item = source.currentItem()
        target_item = self.itemAt(event.pos())

        #if dragged into a parent item
        if(source_item is not None and not target_item.parent()):
            print('dragging into the Parent')
            self.add_test_item(target_item, source_item)

            # TODO: update the database

        # if dragged into a child item
        elif(source_item is not None and target_item.parent()):
            print('Dragging into child element')
            parentItem = target_item.parent()
            self.add_test_item(parentItem, source_item)

    def add_macro_item(self, macro_id, macro_item):
        show_status = 'True' if macro_item.is_displayed == 1 else 'False'

        tree_item = QTreeWidgetItem()
        tree_item.setData(0, Qt.DisplayRole, macro_id)
        tree_item.setText(1, macro_item.macro_name)
        tree_item.setText(2, show_status)

        self.addTopLevelItem(tree_item)

        bold_font = QFont()
        bold_font.setBold(True)

        # set bold font for the micro names
        for col in range(3):
            tree_item.setFont(col, bold_font)

        for test_id in macro_item.tests:
            if(test_id in self.test_manager.tests):

                test_name = self.test_manager.tests[test_id].test_name
                show_status = 'True' if self.test_manager.tests[test_id].show_status == 1 else 'False'

                test_item = QTreeWidgetItem([str(test_id), str(test_name), show_status])

                tree_item.addChild(test_item)

                remove_btn = self.create_remove_btn(test_item)
                self.setItemWidget(test_item, 3, remove_btn)

        action_widget = self.create_action_widget(tree_item, macro_item)
        self.setItemWidget(tree_item, 3, action_widget)

        return tree_item

    def add_test_item(self, target_item, source):

        test_id = source.text(0)
        test_name = source.text(1)
        test_show = source.text(3)

        macro_id = target_item.text(0)
        logger.info(f'test_id: {test_id}, macro_id: {macro_id}')

        childNums = []

        for i in range(target_item.childCount()):
            childItem = target_item.child(i)

            if childItem is not None:
                childNum = childItem.data(0, Qt.DisplayRole)
                childNums.append(childNum)

        # Prevent duplicates from being added to the
        if(int(test_id) not in childNums):

            new_item = QTreeWidgetItem([str(test_id), test_name, test_show])
            remove_btn = self.create_remove_btn(new_item)

            #add the item to the trees
            target_item.addChild(new_item)

            # Set the background color of the clone item
            for j in range(self.columnCount()):
                # currently selected color is green
                new_item.setBackground(j, QBrush(QColor(0, 255, 0)))

            # Set the container widget as the item widget
            self.setItemWidget(new_item, 3, remove_btn)

            # Expand open it
            self.expandItem(target_item)

            self.add_test.emit(int(test_id))

    def create_action_widget(self, tree_item, data_item):

        action_widget = QWidget()
        button_layout = QHBoxLayout(action_widget)
        button_layout.setContentsMargins(1, 1, 1, 1)

        edit_btn =  QPushButton('')
        delete_btn = QPushButton('')

        edit_btn.clicked.connect(lambda: self.handle_edit_macro_btn(tree_item, data_item))
        delete_btn.clicked.connect(lambda: self.handle_delete_macro_btn(tree_item))

        # define the icon
        edit_btn.setIcon(EDIT_ICON)
        delete_btn.setIcon(DELETE_ICON)

        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch(1)

        return action_widget

    def create_remove_btn(self, source_item):
        # Define the container and layout
        containerWidget = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(1, 1, 1, 1)

        # Define and configure the remove button
        remove_tests_brn = QPushButton('Remove')
        remove_tests_brn.setFixedSize(50, 20)
        #remove_tests_brn.setStyleSheet("color: red; border: 0px;")
        remove_tests_brn.clicked.connect(lambda _, item=source_item: self.handle_delete_test_btn(item))

        # Add button to the layout
        buttonLayout.addWidget(remove_tests_brn)
        buttonLayout.addStretch(1)

        # Set the layout for the container widget
        containerWidget.setLayout(buttonLayout)

        return containerWidget

    def handle_edit_macro_btn(self, tree_item, data_item):


        #TODO: fix this

        return

        title = 'Edit Micro'
        macro_id = data_item.macro_id

        data_item = self.macro_manager.get_macro_info(macro_id)
        tests = self.test_manager.get_tests()

        edit_macro_dialog = MacroEditDialog( macro_id, title, tests, data_item)

        # connect signal to manager to update and database
        edit_macro_dialog.update_macro.connect(lambda macro_id, new_item: self.handle_update_macro_item(macro_id, new_item, tree_item))
        edit_macro_dialog.exec()

    def handle_update_macro_item(self, macro_id, macro_item, tree_item):

        status = self.macro_manager.update_macro(macro_id, macro_item)

        if(status):

            macro_name = macro_item.macro_name

            # update macro name
            tree_item.setText(0, macro_name)

            # TODO: update macro tests lists

            # TODO: update manager and database


    def handle_delete_macro_btn(self, item):

        response = yes_or_no_dialog('Delete Macro', 'Are you sure you wanna delete this Macro?')

        macro_id = int(item.text(0))

        if(response):
            # delete root item
            self.delete_item(item)

            # remove macro from macro manager & update database
            self.macro_manager.delete_macro_item(macro_id)

    def handle_delete_test_btn(self, item):

        macro_id = item.parent().text(0)

        test_id = int(item.text(0))
        test_name = item.text(1)

        response = yes_or_no_dialog('Delete Tests', f'Are you sure you want remove {test_name}?')

        if(response):
            # remove tests item from tree
            self.delete_child_item(item)

            # remove tests item from macro manager & update database
            self.macro_manager.delete_test_items(macro_id, test_id)


    def delete_item(self, item):
        index = self.indexOfTopLevelItem(item)
        self.takeTopLevelItem(index)

    def delete_child_item(self, item):

        parent = item.parent()
        if parent is not None:
            index = parent.indexOfChild(item)

            parent.takeChild(index)

            return True

        return False