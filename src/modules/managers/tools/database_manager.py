import sqlite3
import psycopg2
import time

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


class PostgresDatabaseManager:
    """
    Base class for database management.
    """
    def __init__(self, host, dbname, port, user, password):

        #login info
        self.host = host
        self.dbname = dbname
        self.port = port
        self.user = user
        self.password = password

        self._conn = None
        self.__cursor = None

        self.connect_to_server()

    def __enter__(self):
        logger.debug("Entering database context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Exiting database context manager")
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def test_connection(self):
        logger.info('Entering handle_test_btn')

        if(self._conn):

            try:
                self._cursor.execute("SELECT 1;")
                result = self._cursor.fetchone()
                logger.info(f"Connection successful! Result: {result}")
                return True

            except psycopg2.Error as e:
                logger.debug(f"Connection failed: {e}")

                return False

        return False

    def connect_to_server(self, max_retries=3):
        logger.info('Entering connect_to_postgres')

        for attempt in range(max_retries):
            logger.debug(f'Attempt {attempt} to connect to {self.host}')

        try:
            self._conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            #self._conn.autocommit = True
            self._cursor = self._conn.cursor()

            logger.debug(f"Connected to {self.host} successfully!")

        except psycopg2.Error as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff (1s, 2s, 4s...)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

        except Exception as error:
            logger.error(f"Error connecting to database: {error}")



    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()
        logger.debug("Database connection closed.")

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
