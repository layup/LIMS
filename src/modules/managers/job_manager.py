import sqlite3

from datetime import date
from base_logger import logger

'''

    jobs (front intake)
    - job_num (pk)
    - company_id
    - company_info
    - creation_date
    - total_samples
    - sample_names
    - status

    reports (general information )
    - job_num (PK)
    - report_id (PK)
    - matrix_id
    - dilution
    - creation_date
    - author_one_id
    - author_two_id

    icp_upload
    - job_num (PK)
    - sample_num (PK)
    - file_name
    - upload_date
    - machine_id

    icp_data
    - sample_num (PK)
    - element_id (PK)
    - element_val

    chm_data
    - job_num
    - sample_num (PK)
    - test_id (PK)
    - test_val
    - standard_val
    - unit_val
    -

'''


'''

CREATE TABLE reports (
    job_num INTEGER NOT NULL,       -- Primary Key (TEXT if it's not always a number)
    report_id INTEGER NOT NULL,    -- Primary Key (INTEGER for auto-incrementing if needed)
    matrix_id INTEGER,             -- Can be NULL if not applicable
    dilution REAL,              -- Or appropriate data type (INTEGER, TEXT, etc.)
    creation_date TEXT,          -- Or DATE, DATETIME, etc. - choose a consistent format
    author_one_id INTEGER,       -- Or TEXT, depending on how you identify authors
    author_two_id INTEGER,       -- Or TEXT, depending on how you identify authors
    PRIMARY KEY (job_num, report_id) -- Composite primary key
    FOREIGN KEY (report_id) REFERENCES report_type(report_id)
);

CREATE TABLE icp_upload (
    job_num INTEGER,
    report_id INTEGER,
    matrix_id INTEGER,
    dilution REAL,
    creation_date TEXT,
    author_one_id INTEGER,
    author_two_id INTEGER,
    PRIMARY KEY (job_num, report_id)

);

'''


