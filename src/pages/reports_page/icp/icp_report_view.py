from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import  QHeaderView, QTableWidgetItem, QSpacerItem, QSizePolicy

from pages.reports_page.icp.icp_report_items import IcpReportSampleItem, IcpReportElementsItem

class IcpReportView(QObject):

    tableItemChangeEmit = pyqtSignal(QTableWidgetItem)

    def __init__(self,  table):
        super().__init__()

        self.table = table

        self.reset_btn = None
        self.calculate_dilution = None
        self.calculate_hardness = None

        self.samples_start = 6

        self.table.itemChanged.connect(self.item_changed_handler)

    def item_changed_handler(self, item):
        self.tableItemChangeEmit.emit(item)

    def total_rows(self):
        return self.table.rowCount()

    def total_cols(self):
        return self.table.columnCount()

    def get_column_index(self, header_text):
        for col in range(self.table.columnCount()):
            if header_text == self.table.horizontalHeaderItem(col).text():
                return col
        return -1

    def set_row_count(self, row_count):
        logger.info('Entering set_row_count')

       # additional_rows = ['Hardness', 'pH']
       # symbol_name = ['CaC0₃', '']
       # unit_type = ['ug/L', '']

        additional_rows = ['pH', 'Hardness']
        symbol_name = ['', 'CaC0₃']
        unit_type = ['',  'ug/L']

        self.table.setRowCount(row_count + len(additional_rows))

        # Set all the sample items to be center and adds an item to all the blank
        for col in range(2, self.table.columnCount()):
            for row in range(self.table.rowCount()):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        for index in range(len(additional_rows)):
            total_rows = self.table.rowCount()
            current_row = total_rows - index -1

            self.add_table_item(current_row, 0, additional_rows[index])
            self.add_table_item(current_row, 1, symbol_name[index])
            self.add_table_item(current_row, 2, unit_type[index])

    def add_table_item(self, row, col, value):
        logger.info('Entering add_table_item')

        item = QTableWidgetItem(str(value) if value is not None else '')

        uneditable_cols = [0,1]

        item.setFlags(item.flags() | Qt.ItemIsEditable if col not in uneditable_cols else item.flags() & ~Qt.ItemIsEditable)

        if(col != 0):
            item.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row, col, item)

    def update_table_elements(self, elements, dilution):
        logger.info('Entering update_table_elements')
        logger.info(f'dilution: {dilution}')

        logger.info(f'elements')

        element_row_nums = []

        for row, (element_num, element_item) in enumerate(elements.items()):
            if(isinstance(element_item, IcpReportElementsItem)):
                logger.debug(f'row: {row} item: {element_item.__repr__}')
                self.add_table_item(row, 0, element_item.element_name)
                self.add_table_item(row, 1, element_item.element_symbol)
                self.add_table_item(row, 2, element_item.unit)
                self.add_table_item(row, 3, element_item.lower_limit)
                self.add_table_item(row, 4, element_item.upper_limit)

                if(row not in element_row_nums):
                    element_row_nums.append(row)

            # Populate the dilution column
            if(is_string_int(dilution)):
                self.add_table_item(row, 5, dilution)
            else:
                self.add_table_item(row, 5, 1)

        return element_row_nums

    def update_table_samples(self, samples_info):
        logger.info('Entering update_table_samples')

        for col_index in range(self.samples_start, self.table.columnCount()):

            if(self.table.horizontalHeaderItem(col_index)):
                col_name = self.table.horizontalHeaderItem(col_index).text()

                logger.debug(f'col_index: {col_index}, col_name: {col_name}')

                if(col_name in samples_info):
                    sample_data = samples_info[col_name].get_data()

                    for row, row_val in sample_data.items():
                        self.add_table_item(row, col_index, row_val)

    def update_table_dilution(self, dilution):
        logger.info('Entering update_table_dilution')

        if(is_string_float(dilution)):
            dilution_factor = float(dilution)
        else:
            dilution_factor = 1

        for col_index in range(self.samples_start, self.table.columnCount()):
            for row_index in range(self.table.rowCount()):
                current_item = self.table.item(row_index, col_index)
                if(current_item):
                    current_value = current_item.text()
                    if(current_value != '' and is_string_float(current_value)):
                        current_value = float(current_value)
                        new_value = round(current_value * dilution_factor, 3)

    def update_table_hardness(self, samples_info):
        logger.info('Entering update_table_hardness')

        for col_index in range(self.samples_start, self.table.columnCount()):

            if(self.table.horizontalHeaderItem(col_index)):
                col_name = self.table.horizontalHeaderItem(col_index).text()

                logger.debug(f'col_index: {col_index}, col_name: {col_name}')

                if(col_name in samples_info):
                    sample_hardness = samples_info[col_name].get_hardness()

                    hardness_row = self.table.rowCount() - 2

                    if(sample_hardness != ''):
                        self.add_table_item(hardness_row, col_index, sample_hardness)
                    else:
                        self.add_table_item(hardness_row, col_index, 'HARD')

def is_string_int(value):
    """Check if the string can be converted to an integer."""
    try:
        int(value)
        return True
    except ValueError:
        return False

def is_string_float(value):
    """Check if the string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False