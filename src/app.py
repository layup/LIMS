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
from pages.chm_tools import (chmLoadTestsNames, loadChmDatabase, chemistySetup, getTestsAndUnits, chmClearEnteredTestsData, ) 
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

        #
        self.dataTransfer()

        # Page Setups 
        reportSetup(self) 
        settingsSetup(self)
        historyPageSetup(self)
        icpSetup(self)
        chemistySetup(self)

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
        print(f'Current Index: {index}')
        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)
        
        #FIXME: issue that arises when the active creation setting is thing 
        for btn in btn_list:
            #if index in [1,2,3,4]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            btn.setAutoExclusive(True)
                   
        if(index == 0): # History
            self.ui.reportsHeader.setText('Reports History'); 
            self.ui.totalReportsHeader.setText('Recently created reports')
            self.ui.historyTabWidget.setCurrentIndex(0)
            
            loadReportsPage(self)
            
        if(index == 1): # Create Report
            
            # Clearing the report page section 
            self.ui.jobNumInput.setText('')
            self.ui.reportType.setCurrentIndex(0)
            self.ui.paramType.setCurrentIndex(0)
            self.ui.dilutionInput.setText('')
            
        if(index == 2): # ICP Page 
            # TODO: set the title text to nothing by default or something, keeps loading the wrong thing 
            # TODO: check what the current item is
            
            pass; 
        
        if(index == 3): # CHM Page 
            pass; 
            
        if(index == 4): # Settings  
            pass; 

        if(self.previous_index == 5): # Creating Reports 
            deleteAllSampleWidgets(self) 
        

    #FIXME: have a single header that is controlled by the global, instead of each having their own seperate one 
    def on_icpTabWidget_currentChanged(self, index):
        #TODO: set the machine values for both of theses, create a single inqury that fetches based on date
        
        if(index == 0): #History 
            self.ui.icpPageTitle.setText("ICP Page")
            self.ui.icpLabel.setText("")
        
        #TODO: create a single function that loads this all to begin with isntead of having to reload this each time 
        #try lazy loading 
        if(index == 0): #History  
            self.ui.icpPageTitle.setText("ICP Database")
            self.ui.icpLabel.setText("")
        
            # Load the data again when the 
            loadIcpHistory(self)
        
        if(index == 1): # Elements Info 
            self.ui.icpPageTitle.setText("ICP Elements Information")
        
            totalElements = self.elementManager.getTotalElements()
            self.ui.icpLabel.setText("Total Elements: {}".format(totalElements))
            
            #loadDefinedElements(self)

        if(index == 2): #  Reports Info 
            self.ui.icpPageTitle.setText("ICP Reports Information")
            self.ui.icpLabel.setText("Total Reports:") 
            loadReportList(self)

    def on_chmTabWidget_currentChanged(self, index): 
        print(f'CHM TAB CHANGE INDEX {index}')
        
        if(index == 0): # Database 
            self.ui.chmTitleLabel.setText('Chemisty Tests Database') 
            self.ui.gcmsSubTitleLabel.setText('')
            loadChmDatabase(self);  
            
        if(index == 1): # Input Data 
            self.ui.chmTitleLabel.setText('Chemisty Data Entry')
            self.ui.gcmsSubTitleLabel.setText('') 
            chmClearEnteredTestsData(self)
            
            temp = getTestsAndUnits(self)
            print('*CHM Tests and Unit Values')
            print(temp)
            
            self.ui.gcmsTests.addItems(temp[0])
            self.ui.gcmsUnitVal.addItems(temp[1])
        
        if(index == 2): # Test Info  
            self.ui.chmTitleLabel.setText('Chemisty Tests Information')
            #totalTests = getChmTotalTests(self.db) 
            
            #self.ui.gcmsSubTitleLabel.setText('Total Tests: ' + str(totalTests))
            #chmLoadTestsNames(self)
            
        if(index == 3): # Report Info 
            self.ui.chmTitleLabel.setText('Chemisty Reports Information')
            self.ui.gcmsSubTitleLabel.setText('Total Reports: ') 

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


        # Sets the stacks to home page 
        self.ui.stackedWidget.setCurrentIndex(0) 
        self.ui.icpTabWidget.setCurrentIndex(0)
        self.ui.chmTabWidget.setCurrentIndex(0)

        # Sets the tab order for three widgets
        self.setTabOrder(self.ui.gcmsTestsJobNum, self.ui.gcmsTestsSample)
        self.setTabOrder(self.ui.gcmsTestsSample, self.ui.gcmsTestsVal) 
       
    def loadDatabase(self): 
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
            
            #TODO: try to connect the each of the databases 
            #TODO: need to update the widget opening item 

            # if(databaseStatus.count() != 3): 
                
            try: 
                mainDatabasePath = self.preferences.get('databasePath') 
                officeDatabasePath = self.preferences.get('officeDbPath')
                preferencesDatabasePath = self.preferences.get('preferencesPath')
                tempPath = self.preferences.get('temp_backend_path')

                self.tempDB = Database(tempPath)
                

                # Connect the backend database (Harry Systems)
                self.db = Database(mainDatabasePath)


                # Connect the Office database (Front and Histroy Systems)
                self.officeDB = Database(officeDatabasePath)
            
                # Connect the preferences database
                self.preferencesDB = Database(preferencesDatabasePath)

                return

            except Exception as error: 
                print(error)

                if attempt == 2:
                    print("Max attempts reached. Unable to connect to databases.")
                    return
                else:
                    # Dialog popup to load the necessaary database Information for the user 
                    dialog = FileLocationDialog(self.preferences)
                    dialog.exec_()
        
          
    #******************************************************************
    #   Helper/Other Functions 
    #******************************************************************         
    #TODO: could be moved to the utiles.py 
    #TODO: find out what this does 
    
    def on_tab_pressed1(self): 
        self.ui.gcmsTestsVal.setFocus()
    
    def loadCreatePage(self): 
        print('[FUNCTION]: loadCreatePage(self)')
 
        #load the report Types
        self.ui.reportType.clear()
        self.ui.reportType.addItems(REPORTS_TYPE)
        
        #paramResults = sorted(getReportTypeList(self.db))
        paramResults = sorted(getAllParameters(self.preferencesDB))
        paramResults =  [sublist[1] for sublist in paramResults]
        
        paramResults.insert(0, "")
        self.ui.paramType.addItems(paramResults)

    def loadPreferences(self): 
        
        #load the settings information
        
        #load the create page preferences (Parameter and Report Type)
        
        #load the test pages (authors)
        
        
    
        pass; 
    
    
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
 
    def getElementLimits(self): 
        elementsQuery = 'SELECT element FROM icpLimits WHERE reportType = ? ORDER BY element ASC'
        elementWithLimits = self.db.query(elementsQuery, ('Water',))    
        
        return [item[0] for item in elementWithLimits]

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



    



