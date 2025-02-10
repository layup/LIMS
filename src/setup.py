__author__ = "Tommy Lay"
__version__ = "0.1.0"
__license__ = "MIT"

import sys

from dotenv import find_dotenv, load_dotenv

from app import MainWindow
from base_logger import logger

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QStyleFactory, QDialog

from modules.widgets.SplashScreenWidget import SplashScreen
from modules.dialogs.connect_server_dialog import ConnectServerDialog

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    print(f'Qt hasattr AA_EnableHighDpiScaling')
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    print(f'Qt hasattr AA_UseHighDpiPixmaps')
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def setup_logging():
    """Set up the logging configuration."""

    logger_level_meaning = {
        10: 'DEBUG',
        20: 'INFO',
        30: 'WARNING',
        40: 'ERROR',
        50: 'CRITICAL'
    }

    print('*Starting Program')
    print(f'*Logging Level: {logger_level_meaning[logger.level]}')
    print(f"*Logger Propagation: {logger.propagate}")

    logger.info('Display Settings')
    logger.info(f"Using AA_EnableHighDpiScaling : {QApplication.testAttribute(Qt.AA_EnableHighDpiScaling)}")
    logger.info(f"Using AA_UseHighDpiPixmaps    : {QApplication.testAttribute(Qt.AA_UseHighDpiPixmaps)}")

def setup_env_files():

    # find the .env path
    dotenv_path = find_dotenv()

    # load the .env file into
    load_dotenv(dotenv_path)

def connect_to_server():

    server_dialog = ConnectServerDialog()
    results = server_dialog.exec_()

    if results ==  QDialog.Accepted:

        return True

    elif results == QDialog.Rejected:
        #TODO: temp has this so server is doing the thing
        return True

def screen_resolution_adjust(app):

    # set the style for it
    app.setStyle(QStyleFactory.create('Fusion'))

    # Get the screen size
    screen = app.primaryScreen()
    screen_size = screen.size()
    width, height = screen_size.width(), screen_size.height()

    # Set font size based on screen resolution
    font_size = 10  # Default font size
    if width <= 1280:
        font_size = 10  # Smaller font for lower resolution
    elif width >= 1920:
        font_size = 13  # Larger font for high resolution

    # set the default font and font size for the whole application
    font = QFont("Arial", font_size)

    app.setFont(font)

if __name__ == "__main__":

    # connect the logger
    setup_logging()

    # connect the .env file
    setup_env_files()

    app = QApplication(sys.argv)
    screen_resolution_adjust(app)

    connection_status = connect_to_server()

    if(connection_status):
        splash = SplashScreen()
        splash.show()

        def show_main_window():
            # Create and show the main window
            window = MainWindow(logger)
            window.show()

            # Finish the splash screen
            splash.finish(window)

        QTimer.singleShot(1000, lambda: show_main_window())


    else:
        sys.exit(1)

    sys.exit(app.exec_())