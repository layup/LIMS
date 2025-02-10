import math

from base_logger import logger

from pages.chm_page.history_tab.HistoryItem import HistoryItem

# managers the data and logic
class HistoryModel:
    def __init__(self, db, chm_test_data_manager):
        self.db = db
        self.chm_test_data_manager = chm_test_data_manager

        self.history_items = []

        self.current_page = 1
        self.total_pages = 1

        self.off_set = 0
        self.page_size = 100
        self.page_sizes = []

    def add_item(self, item):
        sample_num = item[0]
        test_id = item[1]
        test_val = item[2]
        standard = item[3]
        unit = item[4]
        jobNum = item[5]
        creation_date = item[6]

        test_name = self.chm_test_data_manager.find_test_name(test_id)

        self.history_items.append(HistoryItem(jobNum, sample_num, test_id, test_name, test_val, unit, standard, creation_date))

    def total_items(self):
        return len(self.history_items)

    def get_all_item(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def load_items(self, limit, offset, search_query=''):

        self.clear_items()

        if(search_query == ''):

            results = self.chm_test_data_manager.get_limited_tests(limit, offset)
           # print(results);
        else:
            results = self.chm_test_data_manager.search_tests(limit, offset, search_query)

        for current_item in results:
            self.add_item(current_item)

        return self.history_items

    def calculate_total_pages(self, search_query=""):
        #total pages

        if(search_query == ''):
            total_items = self.chm_test_data_manager.get_tests_count()

        else:
            total_items = self.chm_test_data_manager.search_tests_count(search_query)

        # set total pages
        self.total_pages = math.ceil(total_items / self.page_size)

        return self.total_pages

    def remove_item(self, current_item):

        try:
            deleted_row = self.chm_test_data_manager.delete_test(current_item.jobNum, current_item.sampleNum, current_item.testNum)

            if(deleted_row):

                self.history_items.remove(current_item)
                return True
            else:
                return False

        except Exception as error:
            return False

    def update_item(self, current_item, new_data):

        try:
            test_id = new_data[0]
            testName = self.chm_test_data_manager.find_test_name(test_id)
            test_val = new_data[1]
            standard = new_data[2]
            unit = new_data[3]

            updated_rows = self.chm_test_data_manager.update_test(current_item.jobNum, current_item.sampleNum, test_id, test_val, standard, unit)

            if(updated_rows):

                current_item.side_edit_update(test_id, testName, test_val, standard, unit)
                return True

            return False;

        except Exception as error:
            print(error)

            return False

