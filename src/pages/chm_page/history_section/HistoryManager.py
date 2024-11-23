
import math
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QCompleter, QAbstractItemView, QHeaderView, QTableWidgetItem, QPushButton, QWidget,
    QHBoxLayout
)

from modules.dbFunctions import updateChmTestsData, deleteChmTestDataItem
from modules.constants import  TABLE_ROW_HEIGHT


'''
How the table controller fits into MVC:

    Model:
        Represents the data, like the table contents, database records, etc.
        The model handles the logic for data manipulation (insertion, deletion, update) and communicates with the database or any data storage.

    View:
        The UI representation of the data (e.g., QTableView, QComboBox, etc.).
        It is responsible for displaying the data and triggering UI events (e.g., mouse clicks, text changes).

    Controller:
        The table controller (or view controller) is the intermediary between the model and the view.
        It listens for signals from the view (e.g., cell clicked, value edited, page changed) and updates the model/data accordingly.
        It also listens to the model for any updates to the data and tells the view to refresh or re-render the table.

'''
class HistoryItem:
    def __init__(self, jobNum, sampleNum, testNum, testName, testVal, unit, standard, creation):
        self.jobNum = jobNum
        self.sampleNum = sampleNum
        self.testNum = testNum
        self.testName = testName
        self.testVal = testVal
        self.unit = unit
        self.standard = standard
        self.creation = creation

    def get_values(self):
        return self.jobNum, self.sampleNum, self.testNum, self.testName, self.testVal, self.unit, self.standard, self.creation

    def side_edit_update(self, testNum, testName, testVal, standard, unit):
        self.testName = testName
        self.testNum = testNum
        self.testVal = testVal
        self.standard = standard
        self.unit = unit

    def __eq__(self, other):
        # To ensure `remove()` knows what qualifies as an equal HistoryItem
        if isinstance(other, HistoryItem):
            return (self.jobNum == other.jobNum and self.sampleNum == other.sampleNum
                    and self.testNum == other.testNum and self.testName == other.testName
                    and self.testVal == other.testVal and self.unit == other.unit
                    and self.standard == other.standard and self.creation == other.creation)
        return False

    def __repr__(self):
       return (f"HistoryItem(jobNum={self.jobNum}, sampleNum={self.sampleNum}, testNum={self.testNum}, "
                f"testName='{self.testName}', testVal={self.testVal}, unit='{self.unit}', "
                f"standard='{self.standard}', creation='{self.creation}')")



# managers the data and logic
class HistoryModel:
    def __init__(self, db):
        self.db = db;

        self.history_items = []

        self.current_page = 1;
        self.total_pages = 1;

        self.off_set = 0;
        self.page_size = 100;
        self.page_sizes = []

    def add_item(self, item):
        sampleNum = item[0]
        testNum = item[1]
        testVal = item[2]
        standard = item[3]
        unit = item[4]
        jobNum = item[5]
        creationDate = item[6]
        #TODO: get testName
        testName = get_tests_name(self.db, testNum)

        self.history_items.append(HistoryItem(jobNum, sampleNum, testNum, testName, testVal, unit, standard, creationDate))

    def total_items(self):
        return len(self.history_items)

    def get_all_item(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def load_items(self, limit, offset, search_query=''):

        self.clear_items()

        if(search_query == ''):
            results = get_chem_tests(self.db, limit, offset)
           # print(results);
        else:
            results = search_jobs(self.db, limit, offset, search_query)

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = get_chem_tests_count(self.db)
        else:
            total_items = search_jobs_count(self.db, search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages

    def remove_item(self, current_item):

        try:
            if(deleteChmTestDataItem(self.db, current_item.sampleNum, current_item.testNum, current_item.jobNum)):

                self.history_items.remove(current_item)
                return True
            else:
                return False;

        except Exception as error:
            return False;

    def update_item(self, current_item, new_data):

        try:
            testNum = new_data[0]
            testName = get_tests_name(self.db, testNum)
            testVal = new_data[1]
            standard = new_data[2]
            unit = new_data[3]

            if(updateChmTestsData(self.db, current_item.sampleNum, testNum, current_item.jobNum, testVal, standard, unit )):

                current_item.side_edit_update(testNum, testName, testVal, standard, unit)
                return True

            return False;

        except Exception as error:
            print(error)

            return False






def get_chem_tests(db, limit, offset):
    query = '''
        SELECT *
        FROM chemTestsData
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?

    '''
    results = db.query(query, (limit, offset))
    return results

def get_chem_tests_count(db):
    query = '''
        SELECT count(jobNum)
        FROM chemTestsData
    '''
    results = db.query(query)
    return results[0][0]

def get_tests_name(db, test_id):
    logger.info('Entering get_tests_name')
    query = '''
        SELECT testName
        FROM Tests
        WHERE testNum = ?

    '''

    results = db.query(query, (test_id, ))

    return results[0][0]


def search_jobs(db, limit, offset, search_query):
    query = """
        SELECT *
        FROM chemTestsData
        WHERE jobNum LIKE ?
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, limit, offset))

    return results

def search_jobs_count(db, search_query):
    query = """
        SELECT count(jobNum)
        FROM chemTestsData
        WHERE jobNum LIKE ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, ))

    return results[0][0]


