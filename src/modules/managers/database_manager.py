import sqlite3
import psycopg2


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



class PostgresDatabaseManager:
    """
    Base class for database management.
    """
    def __init__(self, host, database, user, password):
        self.logger = logger
        self.logger.debug(f"Connecting to database: {database}")
        try:
            self._conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            self._conn.autocommit = True
            self._cursor = self._conn.cursor()
            self.logger.debug(f"Connected to database: {database}")
        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Error connecting to database: {error}")
            raise

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
        self.logger.debug("Database connection closed.")

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

def connect_to_postgres(host, database, user, password):
    """
    Connects to a PostgreSQL database.

    Args:
    host: The hostname of the PostgreSQL server.
    database: The name of the database to connect to.
    user: The username to use for authentication.
    password: The password for the user.

    Returns:
    A connection object to the PostgreSQL database.

    Raises:
    Exception: If an error occurs during the connection process.
    """

    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        conn.autocommit = True  # Autocommit changes to the database
        return conn

    except (Exception) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None
