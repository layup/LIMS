
from base_logger import logger

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import (
    QTableWidget, QHeaderView, QAbstractItemView,
    QTableWidgetItem, QMessageBox, QPushButton, QWidget,
    QHBoxLayout
)

from modules.dialogs.basic_dialogs import yes_or_no_dialog
from modules.dbFunctions import getTestsName, deleteChmTestDataItem
from modules.constants import  TABLE_ROW_HEIGHT, TABLE_COL_SMALL, TABLE_COL_MED
from modules.widgets.TableFooterWidget import TableFooterWidget

class DatabaseTableView(QObject):

    footerAction = pyqtSignal(int)
    dialogAction = pyqtSignal(int, list)

    def __init__(self, database, table, layout, dataModel, editWidgetSection):
        super().__init__()
        self.db = database
        self.table = table
        self.data_model = dataModel
        self.layout = layout
        self.editWidget = editWidgetSection

        # Footer Widget setup
        self.footerWidget = TableFooterWidget()
        self.layout.addWidget(self.footerWidget)

        self.setup_table()
        self.populate_table()

        self.setup_footer()

        self.footerWidget.nextBtn.clicked.connect(self.handle_next_page)
        self.footerWidget.prevBtn.clicked.connect(self.handle_prev_page)
        self.footerWidget.QSpinBox.valueChanged.connect(self.handle_spinBox_change)
        self.footerWidget.QComboBox.currentIndexChanged.connect(self.handle_row_filter_change)

    def setup_table(self):
        # Define table columns
        column_headers = ['Job Number', 'Sample Number', 'Tests Name', 'Test Value', 'Unit Value', 'Standard Value', 'Upload Date' , 'Actions']

        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Show the vertical rows
        self.table.verticalHeader().setVisible(True)

        # Disable Editing of the table
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set the width of the tables
        self.table.setColumnWidth(0, TABLE_COL_SMALL)
        self.table.setColumnWidth(1, TABLE_COL_SMALL)
        self.table.setColumnWidth(2, TABLE_COL_MED)
        self.table.setColumnWidth(3, TABLE_COL_SMALL)
        self.table.setColumnWidth(4, TABLE_COL_SMALL)
        self.table.setColumnWidth(5, TABLE_COL_SMALL)
        self.table.setColumnWidth(6, TABLE_COL_SMALL)

        # Set the last column to stretch
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)

    def populate_table(self):
        # Get the init data to populate table
        init_data = self.data_model.fetch_data()
        self.update_table(init_data)

    def setup_footer(self):
        self.update_footer()

    def update_table(self, results):
        logger.info('DatabaseTableView Update Table')

        self.clear_table()

        # Bring the vertical scroll bar back to the top
        self.table.verticalScrollBar().setValue(0)

        # Define table rows
        total_results = len(results)
        self.table.setRowCount(total_results)

        for row , data in enumerate(results):
            logger.debug(f'Row: {row}, Data: {data}')

            # Set the row height of each item
            self.table.setRowHeight(row, TABLE_ROW_HEIGHT)

            for col in range(len(data)):
                item = QTableWidgetItem()
                item.setText(str(data[col]))
                item.setTextAlignment(Qt.AlignCenter)

                # Get the Job Name
                if(col == 2):
                    convert_data = str(data[col])
                    testName = getTestsName(self.db, convert_data)

                    if(testName):
                        item = QTableWidgetItem(testName[0][0])
                        item.setTextAlignment(Qt.AlignCenter)

                if(col == 6):
                    if(data[col] == None):
                        item.setText('N/A');

                self.table.setItem(row ,col ,item)

            actionWidgetCol = 7
            actionWidget = createActionWidget(self, row)
            self.table.setCellWidget(row, actionWidgetCol, actionWidget)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.update_footer()

    def clear_table(self):
        # Get the number of rows
        num_rows = self.table.rowCount()

        # Iterate through all rows (in reverse order to avoid index shifting)
        for i in range(num_rows - 1, -1, -1):
            self.table.removeRow(i)

    def update_footer(self):
        footer_info = self.data_model.get_footer_info()
        print(f'Footer Info: {footer_info}')
        self.footerWidget.load_data(footer_info['current_page'], footer_info['total_rows'], footer_info['total_pages'])
        #self.layoutChanged.emit()

    def handle_search_text(self, text):
        status, result = self.data_model.set_filter(text)

        if(status == 0):
            msgBox = QMessageBox()
            msgBox.setText("No Search Results");
            msgBox.setInformativeText("No search results for given job number");
            msgBox.setStandardButtons(QMessageBox.Ok);
            x = msgBox.exec_()

    def handle_row_filter_change(self, index):
        self.data_model.set_rows(index)

    def handle_spinBox_change(self, newValue):
        self.data_model.set_page(newValue)

    def handle_next_page(self):
        footer_info = self.data_model.get_footer_info()

        if((footer_info['current_page']) != footer_info['total_pages']):
            self.data_model.set_page(footer_info['current_page']+1)

    def handle_prev_page(self):
        footer_info = self.data_model.get_footer_info()

        if((footer_info['current_page']) != 0):
            self.data_model.set_page(footer_info['current_page']-1)


