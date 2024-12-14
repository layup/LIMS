import json

from base_logger import logger
from PyQt5.QtCore import Qt, QObject, pyqtSignal

from modules.dbFunctions import getIcpElementsList, getIcpLimitResults
from modules.utils.logic_utils import is_float

from pages.reports_page.icp.icp_report_items import IcpReportSampleItem, IcpReportElementsItem

'''
    weeekend goal
    - complete icp
    - streamline the report process
    - double check the excel creation files

'''

class IcpReportModel(QObject):

    def __init__(self,  db, jobNum, paramNum, dilution, sample_names):
        super().__init__()
        self.db = db
        self.jobNum = jobNum
        self.paramNum = paramNum
        self.dilution = dilution
        self.sample_names = sample_names

        # element_symbol = element_num
        self.symbol_num = {}
        self.element_row_nums = []

        self.elements_info = {}
        self.samples = {}

    def get_element_nums(self):
        return self.elements_info.keys()

    def init_elements(self):
        logger.info('Entering get_elements_info')

        #TODO: work on the joining two tables
        # get the basic elements info such as their name, num, symbols
        elements = getIcpElementsList(self.db)
        elements_limits = getIcpLimitResults(self.db, self.paramNum)

        # create the basic element items (name, num, symbol)
        for element in elements:
            element_num = element[0]
            element_name = element[1]
            element_symbol = element[2]

            self.elements_info[element_num] = IcpReportElementsItem(element_name, element_num, element_symbol)
            self.symbol_num[element_symbol] = element_num

            # define the placement of the item
            self.element_row_nums.append(element_symbol)

        # load in data about the elements for specific parameter number
        if(elements_limits):
            for element_num, limits in elements_limits.items():
                unit_type = limits[0]
                upper_limit = limits[1]
                lower_limit = limits[2]
                side_comment = limits[3]

                if(element_num in self.elements_info):
                    self.elements_info[element_num].add_limits(unit_type, lower_limit, upper_limit, side_comment)

    def export_elements_info(self):
        logger.info('Entering export_elements_info')

        element_names = []
        element_limits_info = []
        element_units = []

        #element_limits = {}

        for element_num, element_item in self.elements_info.items():
            element_name = element_item.element_name
            lower_limit = element_item.lower_limit
            upper_limit = element_item.upper_limit
            side_comment = element_item.comment
            unit = element_item.unit

            element_names.append(element_name)
            element_limits_info.append([element_name, lower_limit, upper_limit, side_comment, unit])
            element_units.append(unit)
            #element_limits[element_num] = [element_item.unit_type, element_item.upper_limit, element_item.lower_limit, element_item.side_comment]

        return element_names, element_limits_info, element_units

    def export_sample_data(self):
        logger.info('Entering export_sample_data')

        print(self.symbol_num)
        print(self.element_row_nums)

        sample_data = {}

        for sample_name, sample_item in self.samples.items():
            pass;


    def init_samples(self):
        logger.info('Entering init_samples')

        # crate samples items
        for sample_name in self.sample_names:
            jobNum, sample_num = sample_name.split("-")

            self.samples[sample_name] = IcpReportSampleItem(jobNum, sample_num, sample_name)

    def load_samples_data(self):
        logger.info('Entering load_samples_data')

        # retrieve machine data from database
        machine_data = get_machine_data(self.db, self.jobNum)

        # load machine sample data
        for current_item in machine_data:
            sample_name = current_item[0]

            # convert the data into readable dict
            parsed_data = json.loads(current_item[3])

            if(sample_name in self.samples):
                for element_name, element_value in parsed_data.items():

                    if(element_name.lower() in self.element_row_nums):
                        row = self.element_row_nums.index(element_name.lower())

                        diluted_value = self.calculate_dilution_value(element_value)
                        logger.info(f'sample_name: {sample_name}, element: {element_name}, original_value: {element_value}, diluted_value: {diluted_value}')

                        self.samples[sample_name].add_data(row, diluted_value)

                    else:
                        logger.error(f'{element_name} not in self.symbol_num')
            else:
                logger.error(f'{sample_name} not in self.samples')

        return self.samples

    def calculate_sample_hardness(self):
        logger.info('Entering calculate_sample_hardness')

        for sample_name, sample_item in self.samples.items():
            calcium_row = self.symbol_num['ca']
            magnesium_row = self.symbol_num['mg']

            logger.debug(f'calcium_row: {calcium_row}, magnesium_row: {magnesium_row}')

            if(calcium_row in sample_item.data and magnesium_row in sample_item.data):
                calcium_value = sample_item.data[calcium_row]
                magnesium_value = sample_item.data[magnesium_row]

                sample_item.hardness = calculate_hardness(calcium_value, magnesium_value)
            else:
                logger.info(f"{sample_name} doesn't have the ca or mg element defined")

        return self.samples

    def calculate_dilution_value(self, value):
        logger.info('Entering calculate_dilution_values')

        if(is_float(value) and self.dilution != 1):
            calculation = float(value) * float(self.dilution)
            return round(calculation, 3 )
        else:
            try:
                return round(float(value), 3)
            except ValueError:
                logger.warning('Could not convert value to float {value}')
                return value

def calculate_hardness(calcium, magnesium):

    # don't need to multiply it by the dilution since we done it the previous step, but we get a more accurate value when calculate it after
    calcium = float(calcium)
    magnesium = float(magnesium)

    return round(calcium * 2.497 + calcium * 4.11, 1)

def get_machine_data(db, jobNum):
    try:
        query = 'SELECT sampleName, jobNum, machineNum, data FROM icpData WHERE jobNum = ? ORDER BY sampleName ASC'

        return list(db.query(query, (jobNum,)))

    except Exception as e:
        print(e)
        return None