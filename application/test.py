import sys 

from PyQt5.QtWidgets import (
    QApplication, 
    QHBoxLayout, 
    QPushButton, 
    QWidget, 
    QMainWindow, 
    QFileDialog
    
)




from interface import Ui_MainWindow
from modules.ICPConverter import * 


class Window(QWidget): 
    def __init__(self): 
        super().__init__()
        self.setWindowTitle("QHBox Layout Example")
        
        layout = QHBoxLayout()
        
        layout.addWidget(QPushButton('Left-Most'),1)
        layout.addWidget(QPushButton('Center'),2)
        layout.addWidget(QPushButton('Right-Most'),1)
        
        self.setLayout(layout)


def openFile(): 
    fileName, _ = QFileDialog.getOpenFileName(None, 'Single File', '', '*.xlsx')
    print(fileName)

class MainWindow(QMainWindow):
    

    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) #self defined function that setups
        
        self.setWindowTitle("Tommy Lay") 
        

        #Connect the pages   
        self.ui.CreateReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_2))
        self.ui.EditReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.CreateReportPage))
        self.ui.ViewReportBtn.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        #self.ui.ViewReportBtn.clicked.connect(openFile)
        
        #connect the menu bar options 
        
        self.show()
        
        

    
if __name__ == "__main__": 
    ''' 
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
    '''
    
    app = QApplication(sys.argv)
    MainWindow = MainWindow()

    #MainWindow.show()

    sys.exit(app.exec_())