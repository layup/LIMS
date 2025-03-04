import time
import psycopg2

from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

from base_logger import logger

class ServerManager(QThread):
    connection_established = pyqtSignal(bool)  # Signal for connection status
    query_finished = pyqtSignal(list)        # Signal for query results
    error_occurred = pyqtSignal(str)          # Signal for errors

    def __init__(self, host, dbname, port, user, password, min_conn=1, max_conn=4, max_workers=4):
        super().__init__()
        self.host = host
        self.dbname = dbname
        self.port = port
        self.user = user
        self.password = password

        self.min_conn = min_conn
        self.max_conn = max_conn
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.conn = None

    # code that you want to be executed in the background thread.  It's the main function of the thread.
    # This is where the thread starts
    def run(self):
        self.connect()

    def connect(self):
        try:
            future = self.executor.submit(self._connect_to_server)
            success = future.result() # This will block until the connection is established
            self.connection_established.emit(success)

        except Exception as e:
            self.error_occurred.emit(str(e))

    # A leading single underscore is a convention in Python to indicate that a variable or function
    # is intended for internal use within a module or class.  It's a signal to other developers that
    # they should not directly access or modify these members from outside the module or class.

    def _connect_to_server(self, max_retries=3): # The actual connection function
        for attempt in range(max_retries):
            logger.debug(f'Attempt {attempt} to connect to {self.host}')
            try:
                self.conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
                logger.debug(f"Connected to {self.host} successfully!")
                return True

            except psycopg2.Error as e:
                logger.debug(f"Connection attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    wait_time = 1 ** attempt  # Exponential backoff (1s, 2s, 4s...)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to connect after {max_retries} attempts.")
                    return False  # Indicate failure

            except Exception as error:
                logger.error(f"Error connecting to database: {error}")
                return False

    def execute_query(self, sql, params=None):
        # Method to execute queries
        try:
            future = self.executor.submit(self._execute_in_thread, sql, params)
            result = future.result()
            self.query_finished.emit(result)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _execute_in_thread(self, sql, params=None):
         # Function to execute in background thread
        if self.conn is None:
            raise Exception("No connection available. Call connect() first.")
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        return cursor.fetchall()  # Or fetchone(), depending on your needs

    def close(self):
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed.")
        # Shutdown thread pool
        self.executor.shutdown()


class PostgresDatabaseManager:
    def __init__(self, host, dbname, port, user, password):

        # Initialize connection to None
        self.conn = None
        self._cursor = None

        self.db_thread = ServerManager(host, dbname, port, user, password)

        # connect signals
        self.db_thread.connection_established.connect(self._handle_connection_status)
        self.db_thread.query_finished.connect(self._handle_query_result)
        self.db_thread.error_occurred.connect(self._handle_error)

    def __enter__(self):
        logger.debug("Entering database context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Exiting database context manager")
        self.close()

    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        return self._cursor

    def connect(self):
        self.db_thread.start()

    def _handle_connection_status(self, success):
        if success:
            logger.info("Database connection established.")
            self.conn = self.db_thread.conn
            self._cursor = self.conn.cursor()
        else:
            logger.error("Database connection failed.")

    def _handle_query_result(self, result):
        # Process the result here (e.g., update UI)
        logger.info(f"Query result: {result}")
        # ... your code to use the query results ...




    def _handle_error(self, error_message):
        logger.error(f"Database error: {error_message}")


    def commit(self):
        if self.conn: # Check if connection exists
            self.conn.commit()
        else:
            logger.error("No connection available to commit.")


    def close(self, commit=True):
        if self.conn: # Check if connection exists
            if commit:
                self.commit()
            self.db_thread.close() # Close thread and connection
            self.conn = None # Reset
            self._cursor = None
        else:
            logger.warn("Close called but no connection was available.")

    def execute(self, sql, params=None):
        if self.conn is None:
            logger.error("Not connected to the database.")
            return

        self.db_thread.execute_query(sql, params)

    def fetchall(self):
        if self._cursor:
            try:
                return self._cursor.fetchall()
            except psycopg2.Error as e:
                logger.error(f"Database error fetching all: {e}")
                raise
        else:
            logger.error("No cursor available.")
            return None # Or raise an exception, as you prefer

    def fetchone(self):
        if self._cursor:
            try:
                return self._cursor.fetchone()
            except psycopg2.Error as e:
                logger.error(f"Database error fetching one: {e}")
                raise
        else:
            logger.error("No cursor available.")
            return None

    def query(self, sql, params=None):
        if self._cursor:
            try:
                self._cursor.execute(sql, params or ())
                return self.fetchall()
            except psycopg2.Error as e:
                logger.error(f"Database error during query: {e}")
                raise
        else:
            logger.error("No cursor available.")
            return None