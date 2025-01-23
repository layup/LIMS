from PyQt5.QtCore import Qt, QObject, pyqtSignal

from PyQt5.QtWidgets import (
    QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget,
    QHBoxLayout, QSpacerItem, QSizePolicy
)

from pages.icp_page.history_tab.icp_history_item import IcpHistoryItem

class IcpHistoryView(QObject):
    searchTextEmit = pyqtSignal(str)
    filterChanged = pyqtSignal(int)

    uploadBtnClicked = pyqtSignal()
    openBtnClicked = pyqtSignal(IcpHistoryItem)
    printBtnClicked = pyqtSignal(str)

    nextPageClicked = pyqtSignal()
    prevPageClicked = pyqtSignal()

    spinBoxValueChanged = pyqtSignal(int)
    comboBoxIndexChanged = pyqtSignal(int)

    def __init__(self,  table, footer, search, upload_btn):
        super().__init__()
        # view items
        self.table = table
        self.footer = footer

        self.search = search
        self.upload_btn = upload_btn

        self.upload_btn.clicked.connect(self.uploadBtnClicked.emit)

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

    def update_table(self, data):

        # refresh the table with the new data
        self.table.clearContents()

        # Bring the vertical scroll bar back to the top
        self.table.verticalScrollBar().setValue(0)

        row_height = 28;
        total_items = len(data)
        self.table.setRowCount(total_items)

       # disable sorting
        self.table.setSortingEnabled(False)

        for row, current_item in enumerate(data):

            self.table.setRowHeight(row, row_height)

            row_items = [
                QTableWidgetItem(str(current_item.sampleName)),
                QTableWidgetItem(str(current_item.jobNum)),
                QTableWidgetItem(str(current_item.machine)),
                QTableWidgetItem(str(current_item.fileName)),
                QTableWidgetItem(str(current_item.creation)),
            ]

            # Set text alignment to center for each item in the row
            for item in row_items:
                item.setTextAlignment(Qt.AlignCenter)

            # Add items to the table in the specified row and columns
            for col, item in enumerate(row_items):

                self.table.setItem(row, col, item)

            self.create_open_btn(row, 5, current_item)

        self.table.setSortingEnabled(True)

    def create_open_btn(self, row, col, current_item):

        # Create button widget
        button_widget = QWidget()
        layout = QHBoxLayout()
        button_widget.setLayout(layout)

        open_btn = QPushButton("View Sample")
        print_btn = QPushButton('Print Batch')
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        open_btn.setFixedSize(120,18)
        print_btn.setFixedSize(120,18)

        open_btn.clicked.connect(lambda: self.openBtnClicked.emit(current_item))
        print_btn.clicked.connect(lambda: self.printBtnClicked.emit(current_item.fileName))

        layout.addWidget(open_btn)
        layout.addWidget(print_btn)
        layout.addItem(spacer)
        layout.setContentsMargins(2, 0, 0, 0)  # Remove margins

        self.table.setCellWidget(row, col, button_widget)

    def sort_table(self, index):
        if(index in [0,1,4]):
            self.table.sortItems(index, Qt.DescendingOrder)
        else:
            self.table.sortItems(index)


    def update_footer(self, current_page=None, total_pages=None, filter_size=None):

        if(total_pages):
            self.footer.set_total_pages(total_pages)

        if(current_page):
            self.footer.set_current_page(current_page)

