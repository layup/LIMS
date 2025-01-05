
from base_logger import logger

class TestItem:
    def __init__(self, test_id,test_name, test_type, chem_name, micro_name, print_status, show_status ):
        self.test_id=test_id
        self.test_name=test_name
        self.test_type=test_type
        self.chem_name=chem_name
        self.micro_name=micro_name
        self.print_status=print_status
        self.show_status=show_status

    def get_name(self):
        return self.test_name

    def __repr__(self):
        return f"TestItem(id={self.test_id}, name='{self.test_name}', type='{self.test_type}', " \
               f"chem_name='{self.chem_name}', micro_name='{self.micro_name}', " \
               f"print_status={self.print_status}, show_status={self.show_status})"


class TestManager:
    def __init__(self, db):
      self.db = db

      # test_id = TestItem
      self.tests = {}

      self.init_test()

    def init_test(self):
        tests = self.get_all_test()

        for test in tests:
            test_id = test[0]
            test_name = test[1]
            test_type = test[2]
            chem_name = test[3]
            micro_name = test[4]
            print_status = test[5]
            show_status = test[6]

            self.tests[test_id] = TestItem(test_id, test_name, test_type, chem_name, micro_name, print_status, show_status)

    def return_tests(self):
        return self.tests.items()

    def get_test_info(self, test_id):
        return self.tests.get(test_id)

    def get_tests(self):
        return self.tests

    def get_test_name(self, test_id):

        name_list = []

        for test_item in self.tests:
            name_list.append(test_item.get_name())

        return name_list

    def get_test_by_type(self, type_name):

        test_list = []

        #query = 'SELECT testNum, testName FROM Tests WHERE testName NOT LIKE "%ICP%" AND type = "C" ORDER BY testName ASC'

        for test_id, test_item in self.tests.items():
            if test_item.test_type == type_name:
                test_list.append(test_item)

        return test_list

    def get_all_test(self):
        query = 'SELECT TestNum, testName, type, benchChemName, benchMicroName,  printTests, showTests FROM Tests'

        results = self.db.query(query)
        return results

    def update_test(self, test_id, test_item):
        logger.info('Entering update_test with test_id: {test_id}')

        # update the tests
        self.tests[test_id] = test_item

        # update the database

        pass;

    def new_test(self, test_id, test_item):
        pass;

    def add_test(self, test_id, test_name):
        pass;

    def remove_test(self, test_id):
        pass;