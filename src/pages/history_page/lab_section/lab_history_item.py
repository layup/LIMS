

class LabHistoryItem:
    def __init__(self, jobNum, report, parameter, dilution, creation, status):
        self.jobNum = jobNum
        self.report = report
        self.parameter = parameter
        self.dilution = dilution
        self.creation = creation
        self.status = status

    def get_values(self):
        return self.jobNum, self.report, self.parameter, self.dilution, self.creation, self.status

    def side_edit_update(self, jobNum, report, parameter, dilution, creation, status):
        self.jobNum = jobNum
        self.report = report
        self.parameter = parameter
        self.dilution = dilution
        self.creation = creation
        self.status = status

    def __eq__(self, other):
        # Ensure `remove()` knows what qualifies as an equal LabHistoryItem
        if isinstance(other, LabHistoryItem):
            return (
                self.jobNum == other.jobNum and
                self.report == other.report and
                self.parameter == other.parameter and
                self.dilution == other.dilution and
                self.creation == other.creation and
                self.status == other.status
            )
        return False

    def __repr__(self):
        return (f"LabHistoryItem(jobNum={self.jobNum}, report='{self.report}', "
                f"parameter='{self.parameter}', dilution='{self.dilution}', "
                f"creation='{self.creation}', status='{self.status}')")


