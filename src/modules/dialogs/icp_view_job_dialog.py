import os
import json

from base_logger import logger

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem)
from PyQt5.uic import loadUi

from modules.dialogs.basic_dialogs import yes_or_no_dialog

class ViewIcpJobDialog(QDialog):

    def __init__(self, icp_test_data_manager, elements_manager, current_item):
        super().__init__()

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'icp_view_job_dialog.ui')
        loadUi(file_path, self)

        self.icp_test_data_manager = icp_test_data_manager
        self.elements_manager = elements_manager

        self.current_item = current_item
        self.jobNum = None

        self.sample_names = []
        # self.batch_names[machine_id] = [batch_name, creation_date]
        self.batch_names = {}


        self.machine_1_data = {}
        self.machine_2_data = {}

        # set the default button
        self.save_btn.setDefault(True)

        self.delete_btn.clicked.connect(self.handle_delete_btn)
        self.save_btn.clicked.connect(self.handle_save_btn)
        self.cancel_btn.clicked.connect(self.close)

        self.init_setup()


    def init_setup(self):


        if(self.current_item):

            logger.debug(f'self.current_item: {self.current_item}')

            self.jobNum = str(self.current_item.jobNum)

            self.title.setText(f'W{self.jobNum}')

            job_data = self.icp_test_data_manager.get_machine_data(self.jobNum)

            print(f'job_data: {job_data}')

            for item in job_data:
                sample_name = item[0]
                job_number = item[1]
                machine_id = item[2]

                # convert the data into readable dict
                parsed_data = json.loads(item[3])

                batch_name = item[4]
                creation_date = item[5]

                if(batch_name not in self.batch_names):
                    self.batch_names[machine_id] = [batch_name, creation_date]

                # get all of the sample names
                if(sample_name not in self.sample_names):
                    self.sample_names.append(sample_name)

                # append sample data
                if(machine_id == 1):
                    self.machine_1_data[sample_name] = parsed_data

                    if(self.machine_1_line.text() == ''):
                        self.machine_1_line.setText(batch_name)

                elif(machine_id == 2):
                    self.machine_2_data[sample_name] = parsed_data

                    if(self.machine_2_line.text() == ''):
                        self.machine_2_line.setText(batch_name)


            logger.warning('batch info')

            # set up the machine information
            for machine_id, batch_info in self.batch_names.items():

                logger.info(f'machine_id: {machine_id}, batch_info: {batch_info}')

                batch_name = batch_info[0]
                creation_date = batch_info[1]

                if(machine_id == 1):
                    self.machine_1_line.setText(batch_name)
                    self.machine_1_date.setText(creation_date)

                elif(machine_id == 2):
                    self.machine_2_line.setText(batch_name)
                    self.machine_2_date.setText(creation_date)


            #self.setup_tables()
            self.load_table(self.machine_1_table, self.machine_1_data)
            self.load_table(self.machine_2_table, self.machine_2_data)



    def setup_tables(self):
        logger.info('Entering setup_tables')

        element_info = ['Element Name', 'Element Symbol']

        if(self.sample_names):

            vertical_header = element_info + self.sample_names

            print(f'vertical_header: {vertical_header}')

            print(f'machine_1_data: {self.machine_1_data}')
            print(f'machine_2_data: {self.machine_2_data}')

            total_rows = self.elements_manager.get_total_elements()
            total_cols = len(vertical_header)

            self.all_table.setRowCount(total_rows)
            self.all_table.setColumnCount(total_cols)

            # set the vertical headers
            self.all_table.setHorizontalHeaderLabels(vertical_header)

            elements = self.elements_manager.get_elements().values()

            for row, element in enumerate(elements):
                element_name = QTableWidgetItem(element.name)
                element_symbol = QTableWidgetItem(element.symbol)

                self.all_table.setItem(row, 0, element_name)
                self.all_table.setItem(row, 1, element_symbol)

        # other machine setup test


    def load_data(self):


        for col in range(1, self.all_table.columnCount()):
            header_item = self.horizontalHeaderItem(col)

            if header_item is not None:
                header_text = header_item.text()

                logger.info(f'header_text: {header_text}')

                # check machine 1
                if(header_text in self.machine_1_data):

                    for symbol, value in self.machine_1_data[header_text]:
                        pass


                # check machine 2
                if(header_text in self.machine_2_data):
                    pass





    def load_table(self, table, machine_dict):
        logger.info(f'LOADING TABLE')

        element_info = ['Element Name', 'Element Symbol']

        headers = element_info + list(machine_dict.keys())

        symbols = self.elements_manager.get_element_symbols()
        elements = self.elements_manager.get_element_names()

        logger.info(f'symbols: {symbols}')

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        for col in range(1, table.columnCount()):
            header_item = table.horizontalHeaderItem(col)

            if(header_item):
                header_text = header_item.text()

                if(header_text in machine_dict):
                    sample_data = machine_dict[header_text]

                    logger.debug(f'sample_data: {sample_data}')
                    if(table.rowCount() == 0):
                        table.setRowCount(len(sample_data))
                        for row, (symbol, value) in enumerate(sample_data.items()):

                            try:
                                index = symbols.index(symbol.lower())
                                element_name = elements[index]

                                element_item = QTableWidgetItem(element_name)
                                table.setItem(row, 0, element_item)

                            except Exception as e:
                                print(e)

                            symbol_item = QTableWidgetItem(symbol)

                            table.setItem(row, 1, symbol_item)

                    for row in range(table.rowCount()):
                        symbol = table.item(row, 1).text()

                        if(symbol in sample_data):

                            data = QTableWidgetItem(str(sample_data[symbol]))
                            table.setItem(row, col, data)

    def package_data(self, table):
        pass

    def handle_delete_btn(self):
        print('Delete')




    def handle_save_btn(self):
        print('Save')


