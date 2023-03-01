#PYQT Imports 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QLineEdit, QPushButton
from PyQt5.Qt import Qt

#general Imports 
import sys 
import pandas as pd
import json
import sys 
import re 
import asyncio

from modules.utilities import * 
from interface import *
from ui.GSMS_entry_page import Ui_GS_Entry

#from ..assets.icon.icons 
    
class MainWindow(QMainWindow):
    

    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) #self defined function that setups
        
        #define other widget setups 
    
        self.setWindowTitle("Tommy Lay") 
        self.ui.LeftMenuContainerMini.hide()
        self.ui.stackedWidget.setCurrentIndex(5)
        self.ui.reportsBtn1.setChecked(True)


        #print(self.ui.page_3.ui.__dir__())
        #first page options 
        
        #self.ui.jobNumInput.textChanged.connect(lambda: print(self.ui.jobNumInput.text()))

        #connect buttons 
        self.ui.NextSection.clicked.connect(lambda: self.proceedPage())
        self.ui.clientInfoBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.dataEntryBtn.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        
        #self.ui.EditReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_2))
        #self.ui.ViewReportBtn.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        #self.ui.UploadBtn.clicked.connect(lambda: print(load_pickle('data.pickle')))
       
        #can have other keyboard modifiers as well 
        self.ui.stackedWidget.currentChanged.connect(lambda: print("Stacked Widget Changed "))
        
        #connect the menu bar options 
        #self.ui.subHeaderText.setText("Hello World")
        
        self.showMaximized()
        #self.show()


    
    ## Change QPushButton Checkable status when stackedWidget index changed
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.LeftMenuSubContainer.findChildren(QPushButton) \
                    + self.ui.LeftMenuContainerMini.findChildren(QPushButton)
        
        #print(btn_list)
        for btn in btn_list:
            #if index in [5, 6]:
            #    btn.setAutoExclusive(False)
            #    btn.setChecked(False)
            #else:
            btn.setAutoExclusive(True)

    #Define button presses
    def on_reportsBtn1_toggled(self):
        print('being pressed 1 dog')
        self.ui.stackedWidget.setCurrentIndex(0)
        
    def on_reportsBtn2_toggled(self):
        print("Being pressed")
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_createReportBtn1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        
    def on_createReportBtn2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_icpBtn1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        
    def on_icpBtn2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        
    def on_gsmsBtn1_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(3)
    
    def on_gsmsBtn2_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(3)
     
    def on_settingBtn1_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(4)
    
    def on_settingBtn2_toggled(self):
         self.ui.stackedWidget.setCurrentIndex(4)
         
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.test_method()
        if event.key() == Qt.Key_Space: 
            self.test_method()
        

    def test_method(self):
        print('Space key pressed')


    def saveJSONTest(self): 
        print("Saving json file")
        
        jsonLocation = getFileLocation()
        print(jsonLocation) 
        
        locaiton = '/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/fileLocation.json'
        
        tempDictonary = {
            "TXTLOCATION":  jsonLocation
        }
        
        #serializing json data
        json_object = json.dumps(tempDictonary, indent=1)
        
        with open(locaiton, 'w') as outfile: 
            outfile.write(json_object)
    
    def savePickle(self): 
        jsonLocation = getFileLocation()
        
        tempDictonary = {
            "JSONFileLocation":'/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/fileLocation.json', 
            "TXTDirLocation": jsonLocation 
        }
        
        save_pickle(tempDictonary)
        
    
    def proceedPage(self):
        print("running")
        print(self.ui.jobNumInput.text())
        
        #remove whitespaces 
        jobNum = self.ui.jobNumInput.text().strip()
        
        #make sure they entered all the valid information
        #have some style changes later on  
        if(re.match('^([0-9]{6})$', jobNum)): 
            print("valid job number")
            self.jobNum = jobNum; 
            #self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
            self.ui.stackedWidget.setCurrentIndex(5)
            self.ui.jobNum.setText(jobNum)
            
            #scan for user information and setup page 
            tempLocation = scanForTXTFolders(self.jobNum)
            clientInfo, sampleNames = processClientInfo(self.jobNum, tempLocation)
            
            self.clientInfo = clientInfo 
            self.sampleNames = sampleNames
            
            self.loadData()
            
            
        else: 
            print("Hello World")
            msg = QMessageBox() 
            msg.setWindowTitle("Error to procceed")
            msg.setText("Please enter a valid job number!")
            x = msg.exec_()  # this will show our messagebox
            

    def loadData(self): 
        print(self.clientInfo)
        print(self.sampleNames)
         

        
    
        
        
        
         

def window(): 
    #global app, MainWindow 
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    MainWindow = MainWindow()
    #win = Mywindow()
    #win.show()
   
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    #window()
    import sys 
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    #win = Mywindow()
    #win.show()

    #for key, value in GSMS_values.items(): 
    #    print(key, value )

    #print(len(GSMS_values))
    
    sys.exit(app.exec_())