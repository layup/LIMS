import sqlite3


from datetime import date
from base_logger import logger

from modules.utils.logic_utils import remove_control_characters

class TestItem:

    def __init__(self, job_num, sample_num, test_id, test_val, recovery, unit):
        self.job_num = job_num
        self.sample_num = sample_num
        self.test_id = test_id
        self.test_val = test_val
        self.recovery = recovery

        self.unit = unit

    def update_test_val(self, test_val):
        self.test_val = test_val


class ChmTestManager:

    def __init__(self, db):
        self.db = db

    def get_tests_count(self):
        logger.info('Entering get_tests_count')

        try:
            query = 'SELECT COUNT(*) FROM chm_data'
            results = self.db.query(query)
            return results[0][0]

        except sqlite3.Error as e:
            logger.error(f"Database error getting count: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred getting count: {e}")
            return None

    def get_limited_tests(self, limit, offset):
        logger.info(f'Entering get_limited_tests with limit: {limit}, offset: {offset}')

        try:
            query = "SELECT * FROM chm_data ORDER BY creation_date DESC LIMIT ? OFFSET ?"
            results = self.db.query(query, (limit, offset))

            logger.info(f"Retrieved {len(results)} rows from chm_data (limit={limit}, offset={offset}).")
            return results

        except sqlite3.Error as e:
            logger.error(f"Database error during paginated data retrieval: {e}")

            return None
        except Exception as e: # Catch other exceptions
            logger.error(f"An unexpected error occurred during paginated data retrieval: {e}")
            return None

    def get_total_test_count(self):
        try:
            query = 'SELECT count(testName) FROM chm_test_info'
            count = self.db.query(query)
            return count[0][0] if count else 0

        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def get_tests_results(self, job_num, sample_tests):
        logger.info('Entering get_tests_results')

        testsQuery = 'SELECT * FROM chm_data WHERE job_num = ?'
        test_results = self.db.query(testsQuery, (job_num,))

        logger.info(test_results)

        # retrieve data from .txt file and user entered
        chem_tests_list = []

        # examine the .txt items
        for _, tests_list in sample_tests.items():
            for current_test in tests_list:
                current_test = remove_control_characters(str(current_test))
                if(current_test not in chem_tests_list and 'ICP' not in current_test):
                    chem_tests_list.append(current_test)

        # examine the test_names
        if(test_results):
            for item in test_results:
                test_num = item[1]
                test_name = self.get_test_text_name(test_num)

                if(test_name not in chem_tests_list):
                    chem_tests_list.append(test_name)

        return chem_tests_list, test_results

    def get_test_text_name(self, test_id):

        try:
            query = 'SELECT bench_chem_name FROM Tests WHERE test_id = ?'
            result = self.db.query(query, (test_id, ))
            return result[0][0]

        except Exception as e:
            print(e)

    #TODO: edit the thing
    def find_test_name(self, test_id):
        """Retrieves the testName for a given test_id, or None if not found or on error."""
        try:

            #self.db.query("SELECT testName FROM Tests WHERE test_id = ?", (test_id,))
            self.db.query("SELECT testName FROM Tests WHERE test_id = ?", (test_id,))
            result = self.db.fetchone()  # Use fetchone() and handle None

            if result:
                return result[0]  # Return the testName
            else:
                return None  # Return None if no matching test is found

        except sqlite3.Error as e:
            logger.error(f"Database error getting test name: {e}")
            return None

        except Exception as e: # Catch any other exceptions
            logger.error(f"An unexpected error occurred getting test name: {e}")
            return None


    def search_tests(self, limit, offset, search_query):
        """Searches jobs with pagination and returns a list of tuples or None on error."""
        try:
            query = """
                SELECT *
                FROM chm_data
                WHERE job_num LIKE ?
                ORDER BY creation_date DESC
                LIMIT ? OFFSET ?
            """
            search_term = f"{search_query}%"  # Add wildcard
            #cursor.execute(query, (search_term, limit, offset))
            #results = cursor.fetchall()

            results = self.db.query(query, (search_term, limit, offset))

            logger.info(f"Search returned {len(results)} rows (query: {search_query}, limit: {limit}, offset: {offset})")

            return results

        except sqlite3.Error as e:
            logger.error(f"Database error during search: {e}")
            return None

        except Exception as e: # Catch any other exceptions
            logger.error(f"An unexpected error occurred during search: {e}")
            return None

    def search_tests_count(self, search_query):
        """Counts matching jobs and returns the count or None on error."""
        try:
            query = """
                SELECT COUNT(*)  -- Use COUNT(*)
                FROM chm_data
                WHERE job_num LIKE ?
            """
            search_term = f"{search_query}%"
            #cursor.execute(query, (search_term,))
            #count = cursor.fetchone()[0]
            #return count
            results = self.db.query(query, (search_term, ))
            return results[0][0]

        except sqlite3.Error as e:
            logger.error(f"Database error getting search count: {e}")
            return None
        except Exception as e: # Catch any other exceptions
            logger.error(f"An unexpected error occurred getting search count: {e}")
            return None

    def add_test(self, job_num, sample_num, test_id, test_val, recovery, unit):

        current_date = date.today()

        try:
            query = 'INSERT INTO chm_data (sample_num, test_id, test_val, recovery_val, unit_val, job_num, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?)'
            self.db.execute(query, (sample_num, test_id, test_val, recovery, unit, job_num, current_date, ))
            self.db.commit()

            return True

        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity Error: {e}")  # More descriptive message
            self.db.rollback()  # Rollback on integrity error
            return False

        except sqlite3.Error as e:  # Catch other SQLite errors
            logger.error(f"SQLite Error: {e}")  # More descriptive message
            self.db.rollback()
            return False

        except Exception as e: # Catch any other exceptions
            logger.error(f"An unexpected error occurred: {e}")
            self.db.rollback()

            return False

    def update_test(self, job_num, sample_num, test_id, test_val, recovery, unit):

        try:

            # Prepare the SQL UPDATE query
            sql_update_query = """
                UPDATE chm_data
                SET test_val = ?, recovery_val = ?,unit_val = ?
                WHERE sample_num = ? AND test_id = ? AND job_num = ?
            """

            values = (test_val, recovery, unit, sample_num, test_id, job_num)

            self.db.execute(sql_update_query, values)
            self.db.commit()

            # Check if any rows were updated
            if self.db.cursor.rowcount > 0:
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s).")
            else:
                logger.info("No rows were updated.")

            return self.db.cursor.rowcount

        except sqlite3.Error as error:
            logger.error(f"Database error occurred: {error}")
            self.db.rollback()  # Rollback on error
            return None

    def delete_test(self, job_num, sample_num, test_id):

        try:
            query = 'DELETE FROM chm_data WHERE job_num = ? AND sample_num = ? and test_id = ?'
            self.db.execute(query, (job_num, sample_num, test_id))
            self.db.commit()

            # Check how many rows were deleted
            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows
            if deleted_rows > 0:
                logger.info(f"Successfully deleted {deleted_rows} row(s) from chm_data.")
            else:
                logger.info("No rows were deleted (the condition may not have matched any records).")

            return deleted_rows

        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error during delete: {e}")
            self.db.rollback()
            return None

        except Exception as e: # Catch other exceptions
            logger.error(f"An unexpected error occurred during delete: {e}")
            self.db.rollback()
            return None

    def check_test_exists(self, job_num, sample_num, test_id):
        logger.info('Entering check_test_exists with job_num: {job_num}, sample_num: {sample_num}, test_id: {test_id}')

        try:
            query = f"SELECT EXISTS(SELECT 1 FROM chm_data WHERE job_num = ? AND sample_num = ? AND test_id = ?)"
            self.db.execute(query, (job_num, sample_num, test_id))
            result = self.db.fetchone()[0]

            # 1 as a bool is True
            return bool(result)

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return False

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return False



