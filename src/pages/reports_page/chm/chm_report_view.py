
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem, QSpacerItem, QSizePolicy, QPushButton, QHBoxLayout, QWidget

from pages.reports_page.chm.chm_report_items import chmReportSampleItem, chmReportTestItem

class ChmReportView(QObject):

    tableItemChangeEmit = pyqtSignal(QTableWidgetItem)
    reportsTabChangeEmit =pyqtSignal(int)
    createExcelEmit = pyqtSignal()

    hideRowSignal = pyqtSignal(int)

    def __init__(self,  table, comment_table, reports_tab, create_btn):
        super().__init__()

        self.table = table
        self.comment_table = comment_table
        self.reports_tab = reports_tab

        self.create_btn = create_btn

        self.row_test_nums = []

        self.table.itemChanged.connect(self.item_changed_handler)
        self.reports_tab.currentChanged.connect(self.tab_changed_handler)
        #self.create_btn.clicked.connect(self.createExcelEmit.emit)

    def tab_changed_handler(self, row):
        self.reportsTabChangeEmit.emit(row)


    def item_changed_handler(self, item):
        self.tableItemChangeEmit.emit(item)

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)



    def set_row_count(self, row_count):

        # set the row count for both tables
        self.table.setRowCount(row_count)
        self.comment_table.setRowCount(row_count)

        # Set all the sample items to be center
        for col in range(2, self.table.columnCount()):
            for row in range(row_count):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def add_table_item(self, row, col, value):

        uneditable_cols = [0,1,5]

        item = QTableWidgetItem(str(value) if value is not None else '')
        item.setFlags(item.flags() | Qt.ItemIsEditable if col not in uneditable_cols else item.flags() & ~Qt.ItemIsEditable)

        if(col > 3):
            item.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row, col, item)


    def add_comment_item(self, row, col, value):

        item = QTableWidgetItem(str(value) if value is not None else '')
        item.setFlags(item.flags() | ~Qt.ItemIsEditable)

        if(col in [1,3]):
            item.setTextAlignment(Qt.AlignCenter)

        self.comment_table.setItem(row, col, item)

    def update_table_tests(self, test_info):
        logger.info('Entering update_table_tests')
        for row, (key, current_test) in enumerate(test_info.items()):
            if(isinstance(current_test, chmReportTestItem)):
                logger.debug(f'row: {row} item: {current_test.__repr__}')
                self.add_table_item(row, 0, current_test.testName)
                self.add_table_item(row, 1, current_test.textName)
                self.add_table_item(row, 2, current_test.displayName)
                self.add_table_item(row, 3, current_test.unitType)
                self.add_table_item(row, 4, current_test.recovery)
                self.add_table_item(row, 6, current_test.so)

                if(row not in self.row_test_nums):
                    self.row_test_nums.append(current_test.testNum)

            else:
                logger.debug(f'row: {row}, item: {key}')
                self.add_table_item(row, 0, '')
                self.add_table_item(row, 1, current_test)

    def update_table_comments(self, test_info):
        logger.info('Entering update_comments_table')

        for row, (test_id, test_item) in enumerate(test_info.items()):
            if(isinstance(test_item, chmReportTestItem)):
                self.add_comment_item(row, 0, test_item.textName)
                self.add_comment_item(row, 1, test_item.upper_limit)
                self.add_comment_item(row, 2, test_item.side_comment)
                self.add_comment_item(row, 3, 'N/A')
                self.add_comment_item(row, 4, test_item.footer_comment)

    def update_table_samples(self, samples_info):
        logger.info('Entering update_table_samples')

        samples_start = 7

        for col_index in range(samples_start, self.table.columnCount()):

            if(col_index != self.table.columnCount()-1):

                if(self.table.horizontalHeaderItem(col_index)):
                    col_name = self.table.horizontalHeaderItem(col_index).text()
                    logger.debug(f'col_idex: {col_index}: col_name: {col_name}')

                    if(col_name in samples_info):
                        sample_data = samples_info[col_name].get_data()

                        for sample_test_num, sample_test_val in sample_data.items():
                            logger.debug(f'col_index: {col_index}, sample_test_num: {sample_test_num}, sample_test_val: {sample_test_val}')

                            for row, value in sample_data.items():
                                self.add_table_item(row, col_index, value)

    def update_action_row(self):

        action_col = self.table.columnCount() - 1

        for row in range(self.table.rowCount()):
            remove_btn = QPushButton('Remove')
            remove_btn.clicked.connect(lambda i, row=row: self.hideRowSignal.emit(row))

            # Create a layout for the button
            button_layout = QHBoxLayout()
            button_layout.addWidget(remove_btn)

            # Create a widget to hold the button
            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            self.table.setCellWidget(row, action_col, remove_btn)




    def apply_dilution_factor(self, factor):

        for row in range(self.table.rowCount()):
            self.add_table_item(row, 5, factor)

    def update_dilution_factors(self, factor):
        pass

    def update_standard(self, standards):
        pass