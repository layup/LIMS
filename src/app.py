import os

from interface import *
from assets import resource_rc

from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTableWidget, QStyleFactory, QLabel, QMessageBox)

from modules.dialogs.basic_dialogs import yes_or_no_dialog
from modules.utils.apply_drop_shadow_effect import apply_drop_shadow_effect
from modules.dialogs.file_location_dialog import FileLocationDialog

# setup up managers
from modules.managers.authors_manager import AuthorsManager
from modules.managers.client_info_manager import ClientInfoManager
from modules.managers.database_manager import DatabaseManager
from modules.managers.tests_manager import TestManager
from modules.managers.toolbar_manager import ToolbarManager
from modules.managers.status_manager import StatusBarManager
from modules.managers.parameters_manager import ParametersManager
from modules.managers.elements_manager import ElementsManager
from modules.managers.units_manager import UnitManager
from modules.managers.footers_manager import FootersManager
from modules.managers.navigation_manager import NavigationManager
from modules.managers.file_paths_manager import FilePathsManager

# Page setup imports
from pages.reports_page.reports_config import general_reports_setup
from pages.reports_page.reports.report_utils import deleteAllSampleWidgets
from pages.icp_page.icp_page_config import  icp_setup, on_icpTabWidget_currentChanged
from pages.chm_page.chm_page_config import chemistrySetup, on_chmTabWidget_currentChanged
from pages.history_page.history_page_config import history_page_setup, set_total_outgoing_jobs

class MainWindow(QMainWindow):

    def __init__(self,logger):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.logger = logger

        self.ui.setupUi(self)

        # load the setup
        self.load_database()
        self.manager_setup()
        self.init_setup()

        # load signal connections
        self.connect_client_info_signals()

    def closeEvent(self, event):
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
            self.db.close()
            self.tempDB.close()
            self.officeDB.close()

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
        icp_setup(self)
        chemistrySetup(self)

    def manager_setup(self):

        # state managers
        self.status_bar_manager = StatusBarManager(self.ui.statusbar)
        self.client_manager = ClientInfoManager(self.ui.reportsUserInfoWidget)
        self.toolbar_manager = ToolbarManager(self.ui.toolBar)
        self.navigation_manager = NavigationManager(self.ui.navigationTree)

        # shared database tables managers
        self.units_manager = UnitManager(self.tempDB)
        self.tests_manager = TestManager(self.tempDB)
        self.authors_manager = AuthorsManager(self.tempDB)
        self.parameters_manager = ParametersManager(self.tempDB)
        self.footers_manager = FootersManager(self.tempDB)

        # icp database table manager
        self.elements_manager = ElementsManager(self.tempDB)

        # chm database table manager

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
        self.logger.info("Entering load_database")

        self.preferences = FilePathsManager()

        for attempt in range(max_attempts):
            self.logger.debug(f'Attempt: {attempt}')

            try:
                # set the default databases
                self.db = DatabaseManager(self.preferences.get_path('databasePath'))
                self.tempDB = DatabaseManager(self.preferences.get_path('temp_backend_path')) # harry backend database
                self.officeDB = DatabaseManager(self.preferences.get_path('officeDbPath'))  # front end database
                return

            except Exception as error:
                self.logger.error(f"Error loading database: {error}")

                if attempt == max_attempts-1:
                    self.logger.warning("Max attempts reached. Unable to connect to databases.")
                    return

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

