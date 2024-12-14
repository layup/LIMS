from base_logger import logger

from modules.dbFunctions import getTestsName, getTestsInfo
from modules.utils.logic_utils import removeIllegalCharacters, is_float

from pages.reports_page.chm.chm_report_items import chemReportSampleItem, chemReportTestItem

class ChemReportModel:
    def __init__(self, db, jobNum, dilution, sampleTests):
        self.db = db
        self.jobNum = jobNum
        self.sampleTests = sampleTests
        self.dilution = dilution

        self.testsNums = []

        self.test_row_info = {}

        self.samples = {}
        self.tests = {}

    def init_samples(self):
        # define all of the sample items
        for sample_name, sample_tests in self.sampleTests.items():
            job_num, sample_num = sample_name.split('-')
            self.samples[sample_name] = chemReportSampleItem(job_num, sample_num, sample_name)

    def get_lists(self):
        return get_tests_results(self.db, self.jobNum, self.sampleTests);

    def get_samples_data(self):
        return self.samples;

    def export_samples_data(self, row_count):

        export_list = {}

        for sample_name, sample_info in self.samples.items():
            sample_data = sample_info.get_data()

            export_sample_data = []
            for row in range(row_count):
                if(row in sample_data):
                    export_sample_data.append(sample_data[row])
                else:
                    export_sample_data.append('ND')

            export_list[sample_name] = export_sample_data

        return export_list

    def export_tests_data(self):

        display_names = []
        recovery_values = []
        unit_values = []

        for row, tests_info in self.tests.items():
            if(tests_info.displayName):
                display_names.append(tests_info.displayName)
            else:
                display_names.append(tests_info.textName)

            if(tests_info.recovery):
                recovery_values.append(tests_info.recovery)
            else:
                recovery_values.append('')

            if(tests_info.unitType):
                unit_values.append(tests_info.unitType)
            else:
                unit_values.append('')

        return display_names, recovery_values, unit_values;

    def get_tests_data(self):
        return self.tests;

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

        sampleNum = item[0]
        testNum = item[1]
        testValue = item[2]
        recovery = item[3]
        unit = item[4]
        jobNum = item[5]
        sampleName = f'{jobNum}-{sampleNum}'

        if(sampleName in self.samples):
            logger.debug(f'Adding Current Sample: {sampleName}')

            row = self.test_row_info.get(testNum)

            if(row):
                self.samples[sampleName].add_data(row, testValue, recovery, unit)

    def update_sample(self, sampleName, testNum, testVal):
        self.samples[sampleName].update_data(testNum, testVal)

    def load_tests(self, tests_list):
        logger.info(f'Entering load_samples with tests_list: {tests_list}')

        counter = 0;
        for text_name in tests_list:
            self.add_tests(text_name, counter)
            counter +=1;

        return self.tests

    def add_tests(self, text_name, row):
        logger.debug(f'Entering add_tests with text_name: {text_name}, row: {row}')

        test_data = getTestsInfo(self.db, text_name)

        if(test_data):
            testNum = test_data[0]
            testName = test_data[1]
            textName = test_data[2]
            displayName = test_data[3]
            recovery = test_data[4]
            unit = test_data[5]

            if(testNum not in self.testsNums):
                self.testsNums.append(testNum)
                self.test_row_info[testNum] = row

            self.tests[row] = chemReportTestItem(testNum, testName, textName, displayName, unit)
        else:
            logger.info(f'No test_data found for {text_name}')
            self.tests[row] =  chemReportTestItem(textName=text_name)



# find what the user has enter for the tests already
def get_tests_results(db, jobNum, sample_tests):

    testsQuery = 'SELECT * FROM chemTestsData WHERE JobNum = ?'
    test_results = db.query(testsQuery, (jobNum,))

    # retrieve data from .txt file and user entered
    chem_tests_list = []

    # examine the .txt items
    for _, tests_list in sample_tests.items():
        for current_test in tests_list:
            current_test = removeIllegalCharacters(str(current_test))
            if(current_test not in chem_tests_list and 'ICP' not in current_test):
                chem_tests_list.append(current_test)

    # examine the test_names
    if(test_results):
        for item in test_results:
            test_num = item[1]
            tests_name = get_test_text_name(db, test_num)

            if(tests_name not in chem_tests_list):
                chem_tests_list.append(tests_name)

    return chem_tests_list, test_results

def get_test_text_name(db, testNum):
    try:
        query = 'SELECT benchChemName FROM Tests WHERE testNum = ?'
        result = db.query(query, (testNum, ))
        return result[0][0]

    except Exception as e:
        print(e)
        return None

def get_footer_comment(db, paramName):
    pass;
