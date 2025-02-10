import sqlite3

from datetime import date
from base_logger import logger

class IcpTestManager:
    def __init__(self, db):
        self.db = db

    def add_data(self, key, job_num, base_name, package_data):

        try:
            current_date = date.today()

            sql = 'INSERT OR REPLACE INTO icp_data values(?, ?, ?, ?, ?, 1)'
            self.db.execute(sql, (key, job_num, base_name, package_data, current_date))
            self.db.commit()

            logger.info(f"ICP data added/replaced for key: {key}, job_num: {job_num}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Database error adding/replacing ICP data: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred adding/replacing ICP data: {e}")
            return False

    def delete_data(self, sample_name, machine_num):
        logger.info(f'Entering IcpTestManager delete_data with sample_name: {sample_name}, machine_num: {machine_num}')
        try:

            self.db.execute("DELETE FROM icp_data WHERE sample_name = ? AND machine_id = ?", (sample_name, machine_num))
            self.db.commit()

            return self.db.cursor.rowcount > 0 # Return True if any rows are deleted

        except sqlite3.Error as e:
            logger.error(f"Database error deleting ICP data: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred deleting ICP data: {e}")
            return False

    def get_machine_data(self, job_num):
        try:
            query = 'SELECT sample_name, job_num, machine_id, data FROM icp_data WHERE job_num = ? ORDER BY sample_name ASC'

            return list(self.db.query(query, (job_num,)))

        except Exception as e:
            print(e)
            return None

    def get_limited_data(self, limit, offset):
        logger.info(f'Entering IcpTestManager get_limited_data: with limit: {limit}, offset: {offset}')

        try:
            query = '''
                SELECT sample_name, job_num, machine_id, batch_name, creation_date, data
                FROM icp_data
                ORDER BY creation_date DESC
                LIMIT ? OFFSET ?
            '''
            results = self.db.query(query, (limit, offset))

            return results

        except sqlite3.Error as e:
            logger.error(f"Database error getting count: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred getting count: {e}")
            return None

    def get_total_count(self):
        logger.info(f'Entering IcpTestManager get_total_count')
        try:

            query = '''
                SELECT count(job_num)
                FROM icp_data
            '''
            results = self.db.query(query)
            return results[0][0]


        except sqlite3.Error as e:
            logger.error(f"Database error getting get_total_count: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred get_total_count: {e}")
            return None

    def get_samples_from_batch(self, batch_name):
        try:
            query = 'SELECT sample_name FROM icp_data WHERE batch_name = ?'

            results = self.db.query(query, (batch_name, ))
            return results

        except Exception as e:
            logger.error(f"An unexpected error occurred get_samples_from_batch: {e}")
            return None


    def search_limited_data(self, limit, offset, search_query):
        logger.info(f'Entering IcpTestManager search_limited_data: with limit: {limit}, offset: {offset}, search_query: {search_query}')

        try:

            query = '''
                SELECT sample_name, job_num, machine_id, batch_name, creation_date, data
                FROM icp_data
                WHERE sample_name LIKE ?
                ORDER BY creation_date DESC
                LIMIT ? OFFSET ?
            '''
            # Add wildcards to the search term for partial matching
            search_term = f"{search_query}%"

            # Execute the query with the search term and pagination parameters
            results = self.db.query(query, (search_term, limit, offset))

            return results

        except sqlite3.Error as e:
            logger.error(f"Database error getting search_limited_data: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred search_limited_data: {e}")
            return None


    def search_data_count(self, search_query):
        try:


            query = '''
                SELECT count(job_num)
                FROM icp_data
                WHERE job_num LIKE ?
            '''

            search_term = f"{search_query}%"

            results = self.db.query(query, (search_term,))

            return results[0][0]

        except sqlite3.Error as e:
            logger.error(f"Database error getting search_data_count: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred search_data_count: {e}")
            return None

