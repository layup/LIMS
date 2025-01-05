
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem, QSpacerItem, QSizePolicy

from pages.reports_page.chm.chm_report_items import chmReportSampleItem, chmReportTestItem

class ChmReportView(QObject):

    tableItemChangeEmit = pyqtSignal(QTableWidgetItem)
    createExcelEmit = pyqtSignal()

    def __init__(self,  table, create_btn):
        super().__init__()

        self.table = table
        self.create_btn = create_btn

        self.row_test_nums = []

        self.table.itemChanged.connect(self.item_changed_handler)
        #self.create_btn.clicked.connect(self.createExcelEmit.emit)

    def item_changed_handler(self, item):
        self.tableItemChangeEmit.emit(item)

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

    def set_row_count(self, row_count):
        self.table.setRowCount(row_count)

        # Set all the sample items to be center
        for col in range(2, self.table.columnCount()):
            for row in range(row_count):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def add_table_item(self, row, col, value):
        item = QTableWidgetItem(str(value) if value is not None else '')

        uneditable_cols = [0,1,4]

        item.setFlags(item.flags() | Qt.ItemIsEditable if col not in uneditable_cols else item.flags() & ~Qt.ItemIsEditable)

        if(col > 3):
            item.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row, col, item)

    def update_table_tests(self, test_info):
        logger.info('Entering update_table_tests')
        for row, (key, current_test) in enumerate(test_info.items()):
            if(isinstance(current_test, chmReportTestItem)):
                logger.debug(f'row: {row} item: {current_test.__repr__()}')
                self.add_table_item(row, 0, current_test.testName)
                self.add_table_item(row, 1, current_test.textName)
                self.add_table_item(row, 2, current_test.displayName)

                if(row not in self.row_test_nums):
                    self.row_test_nums.append(current_test.testNum)

            else:
                logger.debug(f'row: {row}, item: {key}')
                self.add_table_item(row, 0, '')
                self.add_table_item(row, 1, current_test)


    def update_table_samples(self, samples_info):
        logger.info('Entering update_table_samples')

        samples_start = 6;

        for col_index in range(samples_start, self.table.columnCount()):

            if(self.table.horizontalHeaderItem(col_index)):

                col_name = self.table.horizontalHeaderItem(col_index).text()
                logger.debug(f'col_idex: {col_index}: col_name: {col_name}')

                if(col_name in samples_info):
                    sample_data = samples_info[col_name].get_data()

                    for sample_test_num, sample_test_val in sample_data.items():
                        logger.debug(f'col_index: {col_index}, sample_test_num: {sample_test_num}, sample_test_val: {sample_test_val}')

                        # determine if the current samples test num and knows where the row is
                        if(sample_test_num in self.row_test_nums):
                            row_index_of_tests = self.row_test_nums.index(sample_test_num)

                            self.add_table_item(row_index_of_tests, col_index, sample_test_val)
                        else:
                            logger.warning(f'sample_test_num {sample_test_num} not in row_test_nums')

    def update_table_samples2(self, samples_info):
        logger.info('Entering update_table_samples')

        samples_start = 6;

        for col_index in range(samples_start, self.table.columnCount()):

            if(self.table.horizontalHeaderItem(col_index)):
                col_name = self.table.horizontalHeaderItem(col_index).text()
                logger.debug(f'col_idex: {col_index}: col_name: {col_name}')

                if(col_name in samples_info):
                    sample_data = samples_info[col_name].get_data()

                    for sample_test_num, sample_test_val in sample_data.items():
                        logger.debug(f'col_index: {col_index}, sample_test_num: {sample_test_num}, sample_test_val: {sample_test_val}')

                        for row, value in sample_data.items():
                            self.add_table_item(row, col_index, value)



    def apply_dilution_factor(self, factor):

        for row in range(self.table.rowCount()):
            self.add_table_item(row, 4, factor)

    def update_dilution_factors(self, factor):
        pass;

    def update_standard(self, standards):
        pass;

