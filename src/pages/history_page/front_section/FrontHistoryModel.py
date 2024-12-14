import math

from base_logger import logger

from pages.history_page.front_section.FrontHistoryItem import FrontHistoryItem


class FrontHistoryModel:
    def __init__(self, db):
        self.db = db;

        self.history_items = []

        self.current_page = 1;
        self.total_pages = 1;

        self.off_set = 0;
        self.page_size = 100;
        self.page_sizes = []

    def add_item(self, item):
        jobNum = item[0]
        companyName = item[1]
        creation = item[2]
        status = item[3]

        self.history_items.append(FrontHistoryItem(jobNum, companyName, creation , status))

    def total_items(self):
        return len(self.history_items)

    def get_all_item(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def load_items(self, limit, offset, search_query=''):

        self.clear_items()

        if(search_query == ''):
            results = get_front_history(self.db, limit, offset)
           # print(results);
        else:
            results = search_front_jobs(self.db, limit, offset, search_query)

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = get_front_tests_count(self.db)
        else:
            total_items = search_front_jobs_count(self.db, search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages



def get_front_history(db, limit, offset):
    query = '''
        SELECT jobNumber, companyName, creationDate, status
        FROM History
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?

    '''
    results = db.query(query, (limit, offset))
    return results

def get_front_tests_count(db):
    query = '''
        SELECT count(jobNumber)
        FROM History
    '''
    results = db.query(query)
    return results[0][0]


def search_front_jobs(db, limit, offset, search_query):
    query = """
        SELECT jobNumber, companyName, creationDate, status
        FROM History
        WHERE jobNumber LIKE ?
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, limit, offset))

    return results

def search_front_jobs_count(db, search_query):
    query = """
        SELECT count(jobNumber)
        FROM History
        WHERE jobNumber LIKE ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, ))

    return results[0][0]