from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from modules.dialogs.basic_dialogs import yes_or_no_dialog

class IcpReportController(QObject):

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        self.loaded = False;

        self.load_init_data()

        self.view.tableItemChangeEmit.connect(self.handle_table_change)
        self.view.reloadBtnClicked.connect(self.handle_reload_btn)
        self.view.hardnessBtnClicked.connect(self.handle_hardness_btn)
        self.view.reportsTabChangeEmit.connect(self.handle_reports_tab)

    def handle_hardness_btn(self):
        self.model.calculate_sample_hardness()

        self.view.update_table_hardness(self.model.samples)

    def handle_reload_btn(self):

        response = yes_or_no_dialog('Are you sure you want to reload tests data', 'will overwrite existing data in tests data table section')

        if(response):
            reloaded_info = self.model.load_samples_data()

            self.view.update_table_samples(reloaded_info)

    def load_init_data(self):
        logger.info('Entering ICP load_init_data')

        # init the tests and samples
        self.model.init_elements()
        self.model.init_samples()

        # retrieve the samples and elements
        elements_info = self.model.elements_info
        samples_info = self.model.load_samples_data()

        # set the row count
        self.view.set_row_count(len(elements_info))

        # update the table
        self.view.update_table_elements(elements_info, self.model.dilution)
        self.view.update_table_samples(samples_info)

        self.view.update_table_comments(elements_info)

        # update dilution values

        # calculate hardness
        self.model.calculate_sample_hardness()

        self.view.update_table_hardness(samples_info)

        self.loaded = True;

    def handle_reports_tab(self, index):
        logger.info(f'Entering handle_reports_tab with index: {index}')

        if(index == 3):

            for row, element_symbol in enumerate(self.model.element_row_nums):

                element_num = self.model.symbol_num[element_symbol]
                upper_limit = self.model.elements_info[element_num].upper_limit

                logger.info(f'row: {row}, symbol: {repr(element_symbol)}, num: {element_num}, upper_limit: {upper_limit}')

                if(upper_limit):
                    status = self.get_max_element_value(row, upper_limit)
                    new_status = 'True' if status else 'False'

                    self.view.update_comments_status(row, new_status)


    def get_max_element_value(self, row, upper_limit):

        for sample_name, sample_info in self.model.samples.items():

            if(row in sample_info.data):
                current_val = sample_info.data[row]

                if(is_float(current_val)):

                    if(float(current_val) >= float(upper_limit)):

                        return True
        return False

    def handle_table_change(self, item):

        if(self.loaded):
            try:
                row = item.row()
                col = item.column()
                new_data = item.text()

                logger.debug(f'row: {row}, col: {col}, new_data: {new_data}')

                if(col > 5):
                    sample_name = self.view.table.horizontalHeaderItem(col).text()
                    sample_info = self.model.samples[sample_name]
                    sample_info.add_data(row, new_data)

                    logger.info(self.model.samples[sample_name].data)


            except Exception as e:
                print(e)

        for key, value in self.model.samples.items():
            logger.info(value.__repr__)

    def export_data(self):
        logger.info('Entering export_data')

        element_names, element_symbols, element_limits_info, element_units = self.model.export_elements_info()

        row_count = self.view.table.rowCount()
        sample_data = self.model.export_samples_data(row_count)
        extra_data = self.model.export_samples_extra()

        logger.info(f'extra_data: {extra_data}')

        for sample_name, data in sample_data.items():
            logger.info(f'{sample_name}, {data}')

        return element_names, element_symbols, element_limits_info, element_units, sample_data

    def get_sample_data_from_table(self):
        logger.info('Entering get_sample_data_from_table')

        total_rows = self.view.table.rowCount()
        sample_data = {}

        for col in range(self.view.samples_start, self.view.table.horizontalHeader().count()):
            job_name = self.view.table.horizontalHeaderItem(col).text()

            logger.debug(f"col: {col}, job_name: {job_name}")
            job_values = []

            for row in range(total_rows):
                current_row_item = self.view.table.item(row, col)

                if(current_row_item is None or (current_row_item.text().strip() == '')):
                    job_values.append('ND')
                else:
                    job_values.append(current_row_item.text().strip())

            sample_data[job_name] = job_values

        return sample_data


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False