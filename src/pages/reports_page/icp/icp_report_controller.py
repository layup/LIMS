from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

class IcpReportController(QObject):

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        self.loaded = False;

        self.load_init_data()

        self.view.tableItemChangeEmit.connect(self.handle_table_change)

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

        # update dilution values


        # calculate hardness
        self.model.calculate_sample_hardness()
        self.view.update_table_hardness(samples_info)

        self.loaded = True;

    def handle_table_change(self, item):

        if(self.loaded):
            try:
                logger.debug(f'row: {item.row()}, col: {item.column()}, text: {item.text()}')
                row = item.row()
                col = item.column()
                new_data = item.text()

                if(col > 5):
                    sample_name = self.view.table.horizontalHeaderItem(col).text()
                    self.model.samples[sample_name].add_data(row, new_data)

            except Exception as e:
                print(e)

        for key, value in self.model.samples.items():
            print(value.__repr__)

    def export_data(self):
        logger.info('Entering export_data')

        element_names, element_limits_info, element_units = self.model.export_elements_info()

        sample_data = self.get_sample_data_from_table()


        return element_names, element_limits_info, element_units, sample_data


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