# manages the interaction between the view and model
class HistoryController:

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.search_query = ''
        self.active_row_item = None;
        self.edit_item = None;

        self.view.filterChanged.connect(self.handle_filter_change)

        self.view.searchTextEmit.connect(self.handle_search)
        self.view.editClicked.connect(self.handle_edit_btn)
        self.view.deleteClicked.connect(self.handle_delete_btn)

        self.view.cancelBtnClicked.connect(self.handle_cancel_btn)
        self.view.saveBtnClicked.connect(self.handle_save_btn)
        self.view.nextPageClicked.connect(self.handle_next_page)
        self.view.prevPageClicked.connect(self.handle_prev_page)
        self.view.spinBoxValueChanged.connect(self.handle_spinbox_change)
        self.view.comboBoxIndexChanged.connect(self.handle_combobox_change)

        # load initial values
        self.load_initial_data()

    def load_initial_data(self):
        # load in the initial data
        valid_rows = [25, 50, 100]

        self.model.page_size = valid_rows[0]
        self.model.page_sizes = valid_rows;
        self.view.footer.set_valid_rows(valid_rows)

        # load in the initial data
        data = self.model.load_items(limit=self.model.page_size , offset=self.model.off_set)
        total_pages = self.model.calculate_total_pages()

        # update database
        self.view.update_table(data)
        self.view.update_footer(total_pages=total_pages)

    def handle_cancel_btn(self):
        logger.info('Entering handle_cancel_btn')

        self.handle_hide_side_edit()


    def handle_save_btn(self, updated_data):
        logger.info(f'Entering handle_save_btn with updated_data: {updated_data}')

        self.view.update_side_edit_visibility(False)

        update_status = self.model.update_item(self.edit_item, updated_data)

        if(update_status):
            self.view.update_table_row(self.active_row_item, self.edit_item)


    def handle_edit_btn(self, current_item, row_item):
        logger.info('Entering handle_edit_btn')

        # toggle the visibility
        self.view.update_side_edit_visibility(True)

        # save the info for what side edit is being edited
        self.edit_item = current_item
        self.active_row_item = row_item

        logger.info(current_item.__repr__())

        # load in the data to the side edit
        self.view.update_side_edit(current_item, row_item)


    def handle_delete_btn(self, current_item, row_items):
        logger.info('Entering handle_delete_btn')

        # TODO: delete model item
        self.model.remove_item(current_item)
        self.view.remove_table_row(row_items[0])

        # TODO: remove from database

        self.handle_hide_side_edit()

    def handle_combobox_change(self, index):
        logger.info(f'Entering handle_combobox_change with index: {index}')

        if(index != -1):
            print(f'index: {index}, new_page_size: {self.model.page_sizes[index]}')
            # update the page size
            self.model.page_size = self.model.page_sizes[index]
            # reset the current_page and offset
            self.model.current_page = 1;
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size

            self.update_view()

    def handle_search(self, search_query):
        logger.info(f'Entering handle_search with search_query: {search_query}')

        self.search_query = search_query
        self.model.current_page = 1;
        self.model.off_set = (self.model.current_page - 1) * self.model.page_size

        self.update_view()

    def handle_next_page(self):
        logger.info('Entering handle_next_page')

        if(self.model.current_page < self.model.total_pages):
            self.model.current_page +=1;
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_prev_page(self):
        logger.info('Entering handle_prev_page')

        if(self.model.current_page > 1):
            self.model.current_page -=1;
            self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_spinbox_change(self, new_page):
        logger.info('Entering handle_spinbox_change')

        self.model.current_page = new_page;
        self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
        self.update_view()


    def handle_filter_change(self, index):
        logger.info(f'Entering handle_filter_change index: {index}')

        self.view.sort_table(index)


    def handle_hide_side_edit(self):
        logger.info('Entering handle_hide_side_edit')

        self.view.update_side_edit_visibility(False)
        self.edit_item = None;
        self.active_row_item = None;

    def update_view(self):
        logger.info('Entering update_view')

        # toggle hide side edit
        self.handle_hide_side_edit()

        data = self.model.load_items(limit=self.model.page_size, offset=self.model.off_set, search_query=self.search_query)
        total_pages = self.model.calculate_total_pages(search_query=self.search_query)
        self.view.update_table(data)
        self.view.update_footer(current_page=self.model.current_page, total_pages=total_pages)



# table, footer, side edit
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

        #self.table.horizontalHeader().sectionClicked.connect(self.sort_table_row)



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
                QTableWidgetItem(str(current_item.standard)),
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
        delete_btn = QPushButton("Delete")

        # Connect buttons to appropriate controller signals
        edit_btn.clicked.connect(lambda: self.action_edit_button_clicked(row, current_item, row_items))
        delete_btn.clicked.connect(lambda: self.action_delete_button_clicked(row, current_item, row_items))

        edit_btn.setFixedSize(120,18)
        delete_btn.setFixedSize(120,18)

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
        row_items[5].setText(current_item.standard)


    def sort_table(self, index):

        if(index in [1, 6]):
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
        # update rows
        # update current page
        # update total page
        pass


