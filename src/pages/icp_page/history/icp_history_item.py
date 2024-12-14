import json

class IcpHistoryItem:
    def __init__(self, jobNum, sampleName, machine, fileName, creation):
        self.jobNum = jobNum
        self.sampleName = sampleName
        self.machine = machine
        self.fileName = fileName
        self.creation = creation

        self.data = {}

    def add_data(self, data):
        unpack_data = json.loads(data)

        for key, value in unpack_data.items():
            self.data[key] = value

    def __repr__(self):
        return (f"IcpHistoryItem(jobNum={self.jobNum!r}, sampleName={self.sampleName!r}, "
                f"machine={self.machine!r}, fileName={self.fileName!r}, creation={self.creation!r})")