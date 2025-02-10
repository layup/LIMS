from base_logger import logger

from modules.utils.logic_utils import removeIllegalCharacters, is_float, remove_control_characters

from pages.reports_page.chm.chm_report_items import chmReportSampleItem, chmReportTestItem

class ChmReportModel:
    def __init__(self, tests_manager, chm_test_data_manager, jobNum, dilution, sample_tests):
        self.tests_manager = tests_manager
        self.chm_test_data_manager = chm_test_data_manager
        self.jobNum = jobNum
        self.sample_tests = sample_tests
        self.dilution = dilution


        self.tests_ids = []

        self.test_row_info = {}

        self.samples = {}
        self.tests = {}

        self.hidden_rows = {}

    def init_samples(self):
        ''' load in the sample tests '''

        logger.info('Entering init_samples')

        # define all of the sample items
        for sample_name, sample_tests in self.sample_tests.items():
            job_num, sample_num = sample_name.split('-')
            self.samples[sample_name] = chmReportSampleItem(job_num, sample_num, sample_name)

    def get_lists(self):
        ''' return a list of all entered users tests data'''
        #return get_tests_results(self.db, self.jobNum, self.sample_tests);
        return self.chm_test_data_manager.get_tests_results(self.jobNum, self.sample_tests)

    def get_samples_data(self):
        return self.samples;

    def get_tests_data(self):
        return self.tests

    def get_tests_names(self):
        return list(self.tests.keys())

    def load_samples(self, samples_list):
        ''' Check if there is existing data in the database associated with sample numbers'''
        logger.info('Entering load_samples with samples_list: {samples_list}')

        for current_sample in samples_list:
            self.add_samples(current_sample)

        return self.samples

    def add_samples(self, item):
        logger.info('Entering add_samples')

        sample_num = item[0]
        test_id = item[1]
        test_value = item[2]
        recovery = item[3]
        unit = item[4]
        job_num = item[5]
        sample_name = f'{job_num}-{sample_num}'

        if(sample_name in self.samples):
            logger.debug(f'Adding Current Sample: {sample_name}')

            row = self.test_row_info.get(test_id)

            if(row or row == 0):
                logger.debug('big if buddy')
                self.samples[sample_name].add_data(row, test_value, recovery, unit)

        if(test_id in self.tests_ids):
            row = self.test_row_info[test_id]
            self.tests[row].unitType = unit
            self.tests[row].recovery = recovery


    def update_sample(self, sample_name, test_id, test_value):
        self.samples[sample_name].update_data(test_id, test_value)

    def load_tests(self, tests_list):
        logger.info(f'Entering load_samples with tests_list: {tests_list}')

        for i, text_name in enumerate(tests_list):
            self.add_tests(text_name, i)
            self.hidden_rows[i] = 0

        return self.tests

    def add_tests(self, text_name, row):
        logger.debug(f'Entering add_tests with text_name: {text_name}, row: {row}')

        test_info = self.tests_manager.get_tests_by_text(text_name)

        logger.info(f'test_info: {test_info}')

        if(test_info):
            test_id = test_info.test_id
            test_name = test_info.test_name
            chem_name = test_info.chem_name
            display_name = test_info.display_name

            unit_type = None
            recovery = None
            so = test_info.so

            side_comment = test_info.comment
            footer_comment = test_info.footer
            upper_limit = test_info.upper_limit
            lower_limit = test_info.lower_limit


            if(test_id not in self.tests_ids):
                self.tests_ids.append(test_id)
                self.test_row_info[test_id] = row

            self.tests[row] = chmReportTestItem(test_id, test_name, chem_name, display_name, unit_type, recovery, so,  lower_limit, upper_limit, side_comment, footer_comment)

        else:
            logger.info(f'No test_data found for {text_name}')
            self.tests[row] = chmReportTestItem(textName=text_name)


    def export_samples_data(self, row_count):

        export_list = {}

        for sample_name, sample_info in self.samples.items():
            sample_data = sample_info.get_data()

            export_sample_data = []
            for row in range(row_count):
                if(row in sample_data):
                    export_sample_data.append(sample_data[row])
                else:
                    # when row item is blank
                    export_sample_data.append('---')

            export_list[sample_name] = export_sample_data

        return export_list

    def export_tests_data(self):
        logger.info('Entering export_tests_data')

        display_names = []
        recovery_values = []
        unit_values = []
        so_values =[]

        for row, tests_info in self.tests.items():
            display_names.append(tests_info.displayName or tests_info.textName)
            recovery_values.append(tests_info.recovery or '')
            unit_values.append(tests_info.unitType or '')
            so_values.append(tests_info.so or '')

        return display_names, recovery_values, unit_values, so_values

    def export_comments_data(self):
        logger.info('Entering export_comments_data')

        upper_limits = []
        lower_limits = []
        side_comments = []
        extra_comments = []

        for row, tests_info in self.tests.items():
            upper_limits.append(tests_info.upper_limit)
            lower_limits.append(tests_info.lower_limit)
            side_comments.append(tests_info.side_comment)
            extra_comments.append(tests_info.footer_comment)

        return lower_limits, upper_limits, side_comments, extra_comments


