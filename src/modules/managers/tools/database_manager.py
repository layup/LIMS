import os
import psycopg2
import psycopg2.pool
import sqlite3


from base_logger import logger
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread


from base_logger import logger

class DatabaseManager(QThread):
    connection_established = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def get_connection(self):
        raise NotImplementedError

    def put_connection(self, conn):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def fetchall(self):
        raise NotImplementedError

    def fetchone(self):
        raise NotImplementedError

    def query(self):
        raise NotImplementedError

class SqLiteManager(DatabaseManager):

    def __init__(self, path):
        super().__init__()
        self.path = path

        self._conn = None
        self._cursor = None

    # creates a method that can be accessed like an  attribute
    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    # method contains the code that you want to be executed in the separate thread
    def run(self):
        logger.info(f'sqlite3 connecting to {self.path}')

        error_status =  self.error_check()

        if(not error_status):
            return

        try:
            # Attempt to connect (might still succeed even if it's not a valid database)
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
            self._cursor = self._conn.cursor()

            # Immediately test the connection
            self._cursor.execute("SELECT * from authors")
            self._conn.commit()
            self.connection_established.emit(True)
            logger.debug(f'Connection to local database at {self.path} established')

        except sqlite3.Error as e:
            logger.error(f'Local database connection error: {e}')

            self._conn.close()
            self._conn = None
            self.connection_established.emit(False)
            self.error_occurred.emit(f'Error connecting: {str(e)}')
            return

    def error_check(self):
        file_name, file_extension = os.path.splitext(self.path)

        if(file_extension.lower() == '.db'):
            return True

        self.error_occurred.emit('Invalid file type for local database, please try again')
        return False

    def get_connection(self):
        return self.conn

    def put_connection(self, conn):
        pass # No need to put back for sqlite single connectio

    # when you are enter the with block
    def __enter__(self):
        logger.debug("Entering SqLiteManager")
        return self

    # when you exit the with block
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Exiting SqLiteManager")
        self.close()

    def close(self, commit=True):
        if commit:
            self.commit()

        if self.connection:
            self.connection.close()

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        #self.logger.debug(f"Executing SQL: {sql} with params: {params}")
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        try:
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database error fetching all: {e}")
            raise

    def fetchone(self):
        try:
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Database error fetching one: {e}")
            raise

    def query(self, sql, params=None):
        try:
            #logger.debug(f"Querying SQL: {sql} with params: {params}")
            self.cursor.execute(sql, params or ())
            return self.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database error during query: {e}")
            raise


class PostgresManager(DatabaseManager):

    def __init__(self, connection_params, min_conn=1, max_conn=4):
        super().__init__()
        self.running = True
        self.connection_params = connection_params
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.pool = None

    def run(self): # Establish connection pool in thread's run method

        error_status = self.error_check()

        if(not error_status):
            return

        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(self.min_conn, self.max_conn, **self.connection_params)
            self.connection_established.emit(True)
        except psycopg2.Error as e:
            self.error_occurred.emit(str(e)) # Emit the error message
            self.connection_established.emit(False)
            return

    def error_check(self):

        # check that all of the postgreSql information is valid
        for key, value in self.connection_params.items():
            if(value == ''):
                self.error_occurred.emit('Please fill in all the PostgreSQL Server Information')
                return False
        return True

    def get_connection(self):
        if self.pool:
            return self.pool.getconn()
        return None

    def put_connection(self, conn):
        if self.pool and conn:
            self.pool.putconn(conn)

    def close(self):
        if self.pool:
            self.pool.closeall()

    def stop(self):
        self.running = False

    def commit(self):
        conn = self.get_connection() # Get connection to commit
        if conn:
            try:
                conn.commit()
            except psycopg2.Error as e:
                logger.error(f"Database commit error: {e}")
                raise
            finally:
                self.put_connection(conn) # Return the connection

    def execute(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
        except psycopg2.Error as e:
            logger.error(f"Database execute error: {e} (SQL: {sql}, Params: {params})")
            raise

    def fetchall(self):
        try:
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Database fetchall error: {e}")
            raise

    def fetchone(self):
        try:
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            logger.error(f"Database fetchone error: {e}")
            raise

    def query(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            return self.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e} (SQL: {sql}, Params: {params})")
            raise