import os
import pickle

from assets import resource_rc
from PyQt5.QtCore import pyqtSlot, QTimer, QDateTime
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTableWidget, QStyleFactory, QLabel, QMessageBox)

from modules.constants import REPORTS_TYPE
from modules.dbFunctions import getAllParameters
from modules.utils.apply_drop_shadow_effect import apply_drop_shadow_effect
from modules.utils.file_utils import openFile
from modules.dialogs.FileLocationDialog import FileLocationDialog

from interface import *

# Page setup imports
#from pages.reports_page.create_report_page import reportSetup
from pages.reports_page.reports_config import general_reports_setup
from pages.reports_page.reports.report_utils import deleteAllSampleWidgets
from pages.icp_page.icp_page_config import  icpSetup, on_icpTabWidget_currentChanged
from pages.chm_page.chm_page_config import chemistrySetup, on_chmTabWidget_currentChanged
from pages.settings_page.settings_page_config import settingsSetup
from pages.history_page.history_page_config import history_page_setup, set_total_outgoing_jobs

from modules.managers.client_info_manager import ClientInfoManager
from modules.managers.status_manager import StatusBarManager
from modules.managers.database_manager import DatabaseManager

#TODO: include yaml for config and file locations

class MainWindow(QMainWindow):

    def __init__(self,logger):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.logger = logger

        self.ui.setupUi(self)

        self.status_bar_manager = StatusBarManager(self.ui.statusbar)
        self.client_manager = ClientInfoManager(self.ui.reportsUserInfoWidget)

        # load the setup
        self.loadDatabase()
        self.loadStartup()

        # load signal connections
        self.connect_navigation_buttons()
        self.connect_client_info_signals()

    def closeEvent(self, event):
        """Override this method to handle the close event."""
        reply = QMessageBox.question(self, 'Exit Confirmation',
                                        "Are you sure you want to exit?",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Close the database connections
            self.db.close()
            self.tempDB.close()
            self.officeDB.close()

            event.accept()  # Allow the window to close
        else:
            event.ignore()  # Prevent the window from closing

    #******************************************************************
    #    Setup Loading
    #******************************************************************

    def loadStartup(self):
        self.logger.info("Entering loadStartup function")

        # Set the title and style
        self.setWindowTitle("Laboratory Information management System")
        self.setStyle(QStyleFactory.create('Fusion'))

        # Set the current working directory to the directory containing the script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        apply_drop_shadow_effect(self.ui.headerWidget)
        apply_drop_shadow_effect(self.ui.createReportHeader)

        self.ui.LeftMenuContainerMini.hide()
        self.showMaximized()

        self.ui.reportsBtn1.setChecked(True)
        self.previous_index = -1

        # define the default stacks
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.icpTabWidget.setCurrentIndex(0)
        self.ui.chmTabWidget.setCurrentIndex(0)

        # Sets the tab order for three widgets
        self.setTabOrder(self.ui.gcmsTestsJobNum, self.ui.gcmsTestsSample)
        self.setTabOrder(self.ui.gcmsTestsSample, self.ui.gcmsTestsVal)

        # Load page setup functions
        general_reports_setup(self)
        settingsSetup(self)
        history_page_setup(self)
        icpSetup(self)
        chemistrySetup(self)

    def loadDatabase(self, max_attempts=3):
        self.logger.info("Entering loadDatabase function")

        # self.paths = load_pickle('data.pickle')
        self.preferences = LocalPreferences('data.pickle')
        preferences = self.preferences.values()

        self.logger.debug('Preferences Items')
        for key, value in preferences.items():
            self.logger.debug(f'Database Path Name: {key}, Path: {value}')

        for attempt in range(max_attempts):
            self.logger.debug(f'Attempt: {attempt}')

            try:
                self.db = DatabaseManager(self.preferences.get('databasePath'))
                self.tempDB = DatabaseManager(self.preferences.get('temp_backend_path')) # harry backend database
                self.officeDB = DatabaseManager(self.preferences.get('officeDbPath'))  # front end database
                return

            except Exception as error:
                self.logger.error(f"Error loading database: {error}")

                if attempt == max_attempts-1:
                    self.logger.warning("Max attempts reached. Unable to connect to databases.")
                    return

                # TODO: remove this later
                #tempLocation = openFile()
                #print(f'Temp Location: {tempLocation}')
                #self.preferences.update('temp_backend_path', tempLocation)

                # Dialog popup to load the necessary database Information for the user
                dialog = FileLocationDialog(self.preferences)
                dialog.exec_()

    #******************************************************************
    #    Signal Connections
    #******************************************************************

    def connect_client_info_signals(self):
        # Field mapping: widget to field name
        field_mapping = {
            self.ui.clientName_1: 'clientName',
            self.ui.date_1: 'date',
            self.ui.time_1: 'time',
            self.ui.attention_1: 'attn',
            self.ui.addy1_1: 'addy1',
            self.ui.addy2_1: 'addy2',
            self.ui.addy3_1: 'addy3',
            self.ui.sampleType1_1: 'sampleType1',
            self.ui.sampleType2_1: 'sampleType2',
            self.ui.totalSamples_1: 'totalSamples',
            self.ui.recvTemp_1: 'recvTemp',
            self.ui.tel_1: 'tel',
            self.ui.email_1: 'email',
            self.ui.fax_1: 'fax',
            self.ui.payment_1: 'payment',
        }

        # Connect signals dynamically
        for widget, field in field_mapping.items():
            widget.textChanged.connect(lambda text, field=field: self.on_client_info_changed(field, text))

    def on_client_info_changed(self, field_name, text):
        self.clientInfo[field_name] = text;

    def connect_navigation_buttons(self):
        NAVIGATION_BUTTONS = {
            'reportsBtn1': 0,
            'reportsBtn2': 0,
            'createReportBtn': 1, # on the history page section
            'createReportBtn1': 1,
            'createReportBtn2': 1,
            'icpBtn1': 2,
            'icpBtn2': 2,
            'chmBtn1': 3,
            'chmBtn2': 3,
            'settingsBtn1':4,
            'settingsBtn2':4
        }

        for button_name, index in NAVIGATION_BUTTONS.items():
            getattr(self.ui, button_name).clicked.connect(lambda _, idx=index: self.change_index(idx))


    def on_tab_pressed1(self):
        self.ui.gcmsTestsVal.setFocus()

   #******************************************************************
   #    Navigation Management
   #******************************************************************
    def change_index(self, index):
        self.logger.info(f'Entering change_index with index: {index}')
        self.previous_index = self.ui.stackedWidget.currentIndex()

        if self.previous_index == 5 and not show_switch_page_dialog(self):
            return  # Don't switch if user cancels

        self.ui.stackedWidget.setCurrentIndex(index)

    def on_stackedWidget_currentChanged(self, index):
        self.logger.info(f"Stack Widget Switched to Index: {index}")
        self.logger.info(f'previous_index: {self.previous_index}')


        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)

        #FIXME: issue that arises when the active creation setting is thing
        for btn in btn_list:
            if index in [5,6]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True) # Ensure only one button can be checked at a time

        self.ui.headerWidget.show()

        if(index == 0): # History
            self.ui.headerTitle.setText('Reports History')
            set_total_outgoing_jobs(self)

        if(index == 1): # Create Report
            self.ui.headerTitle.setText('Create Reports')
            self.ui.headerDesc.setText('')

            self.reset_create_report()

        if(index == 2): # ICP Page
            current_tab = self.ui.icpTabWidget.currentIndex()
            on_icpTabWidget_currentChanged(self, current_tab)

        if(index == 3): # CHM Page
            current_tab = self.ui.chmTabWidget.currentIndex()
            on_chmTabWidget_currentChanged(self, current_tab)

        if(index == 4): # Settings
            self.ui.headerTitle.setText('Settings')
            self.ui.headerDesc.setText('')

        #if(self.previous_index == 5): # Creating Reports
        if(index == 5):
            #TODO: can improve on this section
            self.ui.headerWidget.hide()
            deleteAllSampleWidgets(self)

    def reset_create_report(self):
        # Clearing the report page section
        self.ui.jobNumInput.setText('')
        self.ui.reportType.setCurrentIndex(0)
        self.ui.paramType.setCurrentIndex(0)
        self.ui.dilutionInput.setText('')



class LocalPreferences:
    def __init__(self, path='preferences.pkl'):
        self.path = path
        self.load()

    def load(self):
        try:
            with open(self.path, 'rb') as file:
                self.preferences = pickle.load(file)
        except (FileNotFoundError, EOFError):
            self.preferences = {}

    def values(self):
        return self.preferences

    def update(self,name, value):
        self.preferences[name] = value
        self.save()

    def get(self, value):
        return self.preferences[value]

    def remove(self, value):
        del self.preferences[value]

    def save(self):
        with open(self.path, 'wb') as file:
            pickle.dump(self.preferences, file)


#TODO: move to dialog section
def show_switch_page_dialog(self):
    reply = QMessageBox.question(
        self,
        "Confirm Switch",
        "Are you sure you want to switch pages? Unsaved changes will be lost.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No  # Default button
    )

    return reply == QMessageBox.Yes  # Return True if user confirms
