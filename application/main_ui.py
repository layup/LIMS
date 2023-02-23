from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox
from PyQt5.Qt import Qt

import sys 
import pandas as pd
import json
import sys 
import re 


from modules.utilities import * 
from ui.interface import Ui_MainWindow
from ui.GSMS_entry_page import Ui_GS_Entry

    
class MainWindow(QMainWindow):
    

    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) #self defined function that setups
        
        #define other widget setups 
        self.GSMSPageCreation()
        self.setWindowTitle("Tommy Lay") 


        #print(self.ui.page_3.ui.__dir__())
        #first page options 
        
        #self.ui.jobNumInput.textChanged.connect(lambda: print(self.ui.jobNumInput.text()))

        #connect menu buttons 
        self.ui.CreateReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.CreateReportPage))
        #self.ui.NextSection.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        self.ui.NextSection.clicked.connect(self.proceedPage)
        
        #self.ui.EditReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_2))
        self.ui.ViewReportBtn.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        self.ui.UploadBtn.clicked.connect(lambda: print(load_pickle('data.pickle')))
       
        #can have other keyboard modifiers as well 
        
        #connect the menu bar options 
        #self.ui.subHeaderText.setText("Hello World")
        
        self.showMaximized()
        #self.show()
    
    #later problem 
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
        
    
    
        #obj2 = load_pickle('data.pickle')
        #print(obj2)
        
    def proceedPage(self):
        print(self.ui.jobNumInput.text())
        
        #remove whitespaces 
        jobNum = self.ui.jobNumInput.text().strip()
        
        #make sure they entered all the valid information
        #have some style changes later on  
        if(re.match('^([0-9]{6})$', jobNum)): 
            print("valid job number")
            self.jobNum = jobNum; 
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
            
            #self.ui.labelJobNumHeader.setText("Hello World")
            self.ui.page_3.ui.labelJobNumHeader.setText("Job Number: " + "W" + jobNum)
            
            
            #scan for user information and setup page 

            tempLocation = scanForTXTFolders(self.jobNum)

            processClientInfo(self.jobNum, tempLocation )
            
            
            
        else: 
            msg = QMessageBox() 
            msg.setWindowTitle("Error to procceed")
            msg.setText("Please enter a valid job number!")
            x = msg.exec_()  # this will show our messagebox
            
        

    def GSMSPageCreation(self): 
        self.ui.page_3 = QtWidgets.QWidget()
        self.ui.page_3.ui = Ui_GS_Entry() 
        self.ui.page_3.ui.setupUi(self.ui.page_3)
        self.ui.page_3.setObjectName("page_3")
        self.ui.stackedWidget.addWidget(self.ui.page_3)
        
        
    def GSMS_loader(self): 
        
        return; 
        
    

        
        
            

    
        



    

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