import math

from base_logger import logger

from pages.history_page.lab_section.lab_history_item import LabHistoryItem

# managers the data and logic
class LabHistoryModel:
    def __init__(self, db):
        self.db = db;

        self.history_items = []

        self.current_page = 1;
        self.total_pages = 1;

        self.off_set = 0;
        self.page_size = 100;
        self.page_sizes = []

        self.param_names = {}

        self.init_setup()

    def init_setup(self):
        logger.info('Entering init_setup')
        self.param_names = get_parameters(self.db)
        logger.info(f'self.param_names: {self.param_names}')

    def add_item(self, item):
        jobNum = item[0]
        report = item[1]
        parameter = item[2]
        dilution = item[3]
        creationDate = item[4]
        status = item[5]


        self.history_items.append(LabHistoryItem(jobNum, report, parameter, dilution, creationDate, status))

    def total_items(self):
        return len(self.history_items)

    def get_all_item(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def load_items(self, limit, offset, search_query=''):

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
        SELECT jobNum, reportNum, parameterNum, dilution, creationDate, status
        FROM jobs
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?

    '''
    results = db.query(query, (limit, offset))
    return results

def get_jobs_count(db):
    query = '''
        SELECT count(jobNum)
        FROM jobs
    '''
    results = db.query(query)
    return results[0][0]

def search_jobs(db, limit, offset, search_query):
    query = """
        SELECT jobNum, reportNum, parameterNum, dilution, creationDate, status
        FROM jobs
        WHERE jobNum LIKE ?
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, limit, offset))

    return results

def search_jobs_count(db, search_query):
    query = """
        SELECT count(jobNum)
        FROM jobs
        WHERE jobNum LIKE ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, ))

    return results[0][0]


def get_parameters(db):
    query = '''
        SELECT * FROM parameters
    '''

    results = db.query(query)

    if(results):
        return {item[0]: item[1] for item in results}

    return {}
