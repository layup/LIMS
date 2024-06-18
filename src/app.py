import sys 
import re 
import pickle

from PyQt5 import QtWidgets
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy, QCompleter, QStyleFactory, QGraphicsDropShadowEffect
)

from modules.constants import *
from modules.createExcel import * 
from modules.dbManager import *
from modules.dbFunctions import * 
from modules.dialogBoxes import *
from modules.utilities import * 

from assets import resource_rc

from interface import *

from pages.createReportPage import reportSetup, deleteAllSampleWidgets
from pages.icp_tools import  icpSetup, loadReportList, loadIcpHistory
from pages.chm_tools import ( populateChmDatabase, chemistySetup, chmClearEnteredTestsData, ) 
from pages.settingsPage import settingsSetup
from pages.historyPage import historyPageSetup, loadReportsPage

from widgets.widgets import * 
    
    
#TODO: need to have more class objects that deal with insertion, that way we can have lazy loading isntead of constant 
# need to get more info 
class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 

        # Set the current working directory to the directory containing the script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Load the setup 
        self.loadDatabase()
        self.loadCreatePage()
        self.loadStartup() 

        self.dataTransfer()

        # Page Setups 
        reportSetup(self) 
        settingsSetup(self)
        historyPageSetup(self)
        icpSetup(self)
        chemistySetup(self)

        apply_drop_shadow_effect(self.ui.headerWidget)
        
   #******************************************************************
   #    inline Slot Function Calls 
   #******************************************************************  
   #FIXME: not sure if it is good pratice to have just something like this 
   #FIXME: can replace with something that just scans all of the files 
    def on_clientName_1_textChanged(self):
        self.clientInfo['clientName'] = self.ui.clientName_1.text()
     
    def on_date_1_textChanged(self): 
        self.clientInfo['date'] = self.ui.date_1.text()
    
    def on_time_1_textChanged(self):
        self.clientInfo['time'] = self.ui.time_1.text()
    
    def on_attention_1_textChanged(self):
        self.clientInfo['attn'] = self.ui.attention_1.text()
        
    def on_addy1_1_textChanged(self): 
        self.clientInfo['addy1'] = self.ui.addy1_1.text()
        
    def on_addy2_1_textChanged(self): 
        self.clientInfo['addy2'] = self.ui.addy2_1.text()
    
    def on_addy3_1_textChanged(self): 
        self.clientInfo['addy3'] = self.ui.addy3_1.text()
        
    def on_sampleType1_1_textChanged(self):
        self.clientInfo['sampleType1'] = self.ui.sampleType1_1.text()
        
    def on_sampleType_2_textChanged(self):
        self.clientInfo['sampleType2'] = self.ui.sampleType2_1.text()
    
    def on_totalSamples_1_textChanged(self): 
        self.clientInfo['totalSamples'] = self.ui.totalSamples_1.text() 
    
    def on_recvTemp_1_textChanged(self): 
        self.clientInfo['recvTemp'] = self.ui.recvTemp_1.text()
        
    def on_tel_1_textChanged(self):
        self.clientInfo['tel'] = self.ui.tel_1.text()
    
    def on_email_1_textChanged(self):
        self.clientInfo['email'] = self.ui.email_1.text()
    
    def on_fax_1_textChanged(self): 
        self.clientInfo['fax'] = self.ui.fax_1.text()
    
    def on_payment_1_textChanged(self): 
        self.clientInfo['payment'] = self.ui.payment_1.text()
       
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
   #    Navigatioin Mangament 
   #****************************************************************** 
    def change_index(self, index): 
        self.previous_index = self.ui.stackedWidget.currentIndex() 
        self.ui.stackedWidget.setCurrentIndex(index)
    
    def on_stackedWidget_currentChanged(self, index):
        print(f'Stack Index: {index}')
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

    def on_icpTabWidget_currentChanged(self, index):
        print(f'ICP TAB INDEX: {index}')
        if(index == 0): #History  
            self.ui.headerTitle.setText('ICP Database'); 
            self.ui.headerDesc.setText(''); 
        
            # Load the data again when the 
            #loadIcpHistory(self)
        
        if(index == 1): # Elements Info 
            self.ui.headerTitle.setText('ICP Elements Information'); 

            totalElements = self.elementManager.getTotalElements()
            self.ui.headerDesc.setText("Total Elements: {}".format(totalElements))
            
            #loadDefinedElements(self)

        if(index == 2): #  Reports Info 
            self.ui.headerTitle.setText('ICP Reports Information'); 
            self.ui.headerDesc.setText(''); 
            
            loadReportList(self)

    def on_chmTabWidget_currentChanged(self, index): 
        #TODO: reload in the data for all the sections (new data)? 
        print(f'CHM TAB CHANGE INDEX {index}')
        
        if(index == 0): # Database 
            self.ui.headerTitle.setText('Chemisty Tests Database'); 
            self.ui.headerDesc.setText(''); 
            populateChmDatabase(self);  
            
        if(index == 1): # Input Data 
            self.ui.headerTitle.setText('Chemisty Data Entry'); 
            self.ui.headerDesc.setText(''); 
           
        if(index == 2): # Test Info  
            self.ui.headerTitle.setText('Chemisty Tests Information'); 
            self.ui.headerDesc.setText(''); 
            #totalTests = getChmTotalTests(self.db) 
            #self.ui.gcmsSubTitleLabel.setText('Total Tests: ' + str(totalTests))

        if(index == 3): # Report Info 
            self.ui.headerTitle.setText('Chemisty Reports Information')
            self.ui.headerDesc.setText('Total Reports: ') 

   #******************************************************************
   #    Setup Loading
   #******************************************************************  
    def loadStartup(self): 
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
        #TODO: convert all the database into one data base for the front and backend
        # self.paths = load_pickle('data.pickle')
        self.preferences = LocalPreferences('data.pickle')
        preferences = self.preferences.values()
        
        print('Preferences Items')
        for key, value in preferences.items(): 
            print(f'*{key}: {value}')
        print('\n')
       
        # Represents the three databases 
        databaseStatus = [0, 0, 0] 

        for attempt in range(3):  
            print(f'Attemp: {attempt}')
                            
            try: 
                mainDatabasePath = self.preferences.get('databasePath') 
                officeDatabasePath = self.preferences.get('officeDbPath')
                preferencesDatabasePath = self.preferences.get('preferencesPath')
                tempPath = self.preferences.get('temp_backend_path')

                # Connect the temp new database that will be replacing the main database 
                self.tempDB = Database(tempPath)
                
                # Connect the backend database (Harry Systems)
                self.db = Database(mainDatabasePath)

                # Connect the Office database (Front and Histroy Systems)
                self.officeDB = Database(officeDatabasePath)
            
                # Connect the preferences database
                #self.preferencesDB = Database(preferencesDatabasePath)

                return

            except Exception as error: 
                print(error)

                if attempt == 2:
                    print("Max attempts reached. Unable to connect to databases.")
                    return
                else:
                    
                    # TODO: remove this later 
                    tempLocation = openFile()
                    print(f'Temp Location: {tempLocation}')
                    self.preferences.update('temp_backend_path', tempLocation)
                    
                    # Dialog popup to load the necessaary database Information for the user 
                    dialog = FileLocationDialog(self.preferences)
                    dialog.exec_()
          
    #******************************************************************
    #   Helper/Other Functions 
    #******************************************************************         
    #TODO: could be moved to the utiles.py 
    #TODO: find out what this does 
    
    def connect_to_database(path): 
        try: 
            connection = Database(path);
            return connection
            
        except Exception as error: 
            print(f'Could not connect to database {path}')
            print(error)
            
    
    def on_tab_pressed1(self): 
        self.ui.gcmsTestsVal.setFocus()
    
    def loadCreatePage(self): 
        print('[FUNCTION]: loadCreatePage(self)')
 
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
        print(f'Update Sample Name: {self.sampleNames}')
 

    @pyqtSlot()
    def on_testBtn_clicked(self): 
        print('Test Button Pressed')

        dialog = ChmTestsDialog()
        user_input = dialog.get_user_input()

        if user_input is not None:
            print(f"User entered: {user_input}")
        else:
            print("User canceled.")
            
    def dataTransfer(self): 
        print('Data Transfer File test')
        
            
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
    



