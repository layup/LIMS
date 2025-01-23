from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from modules.utils.logic_utils import is_float

class ChmReportController(QObject):

    def __init__(self, model, view, sample_names):
        super().__init__()

        self.model = model
        self.view = view

        self.sample_names = sample_names
        self.loaded = False
        self.test_headers_size = 6

        self.view.tableItemChangeEmit.connect(self.handle_table_change)
        self.view.reportsTabChangeEmit.connect(self.handle_report_tab_change)
        self.view.hideRowSignal.connect(self.handle_hide_row)

        self.load_init_data()

    def load_init_data(self):
        logger.info('Entering load_init_data')

        # define all the samples i
        self.model.init_samples()

        # retrieve the user tests lists from the txt file and user input from database
        test_list, samples_data = self.model.get_lists()

        # load the defined user data and the default
        tests_info = self.model.load_tests(test_list)
        samples_info = self.model.load_samples(samples_data)

        logger.debug(f'total_tests: {len(test_list)}')
        logger.debug(f'test_list: {test_list}')
        logger.debug(f'samples_data: {samples_data}')
        logger.debug(f'tests_info: {tests_info}')
        logger.debug(f'samples_info: {samples_info}')

        # setup the table
        self.view.set_row_count(len(test_list))
        self.view.update_table_tests(tests_info)
        self.view.update_table_comments(tests_info)
        self.view.update_table_samples(samples_info)
        self.view.update_action_row()
        self.view.apply_dilution_factor(self.model.dilution)

        # load in the initial data allowing the signal to fire
        self.loaded = True

    def handle_hide_row(self, row):
        logger.info(f'Entering handle_hide_row with row: {row}')
        self.view.table.setRowHidden(row, True)

        self.model.hidden_rows[row] = 1

        logger.info(f'hidden_rows: {self.model.hidden_rows}')

    def handle_table_change(self, item):

        if(self.loaded):
            if(item):
                try:
                    row = item.row()
                    col = item.column()
                    new_data = item.text()

                    logger.debug(f'row: {row}, col: {col}, new_data: {new_data}')

                    if(col == 2):
                        self.model.tests[row].displayName = new_data
                        logger.debug(f'Updated displayName value: {new_data}')

                    if(col == 3):
                        self.model.tests[row].unitType = new_data
                        logger.debug(f'Updated unitType value: {new_data}')

                    if(col == 4):
                        self.model.tests[row].recovery = new_data
                        logger.debug(f'Updated recovery value: {new_data}')

                    if(col == 6):
                        self.model.tests[row].so = new_data
                        logger.debug(f'Updated so value: {new_data}')

                    if(col > 6 and col != self.view.table.columnCount() - 1):
                        sample_name = self.view.table.horizontalHeaderItem(col).text()
                        self.model.samples[sample_name].add_data(row, new_data)
                        logger.debug(f'Updated sample_name value: {new_data}')

                except Exception as e:
                    logger.error(f'Error with updating col: {col}, {e}')

    def handle_report_tab_change(self, index):

        if(index == 3):
            logger.info('Entering Comments Table')


            for row, test_info in self.model.tests.items():

                upper_limit = test_info.upper_limit

                if(upper_limit):
                    pass

    def export_data(self):
        logger.info('Entering export_data')

        row_count = self.view.table.rowCount()

        sample_data = self.model.export_samples_data(row_count)
        display_names, recovery_vals, units, so_vals = self.model.export_tests_data()


        hidden_rows = self.model.hidden_rows

        for sample_name, sample_values in sample_data.items():
            logger.info(f'sample_name: {sample_name}, sample_values: {sample_values}')

        for i, display_name in enumerate(display_names):
            logger.debug(f'display_name: {display_name}, percent_recovery: {recovery_vals[i]}, unit: {units[i]}, so: {so_vals[i]}')

        return sample_data, display_names, recovery_vals, units, so_vals, hidden_rows

    def export_comments(self):
        return self.model.export_comments_data()

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

        display_names = []
        recovery = []
        unitType = []
        so = []

        for row in range(total_tests):

            # get the test name values
            test_item = self.view.table.item(row, 1)
            if test_item is None or not test_item.text().strip():
                display_names.append(text_names[row])
            else:
                testsName = test_item.text()
                display_names.append(testsName)

            # get the unit type values
            unit_item = self.view.table.item(row, 4)
            if unit_item is None or not unit_item.text().strip():
                unit_item.append('')
            else:
                currentVal = unit_item.text()
                unitType.append(currentVal)

            # get the recovery value from the table
            recovery_item = self.view.table.item(row, 5)
            if recovery_item is None or not recovery_item.text().strip():
                recovery.append('')
            else:
                recoveryVal = recovery_item.text()
                recovery.append(float(recoveryVal) if is_float(recoveryVal) else recoveryVal)

            # get the so value from table
            so_item = self.view.table.item(row, 6)
            if(so_item is None or not so_item.text().strip()):
                so.append('')
            else:
                so_val = so_item.text()
                so.append(float(so_val))

        return display_names, recovery, unitType