from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDesktopWidget 

def loadReportDialog(self): 
    msgBox = QMessageBox()  
    msgBox.setText("Report Already Exists");
    msgBox.setInformativeText("Would you like to load existing report or overwrite report?");
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Yes);
    
    x = msgBox.exec_()

    if(x == QMessageBox.Yes): 
        pass
        #FIXME: load in the values as well 
    if(x == QMessageBox.No):
        pass 
    if(x == QMessageBox.Cancel):
        pass 
    
def showErrorDialog(self, errorTitle, errorMsg, detailedErrorMsg=None):
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText(errorTitle)
    msg.setInformativeText(errorMsg)
    
    if(detailedErrorMsg): 
        msg.setDetailedText(detailedErrorMsg)
        
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    retval = msg.exec_()
    print("value of pressed message box button:", retval)

def createdReportDialog(fileName): 

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText('Success')
    msg.setInformativeText(f'Report successfully created.')
        
    msg.setStandardButtons(QMessageBox.Ok )
    
    msg.exec_()
    
    


## Change QPushButton Checkable status when stackedWidget index changed
def messageBox(self):
    msgBox = QMessageBox()  
    msgBox.setText("The document has been modified.");
    msgBox.setInformativeText("Do you want to save your changes?");
    msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Save);
    #msgBox.buttonClicked.connect(self.msgbtn)
    x = msgBox.exec_()  # this will show our messagebox
    
    if(x == QMessageBox.Save): 
        self.ui.stackedWidget.setCurrentIndex(0)  
        self.activeCreation = False; 
    if(x == QMessageBox.Discard):
        self.ui.stackedWidget.setCurrentIndex(0) 
        self.activeCreation = False; 
    if(x == QMessageBox.Cancel):
        pass 
            

def deleteBox(self, title, message, action):
    msgBox = QMessageBox()  
    msgBox.setText(title);
    msgBox.setInformativeText(message);
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    x = msgBox.exec_() 
    
    if(x == QMessageBox.Yes): 
        pass
    if(x == QMessageBox.No):
        pass 

def replaceError(self,sampleName):
    msgBox = QMessageBox()  
    msgBox.setText("Duplicate Data?");
    message = 'There is sample named ' + str(sampleName) 
    
    msgBox.setInformativeText(message);
    msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save);
    msgBox.setDefaultButton(QMessageBox.Save);
    #msgBox.buttonClicked.connect(self.msgbtn)
    x = msgBox.exec_()  # this will show our messagebox
    
    if(x == QMessageBox.Save): 
        pass      

    if(x == QMessageBox.Cancel):
        pass 
    
class openJobDialog(QDialog):
    def __init__(self, jobNum, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open")
        self.setFixedSize(300, 100)
        
        self.jobNum = jobNum
        
        self.center_on_screen()


        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(f"Do you want to open job number {self.jobNum}")
        layout.addWidget(label)

        button_layout = QHBoxLayout()  # Use QHBoxLayout for horizontal arrangement
        layout.addLayout(button_layout)

        yes_button = QPushButton("Yes")
        yes_button.clicked.connect(self.accept)
        button_layout.addWidget(yes_button)

        no_button = QPushButton("No")
        no_button.clicked.connect(self.reject)
        button_layout.addWidget(no_button)


    def center_on_screen(self):
        desktop_rect = QDesktopWidget().availableGeometry(self)
        self.move(desktop_rect.center() - self.rect().center())


 