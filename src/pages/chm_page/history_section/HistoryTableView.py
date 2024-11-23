from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget,
    QHBoxLayout
)

#! this is the error with this
from modules.constants import STATUS_STATE

class HistoryTableView(QObject):

    error_status = pyqtSignal(int) # pass an error signal

    def __init__(self, table):
        self.table = table;

    error_status = pyqtSignal(int) # pass an error signal

    pass;


    def format_table(self):
        pass;

class HistoryTableView2(QObject):

    open_signal = pyqtSignal(int) # Emits a job Number as int
    toggle_status = pyqtSignal(int) # pass edited row
    error_status = pyqtSignal(int) # pass an error signal
    filter_col = pyqtSignal(int)

    def __init__(self, table, history_manager):
        super().__init__()
        self.table = table

        self.history_manager = history_manager

        self.format_table()

        #self.table.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_changed)

    def format_table(self):
        #TODO: show the total tests, type, rush
        #TODO: settings can allow for this

        column_names = ['Job Number', 'Client Name', 'Creation Date','Status', 'Actions']

        self.table.setColumnCount(len(column_names))
        self.table.setHorizontalHeaderLabels(column_names)

        # set the width for items
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 400)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 200)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

        # disable table editing
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Enable sorting
        self.table.setSortingEnabled(True)


    def filter_table_by(self, filter_col):
        if(filter_col == 1):
            self.table.sortItems(filter_col, Qt.AscendingOrder)
        else:
            self.table.sortItems(filter_col, Qt.DescendingOrder)

    def on_sort_changed(self, sort_col):
        logger.info(f'Entering on_sort_changed sort_col: {sort_col}')

        sorting_order = self.table.horizontalHeader().sortIndicatorOrder()
        logger.debug(f'sorting_order: {sorting_order}')

        self.filter_col.emit(sort_col)


    def populate_table(self):
        self.clear_table()

        table_items = self.history_manager.get_all_items()

        row_height = 24
        self.table.setRowCount(len(table_items))

        # must load in all of the data before we can use the existing sort feature
        self.table.setSortingEnabled(False)

        for row, current_item in enumerate(table_items):
            jobNum = current_item.jobNum
            companyName = current_item.companyName
            creationDate = current_item.creationDate
            status = current_item.status

            self.table.setRowHeight(row, row_height)

            # Create QTableWidgetItem for each column
            jobNum_item = QTableWidgetItem(str(jobNum))
            companyName_item = QTableWidgetItem(companyName)
            creationDate_item = QTableWidgetItem(str(creationDate))
            status_item = QTableWidgetItem('Complete' if status == 1 else 'Incomplete')

            # Optionally align the text in the center
            jobNum_item.setTextAlignment(Qt.AlignCenter)
            creationDate_item.setTextAlignment(Qt.AlignCenter)
            status_item.setTextAlignment(Qt.AlignCenter)

            # Assign each item to the correct row and column
            self.table.setItem(row, 0, jobNum_item)         # Column 0 for jobNum
            self.table.setItem(row, 1, companyName_item)    # Column 1 for companyName
            self.table.setItem(row, 2, creationDate_item)   # Column 2 for creationDate
            self.table.setItem(row, 3, status_item)         # Column 3 for status

            # Set Status Widget Color
            color = "green" if status == 1 else "red"
            status_item.setForeground(QColor(color))

            # Create the action buttons
            self.create_action_buttons(row, jobNum, status_item)

        self.table.setSortingEnabled(True)


    def clear_table(self):
        logger.info('Entering clear_table')
        self.table.clearContents()
        self.table.setRowCount(0)

        # Function to create action buttons for each row
    def create_action_buttons(self, row, jobNum, status_widget):
        logger.info(f'Entering create_action_buttons with parameter: row: {row}, jobNum: {jobNum}')

        action_widget = QWidget()

        # Create the state toggle button
        status_btn = QPushButton("Toggle Status")
        status_btn.setProperty('jobNum', jobNum)
        status_btn.setProperty('status', 'test')

        # Create the open button
        open_btn = QPushButton("Open")
        open_btn.setProperty('jobNum', jobNum)

        status_btn.clicked.connect(lambda: self.toggle_status_clicked(row, status_widget))
        open_btn.clicked.connect(lambda: self.open_button_clicked(jobNum))

        status_btn.setFixedSize(120,20)
        open_btn.setFixedSize(120,20)

        layout = QHBoxLayout(action_widget)
        layout.addWidget(status_btn)
        layout.addWidget(open_btn)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(1)
        layout.addStretch(0)

        self.table.setCellWidget(row, 4, action_widget)  # Assuming 5 columns in total

    def open_button_clicked(self, jobNum):
        self.open_signal.emit(int(jobNum))

    def toggle_status_clicked(self, row, status_widget):
        logger.info('Entering toggle_status_clicked')

        # update item and database
        status = self.history_manager.toggle_item_status(row)

        new_status = STATUS_STATE[status]

        status_widget.setText(new_status)

        color = "green" if status == 1 else "red"
        status_widget.setForeground(QColor(color))
