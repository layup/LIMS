from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import sys 

from modules.utilities import * 


class Mywindow(QMainWindow): 
    def __init__(self): 
        super(Mywindow, self).__init__()
        self.setGeometry(200,200,300,300)
        self.setWindowTitle('Hello World')
        self.initUI()
        
    def initUI(self):
        #want to be able to access if from anywhere in this class 
        self.label = QtWidgets.QLabel(self)
        self.label.setText("My First Label") 
        self.label.move(50,50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Click Me")
        self.b1.clicked.connect(self.clicked) 
    
    def clicked(self): 
        #problem when we do something the width gets cut off 
        #need to add a way to update that 
        #self.label.setText('You Pressed the button')
        directory = getFiles()
        scanDir(directory)
        
        #scanDir(file)
        #self.update() 
        
    def update(self): 
        self.label.adjustSize()

    


    

def window(): 
    app = QApplication([])
    win = Mywindow()

    win.show()
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    window() 