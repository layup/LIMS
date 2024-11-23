
class HistoryItem:
    def __init__(self, jobNum, sampleNum, testNum, testName, testVal, unit, standard, creation):
        self.jobNum = jobNum
        self.sampleNum = sampleNum
        self.testNum = testNum
        self.testName = testName
        self.testVal = testVal
        self.unit = unit
        self.standard = standard
        self.creation = creation

    def get_values(self):
        return self.jobNum, self.sampleNum, self.testNum, self.testName, self.testVal, self.unit, self.standard, self.creation
