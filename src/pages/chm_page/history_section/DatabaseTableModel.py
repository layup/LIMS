import math;


from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

class DatabaseTableModel(QObject):
    #TODO: allow for filter search via the footer somehow
    dataChanged = pyqtSignal(list)

    def __init__(self, database, current_page=1, total_rows=100):
        super().__init__()
        self.db = database

        self.data = []
        self.filtered_data = self.data

        #TODO: introduce a filter system that we can use
        self.filter_by = None;

        self.current_page = current_page
        self.total_rows = total_rows
        self.total_pages = self.get_total_rows()

        self.load_init_data()

    def get_data(self):
        self.data = self.fetch_data()
        return self.data

    def get_total_rows(self):
        query = 'SELECT COUNT(*) FROM chemTestsData'

        totalPages = self.db.query(query)[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));

        return totalPages

    def get_total_rows_filter(self, text: str) -> int:
        query = f'SELECT COUNT(*) FROM chemTestsData WHERE sampleNum LIKE ?'
        sample_text = '%' + text + '%'

        totalPages = self.db.query(query, (sample_text, ))[0][0]
        totalPages = int(math.ceil(totalPages/self.total_rows));

        return totalPages

    def get_footer_info(self):
        return {
            'current_page': self.current_page,
            'total_rows': self.total_rows,
            'total_pages': self.total_pages,
        }

    def load_init_data(self):
        self.data = self.fetch_data()

    def fetch_data(self) -> list:
        #TODO: redo this and add the creation date
        machineDataQuery = 'SELECT jobNum, sampleNum, testNum, testValue, unitValue, standardValue, creationDate FROM chemTestsData ORDER BY creationDate DESC LIMIT ? OFFSET ?'
        offSet = (self.current_page -1) * self.total_rows

        self.db.execute(machineDataQuery, (self.total_rows, offSet,))  # Pass offset as a single value
        self.data = list(self.db.fetchall())

        self.dataChanged.emit(self.data)
        return self.data

    def set_filter(self, jobNum):

        print(f'set_filter: {jobNum}');

        self.current_page = 1;

        if(jobNum == ''):
            # Reset the search to normal
            self.total_pages = self.get_total_rows()
            return 1, self.fetch_data()
        else:
            self.total_pages = self.get_total_rows_filter(jobNum)
            offSet = (self.current_page -1) * self.total_rows

            inquiry = 'SELECT jobNum, sampleNum, testNum, testValue, unitValue, standardValue, creationDate FROM chemTestsData WHERE jobNum LIKE ? ORDER BY creationDate DESC LIMIT ? OFFSET ?'
            self.filtered_data = list(self.db.query(inquiry,('%' + jobNum + '%', self.total_rows, offSet)))

            if(self.filtered_data):
                self.dataChanged.emit(self.filtered_data)
                return 2, self.filtered_data
            else:
                return 0, None

    def set_page(self, page_number):
        self.current_page = page_number
        print(f'Changed Page to {self.current_page} of {self.total_pages}')
        # offset will be updated
        self.fetch_data()

    def set_rows(self, index):
        valid_rows = {0: 50, 1: 100, 2:300}

        if(index in valid_rows):
            self.total_rows = valid_rows[index]
            self.fetch_data()