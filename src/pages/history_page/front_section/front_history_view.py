
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QHeaderView, QDialog, QPushButton, QAbstractItemView, QTableWidgetItem, QCompleter

from pages.history_page.front_section.front_history_item import FrontHistoryItem

class FrontHistoryView(QObject):
    # Search Widget items
    searchTextEmit = pyqtSignal(str)
    filterChanged = pyqtSignal(int)

    sortIndicatorChanged = pyqtSignal(int)

    # Footer items
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

        self.table.horizontalHeader().sortIndicatorChanged.connect(self.sortIndicatorChanged.emit)


    def search_activated(self):
        current_text = self.search.get_search_text()
        self.searchTextEmit.emit(current_text)

    def update_table(self, data):
        # refresh the table with the new data
        self.table.clearContents()

        # Bring the vertical scroll bar back to the top
        self.table.verticalScrollBar().setValue(0)

        row_height = 24;
        total_items = len(data)
        self.table.setRowCount(total_items)

        # disable sorting
        self.table.setSortingEnabled(False)

        for row, current_item in enumerate(data):

            self.table.setRowHeight(row, row_height)

            row_items = [
                QTableWidgetItem(str(current_item.jobNum)),
                QTableWidgetItem(str(current_item.clientName)),
                QTableWidgetItem(str(current_item.creation)),
                QTableWidgetItem(str(current_item.status)),
            ]

            # Set text alignment to center for each item in the row
            for item in row_items:
                item.setTextAlignment(Qt.AlignCenter)

            # Add items to the table in the specified row and columns
            for col, item in enumerate(row_items):

                if(col != 3):
                    self.table.setItem(row, col, item)
                else:
                    if(int(current_item.status) == 0):
                        item.setText('INCOMPLETE')
                        item.setForeground(QBrush(QColor("red")))
                    else:
                        item.setText('COMPLETE')
                        item.setForeground(QBrush(QColor("green")))

                    self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)

        self.sort_table(self.search.filters.currentIndex())

    def sort_table(self, index):

        if(index == 0):
            self.table.sortItems(index, Qt.DescendingOrder)
        else:
            self.table.sortItems(index)


    def update_filter_index(self, index):
        self.search.filters.setCurrentIndex(index)

    def update_footer(self, current_page=None, total_pages=None, filter_size=None):

        if(total_pages):
            self.footer.set_total_pages(total_pages)

        if(current_page):
            self.footer.set_current_page(current_page)