#******************************************************************
#    ActionWidget Functions
#******************************************************************

def createActionWidget(self, row):
    deleteBtn = QPushButton("Delete")
    editBtn = QPushButton('Edit')

    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.addWidget(editBtn)
    button_layout.addWidget(deleteBtn)
    button_layout.setContentsMargins(5, 0, 0, 0)
    button_layout.setAlignment(Qt.AlignLeft)

    # Connect signals
    deleteBtn.clicked.connect(lambda: actionDeleteBtn(self, row ))
    editBtn.clicked.connect(lambda: actionEditBtn(self, row))

    return button_widget

def actionEditBtn(self, row):
    logger.info(f'Entering actionEditBtn with parameter: row: {row}')

    # Clear the existing data
    self.editWidget.clear_data()

    # highlight the current row in the table
    self.table.selectRow(row)
    self.editWidget.setVisible(True)
    #updateChmTestsData
    current_data = []

    for col in range(self.table.columnCount() -2):
        value = self.table.item(row, col).text()
        current_data.append(value)

    self.editWidget.set_data(current_data)
    self.editWidget.set_item(row);

def actionDeleteBtn(self, row):
    logger.info(f'Entering actionDeleteBtn with parameter: row: {row}')

    jobNum    = self.table.item(row, 0).text()
    sampleNum = self.table.item(row, 1).text()
    testsName = self.table.item(row, 2).text()

    logger.debug(f'Job Num: {jobNum}, Sample Num: {sampleNum}, Tests Name: {testsName}')

    result = yes_or_no_dialog('Delete Item?', 'This will delete this from the database. You cannot undo this action!')

    if(result):
        print(result)

        self.table.removeRow(row)

        #TODO: Lazy way of resolving the issue, but it works
        update_action_buttons(self)

        update_side_edit_info(self, row)

        #TODO: have the delete implemented from the SQL
        testNumQuery = 'SELECT testNum FROM Tests WHERE testName = ?'
        testNum = self.db.query(testNumQuery, (testsName, ))

        if(testNum):
            testNum = testNum[0][0]

            logger.debug(f'testNum: {testNum}')

            checkExistsQuery = 'SELECT 1 FROM chemTestsData WHERE sampleNum = ? AND testNum = ? AND jobNum = ?'
            self.db.execute(checkExistsQuery, (sampleNum, testNum, jobNum))
            result = self.db.fetchone()
            logger.debug(f'Result: {result}')

            if(result != None):
                deleteChmTestDataItem(self.db, sampleNum, testNum, jobNum)

def update_action_buttons(self):
    # Re-create the delete buttons after a row has been deleted
    for row in range(self.table.rowCount()):
        actionWidgetCol = 7
        actionWidget = createActionWidget(self, row)
        self.table.setCellWidget(row, actionWidgetCol, actionWidget)

def update_side_edit_info(self, removed_row):
    side_edit_row = self.editWidget.get_item()

    if(side_edit_row is not None):

        # Equal the same row as the edit thing
        if(removed_row == side_edit_row):
            self.editWidget.clear_data()
            self.editWidget.hide()
            self.editWidget.set_item(None);

        if(removed_row <= side_edit_row):
            updated_row = side_edit_row -1
            self.editWidget.set_item(updated_row)

            if(self.editWidget.isVisible()):
                self.table.selectRow(updated_row)
        else:
            if(self.editWidget.isVisible()):
                self.table.selectRow(self.editWidget.get_item())
            else:
                self.table.clearSelection()