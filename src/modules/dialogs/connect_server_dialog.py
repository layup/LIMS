import os
import time

from base_logger import logger
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi

from modules.dialogs.basic_dialogs import  okay_dialog
from modules.utils.file_utils import openFile

from modules.managers.tools.database_manager import SqLiteManager, PostgresManager, DatabaseManager

class ConnectServerDialog(QDialog):

    login_accepted = pyqtSignal(DatabaseManager)  # Emit the DatabaseManager instance

    def __init__(self, preferences):
        super().__init__()

        self.preferences = preferences
        self.temp_paths = self.preferences.paths.copy()

        self.db_manager = None

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'connect_server.ui')
        loadUi(file_path, self)

        self.init_setup()

    def init_setup(self):

        # set the window name
        self.setWindowTitle("Connect to PostgreSQL Server")

        # set the default to local db
        self.connection_type.setCurrentIndex(0)
        self.postgreSQL_box.setVisible(False)

        # load both the postgreSQL server and local db information
        self.load_post_server_info()
        self.load_local_db_info()

        # connect the signals
        self.connect_btn.clicked.connect(self.handle_connect_btn)
        self.cancel_btn.clicked.connect(self.handle_cancel_btn)
        self.browse_btn.clicked.connect(self.handle_browse_btn)
        self.connection_type.currentIndexChanged.connect(self.handle_drop_down_changed)

    def load_post_server_info(self):
        logger.info('Entering load_post_server_info')

        # load the .env saved info
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
            print(f'Exception when loading .env information: {e}')

    def load_local_db_info(self):
        logger.info('Entering load_local_db_info')

        try:
            db_path = self.preferences.get_path('temp_backend_path')
            self.lineEdit.setText(db_path)

        except Exception as e:
            print(f'Exception when loading preferences information: {e}')

    def get_server_info(self):
        logger.info('Entering get_server_info')

        server = self.server.text()
        port = self.port.text()
        db = self.database.text()
        username = self.username.text()
        password = self.password.text()

        return [server, port, db, username, password]

    def handle_drop_down_changed(self, index):
        logger.info(f'Entering handle_drop_down_changed index:{index}')

        self.message.setText('')

        if(self.db_manager and self.db_manager.isRunning()):
            okay_dialog('Currently trying to establish a connection', 'Please wait a moment')
            return


        if(index == 0):
            self.postgreSQL_box.setVisible(False)
            self.local_box.setVisible(True)
            return

        self.postgreSQL_box.setVisible(True)
        self.local_box.setVisible(False)

    def handle_browse_btn(self):
        logger.info('Entering handle_browse_btn')

        file_location = openFile()
        print(f'file_location: {file_location}')

        if(file_location):

            self.temp_paths['temp_backend_path'] = file_location
            self.lineEdit.setText(file_location)

    def handle_connect_btn(self, wait_time=2):
        logger.info('Entering handle_connect_btn')

        # Local connection or postgreSQL connection selected
        current_index = self.connection_type.currentIndex()

        self.message.setText('')

        if(current_index == 0):

            # update the database path
            self.preferences.update_paths(self.temp_paths)

            file_path = self.preferences.get_path('temp_backend_path')
            file_name = os.path.basename(file_path)

            self.message.setText(f'Attempting to local server {file_name} ...')

            self.db_manager = SqLiteManager(file_path)

        elif(current_index == 1):

            server, port, db, username, password = self.get_server_info()

            db_params = { # Server db parameters
                "host": server,
                "database": db,
                "user": username,
                "password": password,
                "port": port
            }

            self.message.setText(f'Attempting to connect to postgres host {server}...')

            self.db_manager = PostgresManager(db_params)

        # test the db_manager connection to see if it works
        self.db_manager.connection_established.connect(lambda success: self.handle_connection_result(self.db_manager, success)) # Connect to result
        self.db_manager.error_occurred.connect(self.handle_connection_error)

        # when finished signal of the QTread emits
        #self.db_manager.finished.connect(self.on_connection_finished)

        # Start connection in thread
        time.sleep(wait_time)
        self.db_manager.start()

    def handle_cancel_btn(self):
        logger.info('Entering handle_cancel_btn')

        self.close() # close the dialog


        if self.db_manager and self.db_manager.isRunning():  # Stop the thread if it is running
            self.db_manager.stop()  # Tell the thread to stop
            self.db_manager.wait()  # Wait for the thread to actually finish
            self.db_manager = None  # Now it's safe to reset

    def handle_connection_result(self, db_manager, success):
        logger.info(f'Entering handle_connection_result with db_manager:{db_manager},  success: {success}')

        if success and db_manager:
            self.login_accepted.emit(db_manager)  # Emit the db_manager
            self.accept()  # Close the dialog


        else:
            #self.message.setText("Failed to connect to the database.")
            QMessageBox.critical(self, "Connection Error", "Failed to connect to the database.")
            self.db_manager = None

    def on_connection_finished(self):
        # Reset the db_manager after connection is finished (success or failure)
        self.db_manager = None  # Allow a new connection to be started
        logger.info("Connection attempt finished.")

    def handle_connection_error(self, error_message):
        logger.error(f'{error_message}')

        self.message.setText(error_message)