import sqlite3

from base_logger import logger

class DatabaseManager:

    def __init__(self, path):
        self.logger = logger
        self.logger.debug(f"Creating Database instance with path: {path}")
        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        self.logger.debug("Entering database context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Exiting database context manager")
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        #self.logger.debug(f"Executing SQL: {sql} with params: {params}")
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        #self.logger.debug(f"Query SQL: {sql} with params: {params}")
        self.cursor.execute(sql, params or ())
        return self.fetchall()


