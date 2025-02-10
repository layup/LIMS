import math
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget,
    QHBoxLayout
)


from pages.chm_page.history_tab.HistoryItem import HistoryItem

class HistoryView(QObject):
    searchTextEmit = pyqtSignal(str)
    filterChanged = pyqtSignal(int)

    deleteClicked = pyqtSignal(HistoryItem, list)
    editClicked = pyqtSignal(HistoryItem, list)

    sideEditCancelBtn = pyqtSignal()
    sideEditSaveBtn   =  pyqtSignal()

    cancelBtnClicked = pyqtSignal()
    saveBtnClicked = pyqtSignal(list)
    nextPageClicked = pyqtSignal()
    prevPageClicked = pyqtSignal()

    spinBoxValueChanged = pyqtSignal(int)
    comboBoxIndexChanged = pyqtSignal(int)

    def __init__(self,  table, side_edit, footer, search_line, search_btn, filter_item):
        super().__init__()
        # view items
        self.table = table
        self.side_edit = side_edit
        self.footer = footer

        #TODO: maybe move into the controller or have outside function that connects to it
        self.search_line = search_line
        self.search_btn = search_btn
        self.filter = filter_item

        self.filter.currentIndexChanged.connect(self.filterChanged.emit)

        self.search_line.returnPressed.connect(lambda: self.searchTextEmit.emit(self.search_line.text()))
        self.search_btn.clicked.connect(lambda: self.searchTextEmit.emit(self.search_line.text()))

        # emit signals on button clicks, value changes
        self.side_edit.cancelBtn.clicked.connect(lambda: self.cancelBtnClicked.emit())
        self.side_edit.saveBtn.clicked.connect(lambda: self.saveBtnClicked.emit(self.side_edit.get_job_info()))

        self.footer.nextBtn.clicked.connect(lambda: self.nextPageClicked.emit())
        self.footer.prevBtn.clicked.connect(lambda: self.prevPageClicked.emit())
        self.footer.QSpinBox.valueChanged.connect(self.spinBoxValueChanged.emit)
        self.footer.QComboBox.currentIndexChanged.connect(self.comboBoxIndexChanged.emit)


    def update_side_edit_visibility(self, status):
        self.side_edit.setVisible(status)

    def toggle_side_edit_visibility(self, status=None):

        if(status):
            self.side_edit.setVisible(status)
        else:
            current_visibility = self.side_edit.isVisible()
            self.side_edit.setVisible(not current_visibility)


    def update_side_edit(self, history_item, row_item):
        logger.info(f'Entering update_side_edit with {history_item.__repr__()}')

        self.side_edit.load_job_info(history_item, row_item)


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
                QTableWidgetItem(str(current_item.sampleNum)),
                QTableWidgetItem(str(current_item.testName)),
                QTableWidgetItem(str(current_item.testVal)),
                QTableWidgetItem(str(current_item.unit)),
                QTableWidgetItem(str(current_item.recovery)),
                QTableWidgetItem(str(current_item.creation))
            ]

            # Set text alignment to center for each item in the row
            for item in row_items:
                item.setTextAlignment(Qt.AlignCenter)

            # Add items to the table in the specified row and columns
            for col, item in enumerate(row_items):
                self.table.setItem(row, col, item)

            self.create_action_buttons(row, 7, current_item, row_items)

        self.table.setSortingEnabled(True)
        self.sort_table(self.filter.currentIndex())


    # Function to create action buttons for each row
    def create_action_buttons(self, row, col, current_item,  row_items):
        action_widget = QWidget()

        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("")

        # Load the SVG file
        svg_renderer = QSvgRenderer('assets/icons/delete_button.svg')
        pixmap = QPixmap(64, 64)  # Specify the desired size 64x64 or any suitable size
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        # Set the icon to the button
        icon = QIcon(pixmap)
        delete_btn.setIcon(icon)

        # Connect buttons to appropriate controller signals
        edit_btn.clicked.connect(lambda: self.action_edit_button_clicked(row, current_item, row_items))
        delete_btn.clicked.connect(lambda: self.action_delete_button_clicked(row, current_item, row_items))

        edit_btn.setFixedSize(120,18)
        delete_btn.setFixedSize(20,18)

        layout = QHBoxLayout(action_widget)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(1)
        layout.addStretch(0)

        self.table.setCellWidget(row, col, action_widget)  # Assuming 5 columns in total

        # Emit signals when buttons are clicked
    def action_edit_button_clicked(self, row, current_item, row_item):
        # Emit signal to controller that the "Edit" button was clicked

        self.editClicked.emit(current_item, row_item)

    def action_delete_button_clicked(self, row, current_item, row_item):
        # Emit signal to controller that the "Delete" button was clicked

        self.deleteClicked.emit(current_item, row_item)

    def update_table_row(self, row_items, current_item):
        row_items[2].setText(current_item.testName)
        row_items[3].setText(current_item.testVal)
        row_items[4].setText(current_item.unit)
        row_items[5].setText(current_item.recovery)

    def sort_table(self, index):

        logger.info(f'Entering sort_table with index: {index}')
        print(f'index type: {type(index)}, index: {index}')


        # issue with sorting column 1
        if(index in [0, 1, 6]):
            self.table.sortItems(index, Qt.DescendingOrder)
        else:
            self.table.sortItems(index)

    def remove_table_row(self, row_item):

        if row_item:
            row_to_remove = self.table.row(row_item)  # Get the row item
            self.table.removeRow(row_to_remove)

    def update_footer(self, current_page=None, total_pages=None, filter_size=None):

        if(total_pages):
            self.footer.set_total_pages(total_pages)

        if(current_page):
            self.footer.set_current_page(current_page)