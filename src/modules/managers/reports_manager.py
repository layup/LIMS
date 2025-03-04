import sqlite3

from datetime import date
from base_logger import logger


#TODO: I can just pass this item that contains all of the report information
class ReportItem:

    def __init__(self, job_num:int, report_id:int, param_id:int, dilution:float):
        self.job_num = job_num
        self.report_id = report_id
        self.param_id = param_id
        self.dilution = dilution

        # Author information
        self.author_one_id = None
        self.author_two_id = None

        # client information
        self.client_info = None

        # Sample Information
        self.total_samples = 0
        self.samples_info = None


    def set_author(self, author_one, author_two):
        self.author_one_id = author_one
        self.author_two_id = author_two

    def set_client_info(self, client_info):
        self.client_info = client_info

    def add_sample(self, sample_num, sample_name, sample_time, sample_date):
        pass

    def update_sample(self):
        pass

    def remove_sample(self):
        pass


class ReportsManager:

    def __init__(self, db):
        self.db = db

        self.active_report = None

    def add_report(self, job_num:int, report_id:int, param_id:int, dilution:float) -> bool:
        logger.info('Entering ReportsManager add_report')

        try:
            current_date = date.today()
            status = 0

            query = """
                INSERT INTO reports
                (job_num, report_id, param_id, dilution, creation_date, status)
                values (?, ?, ?, ?, ?, ?)
            """
            self.db.execute(query, (job_num, report_id, param_id, dilution, current_date, status ))
            self.db.commit()

            logger.debug(f'{job_num} successfully added to reports')
            return True

        except sqlite3.IntegrityError as e: # Handle IntegrityErrors (e.g., unique constraints)
            logger.warning(f"Integrity error adding report {job_num}: {e}")
            return False

        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error adding report {job_num}: {e}") # Log as error
            return False

        except Exception as e:  # Catch any other exceptions
            logger.error(f"An unexpected error occurred adding report {job_num}: {e}")
            return False

    def update_authors(self, job_num: int, report_id: int, author_one_id: int, author_two_id: int) -> bool:
        logger.info('Entering ReportsManager update_authors')

        try:
            query = """
                UPDATE reports
                SET author_one_id=?, author_two_id=?
                WHERE job_num=? AND report_id=?
            """
            self.db.execute(query, (author_one_id, author_two_id, job_num, report_id,))
            self.db.commit()

            return True

        except Exception as e:
            logger.error(f"An unexpected error occurred updating authors report {job_num}: {e}")
            return False

    def update_status(self, job_num:int, report_id: int, status:int) -> bool:
        logger.info('Entering ReportsManager update_status')

        try:
            query = """
                UPDATE reports
                SET status=?
                WHERE job_num=? AND report_id=?
            """
            self.db.execute(query, (status, job_num, report_id,))
            self.db.commit()

            return True

        except Exception as e:
            logger.error(f"An unexpected error occurred updating authors report {job_num}: {e}")
            return False

    def update_report(self, job_num:int, report_id:int, param_id:int, dilution:float)-> int:
        logger.info('Entering ReportsManager update_report')

        try:
            update_date = date.today()

            query = """
                INSERT OR REPLACE INTO reports (job_num, report_id, param_id, dilution, creation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            self.db.execute(query, (job_num, report_id, param_id, dilution, update_date))
            self.db.commit()

            return self.db.cursor.rowcount  # Number of rows affected (1 for update or insert)

        except sqlite3.Error as e:
            logger.error(f"Error updating report: {e}")
            return 0

        except Exception as e:
            logger.error(f"An unexpected error occurred updating report {job_num}: {e}")
            return 0


    def delete_report(self, job_num:int, report_id:int):
        logger.info(f'Entering ReportsManager delete_report with job_num: {job_num}, report_id: {report_id}')

        try:
            query = 'DELETE FROM reports WHERE job_num=? AND report_id=?'
            self.db.execute(query, (job_num, report_id, ))
            self.db.commit()

            # Check how many rows were deleted
            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows

            if deleted_rows > 0:
                logger.info(f"Successfully deleted {deleted_rows} row(s) from reports.")
                return True

            else:
                logger.info("No rows were deleted (the condition may not have matched any records).")
                return None

        except sqlite3.Error as e:
            logger.info(f"Error removing {job_num} from reports: {e}")
            return None

        except Exception as e:
            logger.error(f'Error: {e}')
            return None

    def get_report(self, job_num:int, report_id:int):
        logger.info(f'Entering ReportsManager get_report with job_num: {job_num}, report_id: {report_id}' )

        try:
            query = '''
                SELECT job_num, report_id, param_id, dilution, creation_date, author_one_id, author_two_id, status
                FROM reports
                WHERE job_num=? AND report_id=?
            '''
            results = self.db.query(query, (job_num, report_id))
            return results[0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def get_report_status(self, job_num:int, report_id:int):
        logger.info(f'Entering ReportsManager get_report_status with job_num: {job_num}, report_id: {report_id}' )

        try:
            query = 'SELECT status FROM reports WHERE job_num=? AND report_id=?'

            results = self.db.query(query, (job_num, report_id))
            return results[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def get_limited_reports(self, limit:int, offset:int):
        logger.info(f'Entering ReportsManager get_limited_reports with limit: {limit}, offset: {offset}')

        try:
            query = '''
                SELECT job_num, report_id, param_id, dilution, creation_date, status
                FROM reports
                ORDER BY creation_date DESC
                LIMIT ? OFFSET ?

            '''
            results = self.db.query(query, (limit, offset, ))

            return results

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def get_total_reports_count(self):
        logger.info('Entering ReportsManager get_total_reports_count')

        try:
            query = '''
                SELECT count(job_num)
                FROM reports
            '''
            results = self.db.query(query)
            return results[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return 0

    def get_all_job_nums(self):

        logger.info('Entering ReportsManager get_all_job_nums')

        try:
            query = 'SELECT DISTINCT job_num FROM reports'
            self.db.execute(query)

            job_nums = self.db.fetchall()
            return  [item[0] for item in job_nums]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return []


    def search_reports(self, search_value:str):
        logger.info(f'Entering search_reports with search_value: {search_value}')

        try:
            query = 'SELECT * FROM reports WHERE job_num LIKE ? ORDER BY creation_date DESC'
            results = list(self.db.query(query, (search_value + '%',)))
            return results

        except Exception as e:
            logger.error(f"An error occurred during the database query: {e}")
            return None

    def search_limited_reports(self, limit:int, offset:int, search_value:str):
        logger.info(f'Entering search_limited_reports with limit: {limit}, offset: {offset}, search_value: {search_value}')

        try:
            query = """
                SELECT job_num, report_id, param_id, dilution, creation_date, status
                FROM reports
                WHERE job_num LIKE ?
                ORDER BY creation_date DESC
                LIMIT ? OFFSET ?
            """

            # Add wildcards to the search term for partial matching
            search_term = f"{search_value}%"

            # Execute the query with the search term and pagination parameters
            results = self.db.query(query, (search_term, limit, offset))

            return results

        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error during job count: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred during job count: {e}")
            return None


    def search_reports_count(self, search_value:str):
        logger.info(f'Entering search_reports_count with search_value: {search_value}')

        try:
            query = """
                SELECT count(job_num)
                FROM reports
                WHERE job_num LIKE ?
            """

            # Add wildcards to the search term for partial matching
            search_term = f"{search_value}%"

            # Execute the query with the search term and pagination parameters
            results = self.db.query(query, (search_term, ))

            return results[0][0]

        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error during reports count: {e}")
            return None

        except Exception as e: # Catch other exceptions
            logger.error(f"An unexpected error occurred during reports count: {e}")
            return None