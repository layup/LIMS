
from base_logger import logger

from PyQt5.QtCore import (Qt, pyqtSignal, QObject, QSize, QVariant)
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QIcon

class NavigationManager(QObject):

    stack_change = pyqtSignal(int)
    report_tab_change = pyqtSignal(int)
    icp_tab_change = pyqtSignal(int)
    chm_tab_change = pyqtSignal(int)

    def __init__(self, navigation ):
        super().__init__()

        self.navigation_tree = navigation

        # connect signal
        self.navigation_tree.itemClicked.connect(self.handle_item_clicked)

        self.setup()

    def setup(self):

        self.navigation_tree.clear()
        self.navigation_tree.setIconSize(QSize(20, 20))

        # set parents
        report_item = QTreeWidgetItem(self.navigation_tree, ["Reports History"])
        icp_item = QTreeWidgetItem(self.navigation_tree, ["ICP Tools"])
        chm_item = QTreeWidgetItem(self.navigation_tree, ["CHM Tools"])
        test_item = QTreeWidgetItem(self.navigation_tree, ["Tests/Macros"])
        setting_item = QTreeWidgetItem(self.navigation_tree, ["Settings"])

        # set children items
        report_child1 = QTreeWidgetItem(report_item, ["Laboratory"])
        report_child2 = QTreeWidgetItem(report_item, ["Front"])

        icp_child1 = QTreeWidgetItem(icp_item, ["Database"])
        icp_child2 = QTreeWidgetItem(icp_item, ["Element"])
        icp_child3 = QTreeWidgetItem(icp_item, ["Reports"])

        chm_child1 = QTreeWidgetItem(chm_item, ["Database"])
        chm_child2 = QTreeWidgetItem(chm_item, ["Input Data"])
        chm_child3 = QTreeWidgetItem(chm_item, ["Reports"])


        # set secondary page/tab information
        report_item.setData(0, Qt.UserRole, 0)
        icp_item.setData(0, Qt.UserRole, 2)
        chm_item.setData(0, Qt.UserRole, 3)
        test_item.setData(0, Qt.UserRole, 1)

        report_child1.setData(0, Qt.UserRole, ['report', 0])
        report_child2.setData(0, Qt.UserRole, ['report', 1])

        icp_child1.setData(0, Qt.UserRole, ['icp', 0])
        icp_child2.setData(0, Qt.UserRole, ['icp', 1])
        icp_child3.setData(0, Qt.UserRole, ['icp', 2])

        chm_child1.setData(0, Qt.UserRole, ['chm', 0])
        chm_child2.setData(0, Qt.UserRole, ['chm', 1])
        chm_child3.setData(0, Qt.UserRole, ['chm', 3])

        # set Icons
        report_item.setIcon(0, QIcon("assets/icons/reports_icon.svg"))
        icp_item.setIcon(0, QIcon("assets/icons/tools_icon.svg"))
        chm_item.setIcon(0, QIcon("assets/icons/tools_icon.svg"))
        test_item.setIcon(0, QIcon("assets/icons/lab_panel_icon.svg"))
        setting_item.setIcon(0, QIcon('assets/icons/settings_icon.png'))

        report_child1.setIcon(0, QIcon("assets/icons/reports_icon.svg"))
        report_child2.setIcon(0, QIcon("assets/icons/reports_icon.svg"))

        icp_child1.setIcon(0, QIcon("assets/icons/database_icon.svg"))
        icp_child2.setIcon(0, QIcon("assets/icons/breaker_icon.svg"))
        icp_child3.setIcon(0, QIcon("assets/icons/reports_icon.svg"))

        chm_child1.setIcon(0, QIcon("assets/icons/database_icon.svg"))
        chm_child2.setIcon(0, QIcon("assets/icons/upload_icon.png"))
        chm_child3.setIcon(0, QIcon("assets/icons/reports_icon.svg"))


    def handle_item_clicked(self, item):
        logger.info('Entering handle_item_clicked')

        secret_data = item.data(0, Qt.UserRole)
        logger.info(f"Clicked item: {item.text(0)} | secret_data: {secret_data}")

        if(item.parent() is None):
            #TODO: make sure all of them emit something and double check since 0 is consider fasly
            self.stack_change.emit(secret_data)

        elif item.childCount() > 0:
            #print(f"{item.text(0)} is a parent item.")
            pass;

        else:
            if(secret_data):
                if(secret_data[0] == 'icp'):
                    self.stack_change.emit(item.parent().data(0, Qt.UserRole))
                    self.icp_tab_change.emit(secret_data[1])
                if(secret_data[0] == 'chm'):
                    self.stack_change.emit(item.parent().data(0, Qt.UserRole))
                    self.chm_tab_change.emit(secret_data[1])
                if(secret_data[0] == 'report'):
                    self.stack_change.emit(item.parent().data(0, Qt.UserRole))
                    self.report_tab_change.emit(secret_data[1])


            #print(f"{item.text(0)} is a leaf item.")





