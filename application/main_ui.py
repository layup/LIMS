from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import sys 

import pandas as pd
import json
import sys 


from modules.utilities import * 
from ui.interface import Ui_MainWindow



class Mywindow(QMainWindow): 
    def __init__(self): 
        super(Mywindow, self).__init__()
        self.setGeometry(200,200,300,300)
        self.setWindowTitle('Application')
        self.initUI()
        
    def initUI(self):
        #want to be able to access if from anywhere in this class 
        self.label = QtWidgets.QLabel(self)
        self.label.setText("My First Label") 
        self.label.move(50,50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Select Dir")
        self.b1.clicked.connect(self.clicked) 
        self.b1.move(0,0)
        
        self.b2 = QtWidgets.QPushButton(self)
        self.b2.setText("upload File")
        self.b2.clicked.connect(self.clicked2)
        self.b1.move(100,0)
    
    def clicked(self): 
        #problem when we do something the width gets cut off 
        #need to add a way to update that 
        #self.label.setText('You Pressed the button')
        directory = getFileLocation()
        #scanDir(directory)
        
        #scanDir(file)
        #self.update() 

    def clicked2(self): 
        print("running clicked2")
        
        file = openFile()
        
        dataframe1 = pd.read_excel(file)
        
        
    def update(self): 
        self.label.adjustSize()

    
class MainWindow(QMainWindow):
    

    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) #self defined function that setups
        
        self.setWindowTitle("Tommy Lay") 

        
        

        #Connect the pages   
        self.ui.CreateReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.CreateReportPage))
        self.ui.NextSection.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        
        #self.ui.EditReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_2))
        self.ui.ViewReportBtn.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        #self.ui.ViewReportBtn.clicked.connect(openFile)
        
        #connect the menu bar options 
        self.showMaximized()
        #self.show()
        
        
 

def window(): 
    #global app, MainWindow 
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
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