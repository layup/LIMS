
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem, QWidget,QPushButton, QHBoxLayout, QAbstractItemView, QSpacerItem, QSizePolicy, QTreeWidgetItem


class TestsView(QObject):

    edit_btn_clicked = pyqtSignal(int)
    delete_btn_clicked = pyqtSignal(int)
    add_btn_clicked = pyqtSignal()
    search_btn_clicked = pyqtSignal()
    clear_btn_clicked = pyqtSignal()

    test_selected = pyqtSignal(object)

    def __init__(self,  tree, table, add_btn, search_bar, search_btn, clear_btn):
        super().__init__()

        self.tree = tree
        self.table = table
        self.add_btn = add_btn
        self.search_bar = search_bar
        self.search_btn = search_btn
        self.clear_btn = clear_btn

        self.tree.currentItemChanged.connect(self.test_selected.emit)
        #self.tree.clicked.connect(self.test_selected.emit)

        self.add_btn.clicked.connect(self.add_btn_clicked.emit)
        self.search_bar.returnPressed.connect(self.search_btn_clicked.emit)
        self.search_btn.clicked.connect(self.search_btn_clicked.emit)
        self.clear_btn.clicked.connect(self.clear_btn_clicked.emit)


    def update_tree(self, data):

        self.tree.clear()

        for row, (test_id, test_info) in enumerate(data.items()):

            test_name = test_info.test_name
            text_name = test_info.chem_name
            display_name = test_info.display_name if test_info.display_name  else ''
            side_comment = test_info.comment if test_info.comment  else ''

            parent_item = QTreeWidgetItem([str(test_id), str(test_name)])


            self.tree.addTopLevelItem(parent_item)


    def update_table(self, data):

        self.table.setRowCount(len(data.items()))

        self.table.setSortingEnabled(False)

        for row, (test_id, test_info) in enumerate(data.items()):

            test_name = test_info.test_name
            text_name = test_info.chem_name
            display_name = test_info.display_name if test_info.display_name  else ''
            side_comment = test_info.comment if test_info.comment  else ''

            row_items = [
                QTableWidgetItem(str(test_id)),
                QTableWidgetItem(str(test_name)),
                QTableWidgetItem(str(text_name)),
                QTableWidgetItem(str(display_name)),
                QTableWidgetItem(str(side_comment))
            ]

            for col, item in enumerate(row_items):
                if(col == 0):
                    item.setData(Qt.UserRole, int(test_id))
                    item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row, col, item)

            action_widget = self.create_action_widget(row, test_id)

            # Add the button widget to the table cell
            self.table.setCellWidget(row, 5, action_widget)

            # set the row height
            self.table.setRowHeight(row, 28)

        self.table.setSortingEnabled(True)


    def create_action_widget(self, row, test_id):
        # Create button widget
        button_widget = QWidget()
        layout = QHBoxLayout()
        button_widget.setLayout(layout)

        # Add buttons to the widget
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")

        edit_btn.clicked.connect(lambda: self.edit_btn_clicked.emit(test_id))
        delete_btn.clicked.connect(lambda: self.delete_btn_clicked.emit(test_id))

        edit_btn.setFixedWidth(50)
        delete_btn.setFixedWidth(50)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addItem(spacer)
        layout.setContentsMargins(2, 0, 0, 0)  # Remove margins

        return button_widget
