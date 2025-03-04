import sqlite3

from datetime import date
from base_logger import logger


class SamplesItem:

    def __init__(self, sample_num, sample_name, sample_time, sample_date, total_containers, container_type):
        self.sample_num = sample_num
        self.sample_name = sample_name
        self.sample_time = sample_time
        self.sample_date = sample_date

        self.total_containers = total_containers
        self.container_type = container_type

        self.macros_id = []
        self.test_ids = []



class JobItem:

    def __init__(self, job_num, company_name, total_samples, creation_date, status):
        self.job_num = job_num
        self.company_name = company_name
        self.creation_date = creation_date
        self.status = status

        self.total_samples = total_samples

        self.company_id = None

        keys = ["company_name", "attn", "addr_1", "addr_2", "city", "country", "prov", "postal", "phone", "ext", "fax", "email"]
        self.company_info = {key: "" for key in keys}

        self.samples = {}

    def add_company(self, company_id):
        self.company_id = company_id

    def add_samples(self):
        pass

    def clear_info(self):
        pass;



class JobManager:

    def __init__(self, db):
        self.db = db

        self.current_job = None

    def add_jobs(self, job_num: int, company_name:str, total_samples:int) -> bool:
        logger.info('Entering JobManager add_job')

        try:
            current_date = date.today()
            status = 0

            query = 'INSERT INTO jobs (job_num, company_name, total_samples, status, creation_date values (?,?,?,?,?)'
            self.db.execute(query, (job_num, company_name, total_samples, status, current_date))
            self.db.commit()

            logger.info(f"Job {job_num} added successfully.")  # More informative logging
            return True

        except sqlite3.IntegrityError as e: # Handle IntegrityErrors (e.g., unique constraints)
            logger.warning(f"Integrity error adding job {job_num}: {e}")
            return False

        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error adding job {job_num}: {e}") # Log as error
            return False

        except Exception as e:  # Catch any other exceptions
            logger.error(f"An unexpected error occurred adding job {job_num}: {e}")
            return False

    def update_jobs(self, job_num:int, company_name: str, total_samples: int, status:int, creation_date:int) -> bool:

        try:
            query = 'UPDATE jobs SET company_name = ?, total_samples = ?, status = ?, creation_date =?  WHERE job_num = ?'
            self.db.execute(query, (company_name, total_samples, status, creation_date, job_num))
            self.db.commit()

            if(self.db.cursor.rowcount > 0):
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s) in jobs.")
                return True

            logger.info("No rows were updated.")
            return False

        except Exception as e:
            logger.error(f'An unexpected error occurred when updating job {job_num}: {e}')
            return False

    def delete_job(self, job_num: int) -> int:

        try:
            query = 'DELETE FROM jobs WHERE job_num = ?'
            self.db.execute(query, (job_num))
            self.db.commit()

            # Check how many rows were deleted
            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows
            if deleted_rows > 0:
                logger.info(f"Successfully deleted {deleted_rows} row(s) from jobs.")

                return deleted_rows

            return 0

        except Exception as e:
            logger.error(f'An unexpected error occurred when trying to delete job: {job_num}: {e}')
            return 0

    def update_status(self, job_num , new_status) -> bool:
        try:
            query = 'UPDATE jobs SET status = ? WHERE job_num = ?'
            self.db.execute(query, (new_status, job_num))
            self.db.commit()

            if self.db.cursor.rowcount > 0:
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s).")
                return True
            else:
                logger.info("No rows were updated.")
                return False

        except sqlite3.IntegrityError as e: # Handle IntegrityErrors (e.g., unique constraints)
            logger.warning(f"Integrity error updating status for job {job_num}: {e}")
            return False
        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error updating status for job {job_num}: {e}") # Log as error
            return False
        except Exception as e:  # Catch any other exceptions
            logger.error(f"An unexpected error occurred updating status for job {job_num}: {e}")
            return False

    def get_status(self, job_num:int):
        logger.info(f'Entering JobManager get_status with job_num: {job_num}')

        try:
            query = 'SELECT status FROM jobs WHERE job_num = ?'
            result = self.db.query(query, (job_num))
            return result[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def get_all_jobs(self):
        logger.info('Entering JobManager get_all_jobs')

        try:
            query = 'SELECT job_num FROM jobs'
            self.db.execute(query)

            jobNumbers = self.db.fetchall()
            return  [item[0] for item in jobNumbers]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return []

    def get_total_jobs_count(self):
        logger.info('Entering JobManager get_total_jobs_count')
        try:
            query = '''
                SELECT count(job_num)
                FROM jobs
            '''
            results = self.db.query(query)
            return results[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return 0

    def search_job(self, search_value):
        logger.info(f'Entering search_job with search_value: {search_value}')

        try:
            query = 'SELECT job_num, company_name, creation_date, total_samples, status FROM jobs WHERE job_num LIKE ? ORDER BY creation_date DESC'
            results = list(self.db.query(query, (search_value + '%',)))
            return results

        except Exception as e:
            logger.error(f"An error occurred during the database query: {e}")
            return None

    def search_limited_jobs(self, limit, offset, search_value):
        logger.info(f'Entering search_limited_jobs with limit: {limit}, offset: {offset}, search_value: {search_value}')

        try:
            query = """
                SELECT job_num, reportNum, parameterNum, dilution, creation_date, status
                FROM jobs
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


    def search_jobs_count(self, search_value):
        logger.info(f'Entering search_jobs_count with search_value: {search_value}')

        try:
            query = """
                SELECT count(job_num)
                FROM jobs
                WHERE job_num LIKE ?
            """

            # Add wildcards to the search term for partial matching
            search_term = f"{search_value}%"

            # Execute the query with the search term and pagination parameters
            results = self.db.query(query, (search_term, ))

            return results[0][0]

        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error during job count: {e}")
            return None

        except Exception as e: # Catch other exceptions
            logger.error(f"An unexpected error occurred during job count: {e}")
            return None


