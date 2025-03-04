import os
import time

from interface import *
from assets import resource_rc

from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTableWidget, QStyleFactory, QLabel, QMessageBox)

from modules.dialogs.basic_dialogs import yes_or_no_dialog
from modules.utils.apply_drop_shadow_effect import apply_drop_shadow_effect
from modules.dialogs.file_location_dialog import FileLocationDialog
from modules.utils.report_utils import deleteAllSampleWidgets

# setup database managers
from modules.managers.authors_manager import AuthorsManager
from modules.managers.chm_test_data_manager import ChmTestManager
from modules.managers.icp_test_data_manager import IcpTestManager
from modules.managers.tests_manager import TestManager
from modules.managers.job_manager import JobManager
from modules.managers.reports_manager import ReportsManager
from modules.managers.parameters_manager import ParametersManager
from modules.managers.elements_manager import ElementsManager
from modules.managers.units_manager import UnitManager
from modules.managers.footers_manager import FootersManager
from modules.managers.macros_manager import MacrosManger

from modules.managers.server_manager import PostgresDatabaseManager

# tools manager
from modules.managers.tools.database_manager import DatabaseManager
from modules.managers.tools.client_info_manager import ClientInfoManager
from modules.managers.tools.toolbar_manager import ToolbarManager
from modules.managers.tools.status_manager import StatusBarManager
from modules.managers.tools.navigation_manager import NavigationManager
from modules.managers.tools.file_paths_manager import FilePathsManager

# Page setup imports
from pages.reports_page.reports_config import general_reports_setup
from pages.icp_page.icp_page_config import  icp_setup, on_icpTabWidget_currentChanged
from pages.chm_page.chm_page_config import chm_section_setup, on_chmTabWidget_currentChanged
from pages.macros_page.macros_page_config import macros_page_setup
from pages.history_page.history_page_config import history_page_setup

class MainWindow(QMainWindow):

    def __init__(self, logger, preferences, db_manager):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()

        self.logger = logger
        self.preferences = preferences
        self.db_manager = db_manager

        self.logger.debug(f'self.db_manager: {db_manager}')
        self.logger.debug(f'self.preferences: {preferences}')
        self.logger.debug(f'self.logger: {logger}')

        self.ui.setupUi(self)

        # load the setup
        self.load_database()
        self.manager_setup()
        self.init_setup()

        # load signal connections
        self.connect_client_info_signals()

    def closeEvent(self, event):

        #TODO: be sure to kill the treads too when stopping the server

        """Override this method to handle the close event."""
        reply = QMessageBox.question(
            self,
            'Exit Confirmation',
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Close the database connections
            self.local_db.close()

            event.accept()  # Allow the window to close
        else:
            event.ignore()  # Prevent the window from closing

    #******************************************************************
    #    Setup Loading
    #******************************************************************

    def init_setup(self):
        self.logger.info("Entering load_setups function")

        # Set the title and style
        self.setWindowTitle("Laboratory Information management System")
        self.setStyle(QStyleFactory.create('Fusion'))

        # Set the current working directory to the directory containing the script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        apply_drop_shadow_effect(self.ui.headerWidget)
        apply_drop_shadow_effect(self.ui.createReportHeader)

        self.ui.LeftMenuContainerMini.hide()
        self.showMaximized()

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
        history_page_setup(self)

        chm_section_setup(self)
        icp_setup(self)

        macros_page_setup(self)

    def manager_setup(self):

        # state managers
        self.status_bar_manager = StatusBarManager(self.ui.statusbar)
        self.client_manager = ClientInfoManager(self.ui.reportsUserInfoWidget)
        self.toolbar_manager = ToolbarManager(self.ui.toolBar)
        self.navigation_manager = NavigationManager(self.ui.navigationTree)

        # shared database tables managers
        self.jobs_manager = JobManager(self.local_db)
        self.units_manager = UnitManager(self.local_db)
        self.tests_manager = TestManager(self.local_db)
        self.authors_manager = AuthorsManager(self.local_db)
        self.parameters_manager = ParametersManager(self.local_db)
        self.footers_manager = FootersManager(self.local_db)
        self.reports_manager = ReportsManager(self.local_db)
        self.macros_manager = MacrosManger(self.local_db)

        # icp database table manager
        self.elements_manager = ElementsManager(self.local_db)
        self.icp_test_data_manager = IcpTestManager(self.local_db)

        # chm database table manager
        self.chm_test_data_manager = ChmTestManager(self.local_db)

        # manager signals
        self.toolbar_manager.action_name.connect(self.handle_toolbar_action)
        self.navigation_manager.stack_change.connect(self.change_index)
        self.navigation_manager.icp_tab_change.connect(self.ui.icpTabWidget.setCurrentIndex)
        self.navigation_manager.chm_tab_change.connect(self.ui.chmTabWidget.setCurrentIndex)
        self.navigation_manager.report_tab_change.connect(self.ui.historyTabWidget.setCurrentIndex)

    def handle_toolbar_action(self, action_name):
        self.logger.info(f'Entering handle_toolbar_action with action_name: {action_name}')

        if(action_name == 'create'):
            self.create_report.start()

        if(action_name == 'edit'):
            pass

        if(action_name == 'search'):
            self.change_index(0)
            self.ui.historyTabWidget.setCurrentIndex(0)

        if( action_name == "upload"):
            self.icp_history_controller.handle_upload_btn()

        if(action_name == 'write'):
            self.change_index(3)
            self.ui.chmTabWidget.setCurrentIndex(1)

        if(action_name == 'settings'):
            pass


    def load_database(self, max_attempts=3):
        self.logger.info('Entering load_database')


        #TODO: rename all of the .json files
        self.local_db = self.db_manager

        # check where the output folder location is and if it exists
        output_path = self.preferences.get_path('reportsPath')

        print(f'output_path: {output_path}')

        for attempt in range(max_attempts):
            self.logger.debug(f'Attempt: {attempt}')

            # check where the output folder location is and if it exists
            if(os.path.exists(output_path)):
                return

            else:
                response = yes_or_no_dialog("Output Reports file path doesn't exist", ' would you like to set the file locations?')

                if(response):
                    # Dialog popup to load the necessary database Information for the user
                    dialog = FileLocationDialog(self.preferences)
                    dialog.exec_()
                else:
                    return

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
        #self.clientInfo[field_name] = text;
        self.client_manager.client_info_data[field_name] = text

    #TODO: deal with this
    def on_tab_pressed1(self):
        self.ui.gcmsTestsVal.setFocus()

   #******************************************************************
   #    Navigation Management
   #******************************************************************
    def change_index(self, index):
        self.logger.info(f'Entering change_index with index: {index}')
        self.previous_index = self.ui.stackedWidget.currentIndex()

        if self.previous_index == 5 and not yes_or_no_dialog( "Confirm Switch?", "Are you sure you want to switch pages? Unsaved changes will be lost."):
            return  # Don't switch if user cancels

        self.ui.stackedWidget.setCurrentIndex(index)

    def on_stackedWidget_currentChanged(self, index):
        self.logger.info(f"Stack Widget Switched to Index: {index}")
        self.logger.info(f'previous_index: {self.previous_index}')

        self.ui.headerWidget.show()

        if(index == 0): # History
            self.ui.headerTitle.setText('Reports History')


        if(index == 1): # Micros/Tests
            self.ui.headerTitle.setText('Micros/Tests')
            self.ui.headerDesc.setText('')


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

