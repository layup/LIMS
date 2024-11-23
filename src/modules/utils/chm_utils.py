

def getParameterAndUnitTypes(database):
    query = 'SELECT testNum, testName FROM Tests WHERE testName NOT LIKE "%ICP%" AND type = "C" ORDER BY testName ASC'
    results = database.query(query)

    unitTypes =  ['TCU', 'ug/L', 'mg/g']

    # Convert results into readable
    parameterTypes = [parameterItem(item[0], item[1]) for item in results]

    return parameterTypes, unitTypes

class parameterItem:
    def __init__(self,testNum, testName):
        self.testNum = testNum
        self.testName = testName

def getParameterTypeNum(comboBox):

    index = comboBox.currentIndex()
    if index >= 0:
        item = comboBox.itemData(index)
        if isinstance(item, parameterItem):
            return item.testNum
    return None

