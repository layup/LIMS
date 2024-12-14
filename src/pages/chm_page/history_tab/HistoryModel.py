import math

from base_logger import logger
from modules.dbFunctions import updateChmTestsData, deleteChmTestDataItem

from pages.chm_page.history_tab.HistoryItem import HistoryItem

# managers the data and logic
class HistoryModel:
    def __init__(self, db):
        self.db = db;

        self.history_items = []

        self.current_page = 1;
        self.total_pages = 1;

        self.off_set = 0;
        self.page_size = 100;
        self.page_sizes = []

    def add_item(self, item):
        sampleNum = item[0]
        testNum = item[1]
        testVal = item[2]
        standard = item[3]
        unit = item[4]
        jobNum = item[5]
        creationDate = item[6]
        #TODO: get testName
        testName = get_tests_name(self.db, testNum)

        self.history_items.append(HistoryItem(jobNum, sampleNum, testNum, testName, testVal, unit, standard, creationDate))

    def total_items(self):
        return len(self.history_items)

    def get_all_item(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def load_items(self, limit, offset, search_query=''):

        self.clear_items()

        if(search_query == ''):
            results = get_chem_tests(self.db, limit, offset)
           # print(results);
        else:
            results = search_jobs(self.db, limit, offset, search_query)

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = get_chem_tests_count(self.db)
        else:
            total_items = search_jobs_count(self.db, search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages

    def remove_item(self, current_item):

        try:
            if(deleteChmTestDataItem(self.db, current_item.sampleNum, current_item.testNum, current_item.jobNum)):

                self.history_items.remove(current_item)
                return True
            else:
                return False;

        except Exception as error:
            return False;

    def update_item(self, current_item, new_data):

        try:
            testNum = new_data[0]
            testName = get_tests_name(self.db, testNum)
            testVal = new_data[1]
            standard = new_data[2]
            unit = new_data[3]

            if(updateChmTestsData(self.db, current_item.sampleNum, testNum, current_item.jobNum, testVal, standard, unit )):

                current_item.side_edit_update(testNum, testName, testVal, standard, unit)
                return True

            return False;

        except Exception as error:
            print(error)

            return False

def get_chem_tests(db, limit, offset):
    query = '''
        SELECT *
        FROM chemTestsData
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?

    '''
    results = db.query(query, (limit, offset))
    return results

def get_chem_tests_count(db):
    query = '''
        SELECT count(jobNum)
        FROM chemTestsData
    '''
    results = db.query(query)
    return results[0][0]

def get_tests_name(db, test_id):
    logger.info('Entering get_tests_name')
    query = '''
        SELECT testName
        FROM Tests
        WHERE testNum = ?

    '''

    results = db.query(query, (test_id, ))

    return results[0][0]

def search_jobs(db, limit, offset, search_query):
    query = """
        SELECT *
        FROM chemTestsData
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
        FROM chemTestsData
        WHERE jobNum LIKE ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_query}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, ))

    return results[0][0]
