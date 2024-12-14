import os
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

class TableFooterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_page = 1;
        self.total_pages = 1;
        self.limit = None;

        self.valid_rows = [100, 200, 300]

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'tableFooterWidget.ui')

        self.ui = loadUi(file_path, self)  # Pass 'self' as parent



    def load_data(self, current_page, limit, total_pages):
        self.current_page = current_page
        self.limit = limit
        self.total_pages = total_pages

        # Update the pages
        self.QSpinBox.setValue(current_page)
        self.QSpinBox.setMaximum(total_pages)
        self.pageLabel.setText(f'of {total_pages}')

        if(self.limit in self.valid_rows):
            index = self.valid_rows.index(self.limit)
            self.QComboBox.setCurrentIndex(self.valid_rows[index])

    def set_total_pages(self, total_pages):
        self.total_pages = total_pages

        self.pageLabel.setText(f'of {self.total_pages}')

        self.QSpinBox.setMaximum(self.total_pages)

    def set_current_page(self, current_page):
        self.current_page = current_page;
        self.QSpinBox.setValue(current_page)

    def set_limit_index(self, index):
        self.QComboBox.setCurrentIndex(index)

    def set_valid_rows(self, valid_rows):
        self.QComboBox.clear()
        self.valid_rows = valid_rows
        rows = [str(value) for value in valid_rows]

        self.QComboBox.addItems(rows)

class TableFooterWidget2(QWidget):
    new_page = pyqtSignal(int) # Emits page changes
    new_limit = pyqtSignal(int) # Emits new limit

    def __init__(self):
        super().__init__()

        self.current_page = 1;
        self.total_rows = None
        self.total_pages = None
        self.valid_rows = None

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'tableFooterWidget.ui')

        self.ui = loadUi(file_path, self)  # Pass 'self' as parent

        # Set up the connections
        self._connect_signals()

    def _connect_signals(self):
        self.ui.QComboBox.currentIndexChanged.connect(self.on_total_rows_changed)
        self.ui.QSpinBox.valueChanged.connect(self.on_spinbox_value_changed)
        self.ui.nextBtn.clicked.connect(self.on_next_clicked)
        self.ui.prevBtn.clicked.connect(self.on_prev_clicked)

    def load_data(self, total_pages, total_rows):
        self.total_rows = total_rows # basically the limit
        self.total_pages = total_pages

        # Update the pages
        self.QSpinBox.setValue(self.current_page)
        self.QSpinBox.setMaximum(total_pages)
        self.pageLabel.setText(f'of {total_pages}')

        # Set the current combo box index
        if(self.total_rows in self.valid_rows):
            self.ui.QComboBox.setCurrentIndex(self.valid_rows[total_rows])


    def total_rows_setup(self, valid_rows=None):
        if valid_rows is None:  # Initialize valid_rows if not provided
            valid_rows = {100: 0, 200: 1, 300: 3}

        self.set_valid_rows(valid_rows)


    def set_valid_rows(self, valid_rows):
        self.valid_rows = valid_rows

        valid_rows_list = [str(key) for key in self.valid_rows.keys()]

        if valid_rows_list:  # Check if the list is not empty
            self.total_rows = valid_rows_list[0]

        self.ui.QComboBox.clear()
        self.ui.QComboBox.addItems(valid_rows_list)

    def set_total_pages(self, total_pages):

        # Reset current page and set the total pages
        self.current_page = 1
        self.total_pages = total_pages

        # Update the spin box and page label
        self.QSpinBox.setValue(self.current_page)
        self.QSpinBox.setMaximum(self.total_pages)
        self.pageLabel.setText(f'of {self.total_pages}')


    def on_total_rows_changed(self, index):
        # Emit the new limit when combo box index changes
        selected_value = list(self.valid_rows.keys())[index]
        self.new_limit.emit(selected_value)


    def on_spinbox_value_changed(self, value):
        print(f'new value: {value}')

        self.current_page = value
        self.new_page.emit(self.current_page)


    def on_next_clicked(self):
        print('on_next_clicked clicked')

        if self.current_page < self.total_pages:
            self.current_page += 1
            self.QSpinBox.setValue(self.current_page)

    def on_prev_clicked(self):
        print('on_prev_clicked Clicked')

        if self.current_page > 1:
            self.current_page -= 1
            self.QSpinBox.setValue(self.current_page)
