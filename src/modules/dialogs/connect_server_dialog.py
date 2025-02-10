import os
import time
import psycopg2

from dotenv import load_dotenv, dotenv_values

from base_logger import logger
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi



from modules.utils.file_utils import update_env_file


class ConnectServerDialog(QDialog):

    server_info = pyqtSignal()

    def __init__(self):
        super().__init__()

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'connect_server.ui')
        loadUi(file_path, self)

        self.init_setup()

    def init_setup(self):

        # set the window name
        self.setWindowTitle("Connect to PostgreSQL Server")

        # load the .env saved info
        self.load_server_info()

        # connect the signals
        self.connect_btn.clicked.connect(self.handle_connect_btn)
        self.cancel_btn.clicked.connect(self.handle_cancel_btn)

    def load_server_info(self):

        try:
            # access the values
            HOST = os.getenv('HOST')
            PORT = os.getenv('PORT')
            DATABASE = os.getenv('DATABASE')
            USERNAME = os.getenv('USERNAME')
            PASSWORD = os.getenv('PASSWORD')

            # set the user information
            self.server.setText(HOST)
            self.port.setText(PORT)
            self.database.setText(DATABASE)
            self.username.setText(USERNAME)
            self.password.setText(PASSWORD)

        except Exception as e:
            print(f'Exception: {e}')

    def get_server_info(self):
        logger.info('Entering get_server_info')

        server = self.server.text()
        port = self.port.text()
        db = self.database.text()
        username = self.username.text()
        password = self.password.text()

        return server, port, db, username, password

    def test_connection(self, max_retries=1):
        logger.info('Entering test_connection')

        host, port, db, username, password = self.get_server_info()

        for attempt in range(max_retries):
            try:
                # with statement guarantees that the __exit__ method of the context manager is called
                with psycopg2.connect(
                    dbname=db,
                    user=username,
                    password=password,
                    host=host,
                    port=port,
                ) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1;")
                        result = cur.fetchone()
                        print(f"Connection successful! Result: {result}")
                        return True

            except psycopg2.Error as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff (1s, 2s, 4s...)
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return False

    def handle_connect_btn(self):
        logger.info('Entering handle_connect_btn')

        host = self.server.text()

        self.message.setText(f'Attempting to connect to {host}')

        connection_status = self.test_connection()

        if(connection_status):
            self.message.setText(f'Connection to {host} successful!')

            time.sleep(2)
            self.accept()

        self.message.setText(f'Connection to {host} failed!')

    def handle_cancel_btn(self):
        logger.info('Entering handle_cancel_btn')

        self.close() # close the dialog


