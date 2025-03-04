import math

from base_logger import logger

from pages.icp_page.history_tab.icp_history_item import IcpHistoryItem

class IcpHistoryModel:
    def __init__(self, icp_test_data_manager, elements_manager):
        self.icp_test_data_manager = icp_test_data_manager
        self.elements_manager = elements_manager

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
            results = self.icp_test_data_manager.get_limited_data(limit, offset)

        else:
            results = self.icp_test_data_manager.search_limited_data(limit, offset, search_query)

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = self.icp_test_data_manager.get_total_count()
        else:
            total_items = self.icp_test_data_manager.search_data_count(search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages

    #TODO: fix this maybe or something
    def print_batch(self, batch_name):
        return self.icp_test_data_manager.get_samples_from_batch(batch_name)