class JobManager:

    def __init__(self, db):
        self.db = db

    def add_job(self, job_num, report_id, matrix_id, dilution, status ):
        logger.info('Entering JobManager add_job')

        try:
            current_date = date.today()
            query = 'INSERT INTO jobs (jobNum, reportNum, parameterNum, status, creation_date, dilution) values (?,?,?, ?,?,?)'
            self.db.execute(query, (job_num, report_id, matrix_id, status, current_date, dilution))
            self.db.commit()

            logger.info(f"Job {job_num} added successfully.")  # More informative logging
            return True

        except sqlite3.IntegrityError as e: # Handle IntegrityErrors (e.g., unique constraints)
            logger.warning(f"Integrity error adding job {job_num}: {e}")
            self.db.rollback() # Rollback on error.
            return False
        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error adding job {job_num}: {e}") # Log as error
            self.db.rollback()  # Rollback on error
            return False
        except Exception as e:  # Catch any other exceptions
            logger.error(f"An unexpected error occurred adding job {job_num}: {e}")
            self.db.rollback()  # Rollback on error
            return False

    def update_job(self, job_num, report_id, matrix_id, dilution, status):
        logger.info('Entering JobManager update_job')

        try:
            current_date = date.today()
            query = 'UPDATE jobs SET status = ?, creation_date = ?, dilution = ? WHERE jobNum = ? AND reportNum = ? AND parameter = ?'
            self.db.execute(query, (status, current_date, dilution, job_num, report_id, matrix_id))
            self.db.commit()

            if self.db.cursor.rowcount > 0:
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s).")

                return True
            else:
                logger.info("No rows were updated.")

                return False

        except sqlite3.IntegrityError as e: # Handle IntegrityErrors (e.g., unique constraints)
            logger.warning(f"Integrity error adding job {job_num}: {e}")
            self.db.rollback() # Rollback on error.
            return False
        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error adding job {job_num}: {e}") # Log as error
            self.db.rollback()  # Rollback on error
            return False
        except Exception as e:  # Catch any other exceptions
            logger.error(f"An unexpected error occurred adding job {job_num}: {e}")
            self.db.rollback()  # Rollback on error
            return False

    def remove_job(self):
        pass


    def update_status(self, job_num, report_id, new_status):
        try:
            query = 'UPDATE jobs SET status = ? WHERE jobNum = ? AND reportNum = ?'
            self.db.execute(query, (new_status, job_num, report_id))
            self.db.commit()

            if self.db.cursor.rowcount > 0:
                logger.info(f"Successfully updated {self.db.cursor.rowcount} row(s).")
                return True
            else:
                logger.info("No rows were updated.")
                return False

        except sqlite3.IntegrityError as e: # Handle IntegrityErrors (e.g., unique constraints)
            logger.warning(f"Integrity error updating status for job {job_num}: {e}")
            self.db.rollback() # Rollback on error.
            return False
        except sqlite3.Error as e:  # Catch SQLite errors specifically
            logger.error(f"Database error updating status for job {job_num}: {e}") # Log as error
            self.db.rollback()  # Rollback on error
            return False
        except Exception as e:  # Catch any other exceptions
            logger.error(f"An unexpected error occurred updating status for job {job_num}: {e}")
            self.db.rollback()  # Rollback on error
            return False

    def get_status(self, job_num, report_id):
        logger.info(f'Entering JobManager get_status with job_num: {job_num}, report_id: {report_id}')

        try:
            query = 'SELECT status FROM jobs WHERE jobNum = ? and reportNum = ?'
            result = self.db.query(query, (job_num, report_id))
            return result[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def get_limited_jobs(self, limit, offset):
        logger.info(f'Entering get_limited_jobs with limit: {limit}, offset: {offset}')

        try:
            query = '''
                SELECT jobNum, reportNum, parameterNum, dilution, creation_date, status
                FROM jobs
                ORDER BY creation_date DESC
                LIMIT ? OFFSET ?

            '''
            results = self.db.query(query, (limit, offset, ))

            return results

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None


    def get_all_jobs(self):
        logger.info('Entering JobManager get_all_jobs')

        try:
            query = 'SELECT DISTINCT jobNum FROM jobs'
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
                SELECT count(jobNum)
                FROM jobs
            '''
            results = self.db.query(query)
            return results[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return 0

    def get_job_status(self, job_num, report_id):
        logger.info(f'Entering JobManager get_job_status with job_num: {job_num}, report_id: {report_id}')

        try:
            query = 'SELECT status FROM jobs WHERE jobNum = ? and reportNum = ?'
            result = self.db.query(query, (job_num, report_id))
            return result[0][0]

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def check_job_exist(self, job_num, report_id):
        logger.info(f'Entering check_job_exist with job_num: {job_num}, report_id: {report_id}')

        try:
            query = 'SELECT * FROM jobs WHERE jobNum = ? and reportNum = ?'
            self.db.execute(query, (job_num, report_id))
            result = self.db.fetchone()
            return result

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            return None

    def search_job(self, search_value):
        logger.info(f'Entering search_job with search_value: {search_value}')

        try:
            query = 'SELECT * FROM jobs WHERE jobNum LIKE ? ORDER BY creation_date DESC'
            results = list(self.db.query(query, (search_value + '%',)))
            return results
        except Exception as e:
            logger.error(f"An error occurred during the database query: {e}")
            return None

    def search_limited_jobs(self, limit, offset, search_value):
        logger.info(f'Entering search_limited_jobs with limit: {limit}, offset: {offset}, search_value: {search_value}')

        try:
            query = """
                SELECT jobNum, reportNum, parameterNum, dilution, creation_date, status
                FROM jobs
                WHERE jobNum LIKE ?
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
                SELECT count(jobNum)
                FROM jobs
                WHERE jobNum LIKE ?
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


