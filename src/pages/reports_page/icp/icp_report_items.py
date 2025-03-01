from base_logger import logger


class IcpReportElementsItem:
    def __init__(self, name, num, symbol):
        self.element_name = name
        self.element_num = num
        self.element_symbol = symbol
        self.unit = ''
        self.lower_limit = ''
        self.upper_limit = ''
        self.comment = ''
        self.footer = ''

    def __repr__(self):
            return (f"IcpReportElementsItem(name={self.element_name}, "
                    f"num={self.element_num}, symbol={self.element_symbol}, "
                    f"unit={self.unit}, lower_limit={self.lower_limit}, "
                    f"upper_limit={self.upper_limit}, comment={self.comment})")

    def add_limits(self, unit, lower, upper, comment, footer):
        self.unit = unit
        self.lower_limit = lower
        self.upper_limit = upper
        self.comment = comment
        self.footer = footer

class IcpReportSampleItem:
    def __init__(self, jobNum, sampleNum, sampleName, hardness ='', ph = ''):
        self.jobNum = jobNum
        self.sampleNum = sampleNum
        self.sampleName = sampleName
        self.hardness = hardness
        self.ph = ph

        # Data consists of data[test_id] = [value, recovery, unitType]
        # data[row] = value
        self.data = {}

        #TODO: not sure about having this
        self.diluted_data = {}

    def __repr__(self):
        return (f"chemReportSampleItem(jobNum={self.jobNum!r}, "
                f"sampleNum={self.sampleNum!r}, "
                f"sampleName={self.sampleName!r}, "
                f"data={self.data!r})")


    def add_data(self, row, testVal, recovery=None, unit=None):
        logger.info(f'Entering add_data with row: {row}, testVal: {testVal}, recovery: {recovery}, unit: {unit}')
        self.data[row] = str(testVal)

    def update_data(self, test_id, test_val):
        self.data[test_id] = test_val

    def add_diluted_data(self, row, value):
        self.diluted_data[row] = value

    def clear_data(self):
        self.data = {}

    def get_data(self):
        return self.data

    def get_hardness(self):
        return self.hardness

    def get_ph(self):
        return self.ph
