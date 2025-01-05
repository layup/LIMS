from base_logger import logger

class chmReportTestItem:
    def __init__(self, testNum=None, testName=None, textName=None, displayName=None, unitType=None, recovery=None):
        self.testNum = testNum
        self.testName = testName
        self.textName = textName
        self.displayName = displayName
        self.unitType = unitType
        self.recovery = None;


    def __repr__(self):
        return (f"chemReportTestItem(testNum={self.testNum!r}, "
                f"testName={self.testName!r}, "
                f"textName={self.textName!r}, "
                f"displayName={self.displayName!r}, "
                f"unitType={self.unitType!r}),"
                f"recovery={self.recovery!r})")

class chmReportSampleItem:
    def __init__(self, jobNum, sampleNum, sampleName):
        self.jobNum = jobNum
        self.sampleNum = sampleNum
        self.sampleName = sampleName

        # Data consists of data[testNum] = [value, recovery, unitType]
        self.data = {}

    def __repr__(self):
        return (f"chemReportSampleItem(jobNum={self.jobNum!r}, "
                f"sampleNum={self.sampleNum!r}, "
                f"sampleName={self.sampleName!r}, "
                f"data={self.data!r})")

    def add_data(self, row, testVal, recovery=None, unit=None):
        logger.info(f'Entering add_data with row: {row}, testVal: {testVal}, recovery: {recovery}, unit: {unit}')
        self.data[row] = str(testVal)


    def update_data(self, testNum, testVal):
        self.data[testNum] = testVal

    def clear_data(self):
        self.data = {}

    def get_data(self):
        return self.data