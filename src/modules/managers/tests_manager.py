import sqlite3

from base_logger import logger

class TestItem:
    def __init__(self, test_id,test_name, test_type, chem_name, micro_name, display_name,  print_status, show_status, comment, footer, so, lower_limit, upper_limit):
        self.test_id=test_id
        self.test_name=test_name
        self.test_type=test_type
        self.chem_name=chem_name
        self.micro_name=micro_name
        self.display_name = display_name
        self.print_status=print_status
        self.show_status=show_status
        self.comment = comment
        self.footer = footer
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.so = so

    def get_name(self):
        return self.test_name

    def __repr__(self):
        return f"TestItem(id={self.test_id}, name='{self.test_name}', type='{self.test_type}', " \
               f"chem_name='{self.chem_name}', micro_name='{self.micro_name}', " \
               f"print_status={self.print_status}, show_status={self.show_status})"


class TestManager:
    def __init__(self, db):
      self.db = db

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
            display_name = test[5]
            print_status = test[6]
            show_status = test[7]
            comment = test[8]
            footer_comment = test[9]
            so = test[10]
            lower_limit = test[11]
            upper_limit = test[12]

            self.tests[test_id] = TestItem(
                test_id,
                test_name,
                test_type,
                chem_name,
                micro_name,
                display_name,
                print_status,
                show_status,
                comment,
                footer_comment,
                so,
                lower_limit,
                upper_limit
            )

    def return_tests(self):

        return self.tests.items()

    def get_test_info(self, test_id):
        if(test_id in self.tests):
            return self.tests.get(test_id)

        return None

    def get_chem_tests_info(self, test_id):
        if(test_id in self.tests):
            test_info = self.tests.get(test_id)

            return [test_info.test_name, test_info.chem_name, test_info.display_name, test_info.comment]

        return None

    def get_tests(self):
        return self.tests.items()

    def get_tests_type(self, test_type):
        return {key: value for key, value in self.tests.items() if value.test_type == test_type}

    def get_search_tests(self, search_query, test_type=None):

        tests = self.tests

        if(test_type):
           tests = self.get_tests_type(test_type)

        try:
            # If search_query is an integer (or can be converted to an integer)
            int_search_query = int(search_query)
            return {key: value for key, value in tests.items() if str(value.test_id).startswith(search_query)}
        except ValueError:
            # If search_query is not an integer, assume it's a string
            return {key: value for key, value in tests.items()
                if (value.test_name and value.test_name.lower().startswith(search_query.lower()))
                or (value.chem_name and value.chem_name.lower().startswith(search_query.lower()))
            }

    def get_tests_by_text(self, text_name):

        for key, value in self.tests.items():
            if text_name == value.chem_name:
                return value

        return None

    def get_test_by_type(self, type_name):

        test_list = []

        #query = 'SELECT test_id, test_name FROM Tests WHERE test_name NOT LIKE "%ICP%" AND type = "C" ORDER BY test_name ASC'

        for test_id, test_item in self.tests.items():
            if test_item.test_type == type_name:
                test_list.append(test_item)

        return test_list

    def get_all_test(self):
        query = 'SELECT test_id, test_name, type, bench_chem_name, bench_micro_name, display_name, print_tests, show_tests, comment, footer_comment, so, lower_limit, upper_limit FROM tests ORDER BY LOWER(test_name) ASC;'

        results = self.db.query(query)
        return results

    def update_chm_test(self, test_id, test_name, text_name, display_name, lower_limit, upper_limit, so, print_tests, show_tests, side_comment, footer_comment):
        logger.info(f'Entering update_chm_test with test_id: {test_id}')

        try:
            if(test_id in self.tests):
                query = 'UPDATE tests SET test_name=?, bench_chem_name=?, print_tests=?, show_tests=?, display_name=?, comment=?, footer_comment=?, lower_limit=?, upper_limit=?, so = ? WHERE test_id =?'
                self.db.execute(query, (test_name, text_name, print_tests, show_tests, display_name, side_comment, footer_comment, lower_limit, upper_limit, so,  test_id))
                self.db.commit()

                rows_affected = self.db.cursor.rowcount

                if(rows_affected > 0):
                    self.tests[test_id].test_name = test_name
                    self.tests[test_id].chem_name = text_name
                    self.tests[test_id].print_status = print_tests
                    self.tests[test_id].show_status = show_tests
                    self.tests[test_id].display_name = display_name
                    self.tests[test_id].comment = side_comment
                    self.tests[test_id].footer = footer_comment
                    self.tests[test_id].upper_limit = upper_limit
                    self.tests[test_id].lower_limit = lower_limit
                    self.tests[test_id].so = so

                    return rows_affected

            logger.warning(f'Could not update test: {test_id} since not in self.tests')
            return None

        except sqlite3.Error as e:
            logger.error(f'sqlite3: {e}')
            return None

        except Exception as e:
            logger.error(f'Exception: {e}')
            return None


    def update_show_status(self, test_id: int, status: int):
        logger.info(f'Entering update_show_status with test_id: {test_id}, status: {status}')

        try:
            if(test_id in self.tests):
                query = 'UPDATE tests SET show_tests=? WHERE test_id =?'
                self.db.execute(query, (status, test_id))
                self.db.commit()

                rows_affected = self.db.cursor.rowcount

                if(rows_affected > 0):
                    self.tests[test_id].show_status = status

                    return rows_affected

            logger.warning(f'Could not update test status: {test_id} since not in self.tests')
            return None

        except sqlite3.Error as e:
            logger.error(f'{e}')
            return None

        except Exception as e:
            logger.error(f'{e}')
            return None

    def update_print_status(self, test_id:int, status:int):
        logger.info(f'Entering update_print_status with test_id: {test_id}, status: {status}')

        try:
            if(test_id in self.tests):
                query = 'UPDATE tests SET printTest=? WHERE test_id =?'
                self.db.execute(query, (status, test_id))
                self.db.commit()

                rows_affected = self.db.cursor.rowcount

                if(rows_affected > 0):
                    self.tests[test_id].show_status = status

                    return rows_affected

            logger.warning(f'Could not update test print status: {test_id} since not in self.tests')
            return None

        except sqlite3.Error as e:
            logger.error(f'{e}')
            return None

        except Exception as e:
            logger.error(f'{e}')
            return None

    def update_test(self, test_id, test_name):
        logger.info('Entering update_test with test_id: {test_id}')

        # update the tests
        #self.tests[test_id] = test_item

        # update the database

        pass;

    def new_test(self, test_id, test_item):
        pass;

    def add_test(self, test_id, test_name, text_name, ):
        pass;


    def add_new_chem_tests(self):
        pass;

    def remove_test(self, test_id):
        try:
            del self.tests[test_id]

            return True

        except KeyError as e:
            print(e)

            return False


