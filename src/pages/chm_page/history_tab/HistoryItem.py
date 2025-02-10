
class HistoryItem:
    def __init__(self, jobNum, sampleNum, testNum, testName, testVal, unit, recovery, creation):
        self.jobNum = jobNum
        self.sampleNum = sampleNum
        self.testNum = testNum
        self.testName = testName
        self.testVal = testVal
        self.unit = unit
        self.recovery = recovery
        self.creation = creation

    def get_values(self):
        return self.jobNum, self.sampleNum, self.testNum, self.testName, self.testVal, self.unit, self.recovery, self.creation

    def side_edit_update(self, testNum, testName, testVal, recovery, unit):
        self.testName = testName
        self.testNum = testNum
        self.testVal = testVal
        self.recovery = recovery
        self.unit = unit

    def __eq__(self, other):
        # To ensure `remove()` knows what qualifies as an equal HistoryItem
        if isinstance(other, HistoryItem):
            return (self.jobNum == other.jobNum and self.sampleNum == other.sampleNum
                    and self.testNum == other.testNum and self.testName == other.testName
                    and self.testVal == other.testVal and self.unit == other.unit
                    and self.recovery == other.recovery and self.creation == other.creation)
        return False

    def __repr__(self):
       return (f"HistoryItem(jobNum={self.jobNum}, sampleNum={self.sampleNum}, testNum={self.testNum}, "
                f"testName='{self.testName}', testVal={self.testVal}, unit='{self.unit}', "
                f"recovery='{self.recovery}', creation='{self.creation}')")


