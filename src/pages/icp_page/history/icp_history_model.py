import math

from pages.icp_page.history.icp_history_item import IcpHistoryItem

class IcpHistoryModel:
    def __init__(self,db):
        self.db = db

        self.history_items = []

        self.current_page = 1;
        self.total_pages = 1;

        self.off_set = 0;
        self.page_size = 100;
        self.page_sizes = []

    def add_item(self, item):
        sampleName = item[0]
        jobNum = item[1]
        machine = item[2]
        fileName = item[3]
        creation = item[4]
        data = item[5]

        current_item = IcpHistoryItem(jobNum, sampleName, machine, fileName, creation)
        current_item.add_data(data)

        self.history_items.append(current_item)

    def total_items(self):
        return len(self.history_items)

    def clear_items(self):
        self.history_items = []

    def load_items(self, limit, offset, search_query='' ):

        self.clear_items()

        if(search_query == ''):
            results = get_jobs(self.db, limit, offset)
           # print(results);
        else:
            results = search_jobs(self.db, limit, offset, search_query)

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = get_jobs_count(self.db)
        else:
            total_items = search_jobs_count(self.db, search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages


def get_jobs(db, limit, offset):
    query = '''
        SELECT sampleName, jobNum, machineNum, batchName, creationDate, data
        FROM icpData
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?
    '''
    results = db.query(query, (limit, offset))
    return results


def get_jobs_count(db):
    query = '''
        SELECT count(jobNum)
        FROM icpData
    '''
    results = db.query(query)
    return results[0][0]


def search_jobs(db, limit, offset, search_query):
    query = '''
        SELECT sampleName, jobNum, machineNum, batchName, creationDate, data
        FROM icpData
        WHERE sampleName LIKE ?
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?
    '''
    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, limit, offset))

    return results


def search_jobs_count(db, search_query):
    query = '''
        SELECT count(jobNum)
        FROM icpData
        WHERE jobNum LIKE ?
    '''

    search_term = f"{search_query}%"

    results = db.query(query, (search_term,))

    return results[0][0]