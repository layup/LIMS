import sqlite3

from datetime import date
from base_logger import logger


class TestItem:

    def __init__(self, test_id, test_name):
        self.test_id = test_id
        self.test_name = test_name




class MacrosItem:

    def __init__(self, macro_id, macro_name, is_displayed):
        self.macro_id = macro_id
        self.macro_name = macro_name
        self.is_displayed = is_displayed

        self.tests = []

    def __repr__(self):
        return f"MacrosItem(macro_id={self.macro_id!r}, macro_name={self.macro_name!r}, is_displayed={self.is_displayed!r}, tests={self.tests!r})"


    def add_tests(self, test_id: int):

        if(test_id not in self.tests):
            self.tests.append(test_id)

    def set_tests(self, tests_list: list):
        self.tests = tests_list

    def remove_tests(self, test_id: int):

        if(test_id in self.tests):
            self.tests.remove(test_id)

    def clear_tests(self):
        self.tests = []


class MacrosManger:

    def __init__(self, db):
        self.db = db

        # macro_id = macros_item
        self.macros_list = {}

        self.init_setup()

    def init_setup(self):

        logger.warning(f'TESTING TESTING TESTING TESTING ')

        macros_list = self.get_all_macros()

        if(macros_list):
            for macro_item in macros_list:

                macro_id = macro_item[0]
                macro_name = macro_item[1]
                is_displayed = macro_item[2]

                self.macros_list[macro_id] = MacrosItem(macro_id, macro_name, is_displayed)

                # note I can get the tests names later with the test_manager
                test_list = self.get_macros_tests(macro_id)
                self.macros_list[macro_id].set_tests(test_list)


    #******************************************************************
    #    macros functions
    #******************************************************************

    def add_macro(self, macro_name: str) -> bool:
        logger.info(f'Entering MacrosManager add_macro with macro_name: {macro_name}')

        try:
            display_status = 1 # true

            query = 'INSERT INTO macros (macro_name, is_displayed) values (?, ?)'
            self.db.execute(query, (macro_name, display_status))
            self.db.commit()

            # Get the last inserted row ID:
            new_macro_id = self.db.lastrowid  # This is the key!

            logger.debug(f'New macro {macro_name} added with ID: {new_macro_id}')

            return True

        except Exception as e:
            logger.error(e)
            return False

    #TODO: set the other functions to cascade if we delete it
    def remove_macro(self, macro_id:int) -> int:
        logger.info(f'Entering MacrosManager remove_macro with macro_id: {macro_id}')

        try:
            query = 'DELETE FROM macros WHERE macro_id = ?'
            self.db.execute(query, (macro_id))
            self.db.commit()

            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows

            if(deleted_rows > 0):
                logger.info(f"Successfully deleted {deleted_rows} row(s) from macros_tests.")
                return deleted_rows
            return 0

        except Exception as e:
            logger.error(f'An unexpected error occurred when trying to remove test from macros: {macro_id}: {e}')
            return 0


    def update_macro_status(self, macro_id:int , new_status: int) -> bool:
        logger.info(f'Entering MacrosManager update_macro_status with macro_id: {macro_id}, new_status: {new_status}')

        try:
            query = 'UPDATE macros SET is_displayed = ?  WHERE macro_id = ? '
            self.db.execute(query, (new_status, macro_id))
            self.db.commit()

            if(self.db.cursor.rowcount > 0):
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s) in macros.")
                return True

            logger.info("No rows were updated.")
            return False

        except Exception as e:
            logger.error(f'An unexpected error occurred when updating macros {macro_id}: {e}')
            return False


    def update_macro_name(self, macro_id:int, new_macro_name: int) -> bool:
        logger.info(f'Entering MacrosManager update_macro_name with macro_id: {macro_id}, new_macro_name: {new_macro_name}')

        try:
            query = 'UPDATE macros SET macro_name = ?  WHERE macro_id = ? '
            self.db.execute(query, (new_macro_name, macro_id))
            self.db.commit()

            if(self.db.cursor.rowcount > 0):
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s) in macros.")
                return True

            logger.info("No rows were updated.")
            return False

        except Exception as e:
            logger.error(f'An unexpected error occurred when updating macros {macro_id}: {e}')
            return False

    def get_all_macros(self):

        try:
            query = 'SELECT * FROM macros'

            self.db.execute(query)

            macros_list = self.db.fetchall()

            return macros_list

        except Exception as e:
            logger.error(f'There was an error trying to get_all_macros: {e}')

            return None

    #******************************************************************
    #    macro_tests functions
    #******************************************************************

    def add_macro_test(self, macro_id: int, test_id: int) -> bool:
        logger.info(f'Entering MacrosManager add_macro_test with macro_id: {macro_id}, test_id: {test_id}')

        try:
            query = 'INSERT INTO macros_tests (macro_id, test_id) values (?, ?)'
            self.db.execute(query, (macro_id, test_id))
            self.db.commit()

            logger.debug(f'macro_id: {macro_id} added test_id: {test_id} to macros_tests')

            return True

        except Exception as e:
            logger.error(e)

            return False

    def remove_macro_test(self, macro_id:int, test_id:int) -> int :
        logger.info(f'Entering MacrosManager remove_macro_test with macro_id: {macro_id}, test_id: {test_id}')

        try:
            query = 'DELETE FROM macros_tests WHERE macro_id = ? and test_id = ?'
            self.db.execute(query, (macro_id, test_id))
            self.db.commit()

            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows

            if(deleted_rows > 0):
                logger.info(f"Successfully deleted {deleted_rows} row(s) from macros_tests.")
                return deleted_rows

            return 0

        except Exception as e:
            logger.error(f'An unexpected error occurred when trying to remove test from macro_test: {macro_id}: {e}')
            return 0


    def get_macros_tests(self, macro_id:int):

        try:
            query = 'SELECT test_id FROM macros_tests WHERE macro_id = ?'
            self.db.execute(query, (macro_id, ))
            test_list = self.db.fetchall()

            test_list = [item[0] for item in test_list]

            return test_list

        except Exception as e:
            logger.error(f"There was en error trying to get_macros_tests: {e}")
            return None

