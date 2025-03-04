
from base_logger import logger

from modules.managers.tools.client_info_manager import ClientInfoManager

# by pressing the save btn, you'll save the report information

class ReportItem:

    def __init__(self, client_manager, reports_manager,  job_num:int, report_id:int, param_id:int, dilution:float, creation_date:str=None, status:int=None):
        self.job_num = job_num
        self.report_id = report_id
        self.param_id = param_id
        self.dilution = dilution
        self.creation_date = creation_date
        self.status = status
        self.author_one_id = None
        self.author_two_id = None

        self.client_manager = client_manager
        self.reports_manager = reports_manager

        self.total_samples = 0
        self.samples_info = {}
        self.samples_data = {}

        self.sample_names = {}
        self.sample_tests = {}

    def get_info(self):
        return self.job_num. self.report_id,

    #TODO: check if there is any author information
    def set_author(self, author_one, author_two):
        self.author_one_id = author_one
        self.author_two_id = author_two

    def get_authors(self):
        return self.author_one_id, self.author_two_id

    def set_client_info(self, client_info):
        logger.info(f'Entering set_client_info with client_info: {client_info}')
        self.client_manager = client_info

    def set_client_data(self, client_info) -> bool:

        if isinstance(client_info, ClientInfoManager):
            self.client_manager = client_info
            return True
        return False

    def get_client_data(self):

        if(self.client_manager):
            return self.client_manager.get_all_client_info()
        return None

    def process_sample_names(self, sample_names):
        logger.info(f'Entering process_sample_names with sample_names: {sample_names}')

        self.sample_names = sample_names

        # check for duplicates

    def process_sample_tests(self, sample_tests):
        logger.info(f'Entering process_sample_tests with sample_tests: {sample_tests}')

        self.sample_tests = sample_tests

    def process_client_info(self, client_info):
        self.client_manager.set_client_info(client_info)