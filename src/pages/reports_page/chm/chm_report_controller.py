import math

from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from modules.utils.logic_utils import is_float

class ChmReportController(QObject):

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view
        self.loaded = False

        self.connect_signals()
        self.init_setup()

    def connect_signals(self):
        self.view.tableItemChangeEmit.connect(self.handle_table_change)
        self.view.reportsTabChangeEmit.connect(self.handle_report_tab_change)
        self.view.hideRowSignal.connect(self.handle_hide_row)
        self.view.sampleRemovedEmit.connect(self.handle_remove_sample)
        self.view.sampleNameChangeEmit.connect(self.handle_update_sample_name)

    def init_setup(self):
        logger.info('Entering ChmReportController init_setup')

        # set up the samples layout
        sample_names = self.model.init_sample_names()
        self.view.update_samples_layout(sample_names)

        #  setup table column
        data_table_columns = self.model.get_column_headers(list(sample_names.keys()))
        self.view.update_table_columns(data_table_columns)

        # define all the samples
        self.model.init_samples()

        # retrieve the user tests lists from the txt file and user input from database
        test_list, sample_data_entries_list = self.model.get_sample_data_entires_lists()

        # load the defined user data and the default
        tests_info = self.model.load_tests(test_list)
        samples_info = self.model.load_samples(sample_data_entries_list)

        logger.debug(f'total_tests: {len(test_list)}')
        logger.debug(f'test_list: {test_list}')
        logger.debug(f'sample_data_entries: {sample_data_entries_list}')
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
        logger.info(f'Entering handle_hide_row  wite row: {row}')

        self.view.table.setRowHidden(row, True)

        self.model.hidden_rows[row] = 1

        self.view.update_comments_status(row, 'Hidden')

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

    def handle_remove_sample(self, sample_id):
        logger.info(f'Entering handle_remove_sample with sample_num: {sample_id}')

        # remove if from self.model
        del self.model.samples[sample_id]

        # remove if from the samples section
        status = self.view.remove_sample_widget(sample_id)

        if(status):
            # remove it from the table section
            remaining_sample_names = self.model.get_sample_names_list()
            new_table_cols = self.model.get_column_headers(remaining_sample_names)
            self.view.update_table_columns(new_table_cols)

            # update the table data information as well
            self.view.update_table_samples(self.model.samples)
            self.view.update_action_row()



    def handle_update_sample_name(self, sample_id, new_sample_name):
        logger.info(f'Entering handle_update_sample_name with sample_id: {sample_id}, new_sample_name: {new_sample_name}')

        #self.model.sample_names[sample_id] = new_sample_name

        self.mode.samples[sample_id].update_sample_name(new_sample_name)


    def handle_report_tab_change(self, index):

        if(index == 3):
            logger.info('Entering Comments Table')

            for row, test_info in self.model.tests.items():
                upper_limit = test_info.upper_limit
                lower_limit = test_info.lower_limit

                lower_limit_status = self.get_least_element_value(row, lower_limit) if lower_limit is not None else False
                upper_limit_status = self.get_max_element_value(row, upper_limit) if upper_limit is not None else False

                status = lower_limit_status or upper_limit_status

                logger.debug(f'row: {row}, lower_limit_status: {lower_limit_status}, upper_limit_status: {upper_limit_status}')
                logger.debug(f'row: {row}, status: {repr(status)}, lower_limit: {lower_limit}, upper_limit: {upper_limit}')

                self.view.update_comments_status(row, str(status))

    def get_max_element_value(self, row, upper_limit):
        for sample_info in self.model.samples.values():  # Iterate directly over values
            current_val = sample_info.data.get(row)  # Use .get() to safely handle missing keys

            if current_val is not None and is_float(current_val):  # Check for None and then float
                try:
                    if float(current_val) >= float(upper_limit):
                        return True
                except ValueError:
                    logger.error(f"Could not convert  {type(current_val)} {current_val} to float for comparison with upper limit")

        return False  # Return False if no matching value or no value greater than or equal to the upper_limit was found.

    def get_least_element_value(self, row, lower_limit):
        for sample_info in self.model.samples.values(): # Iterate directly over values
            current_val = sample_info.data.get(row)  # Use .get() to safely handle missing keys

            if current_val is not None and is_float(current_val):  # Check for None and then float
                try:
                    if float(current_val) <= float(lower_limit):
                        logger.info(f'row: {row}, current_val: {current_val}')
                        return True
                except ValueError:
                    logger.error(f"Could not convert {type(current_val)} {current_val} to float for comparison with lower limit")

        return False  # Return False if no matching value or no value less than or equal to the lower_limit was found.

    def save_data(self):

        row_count = self.view.table.rowCount()

        return self.model.export_save_data(row_count)

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
        logger.info('Entering export_comments')

        return self.model.export_comments_data()

    def export_sample_names(self):
        logger.info('Entering export_sample_names')

        return self.model.export_sample_names()
