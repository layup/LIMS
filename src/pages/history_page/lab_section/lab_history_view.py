import math
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QWidget, QHBoxLayout

from pages.history_page.lab_section.lab_history_item import LabHistoryItem

class LabHistoryView(QObject):
    searchTextEmit = pyqtSignal(str)
    filterChanged = pyqtSignal(int)

    openBtnClicked = pyqtSignal(LabHistoryItem)

    nextPageClicked = pyqtSignal()
    prevPageClicked = pyqtSignal()

    spinBoxValueChanged = pyqtSignal(int)
    comboBoxIndexChanged = pyqtSignal(int)

    def __init__(self,  table, footer, search):
        super().__init__()
        # view items
        self.table = table
        self.footer = footer
        self.search = search

        self.search.filters.currentIndexChanged.connect(self.filterChanged.emit)
        self.search.searchLine.returnPressed.connect(self.search_activated)
        self.search.searchBtn.clicked.connect(self.search_activated)

        self.footer.nextBtn.clicked.connect(self.nextPageClicked.emit)
        self.footer.prevBtn.clicked.connect(self.prevPageClicked.emit)
        self.footer.QSpinBox.valueChanged.connect(self.spinBoxValueChanged.emit)
        self.footer.QComboBox.currentIndexChanged.connect(self.comboBoxIndexChanged.emit)

    def search_activated(self):
        current_text = self.search.get_search_text()
        self.searchTextEmit.emit(current_text)

    def update_side_edit(self, history_item, row_item):
        logger.info(f'Entering update_side_edit with {history_item.__repr__}')

        self.side_edit.load_job_info(history_item, row_item)

    def update_table(self, data, params_name):
        # refresh the table with the new data
        self.table.clearContents()

        # Bring the vertical scroll bar back to the top
        self.table.verticalScrollBar().setValue(0)

        row_height = 24
        total_items = len(data)
        self.table.setRowCount(total_items)

        # disable sorting
        self.table.setSortingEnabled(False)

        for row, current_item in enumerate(data):

            self.table.setRowHeight(row, row_height)

            parameter = get_param_name(current_item.parameter, params_name)

            row_items = [
                QTableWidgetItem(str(current_item.jobNum)),
                QTableWidgetItem(str(current_item.report)),
                QTableWidgetItem(str(parameter)),
                QTableWidgetItem(str(current_item.dilution)),
                QTableWidgetItem(str(current_item.creation)),
                QTableWidgetItem(str(current_item.status)),
            ]

            # Set text alignment to center for each item in the row
            for item in row_items:
                item.setTextAlignment(Qt.AlignCenter)

            # Add items to the table in the specified row and columns
            for col, item in enumerate(row_items):

                if(col == 1):
                    report = current_item.report

                    if(report == 1):
                        item.setText('ICP')
                    else:
                        item.setText('CHM')

                if(col == 5):
                    status = current_item.status

                    print(f'status: {status}, type: {type(status)}')

                    if(status == 0):
                        item.setText('Not Generated')
                    elif(status == 1):
                        item.setText('Generated')
                    else:
                        item.setText('N/A')

                self.table.setItem(row, col, item)

            self.create_open_btn(row, 6, current_item)

        self.table.setSortingEnabled(True)
        self.sort_table(self.search.filters.currentIndex())

    def create_open_btn(self, row, col, current_item):

        open_btn = QPushButton("Open")
        open_btn.setFixedSize(120, 18)

        open_btn.clicked.connect(lambda: self.openBtnClicked.emit(current_item))

        self.table.setCellWidget(row, col, open_btn)

    def sort_table(self, index):

        # sorting the creation_date column, if same date refer to the higher job_num to be
        if index == 4:  # Date column
            self.table.sortItems(index, Qt.DescendingOrder)  # Primary sort: Date (descending)

            # Secondary sort: job_num (descending) for same dates
            for i in range(self.table.rowCount() - 1):
                for j in range(self.table.rowCount() - 1 - i):
                    date1 = self.table.item(j, index).data(Qt.EditRole)  # Get date value
                    date2 = self.table.item(j + 1, index).data(Qt.EditRole)

                    if date1 == date2:  # Same date
                        try:
                            job_num1 = int(self.table.item(j, 0).text())  # Get job_num as integer
                            job_num2 = int(self.table.item(j + 1, 0).text())

                            if job_num1 < job_num2:  # Higher job_num should be earlier
                                for k in range(self.table.columnCount()): # Swap entire rows
                                    item1 = self.table.item(j, k)
                                    item2 = self.table.item(j+1, k)
                                    self.table.setItem(j,k, item2)
                                    self.table.setItem(j+1, k, item1)

                        except ValueError:  # Handle invalid job_num format
                            print("Invalid job number format. Skipping secondary sort for these rows.")
                            pass  # Or handle it differently (e.g., compare as strings)

        elif index == 0: # Job number column
            self.table.sortItems(index, Qt.DescendingOrder)
        else:
            self.table.sortItems(index)  # Default sorting for other columns

    def update_footer(self, current_page=None, total_pages=None, filter_size=None):

        if(total_pages):
            self.footer.set_total_pages(total_pages)

        if(current_page):
            self.footer.set_current_page(current_page)


def get_param_name(param_id, param_names):
    #logger.info(f'Param ID: {param_id}, Type: {type(param_id)}')
    #logger.info(f'Param Names Keys: {list(param_names.keys())}, Key Types: {[type(key) for key in param_names.keys()]}')

    logger.info(f'get_param_name param_id: {param_id}, param_names: {param_names}')

    #TODO: fix this later so is more straight forward
    for current_id, current_item in param_names:
        if(param_id == current_id):
            return current_item.param_name


    return param_id
