import math

from base_logger import logger

from pages.history_page.lab_section.lab_history_item import LabHistoryItem

# managers the data and logic
class LabHistoryModel:
    def __init__(self, db, parameters_manager, jobs_manager):
        self.db = db;
        self.parameters_manager = parameters_manager
        self.jobs_manager = jobs_manager

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
        #self.param_names = get_parameters(self.db)
        #logger.info(f'self.param_names: {self.param_names}')

        self.param_names = self.parameters_manager.get_params()


    def add_item(self, item):
        job_num = item[0]
        report = item[1]
        parameter = item[2]
        dilution = item[3]
        creation_date = item[4]
        status = item[5]


        self.history_items.append(LabHistoryItem(job_num, report, parameter, dilution, creation_date, status))

    def total_items(self):
        return len(self.history_items)

    def get_all_item(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def load_items(self, limit, offset, search_query=''):
        logger.info(f'LabHistoryModel load_items with limit: {limit}, offset: {offset}, search_query: {search_query} ')

        self.clear_items()

        if(search_query == ''):
            results = self.jobs_manager.get_limited_jobs(limit, offset)
        else:
            results = self.jobs_manager.search_limited_jobs(limit, offset, search_query)

        logger.info(f'results: {results}')

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = self.jobs_manager.get_total_jobs_count()
        else:
            total_items = self.jobs_manager.search_jobs_count(search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages


def get_parameters(db):
    query = '''
        SELECT * FROM parameters
    '''

    results = db.query(query)

    if(results):
        return {item[0]: item[1] for item in results}

    return {}
