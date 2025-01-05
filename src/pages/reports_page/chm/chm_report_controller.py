from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from modules.utils.logic_utils import is_float

class ChmReportController(QObject):

    def __init__(self, model, view, sample_names):
        super().__init__()

        self.model = model
        self.view = view;

        self.sample_names = sample_names
        self.loaded = False;

        self.test_headers_size = 6;

        self.view.tableItemChangeEmit.connect(self.handle_table_change)
        #self.view.createExcelEmit.connect(self.handle_create_excel)

        self.load_init_data()

    def load_init_data(self):
        logger.info('Entering load_init_data')

        # define all the samples i
        self.model.init_samples()

        # retrieve the user tests lists from the txt file and user input from database
        test_list, samples_data = self.model.get_lists()
        rowCount = len(test_list)

        # load the defined user data and the default
        tests_info = self.model.load_tests(test_list)
        samples_info = self.model.load_samples(samples_data)

        # setup the table
        self.view.set_row_count(rowCount)
        self.view.update_table_tests(tests_info)
        self.view.update_table_samples2(samples_info)
        self.view.apply_dilution_factor(self.model.dilution)

        # load in the initial data allowing the signal to fire
        self.loaded = True;

    def handle_table_change(self, item):

        if(self.loaded):

            if(item):
                try:
                    logger.debug(f'row: {item.row()}, col: {item.column()}, text: {item.text()}')

                    row = item.row()
                    col = item.column()
                    new_data = item.text()

                    if(col == 2):
                        self.model.tests[col].displayName = new_data

                    if(col == 3):
                        self.model.tests[col].unitType = new_data

                    if(col == 4):
                        self.model.tests[col].standard = new_data

                    if(col > 5):
                        sample_name = self.view.table.horizontalHeaderItem(col).text()
                        self.model.samples[sample_name].add_data(row, new_data)

                except Exception as e:
                    print(e)


    #TODO: maybe can have all of it from here
    def handle_create_excel(self):
        logger.info('Entering handle_create_excel')

        row_count = self.view.table.rowCount()

        sample_data = self.model.export_samples_data(row_count)
        display_name, recovery_vals, units = self.model.export_tests_data()

        for key, value in self.model.test_row_info.items():
            print(key,value)
        for key, value in self.model.samples.items():
            print(key, value)
        for key, value in self.model.tests.items():
            print(key, value)

    def export_data(self):
        logger.info('Entering export_data')
        row_count = self.view.table.rowCount()

        for sample_name, samples_data in self.model.samples.items():
            print(sample_name, samples_data)

        sample_data = self.model.export_samples_data(row_count)
        display_name, recovery_vals, units = self.model.export_tests_data()

        for sample_name, sample_values in sample_data.items():
            logger.info(f'sample_name: {sample_name}, sample_values: {sample_values}')

        logger.info(f'display_name: {display_name}')
        logger.info(f'recovery_vals: {recovery_vals}')
        logger.info(f'units: {units}')

        return sample_data, display_name, recovery_vals, units

    def get_sample_data_from_table(self):
        logger.info('Entering get_sample_data_from_table')

        total_rows = self.view.table.rowCount()
        sample_data = {}

        for col in range(self.test_headers_size, self.view.table.horizontalHeader().count()):
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

    def get_tests_data_from_table(self):
        logger.info('Entering get_tests_data_from_table')

        total_tests = self.view.table.rowCount()
        text_names = self.model.get_tests_names()

        displayNames = []
        recovery = []
        unitType = []

        for row in range(total_tests):
            # get the test name values
            testNameItem = self.view.table.item(row, 1)
            if testNameItem is None or not testNameItem.text().strip():
                displayNames.append(text_names[row])
            else:
                testsName = testNameItem.text()
                displayNames.append(testsName)

            # get the unit type values
            unitTypeItem = self.view.table.item(row, 3)
            if unitTypeItem is None or not unitTypeItem.text().strip():
                unitType.append('')
            else:
                currentVal = unitTypeItem.text()
                unitType.append(currentVal)

            # get the recovery value from the table
            recoveryItem = self.view.table.item(row, 5)
            if recoveryItem is None or not recoveryItem.text().strip():
                recovery.append('')
            else:
                recoveryVal = recoveryItem.text()
                recovery.append(float(recoveryVal) if is_float(recoveryVal) else recoveryVal)


        return displayNames, recovery, unitType