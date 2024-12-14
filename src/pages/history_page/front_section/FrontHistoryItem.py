


class FrontHistoryItem:
    def __init__(self, jobNum, clientName, creation, status):
        self.jobNum = jobNum
        self.clientName = clientName
        self.creation = creation
        self.status = status

    def get_values(self):
        return self.jobNum, self.clientName, self.creation, self.status

    def side_edit_update(self, jobNum, clientName, creation, status):
        self.jobNum = jobNum
        self.clientName = clientName
        self.creation = creation
        self.status = status

    def __eq__(self, other):
        # Ensure `remove()` knows what qualifies as an equal FrontHistoryItem
        if isinstance(other, FrontHistoryItem):
            return (self.jobNum == other.jobNum and self.clientName == other.clientName
                    and self.creation == other.creation and self.status == other.status)
        return False

    def __repr__(self):
        return (f"FrontHistoryItem(jobNum={self.jobNum}, clientName='{self.clientName}', "
                f"creation='{self.creation}', status='{self.status}')")