import os
import pickle

from assets import resource_rc
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTableWidget, QStyleFactory)

from modules.constants import REPORTS_TYPE 
from modules.dbManager import Database 
from modules.dbFunctions import getAllParameters 
from modules.utils.apply_drop_shadow_effect import apply_drop_shadow_effect
from modules.utils.file_utils import openFile
from modules.widgets.dialogs import FileLocationDialog, ChmTestsDialog

from interface import *

# Page setup imports 
from pages.reports_page.create_report_page import reportSetup
from pages.reports_page.reports.report_utils import deleteAllSampleWidgets
from pages.icp_page.icp_page_config import  icpSetup
from pages.chm_page.chm_page_config import chemistrySetup  
from pages.settings_page.settings_page_config import settingsSetup
from pages.history_page.history_page_config import historyPageSetup, loadReportsPage
    
class MainWindow(QMainWindow):
    
    def __init__(self,logger):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 

        # Access the existing logger from setup.py
        self.logger = logger
        self.logger.info('Creating MainWindow class')

        # Set the current working directory to the directory containing the script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        apply_drop_shadow_effect(self.ui.headerWidget)
        
        # Load the setup 
        self.loadDatabase()
        self.loadCreatePage()
        self.loadStartup() 
        
        self.logger.info('Preparing Page Setup Functions')
        reportSetup(self) 
        settingsSetup(self)
        historyPageSetup(self)
        icpSetup(self)
        chemistrySetup(self)

        self.connect_client_info_signals()
        
    def connect_client_info_signals(self):
        self.ui.clientName_1.textChanged.connect(lambda text: self.on_client_info_changed('clientName', text))
        self.ui.date_1.textChanged.connect(lambda text: self.on_client_info_changed('date', text))
        self.ui.time_1.textChanged.connect(lambda text: self.on_client_info_changed('time', text))
        self.ui.attention_1.textChanged.connect(lambda text: self.on_client_info_changed('attn', text))
        self.ui.addy1_1.textChanged.connect(lambda text: self.on_client_info_changed('addy1', text))
        self.ui.addy2_1.textChanged.connect(lambda text: self.on_client_info_changed('addy2', text))
        self.ui.addy3_1.textChanged.connect(lambda text: self.on_client_info_changed('addy3', text))
        self.ui.sampleType1_1.textChanged.connect(lambda text: self.on_client_info_changed('sampleType1', text))
        self.ui.sampleType2_1.textChanged.connect(lambda text: self.on_client_info_changed('sampleType2', text))
        self.ui.totalSamples_1.textChanged.connect(lambda text: self.on_client_info_changed('totalSamples', text))
        self.ui.recvTemp_1.textChanged.connect(lambda text: self.on_client_info_changed('recvTemp', text))
        self.ui.tel_1.textChanged.connect(lambda text: self.on_client_info_changed('tel', text))
        self.ui.email_1.textChanged.connect(lambda text: self.on_client_info_changed('email', text))
        self.ui.fax_1.textChanged.connect(lambda text: self.on_client_info_changed('fax', text))
        self.ui.payment_1.textChanged.connect(lambda text: self.on_client_info_changed('payment', text))
    
    def on_client_info_changed(self, field_name, text): 
        self.clientInfo[field_name] = text; 
        
   #******************************************************************
   #    Menu Buttons 
   #******************************************************************   
    def on_reportsBtn1_toggled(self): 
        self.change_index(0) 
    
    def on_reportsBtn2_toggled(self):
        self.change_index(0)

    def on_createReportBtn1_toggled(self):
        self.change_index(1)
        
    def on_createReportBtn2_toggled(self):
        self.change_index(1)

    def on_icpBtn1_toggled(self):
        self.change_index(2)
        
    def on_icpBtn2_toggled(self):
        self.change_index(2)
        
    def on_gsmsBtn1_toggled(self):
         self.change_index(3)
    
    def on_gsmsBtn2_toggled(self):
         self.change_index(3)
     
    def on_settingBtn1_toggled(self):
         self.change_index(4)
    
    def on_settingBtn2_toggled(self):
         self.change_index(4)
         
   #******************************************************************
   #    Navigation Management 
   #****************************************************************** 
    def change_index(self, index): 
        self.logger.info('Entering change_index with index: {index}')
        self.previous_index = self.ui.stackedWidget.currentIndex() 
        self.ui.stackedWidget.setCurrentIndex(index)
    
    def on_stackedWidget_currentChanged(self, index):
        self.logger.info(f"Stack Widget Switched to Index: {index}")

        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)
        
        #FIXME: issue that arises when the active creation setting is thing 
        for btn in btn_list:
            #if index in [1,2,3,4]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            btn.setAutoExclusive(True)

        self.ui.headerWidget.show()
                   
        if(index == 0): # History
            self.ui.headerTitle.setText('Reports History'); 
            self.ui.headerDesc.setText('Recently created reports'); 
            
            self.ui.historyTabWidget.setCurrentIndex(0)
            
            loadReportsPage(self)
            
        if(index == 1): # Create Report
            self.ui.headerTitle.setText('Create Reports'); 
            self.ui.headerDesc.setText(''); 

            # Clearing the report page section 
            self.ui.jobNumInput.setText('')
            self.ui.reportType.setCurrentIndex(0)
            self.ui.paramType.setCurrentIndex(0)
            self.ui.dilutionInput.setText('')

        if(index == 2): # ICP Page 
            self.ui.icpTabWidget.setCurrentIndex(1)
            self.ui.icpTabWidget.setCurrentIndex(0)
        
        if(index == 3): # CHM Page 
            self.ui.chmTabWidget.setCurrentIndex(1) 
            self.ui.chmTabWidget.setCurrentIndex(0) 
            
        if(index == 4): # Settings  
            self.ui.headerTitle.setText('Settings'); 
            self.ui.headerDesc.setText('');  
                
        #if(self.previous_index == 5): # Creating Reports 
        if(index == 5): 
            self.ui.headerWidget.hide()
            deleteAllSampleWidgets(self) 

  #******************************************************************
   #    Setup Loading
   #******************************************************************  
    def loadStartup(self): 
        self.logger.info("Entering loadStartup function")
        self.setWindowTitle("Laboratory Information management System") 
        self.setStyle(QStyleFactory.create('Fusion'))
        
        self.ui.LeftMenuContainerMini.hide()
        self.showMaximized()

        self.activeCreation = False; 
        self.ui.reportsBtn1.setChecked(True)

        self.previous_index = -1

        # Set the home stack 
        self.ui.stackedWidget.setCurrentIndex(0) 
        self.ui.headerTitle.setText('Reports History'); 
        self.ui.headerDesc.setText('Recently created reports'); 

        # Sets the tab order for three widgets
        self.setTabOrder(self.ui.gcmsTestsJobNum, self.ui.gcmsTestsSample)
        self.setTabOrder(self.ui.gcmsTestsSample, self.ui.gcmsTestsVal) 
       
    def loadDatabase(self): 
        self.logger.info("Entering loadDatabase function")

        #TODO: convert all the database into one data base for the front and backend
        # self.paths = load_pickle('data.pickle')
        self.preferences = LocalPreferences('data.pickle')
        preferences = self.preferences.values()
        
        self.logger.debug('Preferences Items')
        for key, value in preferences.items(): 
            self.logger.debug(f'Database Path Name: {key}, Path: {value}')
   
        # Represents the three databases 
        databaseStatus = [0, 0, 0] 

        for attempt in range(3):  
            print(f'Attempt: {attempt}')
                            
            try: 
                mainDatabasePath = self.preferences.get('databasePath') 
                officeDatabasePath = self.preferences.get('officeDbPath')
                preferencesDatabasePath = self.preferences.get('preferencesPath')
                tempPath = self.preferences.get('temp_backend_path')

                # Connect the temp new database that will be replacing the main database 
                self.tempDB = Database(tempPath)
                
                # Connect the backend database (Harry Systems)
                self.db = Database(mainDatabasePath)

                # Connect the Office database (Front and History Systems)
                self.officeDB = Database(officeDatabasePath)
            
                # Connect the preferences database
                #self.preferencesDB = Database(preferencesDatabasePath)
                return

            except Exception as error: 
                self.logger.error(f"Error loading database: {error}")

                if attempt == 2:
                    self.logger.warning("Max attempts reached. Unable to connect to databases.")
                    return
                else:
                    # TODO: remove this later 
                    tempLocation = openFile()
                    print(f'Temp Location: {tempLocation}')
                    self.preferences.update('temp_backend_path', tempLocation)
                    
                    # Dialog popup to load the necessary database Information for the user 
                    dialog = FileLocationDialog(self.preferences)
                    dialog.exec_()
          
    #******************************************************************
    #   Helper/Other Functions 
    #******************************************************************         
            
    def on_tab_pressed1(self): 
        self.ui.gcmsTestsVal.setFocus()
    
    def loadCreatePage(self): 
        self.logger.info(f'Entering loadCreatePage function')
 
        #load the report Types
        self.ui.reportType.clear()
        self.ui.reportType.addItems(REPORTS_TYPE)
        
        #paramResults = sorted(getReportTypeList(self.db))
        paramResults = sorted(getAllParameters(self.tempDB))
        paramResults =  [sublist[1] for sublist in paramResults]
        
        paramResults.insert(0, "")
        self.ui.paramType.addItems(paramResults)
    
    # TODO: make this more a general application  
    def formatTable(self, table): 
        self.logger.info(f'Entering formatTable with table: {table.objectName()}')
        rowHeight = 25; 
        
        #table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        table.verticalHeader().setVisible(True)
        table.verticalHeader().setDefaultSectionSize(rowHeight)

        #Disable editing for the entire table 
        table.setEditTriggers(QTableWidget.NoEditTriggers)

    def clearDataTable(self): 
        self.ui.dataTable.clearContents()
        self.ui.dataTable.setRowCount(0)

    def handle_item_changed(self, item, test): 
        row = item.row()
        column = item.column()
        value = item.text()
        
        if(column >= 5):
            print(self.ui.dataTable.item(row,column).text())
            
    def updateSampleNames(self, textChange, key):
        self.sampleNames[key] = textChange; 
        self.logger.debug(f'Update Sample Names: {repr(self.sampleNames)}')
 

    @pyqtSlot()
    def on_testBtn_clicked(self): 
        print('Test Button Pressed')

        dialog = ChmTestsDialog()
        user_input = dialog.get_user_input()

        if user_input is not None:
            print(f"User entered: {user_input}")
        else:
            print("User canceled.")
            
#******************************************************************
#   Classes
#******************************************************************    
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
    



