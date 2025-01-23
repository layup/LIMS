from base_logger import logger

class chmReportTestItem:
    def __init__(self, testNum=None, testName=None, textName=None, displayName=None, unitType=None, recovery=None, so=None, upper_limit=None, side_comment=None, footer_comment=None ):
        self.testNum = testNum
        self.testName = testName
        self.textName = textName
        self.displayName = displayName
        self.unitType = unitType
        self.recovery = recovery

        self.so = so

        self.upper_limit = upper_limit
        self.side_comment = side_comment
        self.footer_comment = footer_comment

    def __repr__(self):
        """Returns a string representation of the chmReportTestItem object.

        This method provides a more informative way to represent the object
        during printing or debugging.

        Returns:
        A string representation of the object in the format:
            chmReportTestItem(testNum=..., testName=..., textName=..., displayName=...,
                            unitType=..., recovery=..., so=..., upper_limit=...,
                            side_comment=..., footer_comment=...)
        """

        return f"chmReportTestItem(testNum={self.testNum}, testName={self.testName}, textName={self.textName}, displayName={self.displayName}, unitType={self.unitType}, recovery={self.recovery}, so={self.so}, upper_limit={self.upper_limit}, side_comment={self.side_comment}, footer_comment={self.footer_comment})"


#TODO: have a regular value and dilution value

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